# socket cliente

import socket

host = "localhost"
port = 12000

cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# traduz um nome de host para endereço IPv4
# localhost será convertido para 127.0.0.1
print(socket.gethostbyname(host))

print(socket.gethostname())


def calcular_checksum(mensagem: bytes):

    # se o tamanho da mensagem for ímpar    
    if len(mensagem) % 2 != 0:
        # soma a mensagem com um caracter do tipo byte nulo '0'
        mensagem += b'\x00'

    soma = 0

    # loop que começa em 0 vai até o tamanho da mensagem pulando de 2 em 2
    for i in range(0, len(mensagem), 2):
        palavra = (mensagem[i] << 8) + mensagem[i+1]
        soma += palavra
        soma = (soma & 0xFFFF) + (soma >> 16) # adiciona carry-out
    
    checksum = ~soma & 0xFFFF # complemento de 1
    return checksum

print(socket.setdefaulttimeout(1000))

while True:
    mensagem_envio = input("Digite a mensagem: ")
    
    # checksum precisa ser feito antes de enviar a mensagem ao servidor
    
    # converte a mensagem_envio em partes de 16 bits
    # somar com o complemento de 1
    # adicionar carry-out à soma
    # calcular o complemento de 1 do resultado final
    # converte para string novamente e envia ao servidor

    cliente.sendto(mensagem_envio.encode(), (host, port))

    #recvfrom recebe os dados em bytes
    mensagem_bytes, endereco_ip = cliente.recvfrom(2048)
    
    # checksum precisa ser refeito ao receber a mensagem

    print(mensagem_bytes.decode())

    # essa verificação precisa ser no final
    if mensagem_envio.lower() == "sair":
        socket.close()
        False