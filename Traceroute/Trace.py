import os
import sys
import socket
import struct
import time
import select

ICMP_ECHO_REQUEST = 8 # o traceroute usa do ICMP porém com algo a mais, que é a resolução dos nomes do meio do caminho (a cada salto)
MAX_HOPS = 30 # número máximo de saltos / resoluções possíveis
TIMEOUT = 5.0 # para cada request que demorar mais de 5 segundos o código retorna request timed out
TRIES = 3 # qtd de tentativas de envio e recebimento

# além disso, é bom lembrar que o nosso TTL (time to live) está aumentando ao invés de decrescer quando passa por cada salto

# Função para calcular o checksum dos pacotes ICMP (integridade dos dados)
# mesmo usado no ICMPPinger
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

# Função para construir o pacote ICMP Echo Request com checksum e timestamp
# parecido com o encontrado no ICMPPinger - só muda o que a função retorna
def build_packet(ID, seq_number):
    
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
    
    data = struct.pack("d", time.time())
    my_checksum = checksum(header + data)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, seq_number)
    packet = header + data
    return packet

# Função principal do traceroute
def get_route(hostname):
    destAddr = socket.gethostbyname(hostname) # destAddr é o endereço IP do host
    print(f"\nTraceroute to {hostname} ({destAddr}), {MAX_HOPS} hops max")

    # ID do processo atual
    ID = os.getpid() & 0xFFFF # operação AND obtem os 16 bits (2 bytes) menos significativos do ID do processo
    # ajuda a identificar qual pacote ICMP corresponde a resposta recebida

    seq_number = 1 # identifica a ordem das requisições dos pacotes ICMP enviados individualmente

    for ttl in range(1, MAX_HOPS + 1):
        # o ttl é incrementado diferente das implementações comuns que decrementam ele
        # isso é usado para fazer exploração da rede sem definir um limite de saltos até o destino

        for tries in range(TRIES):
            try:
                # Cria socket raw ICMP - pois o traceroute usa um socket ICMP
                mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
                
                # Defini TTL no socket para controlar saltos
                mySocket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl) # setsockopt é utilizado para configurar opções do socket
                # SOL_IP é um identificador relacionado ao nível do protocolo IP, necessário para definir opções de controle do IP
                #IP_TTL define o time to live no cabeçalho IP, controlando o número máximo de saltos

                mySocket.settimeout(TIMEOUT)

                packet = build_packet(ID, seq_number)
                seq_number += 1

                start_time = time.time()
                mySocket.sendto(packet, (destAddr, 1)) #0

                ready = select.select([mySocket], [], [], TIMEOUT)
                #select.select monitora operações de E/S de baixo nível de cada socket
                # recebe 3 listas de socket
                # 1 - para leitura, confere se tem algum pacote ICMP chegando
                # 2 - para escrita, confere se os sockets estãos prontos para enviar os dados
                # 3 - para erros, contem os socket para detectar erros
                # 4 - timeout, quanto tempo teremos que esperar o pacote ICMP chegar
                # nesse caso, só queremos ler os dados dos pacotes que estão chegando
                
                #print("\n", ready, "\n") # mostre esse comando sendo executado
                
                # saída esperada <socket.socket fd=3, family=2, type=3, proto=1, laddr=('0.0.0.0', 1)>
                # fd (file descriptor) - socket é tratado com um arquivo onde o SO pode fazer modificações, fd=3 é o id usado internamente para esse socket
                # family=2, se refere que o socket é da familia AF_INET, ou seja, usa IPv4
                # type=3, se refere que o socket é do tipo SOCK_RAW
                # proto=1, significa que o protocolo usado para o socket é o ICMP
                # laddr significa endereço e porta do lado local da conexão
                # 0.0.0.0 indica que o socket está escutando em todas as interfaces de rede
                # o número 1 representa a porta local, para sockets raw não é relevante.

                #print(f"TTL={ttl} Packet sent to {destAddr}, waiting for ICMP reply...\n")

                # Checar se o select retornou resultados
                if ready[0] == []:  # Timeout
                    print(f"{ttl}\t* * * Request timed out.")
                else:
                    recvPacket, addr = mySocket.recvfrom(1024)

                    timeReceived = time.time()
                    # os primeiros 20 bytes de um pacote IP é o cabeçalho IP, o cabeçalho ICMP começa após os 20 primeiros bytes
                    icmp_header = recvPacket[20:28] # faço um corte na string

                    # extrai os dados do cabeçalho ICMP
                    type, code, checksum_recv, packetID, sequence = struct.unpack("bbHHh", icmp_header)

                    # não é chamado a função checksum após o recebimento, pois entende-se que o dispositivo / SO já resolveu para nós
                    # por isso o checksum é calculado antes de enviar o pacote somente

                    print(f"TTL={ttl} Received ICMP type={type}, code={code} from {addr[0]}\n")

                    # Obter host do IP
                    try:
                        # consulta reversa de dns para obter o nome do host a partir de seu IP
                        host = socket.gethostbyaddr(addr[0])[0] # [0] obtem o nome do host do primeiro endereço IP da lista addr
                        # retorna o hostname - nome do host, aliaslist - lista de apelidos alternativos para o mesmo endereço, ipaddrlist - lista de IP para o mesmo endereço 
                    except socket.herror:
                        host = addr[0]  # Sem resolução de nome

                    rtt = (timeReceived - start_time) * 1000 # em ms

                    # outros códigos possíveis para type:
                    # type 8 - Echo Request (Solicitação de Ping)
                    # type 3 e code 3 - Destination Unreachable – Port Unreachable (Destino Inacessível – Porta Inacessível), o destino é alcançável, mas a porta de destino não está aberta ou está bloqueada.

                    if type == 11:  # Time Exceeded (Tempo Excedido)
                        print(f"{ttl}\t{host} ({addr[0]})  rtt={round(rtt)} ms")
                    elif type == 3:  # Destination Unreachable (Destino Inacessível)
                        print(f"{ttl}\t{host} ({addr[0]})  Destination Unreachable")
                    elif type == 0:  # Echo Reply (resposta do ping) - destino alcançado - aparece no último TTL / salto
                        print(f"{ttl}\t{host} ({addr[0]})  rtt={round(rtt)} ms")
                        print("Trace complete.")
                        mySocket.close()
                        return
                    else:
                        print(f"{ttl}\tError: ICMP type {type} code {code}")

                mySocket.close()

            # tratamento de exceções
            except socket.timeout:
                print(f"{ttl}\t* * * Request timed out.")
            except PermissionError:
                print("Você precisa executar este programa como root/administrador para usar sockets RAW.")
                sys.exit()
            except Exception as e:
                print(f"Erro: {e}")
                mySocket.close()
                return

if __name__ == "__main__":
    get_route("www.ifc.edu.br")
    #get_route("8.8.8.8")
    #get_route("www.alibaba.com")
    #get_route("www.reddit.com")
    #get_route("www3.nhk.or.jp") # site japonês
