# socket cliente
# UDP Heartbeat implementa um mecanismo de keep-alive que são os pacotes de "verificação" mandados de maneira periódica
# serve para garantir que a conexão esteja ativa em conexões de longa duração
# ao contrário do UDP, Heartbeat oferece uma forma de verificar se a conexão ou o servidor ainda está funcionando, mesmo sem uma conexão persistente como o TCP
# quando o servidor calcula o tempo dos pacotes, se der timeout, ele sabe que houve falha na comunicação, o cliente não está mais ativo ou que houve problema na rede
# monitoramento ativo
# O TCP possui uma implementação keep-alive que envia pacotes de "verificação" para saber se a conexão ainda está ativa.

import socket
import time

host = "localhost"
port = 12000

cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Enviando heartbeats para {host}:{port}...\n")

# quantidade de heartbeats
num_heartbeats = 10
intervalo = 1  # segundos entre envios

for sequencia in range(1, num_heartbeats + 1):
    horario_atual = time.time()
    mensagem = f"Heartbeat {sequencia} {horario_atual}"

    cliente.sendto(mensagem.encode(), (host, port))
    print(f"Heartbeat #{sequencia} enviado às {time.ctime(horario_atual)}")

    time.sleep(intervalo)

print("\nTodos os heartbeats foram enviados.")
cliente.close()
