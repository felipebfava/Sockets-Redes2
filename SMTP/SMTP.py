import socket
import ssl # o nome da biblioteca ficou o mesmo, porém é usado TLS (Transport Layer Security)
import base64

# link base: https://mailtrap.io/pt/blog/smtp-commands-and-responses/

# Configurações do servidor SMTP
mailserver = "smtp.gmail.com" # endereço de servidor do google
porta = 587  # Porta padrão recomendada para SMTP com criptografia STARTTLS

# Credenciais
usuario = "felipebfavarin@gmail.com"
senha = "gmri zkfn prkw nbxa"  # senha (de app) real do google para autenticação de dois fatores

# Definindo Endereços de e-mail remetente-destinatário
email_origem = "felipebfavarin@gmail.com"
email_destino = "felipebfavarin@gmail.com"

# Carrega e codifica imagem em base64, pois é o padrão aceito pelo e-mail MIME (Multipurpose Internet Mail Extensions)
# a imagem dá cerca de 33% de sobrecarga no tamanho
# Design por @kuritafsheen77 - link: https://br.freepik.com/autor/kuritafsheen77
with open("img/arara.png", "rb") as img_file:
    img_bytes = img_file.read()
    img_base64 = base64.b64encode(img_bytes).decode()

def mostrar_codigo_resposta(resposta, comando):
    codigo = resposta[:3]  # Pega os 3 primeiros caracteres que representam o código SMTP
    print(f"{codigo} mensagem recebida de {comando}\n")


# Criação do socket IPv4 - TCP - pois queremos comunicação segura, visto que os dados são importantes
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((mailserver, porta)) # tupla endereço (IP) que será resolvido por DNS com a porta de conexão padrão

# Recebe resposta inicial
# código esperado 220 - O servidor de recebimento está pronto para o próximo comando
recv_Inicial = clientSocket.recv(1024).decode()
mostrar_codigo_resposta(recv_Inicial, "INICIAL")
print(recv_Inicial)

# código esperado 250 - Sucesso! O e-mail foi entregue
clientSocket.send(b"HELO Felipe\r\n")
recv_Helo = clientSocket.recv(1024).decode()
mostrar_codigo_resposta(recv_Helo, "HELO")


# código esperado 250 - Sucesso! O e-mail foi entregue
# EHLO - Extended HELO é uma melhora do HELO
clientSocket.send(b"EHLO Felipe\r\n")
recv_Ehlo = clientSocket.recv(1024).decode()
mostrar_codigo_resposta(recv_Ehlo, "EHLO antes do STARTTLS") 
print(recv_Ehlo)

# 250-smtp.gmail.com at your service, [endereço IP local]
# 250-SIZE 35882577       - tamanho máx aceito da mensagem
# 250-8BITMIME            - servidor suporta versão MIME de 8bits sem codificação extra de 7bits (versões antigas)
# 250-STARTTLS            - suporta TLS para a criptografia
# 250-ENHANCEDSTATUSCODES - suporte a mensagens mais detalhadas
# 250-PIPELINING          - servidor pode processar os comandos em sequência com eficiência
# 250-CHUNKING            - o cliente manda a mensagem em partes em vez de uma sequência grande, dividindo
# 250 SMTPUTF8            - permite o uso de caracteres UTF-8

# Inicia criptografia TLS enviando uma mensagem START TLS
# código esperado 220 - Ready to start TLS
# 220 - O servidor de recebimento está pronto para o próximo comando
clientSocket.send(b"STARTTLS\r\n")
recv_Tls = clientSocket.recv(1024).decode()
mostrar_codigo_resposta(recv_Tls, "STARTTLS")
print(recv_Tls)

# Configurar contexto SSL/TLS após STARTTLS
context = ssl.create_default_context()

# Envolve o socket com SSL/TLS
clientSocket = context.wrap_socket(clientSocket, server_hostname=mailserver)

# Comando EHLO após configuração do SSL/TLS
# código esperado 250
clientSocket.send(b"EHLO Felipe\r\n")
recv_EhloPosStart = clientSocket.recv(1024).decode()
mostrar_codigo_resposta(recv_EhloPosStart, "EHLO depois do STARTTLS") 
print(recv_EhloPosStart)

# imprime novamente os métodos que são disponíveis
# 250-smtp.gmail.com at your service, [177.75.171.95]
# 250-SIZE 35882577
# 250-8BITMIME
# 250-AUTH LOGIN PLAIN XOAUTH2 PLAIN-CLIENTTOKEN OAUTHBEARER XOAUTH - permite autenticações
# 250-ENHANCEDSTATUSCODES
# 250-PIPELINING
# 250-CHUNKING
# 250 SMTPUTF8

# Autenticação
# código esperado 334 - A autenticação foi bem-sucedida
clientSocket.send(b"AUTH LOGIN\r\n")
recv_Auth = clientSocket.recv(1024).decode()
mostrar_codigo_resposta(recv_Auth, "AUTH LOGIN")

# Envia usuário codificado em base64
# código esperado 334
clientSocket.send(base64.b64encode(usuario.encode()) + b"\r\n")
recv_AuthUsuario = clientSocket.recv(1024).decode()
mostrar_codigo_resposta(recv_AuthUsuario, "AUTH LOGIN USUARIO")

# Envia senha codificada em base64
# código esperado 235 - A autenticação do servidor remetente foi bem-sucedida
clientSocket.send(base64.b64encode(senha.encode()) + b"\r\n")
recv_AuthSenha = clientSocket.recv(1024).decode()
mostrar_codigo_resposta(recv_AuthSenha, "AUTH LOGIN SENHA")


# MAIL FROM - inicia transferência de e-mail
# código esperado 250
clientSocket.send(f"MAIL FROM:<{email_origem}>\r\n".encode())
recv_MailFrom = clientSocket.recv(1024).decode()
mostrar_codigo_resposta(recv_MailFrom, "MAIL FROM")


# RCPT TO - especifica destinatário
# código esperado 250
clientSocket.send(f"RCPT TO:<{email_destino}>\r\n".encode())
recv_RcpTo = clientSocket.recv(1024).decode()
mostrar_codigo_resposta(recv_RcpTo, "RCPT TO")


# DATA - início do envio da mensagem
# código esperado 354 - O cabeçalho do e-mail foi recebido; o servidor agora aguarda o corpo da mensagem
clientSocket.send(b"DATA\r\n")
recv_Data = clientSocket.recv(1024).decode()
mostrar_codigo_resposta(recv_Data, "DATA")


# boundary é o limite que separa as partes na mensagem de e-mail MIME
# poderia ser qualquer uma
boundary = "----BOUNDARY----"
# definindo um nome para imagem, caso tenha mais de uma imagem sendo enviada
content_id = "imagem1"

# corpo html usado para melhor formatação / configuração do e-mail MIME enviado
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
# Subject - (assunto) - será a mensagem título do e-mail
# não necessário incluir - Content-Transfer-Encoding: 7bit
mensagem = f"""From: {email_origem}
To: {email_destino}
Subject: Envio arara e-mail Redes-SMTP
MIME-Version: 1.0
Content-Type: multipart/related; boundary="{boundary}"

--{boundary}
Content-Type: text/html; charset="utf-8"

{corpo_html}

--{boundary}
Content-Type: image/png
Content-Transfer-Encoding: base64
Content-Disposition: inline; filename="arara.png"
Content-ID: <{content_id}>

{img_base64}

--{boundary}--
\r\n.\r\n"""

# Envia todo o corpo da mensagem
# código esperado 250 - Sucesso! O e-mail foi entregue.
clientSocket.send(mensagem.encode())
recv_Corpo = clientSocket.recv(1024).decode()
mostrar_codigo_resposta(recv_Corpo, "CORPO MENSAGEM")

# QUIT - solicitação para terminar a sessão SMTP
# código esperado 221 - O servidor de destino está fechando a conexão SMTP.
clientSocket.send(b"QUIT\r\n")
recv_Quit = clientSocket.recv(1024).decode()
mostrar_codigo_resposta(recv_Quit, "QUIT")

# Fecha o socket (libera recursos alocados)
clientSocket.close()
