import socket
import ssl
import base64

# Configurações do servidor SMTP
mailserver = "smtp.gmail.com"
porta = 587  # Porta para STARTTLS

# Credenciais
usuario = "felipebfavarin@gmail.com"
senha = "haqy hypd ndjs xyfd "  # senha (de app) real do google


# Endereços de e-mail
email_origem = "felipebfavarin@gmail.com"
email_destino = "felipebfavarin@gmail.com"

# Mensagem simples
mensagem_texto = "Teste e-mail SMTP para redes de computadores!"

# Carregar e codificar imagem
with open("img/largato.jpg", "rb") as img_file:
    img_bytes = img_file.read()
    img_base64 = base64.b64encode(img_bytes).decode()

# Cabeçalho MIME para e-mail com anexo
boundary = "sep"
mensagem = f"""
From: {email_origem}
To: {email_destino}
Subject: Teste e-mail Redes
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary={boundary}

--{boundary}
Content-Type: text/plain

{mensagem_texto}

--{boundary}
Content-Type: image/jpeg
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="largato.jpg"

{img_base64}
--{boundary}--
"""

# Criação do socket TCP/IP
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((mailserver, porta))

# Recebe resposta inicial
recv = clientSocket.recv(1024).decode()
print(recv)

clientSocket.send(b"EHLO Felipe\r\n")
print(clientSocket.recv(1024).decode())

# Inicia criptografia TLS enviando uma mensagem START TLS
clientSocket.send(b"STARTTLS\r\n")
recv_tls = clientSocket.recv(1024).decode()
print(recv_tls)


# Configurar contexto SSL após STARTTLS
context = ssl.create_default_context()

# Envolve o socket com SSL
clientSocket = context.wrap_socket(clientSocket, server_hostname=mailserver)


# Comando EHLO após configuração do SSL/TLS
clientSocket.send(b"EHLO Felipe\r\n")
print(clientSocket.recv(1024).decode())

# Autenticação
clientSocket.send(b"AUTH LOGIN\r\n")
print(clientSocket.recv(1024).decode())

# Envia usuário codificado em base64
clientSocket.send(base64.b64encode(usuario.encode()) + b"\r\n")
print(clientSocket.recv(1024).decode())

# Envia senha codificada em base64
clientSocket.send(base64.b64encode(senha.encode()) + b"\r\n")
print(clientSocket.recv(1024).decode())

# MAIL FROM
clientSocket.send(f"MAIL FROM:<{email_origem}>\r\n".encode())
print(clientSocket.recv(1024).decode())

# RCPT TO
clientSocket.send(f"RCPT TO:<{email_destino}>\r\n".encode())
print(clientSocket.recv(1024).decode())

# DATA
clientSocket.send(b"DATA\r\n")
print(clientSocket.recv(1024).decode())

# Envia corpo da mensagem
clientSocket.send((mensagem + "\r\n.\r\n").encode())
print(clientSocket.recv(1024).decode())

# QUIT
clientSocket.send(b"QUIT\r\n")
print(clientSocket.recv(1024).decode())

# Fecha conexão
clientSocket.close()