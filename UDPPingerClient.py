# importando bibliotecas
import random
from socket import *

# Cria um socket UDP
clientSocket = socket(AF_INET, SOCK_DGRAM)

# usuário precisa dar input com uma mensagem, que será levada ao servidor
# define um timeout de espera pela resposta do servidor
# socket client precisa enviar 10 pings para o servidor
