import ssl
from socket import *


# Mensagem a ser enviada no e-mail
msg = "\r\n Eu amo redes de computadores!"
endmsg = "\r\n.\r\n"


# Usamos o servidor de e-mail do Google
mailserver = "smtp.gmail.com"
porta = 587 # porta padrão para o serviço de SMTP com TLS, porta 465 para SSl


# Cria o socket cliente usando TCP IP e estabelece comunicação com o servidor de e-mail
clientSocket = socket(AF_INET, SOCK_STREAM)


# abre a conexão com o par/tupla (ip, porta)
# nesse caso o ip é um endereço que será resolvido por DNS
clientSocket.connect((mailserver, porta))


# Recebe a resposta do servidor deixando até 1024 bytes reservados para a resposta
recv = clientSocket.recv(1024).decode()
print(recv)


# pegamos os 3 primeiros caracteres da resposta
# código 220 - Serviço pronto - usado na mensagem inicial


# resposta:
# 220 smtp.gmail.com ESMTP 8926c6da1cb9f-58f729ce076sm6785550173.55 - gsmtp
# 220 resposta recebida do servidor.
# Motivo o Google Colab permite somente o envio do HELO por SMTP e proibe o resto
if recv[:3] != '220':
    print('220 resposta não recebida do servidor.')
else:
    print('220 resposta recebida do servidor.\n')


# Enviar comando HELO e imprimir a resposta do servidor.
heloCommand = 'HELO Felipe\r\n'
clientSocket.send(heloCommand.encode())
recvHelo = clientSocket.recv(1024).decode()
print(recvHelo)

# pegamos os 3 primeiros caracteres da resposta
# código 250 - ação solicitada completada com sucesso
if recvHelo[:3] != '250':
    print('250 resposta não recebida para HELO.')
else:
    print('250 resposta recebida do servidor para HELO.\n')


# Necessário reenviar o HELO, porém versão moderna EHLO
ehloCommand = 'EHLO Felipe\r\n'
clientSocket.send(ehloCommand.encode())
recvEhlo = clientSocket.recv(1024).decode()
print(recvEhlo)
if recvEhlo[:3] != '250':
    print('250 resposta não recebida para EHLO antes do STARTTLS.')
else:
    print('250 resposta recebida do servidor para EHLO antes do STARTTLS.\n')


# necessário adicionar autenticação de segurança com TLS ou SSL antes do MAIL FROM
# Envia STARTTLS solicitando conexão segura
starttlsComand = 'STARTTLS\r\n'
clientSocket.send(starttlsComand.encode())
recvStarttls = clientSocket.recv(1024).decode()
print(recvStarttls)


# pegamos os 3 primeiros caracteres da resposta
# código 220 - Serviço pronto - usado na mensagem inicial
if recvStarttls[:3] != '220':
    print('250 resposta não recebida para STARTTLS.')
else:
    print('250 resposta recebida do servidor para STARTTLS.\n')


# transforma o socket em um canal TLS Seguro
context = ssl.create_default_context()
clientSocket = context.wrap_socket(clientSocket, server_hostname=mailserver)


# Necessário reenviar o HELO, porém versão moderna EHLO
ehloCommand = 'EHLO Felipe\r\n'
clientSocket.send(ehloCommand.encode())
recvEhlo = clientSocket.recv(1024).decode()
print(recvEhlo)
if recvEhlo[:3] != '250':
    print('250 resposta não recebida para EHLO pós-TLS.')
else:
    print('250 resposta recebida do servidor para EHLO pós-TLS.\n')


# continua normalmente


# Enviar comando MAIL FROM (informando o e-mail de origem) e imprimir a resposta do servidor.
mailFromCommand = 'MAIL FROM:<felipe.favarin@estudantes.ifc.edu.br>\r\n'
clientSocket.send(mailFromCommand.encode())
recvMailFrom = clientSocket.recv(1024).decode()
print(recvMailFrom)


# pegamos os 3 primeiros caracteres da resposta
# código 250 - ação solicitada completada com sucesso
if recvMailFrom[:3] != '250':
    print('250 resposta não recebida para MAIL FROM.')


# Enviar comando RCPT TO (informando o e-mail de destino) e imprimir a resposta do servidor.
rcptToCommand = 'RCPT TO:<felipe.favarin@estudantes.ifc.edu.br>\r\n'
clientSocket.send(rcptToCommand.encode())
recvrcptTo = clientSocket.recv(1024).decode()
print(recvrcptTo)


# pegamos os 3 primeiros caracteres da resposta
# código 250 - ação solicitada completada com sucesso
if recvrcptTo[:3] != '250':
    print('250 resposta não recebida para RCPT TO.')


# Enviar comando DATA (indicando que o corpo do e-mail está sendo enviado) e imprimir a resposta do servidor.
dataCommand = 'DATA\r\n'
clientSocket.send(dataCommand.encode())
recvData = clientSocket.recv(1024).decode()
print(recvData)


# pegamos os 3 primeiros caracteres da resposta
# código 354 - Início da entrada da mensagem
if recvData[:3] != '354':
    print('354 resposta não recebida para DATA.')


# Enviar os dados da mensagem.
clientSocket.send(msg.encode())
clientSocket.send(endmsg.encode())


# A mensagem termina com um único ponto.
recvPoint = clientSocket.recv(1024).decode()
print(recvPoint)


# Enviar comando QUIT (encerrando a sessão) e obter a resposta do servidor.
quitCommand = 'QUIT\r\n'
clientSocket.send(quitCommand.encode())
recvQuit = clientSocket.recv(1024).decode()
print(recvQuit)


# pegamos os 3 primeiros caracteres da resposta
# código 221 - Conexão encerrada - opcional
if recvQuit[:3] != '221':
    print('221 resposta não recebida para QUIT.')


# Fechar a conexão com o servidor SMTP
clientSocket.close()
