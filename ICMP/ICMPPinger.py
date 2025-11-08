import os
import sys
import socket
import struct
import time
import select

# ICMP_ECHO_REQUEST é o "tipo" da mensagem ICMP usada pelo comando ping (echo request)
ICMP_ECHO_REQUEST = 8

# Função para calcular o checksum dos pacotes ICMP (protocolo exige esse campo para integridade dos dados)
def checksum(source_string):
    countTo = (int(len(source_string) / 2)) * 2
    sum = 0
    count = 0
    while count < countTo:
        thisVal = source_string[count + 1] * 256 + source_string[count]
        sum = sum + thisVal
        sum = sum & 0xffffffff
        count += 2
    if countTo < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xffffffff
    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

# Função responsável por enviar um pacote ICMP Echo Request para o destino
def sendOnePing(sock, dest_addr, ID, seq_number):
    dest_addr = socket.gethostbyname(dest_addr)
    my_checksum = 0
    # O cabeçalho ICMP tem: tipo, código, checksum, identificador e número de sequência
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, seq_number)
    # Adicionamos dados ao pacote (timestamp) para medir o tempo de ida e volta (RTT)
    data = struct.pack("d", time.time())
    # Calcula o checksum considerando o cabeçalho e os dados
    my_checksum = checksum(header + data)
    # Recria o cabeçalho já com o checksum correto
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, seq_number)
    packet = header + data
    # Envia o pacote usando o socket criado
    sock.sendto(packet, (dest_addr, 1))

# Função responsável por receber um pacote ICMP Echo Reply do destino.
def receiveOnePing(sock, ID, timeout):
    timeLeft = timeout
    while True:
        startedSelect = time.time()
        ready = select.select([sock], [], [], timeLeft)
        timeInSelect = (time.time() - startedSelect)
        if ready[0] == []:
            return None, None  # Adicionado segundo valor (erro)
        timeReceived = time.time()
        recPacket, addr = sock.recvfrom(1024)
        # Pula o cabeçalho IP (20 bytes iniciais) e pega só o cabeçalho ICMP (8 bytes)
        icmpHeader = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)
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
        # Outros erros ICMP podem ser tratados aqui
        timeLeft = timeLeft - timeInSelect
        if timeLeft <= 0:
            return None, None
# --- POR QUE USAR raw sockets ---
        # Precisamos de um socket de baixo nível (raw socket) para enviar e receber pacotes ICMP manualmente,
        # já que ICMP não trabalha com portas (como TCP ou UDP) e é tratado no nível de IP.
        # Isso exige privilégios de superusuário/admin (por questões de segurança)
        # sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
        # parâmetros: AF_INET = IPv4, SOCK_RAW = socket cru, ICMP protocol
    
# Função que combina envio e recebimento de um único pacote ping, retornando o tempo de resposta
def doOnePing(dest_addr, timeout, seq_number, ID):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    except PermissionError:
        print("Você precisa rodar como root/administrador!")
        sys.exit()
    sendOnePing(sock, dest_addr, ID, seq_number)
    delay, icmp_error = receiveOnePing(sock, ID, timeout)
    sock.close()
    return delay, icmp_error

# Função principal que executa vários pings, calcula estatísticas e imprime os resultados
def ping(host, count=4, timeout=1):
    print(f"Pinging {host} with Python ICMP:")
    delays = []
    packet_lost = 0
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
    # Impressão de estatísticas após os pings
    print("\n--- Ping statistics ---")
    sent = count
    received = len(delays)
    loss = ((sent - received) / sent) * 100
    print(f"{sent} packets transmitted, {received} received, {loss}% packet loss")
    if received:
        min_delay = round(min(delays)*1000, 2)
        max_delay = round(max(delays)*1000, 2)
        avg_delay = round(sum(delays)/received*1000, 2)
        stddev = round((sum((d-avg_delay/1000)**2 for d in delays)/received)**0.5*1000, 2)
        print(f"rtt min/avg/max/stddev = {min_delay}/{avg_delay}/{max_delay}/{stddev} ms" )
    else:
        print("No packets received.")

if __name__ == "__main__":
    # Teste: Altere os hosts para quatro continentes diferentes conforme sua apresentação!
    hosts = ['127.0.0.1', '8.8.8.8', 'www.alibaba.com', 'www.ufrj.br']
    for host in hosts:
        ping(host)
        print("\n")
