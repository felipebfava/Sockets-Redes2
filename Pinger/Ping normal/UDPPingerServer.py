# importando bibliotecas
import random
import socket

# Cria um socket UDP
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Atribuir endereço IP e número da porta ao socket
# Usaremos a porta 12000, aceitando requisições de qualquer IP (host)
serverSocket.bind(('', 12000))

# Loop principal
while True:
    # Gerar número aleatório entre 0 e 10
    rand = random.randint(0, 10)
    
    # Receber o pacote do cliente junto com o endereço de origem
    # pacotes terão o tamanho máximo de 1024 bytes
    message, address = serverSocket.recvfrom(1024)
    
    # Coloca a mensagem recebida em maiúscula
    message = message.upper()
    
    # Se o número rand for menor que 4, consideramos que o pacote foi perdido e não respondemos
    # Logo, 40% dos pacotes serão perdidos
    if rand < 4:
        # pula a iteração atual, logo o pacote é perdido e continua o loop com o próximo
        continue

    # Caso contrário do if, o servidor responde, logo o pacote é recebido
    serverSocket.sendto(message, address)