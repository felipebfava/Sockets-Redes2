import os
import sys
import socket
import struct # para juntar as partes do pacote (montar o pacote ICMP) 
import time
import select

# ICMP_ECHO_REQUEST é o tipo da mensagem ICMP usada pelo comando ping (echo request)
# isso é, enviará 8 pings para o destino
ICMP_ECHO_REQUEST = 8

# Função para calcular o checksum dos pacotes ICMP (protocolo possui esse campo para a integridade dos dados)
def checksum(source_string): # recebe uma sequencia em bytes
    countTo = (int(len(source_string) / 2)) * 2 # para processar palavras de 2 em 2 bytes
    sum = 0   # armazena a soma dos blocos de 16 bits
    count = 0

    while count < countTo: # percorre o vetor de 2 em 2 bytes
        # [count + 1] é o byte mais significativo (MSB) deslocado 8 bits a esquerda (*256)
        # [count] é byte menos significativo (LSB)
        thisVal = source_string[count + 1] * 256 + source_string[count]

        sum = sum + thisVal
        sum = sum & 0xffffffff # garante que sum não ultrapasse 32 bits (0xffffffff)
        count += 2 # avança para o proximo par de bytes
    
    if countTo < len(source_string): # se o número de bytes for ímpar
        sum = sum + source_string[len(source_string) - 1] # ele é somado ao total
        sum = sum & 0xffffffff # mantém o valor dentro de 32 bits
    
    sum = (sum >> 16) + (sum & 0xffff) # soma do carry
    sum = sum + (sum >> 16) # repete caso tenha mais carry
    answer = ~sum #  inverte os bits (complemento de 1)
    answer = answer & 0xffff # o resultado final tem 16 bits
    answer = answer >> 8 | (answer << 8 & 0xff00) # inverte a ordem dos bytes
    return answer

# Função responsável por enviar um pacote ICMP Echo Request para o destino (PING)
def sendOnePing(sock, dest_addr, ID, seq_number):
    # gethostbyname resolve o endereço (nome) para IP a partir (antes) do cache local, depois servidor DNS através de sua placa de rede
    dest_addr = socket.gethostbyname(dest_addr)
    my_checksum = 0
    
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, seq_number)
    # "bbHHh" cada letra possui um tamanho (e significado) que somados é o tamanho do cabeçalho ICMP
    # significa:
    # "b" 1 byte - (tipo) tipo da mensagem (8 = Echo Request, 0 = Echo Reply) +
    # "b" 1 byte - (código) para qualquer código de erro +
    # "H" 2 bytes - (checksum) verifica integridade +
    # "H" 2 bytes - (identificador) id que enviou o ping +
    # "h" 2 bytes - (número de sequencia)
    #   = 8 bytes 
    
    # dados do pacote com timestamp para medir o tempo de ida e volta (RTT)
    # timestamp é o tempo transcorrido a partir do instante inicial
    data = struct.pack("d", time.time())

    # Calcula o checksum considerando o cabeçalho e os dados
    my_checksum = checksum(header + data)
    
    # Recria o cabeçalho já com o checksum correto
    # socket.htons converte o checksum da ordem de bytes do host para a ordem de bytes de rede (big-endian)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, seq_number)
    
    # o pacote será a junção do cabeçalho + os dados
    packet = header + data

    # Envia o pacote (em bytes) formado usando o socket criado
    sock.sendto(packet, (dest_addr, 1))

# Função responsável por receber um pacote ICMP Echo Reply do destino (PONG)
def receiveOnePing(sock, ID, timeout):
    timeLeft = timeout
    
    while True:
        startedSelect = time.time()
        ready = select.select([sock], [], [], timeLeft)
        timeInSelect = (time.time() - startedSelect)
        if ready[0] == []:
            return None, None  # Adicionado segundo valor (erro)
        timeReceived = time.time()
        recPacket, addr = sock.recvfrom(1024) # retorna o pacote em bytes e o endereço
        
        # Pula o cabeçalho IP (20 bytes iniciais) e pega só o cabeçalho ICMP (8 bytes)
        # o cabeçalho IP pode ter até 60 bytes enquanto IPv6 tem tamanho fixo de 40 bytes
        icmpHeader = recPacket[20:28] # faço um corte na string-bytes
        
        type, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)
        
        # verificação/ tratamento de erro de códigos de erro ICMP
        # Tipo 0: Echo Reply, lugar do ping normal
        if type == 0 and packetID == ID:
            bytesInDouble = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
            return timeReceived - timeSent, None
        # Tipo 3: Destination Unreachable
        elif type == 3:
            # Exibe mensagem específica conforme o código de erro
            if code == 0:
                return None, "Rede de Destino Inalcançável"
            elif code == 1:
                return None, "Host de Destino Inalcançável"
            else:
                return None, f"Destino inalcançável, código de erro ICMP: {code}"
        
        timeLeft = timeLeft - timeInSelect
        if timeLeft <= 0:
            return None, None
    
# Função que combina envio e recebimento de um único pacote ping, retornando o tempo de resposta
def doOnePing(dest_addr, timeout, seq_number, ID): 
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
        # --- POR QUE USAR raw sockets ---
        # Precisamos de um socket de baixo nível (raw socket) para enviar e receber pacotes ICMP manualmente,
        # já que ICMP não trabalha com portas (como TCP ou UDP) e é tratado no nível de IP (camada de rede).
        # Isso exige privilégios de superusuário/admin (por questões de segurança)
        # sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
        # parâmetros: AF_INET = IPv4, SOCK_RAW = socket cru, ICMP protocol

    except PermissionError:
        print("Você precisa rodar como root/administrador!")
        sys.exit() # encerra a execução do programa
    
    sendOnePing(sock, dest_addr, ID, seq_number)
    delay, icmp_error = receiveOnePing(sock, ID, timeout)
    sock.close()
    return delay, icmp_error

# Função principal que executa pings conforme "count", calcula estatísticas e imprime os resultados
def ping(host, count=4, timeout=1):
    print(f"Pinging {host} with Python ICMP:")
    
    delays = []
    packet_lost = 0 # quantidade de pacotes que serão perdidos
    ID = os.getpid() & 0xFFFF  # identificador único do processo, para distinguir pacotes
    
    for seq in range(count):
        delay, icmp_error = doOnePing(host, timeout, seq + 1, ID)
        if delay is not None:
            print(f"Reply from {host}: seq={seq+1} time={round(delay*1000, 2)} ms")
            delays.append(delay)
        elif icmp_error is not None:
            print(f"Erro ICMP para seq {seq+1}: {icmp_error}")
            packet_lost += 1
        else:
            print(f"Request timed out for seq {seq+1}.")
            packet_lost += 1
        time.sleep(1)
    
    # Estatísticas após os pings
    print("\n--- Ping statistics ---")
    sent = count
    received = len(delays)
    loss = ((sent - received) / sent) * 100
    print(f"{sent} packets transmitted, {received} received, {loss}% packet loss")
    
    # caso tenha pacotes recebidos
    if received:
        min_delay = round(min(delays)*1000, 2) # rtt mínimo em ms
        max_delay = round(max(delays)*1000, 2) # rtt máximo em ms
        avg_delay = round(sum(delays)/received*1000, 2) # rtt médio em ms
        stddev = round((sum((d-avg_delay/1000)**2 for d in delays)/received)**0.5*1000, 2) # desvio padrão em ms
        print(f"rtt min/avg/max/stddev = {min_delay}/{avg_delay}/{max_delay}/{stddev} ms" )
    else:
        print("No packets received.")

if __name__ == "__main__":
    # Testando com 4 IP´s diferentes
    hosts = ['127.0.0.1', '8.8.8.8', 'www.alibaba.com', 'www.ufrj.br']
    for host in hosts:
        ping(host)
        print("\n")
