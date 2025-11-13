import os
import sys
import socket
import struct
import time
import select

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 5.0
TRIES = 2

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
# parecido com o encontrado no ICMPPinger
def build_packet(ID, seq_number):
    my_checksum = 0
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, seq_number)
    data = struct.pack("d", time.time())

    my_checksum = checksum(header + data)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, seq_number)
    packet = header + data
    return packet

# Função principal do traceroute
def get_route(hostname):
    destAddr = socket.gethostbyname(hostname) # destAddr é o endereço IP do host
    print(f"Traceroute to {hostname} ({destAddr}), {MAX_HOPS} hops max")

    ID = os.getpid() & 0xFFFF
    seq_number = 1

    for ttl in range(1, MAX_HOPS + 1):
        for tries in range(TRIES):
            try:
                # Criar socket raw ICMP
                mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
                
                # Definir TTL no socket para controlar saltos
                mySocket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
                mySocket.settimeout(TIMEOUT)

                packet = build_packet(ID, seq_number)
                seq_number += 1

                start_time = time.time()
                mySocket.sendto(packet, (destAddr, 1)) #0

                ready = select.select([mySocket], [], [], TIMEOUT)
                
                # erro nesse if-else
                # você está chamando o recvfrom() apenas na cláusula else, ou seja, somente se o select indicou que o socket está pronto para leitura (ou seja, há dados). Quando ready[0] é vazio ([]), significa que o select expirou o timeout e não detectou dados prontos, então você imprime que houve timeout e segue o laço.
                # No entanto, o que pode estar acontecendo no seu caso é que, mesmo após o select indicar socket pronto, o recvfrom() está recebendo pacotes que não são a resposta esperada para o pacote ICMP enviado, ou pacotes muito antigos, ou que o select está retornando "pronto" mas recvfrom está bloqueando ou causando comportamento inesperado.
                # Além disso, seu código original tem um trecho estranho que tenta chamar recvfrom mesmo quando ready está vazio — isso pode causar um bloqueio ou erro. Isso precisa ser corrigido para garantir que você só chame recvfrom se select indicar que o socket está pronto.
                
                print(ready)
                print(f"TTL={ttl} Packet sent to {destAddr}, waiting for ICMP reply...")
     
                if ready[0] == []:  # Timeout
                    print(f"{ttl}\t* * * Request timed out.")
                else:
                    recvPacket, addr = mySocket.recvfrom(1024)

                    timeReceived = time.time()
                    icmp_header = recvPacket[20:28]

                    type, code, checksum_recv, packetID, sequence = struct.unpack("bbHHh", icmp_header)

                    print(f"Received ICMP type={type}, code={code} from {addr[0]}")

                    # Obter host do IP
                    try:
                        host = socket.gethostbyaddr(addr[0])[0]
                    except socket.herror:
                        host = addr[0]  # Sem resolução de nome

                    rtt = (timeReceived - start_time) * 1000  # em ms

                    if type == 11:  # Time Exceeded
                        print(f"{ttl}\t{host} ({addr[0]})  rtt={round(rtt)} ms")
                    elif type == 3:  # Destination Unreachable
                        print(f"{ttl}\t{host} ({addr[0]})  Destination Unreachable")
                    elif type == 0:  # Echo Reply - destino alcançado
                        print(f"{ttl}\t{host} ({addr[0]})  rtt={round(rtt)} ms")
                        print("Trace complete.")
                        mySocket.close()
                        return
                    else:
                        print(f"{ttl}\tError: ICMP type {type} code {code}")

                mySocket.close()
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
    # Exemplo de uso
    #get_route("www.ifc.edu.br")
    get_route("8.8.8.8")
