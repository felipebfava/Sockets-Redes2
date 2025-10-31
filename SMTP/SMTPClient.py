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
if recv[:3] != '220':
    print('220 resposta não recebida do servidor.')

# Enviar comando HELO e imprimir a resposta do servidor.
heloCommand = 'HELO Felipe\r\n'
clientSocket.send(heloCommand.encode())
recvHelo = clientSocket.recv(1024).decode()
print(recvHelo)
if recvHelo[:3] != '250':
    print('250 resposta não recebida para HELO.')

# Enviar comando MAIL FROM (informando o e-mail de origem) e imprimir a resposta do servidor.
mailFromCommand = 'MAIL FROM:<felipebfavarin@gmail.com>\r\n'
clientSocket.send(mailFromCommand.encode())
recvMailFrom = clientSocket.recv(1024).decode()
print(recvMailFrom)
if recvMailFrom[:3] != '250':
    print('250 resposta não recebida para MAIL FROM.')

# Enviar comando RCPT TO (informando o e-mail de destino) e imprimir a resposta do servidor.
rcptToCommand = 'RCPT TO:<felipebfavarin@gmail.com>\r\n'
clientSocket.send(rcptToCommand.encode())
recvrcptTo = clientSocket.recv(1024).decode()
print(recvrcptTo)
if recvrcptTo[:3] != '250':
    print('250 resposta não recebida para RCPT TO.')

# Enviar comando DATA (indicando que o corpo do e-mail está sendo enviado) e imprimir a resposta do servidor.
dataCommand = 'DATA\r\n'
clientSocket.send(dataCommand.encode())
recvData = clientSocket.recv(1024).decode()
print(recvData)
if recvData[:3] != '354':
    print('354 resposta não recebida para DATA.')

# Enviar os dados da mensagem.
clientSocket.send(msg.encode())
clientSocket.send(endmsg.encode())

# A mensagem termina com um único ponto.
recv6 = clientSocket.recv(1024).decode()
print(recv6)

# Enviar comando QUIT (encerrando a sessão) e obter a resposta do servidor.
quitCommand = 'QUIT\r\n'
clientSocket.send(quitCommand.encode())
recv7 = clientSocket.recv(1024).decode()
print(recv7)

# Fechar a conexão com o servidor SMTP
clientSocket.close()