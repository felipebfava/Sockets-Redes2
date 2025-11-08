# socket cliente

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