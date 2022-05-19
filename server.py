import socket
import time
import threading
import select
import datetime

from soupsieve import select

FORMAT = 'utf-8'
TIMEOUT = 60
LOCALPORT = 9090
HOSTPORT = '127.0.0.1'
SERVER_ADDRESS = (HOSTPORT, LOCALPORT) #MUDAR

#up
NUM_MESSAGES = 51200
TOTAL_DATA_SIZE = 52531200
BUFFERSIZE = 4096
PACKET_SIZE = 1026

udp_sock = socket.socket(family=socket.AF_INET, type = socket.SOCK_DGRAM) #Socket UDP
udp_sock.bind((HOSTPORT, LOCALPORT)) #conecta com as portas


print('Server online.')
bytes_recv = 0 #variável auxiliar

while(True):

    ready = select.select([udp_sock], [], [], TIMEOUT) #Conta TIMEOUT(60) segundos
    
    if len(ready[0]) == 0: #Se ready >= 60seg, break while
        break

    data, addr = udp_sock.recvfrom(1024) #recebe msg -> data and addr
    tempo = time.strftime("%H:%M:%S") #pega hora, minutos e segundos
    client_msg = data.decode(FORMAT) #decodifica msg de data
    print('Msg from {addr}: {data}') #printa msg (data) enviada do addr
    bytes_recv += len(data) #soma bytes dos dados recebidos

    if bytes_recv >= TOTAL_DATA_SIZE: #52428800 se quantidade de dados recebidos for maior que X - break
        break


STD_MESSAGE_PAYLOAD = [i for i in range(1024)]

udp_sent_time_list = [None for _ in range(NUM_MESSAGES)] # [0, 1, ..., 51200]

for i in range(NUM_MESSAGES):
    ct = i + 1
    message = bytes([ct >> 8, (ct % 256), *STD_MESSAGE_PAYLOAD])
    udp_sent_time_list[i] = datetime.now()
    udp_sock.sendto(message, SERVER_ADDRESS)

udp_sock.close()


#TCP
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind((HOST, PORT))
tcp_socket.listen()

tcp_socket.send()







"""
Cálculo de taxa de perda:
taxa de perda = (1 - pacotes recebidos/50) * 100
"""








    






