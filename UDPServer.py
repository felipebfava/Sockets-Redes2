# socket servidor

import socket

servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# host '0.0.0.0' na porta 12000
servidor.bind(('', 12000))

while True:
    mensagem_bytes, endereco_ip_cliente = servidor.recvfrom(2048)
    mensagem_resposta = mensagem_bytes.decode().upper()

    # checksum precisa ser feito antes de enviar a mensagem de volta ao cliente

    servidor.sendto(mensagem_resposta.encode(), endereco_ip_cliente)
    print(mensagem_resposta)
    
    if mensagem_resposta.lower() == "sair":
        socket.close()
        False