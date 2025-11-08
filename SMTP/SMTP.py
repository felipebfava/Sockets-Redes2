import socket
import ssl
import base64

# Configurações do servidor SMTP
mailserver = "smtp.gmail.com"
porta = 587  # Porta para STARTTLS

# Credenciais
usuario = "felipebfavarin@gmail.com"
senha = "gmri zkfn prkw nbxa"  # senha (de app) real do google

# Endereços de e-mail
email_origem = "felipebfavarin@gmail.com"
email_destino = "felipebfavarin@gmail.com"

# Mensagem simples
mensagem_texto = "Teste e-mail SMTP para redes de computadores!"

# Carregar e codificar imagem
# Design por @kuritafsheen77 - link: https://br.freepik.com/autor/kuritafsheen77
with open("img/arara.png", "rb") as img_file:
    img_bytes = img_file.read()
    img_base64 = base64.b64encode(img_bytes).decode()


# Criação do socket TCP/IP
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((mailserver, porta))

# Recebe resposta inicial
# código esperado 220
recv = clientSocket.recv(1024).decode()
print(recv)

# código esperado 250
clientSocket.send(b"EHLO Felipe\r\n")
print(clientSocket.recv(1024).decode())


# Inicia criptografia TLS enviando uma mensagem START TLS
# código esperado 220 - Ready to start TLS
clientSocket.send(b"STARTTLS\r\n")
recv_tls = clientSocket.recv(1024).decode()
print(recv_tls)

# imprime novamente os métodos que são disponíveis
# 250-smtp.gmail.com at your service, [177.75.171.95]
# 250-SIZE 35882577
# 250-8BITMIME
# 250-AUTH LOGIN PLAIN XOAUTH2 PLAIN-CLIENTTOKEN OAUTHBEARER XOAUTH
# 250-ENHANCEDSTATUSCODES
# 250-PIPELINING
# 250-CHUNKING
# 250 SMTPUTF8

# Configurar contexto SSL após STARTTLS
context = ssl.create_default_context()

# Envolve o socket com SSL
clientSocket = context.wrap_socket(clientSocket, server_hostname=mailserver)

# Comando EHLO após configuração do SSL/TLS
# código esperado 250
clientSocket.send(b"EHLO Felipe\r\n")
print(clientSocket.recv(1024).decode())

# Autenticação
# código esperado 334
clientSocket.send(b"AUTH LOGIN\r\n")
print(clientSocket.recv(1024).decode())

# Envia usuário codificado em base64
# código esperado 334
clientSocket.send(base64.b64encode(usuario.encode()) + b"\r\n")
print(clientSocket.recv(1024).decode())

# Envia senha codificada em base64
# código esperado 235
clientSocket.send(base64.b64encode(senha.encode()) + b"\r\n")
print(clientSocket.recv(1024).decode())

# MAIL FROM
# código esperado 250
clientSocket.send(f"MAIL FROM:<{email_origem}>\r\n".encode())
print(clientSocket.recv(1024).decode())

# RCPT TO
# código esperado 250
clientSocket.send(f"RCPT TO:<{email_destino}>\r\n".encode())
print(clientSocket.recv(1024).decode())

# DATA
# código esperado 354
clientSocket.send(b"DATA\r\n")
print(clientSocket.recv(1024).decode()) # esperado 354

boundary = "----BOUNDARY----"
content_id = "imagem1"

corpo_html = f"""
<html>
    <body>
        <p>Aqui está a imagem de uma arara vermelha</p>
        <img src="cid:{content_id}">
    </body>
</html>
"""

# Cabeçalho MIME para e-mail com anexo
# Content-Type: image/jpeg
# Content-Type: image/png
mensagem = f"""From: {email_origem}
To: {email_destino}
Subject: Envio arara e-mail Redes-SMTP
MIME-Version: 1.0
Content-Type: multipart/related; boundary="{boundary}"

--{boundary}
Content-Type: text/html; charset="utf-8"
Content-Transfer-Encoding: 7bit

{corpo_html}

--{boundary}
Content-Type: image/png
Content-Transfer-Encoding: base64
Content-Disposition: inline; filename="arara.png"
Content-ID: <{content_id}>

{img_base64}

--{boundary}--
\r\n.\r\n"""

# Envia corpo da mensagem
clientSocket.send(mensagem.encode())
print(clientSocket.recv(1024).decode()) # esperado 250

# QUIT
clientSocket.send(b"QUIT\r\n")
print(clientSocket.recv(1024).decode()) # esperado 221

# Fecha conexão
clientSocket.close()
