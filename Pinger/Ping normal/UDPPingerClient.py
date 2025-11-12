import socket
import time

# configuraçãos de conexão com o servidor, tupla IP - PORTA
# a biblioteca socket resolve um domínio por DNS via sua placa de rede interna
host = "localhost" # esse nome será resolvido para um IP - 127.0.0.1
port = 12000 # porta qualquer que não entre em conflito com as portas bem conhecidas (0 - 1023)

# criação do socket UDP (SOCK_DGRAM) usando IPv4 (AF_INET) pois para o ping não necessita de segurança e queremos pouca sobrecarga de pacote
# primeiro parametro define o domínio/família, segundo o tipo/protocolo usado
# tipos de dominio de socket: TCP (SOCK_STREAM), UDP (SOCK_DGRAM), CRU (SOCK_RAW)
# tipos de familia de socket: IPv4 (AF_INET), IPv6 (AF_INET6)
# exemplo cliente = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# define um tempo máximo de espera de resposta do servidor (timeout)
cliente.settimeout(1) # tempo de 1 segundo

# Variáveis para as estatísticas
pacotes_enviados = 10
pacotes_recebidos = 0

# irá guardar os tempos de rtt (round trip time) - tempo de ida e volta - para fazer o cálculo do mínimo, máximo e média
# isso é, o tempo em que o ping demora para ir de um ponto A ao ponto B, com isso consigo saber a saúde da conexão
# consigo verificar a conectividade básica das camadas OSI e a qualidade da comunicação
tempos_rtt = []


print(f"\nEnviando 10 pings para {host}:{port}\n")

# Loop que envia os 10 pings, vai de 1 até 11
for i in range (1, pacotes_enviados + 1):

    # formato da Mensagem que será enviada
    inicio = time.time() # Marca o tempo de início do envio
    hora_formatada = time.strftime('%H:%M:%S', time.localtime(inicio))
    mensagem_envio = f"Ping {i} enviado em {hora_formatada}"

    try:

        # Envia a mensagem para o servidor junto com a tupla de endereço
        cliente.sendto(mensagem_envio.encode(), (host, port))
        print(mensagem_envio)
        

        # Aguarda resposta do servidor (até o timeout definido)
        # recebemos de recvfrom a resposta em bytes e o endereço IP (a tupla que enviamos)
        resposta_bytes, endereco_ip = cliente.recvfrom(1024)

        fim = time.time() # Marca o tempo de fim do envio
        
        # calcula o rtt
        rtt = fim - inicio
        tempos_rtt.append(rtt)
        pacotes_recebidos += 1

        # converte rtt para milissegundos para a exibição
        rtt_ms = rtt * 1000

        # transforma a mensagem de bytes para string
        # padrão UTF-8 usado para encode e decode
        mensagem_recebida = resposta_bytes.decode()              
        print(f"Resposta do servidor: {mensagem_recebida}")
        print(f"RTT: {rtt_ms:.2f} ms\n")

    # exceção caso o ping não seja recebido
    except socket.timeout:
        # Se o tempo de espera exceder, considera pacote perdido
        print(f"Request timed out (Ping {i})\n")

# Após enviar os 10 pings, calcula as estatísticas
# gethostbyname utiliza da sua placa de rede para resolver o nome
print(f"Estatísticas do Ping para {socket.gethostbyname(host)}:")

pacotes_perdidos = pacotes_enviados - pacotes_recebidos
porcen_perda_pacotes = pacotes_perdidos / pacotes_enviados * 100

print(f"\tPacotes: Enviados = {pacotes_enviados}, Recebidos = {pacotes_recebidos}, Perdidos = {pacotes_perdidos}\
 ({porcen_perda_pacotes:.0f}% perda),")

# calcula as estatísticas se existir - diferente de vazio/nulo
if tempos_rtt:
    tempo_min = min(tempos_rtt) * 1000
    tempo_max = max(tempos_rtt) * 1000
    tempo_media = (sum(tempos_rtt) / len(tempos_rtt)) * 1000
    
    print("Aproximado Round Trip Time em milissegundos:")
    print(f"\tMínimo: {tempo_min:.2f} ms, Máximo: {tempo_max:.2f} ms, Média: {tempo_media:.2f} ms\n")
else:
    print("Nenhum pacote recebido — não há tempos de RTT para calcular.")

# Fecha o socket cliente
cliente.close()
