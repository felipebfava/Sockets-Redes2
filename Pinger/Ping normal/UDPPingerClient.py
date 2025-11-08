import socket
import time

# configuraçãos de conexão com o servidor
host = "localhost"
port = 12000

# criação do socket UDP
cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# define um tempo máximo de espera de resposta do servidor (timeout)
cliente.settimeout(1) # tempo de 1 segundo

# Variáveis para as estatísticas
pacotes_enviados = 10
pacotes_recebidos = 0

# irá guardar os tempos para fazer o cálculo do mínimo, máximo e média
tempos_rtt = []

print(f"\nEnviando 10 pings para {host}:{port}\n")

# Loop que envia os 10 pings, vai de 1 até 11
for i in range (1, pacotes_enviados + 1):
    # Mensagem que será enviada
    mensagem_envio = f"Ping{i} {time.time()}"
    inicio = time.time() # Marca o tempo do envio

    try:
        # Envia a mensagem para o servidor
        cliente.sendto(mensagem_envio.encode(), (host, port))
        print(f"Ping {i} {inicio:.3f}")

        # Aguarda resposta do servidor (até o timeout definido)
        #recvfrom recebe os dados da mensagem em bytes
        resposta_bytes, endereco_ip = cliente.recvfrom(1024)
        fim = time.time()
        
        # calcula
        rtt = fim - inicio
        tempos_rtt.append(rtt)
        pacotes_recebidos += 1

        # transforma a mensagem de bytes para string
        # padrão UTF-8 usado para encode e decode
        print(f"Resposta do servidor: {resposta_bytes.decode()}")
        print(f"RTT: {rtt:.4f} segundos\n")

    except socket.timeout:
        # Se o tempo de espera exceder, considera pacote perdido
        print(f"Request timed out (Ping {i})\n")

# Após enviar os 10 pings, calcula as estatísticas
print(f"Estatísticas do Ping para {socket.gethostbyname(host)}:")

pacotes_perdidos = pacotes_enviados - pacotes_recebidos
porcen_perda_pacotes = pacotes_perdidos / pacotes_enviados * 100

print(f"\tPacotes: Enviados = {pacotes_enviados}, Recebidos = {pacotes_recebidos}, Perdidos = {pacotes_perdidos}\
 ({porcen_perda_pacotes:.0f}% perda),")

if tempos_rtt:
    # calcula as estatísticas se existir
    tempo_min = min(tempos_rtt)
    tempo_max = max(tempos_rtt)
    tempo_media = sum(tempos_rtt) / len(tempos_rtt)
    
    print("Aproximado Round Trip Time em segundos:")
    print(f"\tMínimo: {tempo_min:.4f}s, Máximo: {tempo_max:.4f}s, Média: {tempo_media:.4f}s\n")
else:
    print("Nenhum pacote recebido — não há tempos de RTT para calcular.")

# Fecha o socket cliente
cliente.close()