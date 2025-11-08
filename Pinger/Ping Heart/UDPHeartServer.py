# importando bibliotecas
import socket
import time

# Cria um socket UDP
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Atribuir endereço IP e número da porta ao socket
# Usaremos a porta 12000, aceitando requisições de qualquer IP "0.0.0.0"
serverSocket.bind(('', 12000))

print("Servidor UDP Heartbeat iniciado. Aguardando pacotes...\n")

ultimo_seq = 0
ultimo_recebimento = time.time()

# Define um tempo máximo de 3 segundos sem receber nenhum pacote
TIMEOUT_CLIENTE = 3

# Loop principal
while True:

    serverSocket.settimeout(1)  # checa a cada 1 segundo
    
    try:
        # Receber o pacote do cliente junto com o endereço de origem
        # pacotes terão o tamanho máximo de 1024 bytes
        message, address = serverSocket.recvfrom(1024)
        agora = time.time()
        ultimo_recebimento = agora

        # decodifica a mesagem
        msg_decod = message.decode()
        
        # vamos dividir a mensagem em partes
        partes = msg_decod.split()

        if len(partes) >= 3:
            tipo = partes[0]
            sequencia = int(partes[1])
            horario_cliente = float(partes[2])

            # calcula a diferença entre a hora do servidor e a recebida do cliente
            diferenca = (agora - horario_cliente) * 1000 # em milissegundos

            if sequencia - ultimo_seq > 1:
                print(f"[!] Pacotes perdidos detectados: {sequencia - ultimo_seq - 1}")
            
            print(f"Heartbeat #{sequencia} recebido de {address}")
            print(f"Diferença de tempo (cliente-servidor): {diferenca:.2f} ms\n")
            
            ultimo_seq = sequencia
        else:
            print(f"Mensagem inválida recebida: {msg_decod}")

    except socket.timeout:
        # se não receber nada por muito tempo, o lado cliente pode ter parado de mandar mensagem
        if time.time() - ultimo_recebimento > TIMEOUT_CLIENTE:
            print("Nenhum heartbeat recebido nos últimos 3s.\n")
            ultimo_recebimento = time.time()  # evita spam contínuo
        