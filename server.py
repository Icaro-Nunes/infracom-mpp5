import socket
import select
from datetime import datetime
import time
import json
import sys
import os

FORMAT = 'utf-8'
TIMEOUT = 60
LOCALPORT = 9090
HOSTPORT = '127.0.0.1'
SERVER_ADDRESS = (HOSTPORT, LOCALPORT) #MUDAR

BUFFERSIZE = 2048
NUM_MESSAGES = 1024
PACKET_SIZE = 1026
PAYLOAD_SIZE = 1024
TOTAL_DATA_SIZE = NUM_MESSAGES*PACKET_SIZE #1050624

SOCKET_RESTING_TIME = 0.01

udp_sock = socket.socket(family=socket.AF_INET, type = socket.SOCK_DGRAM) #Socket UDP
udp_sock.bind((HOSTPORT, LOCALPORT)) #conecta com as portas

udp_received_time_list = [None for _ in range(NUM_MESSAGES)] # [0, 1, ..., 51200]


print('Server online.')
bytes_recv = 0 #variável auxiliar

while(True):

    ready = select.select([udp_sock], [], [], TIMEOUT) #Conta TIMEOUT(60) segundos
    
    if len(ready[0]) == 0: #Se ready >= 60seg, break while
        print('to no break do select 8)')
        break

    
    data, addr = udp_sock.recvfrom(BUFFERSIZE) #recebe msg -> data and addr
    # tempo = time.strftime("%H:%M:%S") #pega hora, minutos e segundos
    # client_msg = data.decode(FORMAT) #decodifica msg de data
    
    received_ct = int(data[0] << 8) + int(data[1])
    received_index = received_ct - 1
    # print('Msg from {}: {}'.format(addr, data)) #printa msg (data) enviada do addr
    # data_2 = int.from_bytes(data, 'little')
    bytes_recv += len(data) #soma bytes dos dados recebidos
    udp_received_time_list[received_index] = datetime.now().timestamp()

    if bytes_recv >= TOTAL_DATA_SIZE: #52428800 se quantidade de dados recebidos for maior que X - break
        print('to no break 8)')
        break

    print(bytes_recv, "/", TOTAL_DATA_SIZE)

#time.sleep(10)
print('finalizando etapa de recebimento')
print('iniciano etapa de envio')

STD_MESSAGE_PAYLOAD = [(i % 256) for i in range(1024)]

udp_sent_time_list = [None for _ in range(NUM_MESSAGES)] # [0, 1, ..., 51200]

for j in range(NUM_MESSAGES):
    ct = j + 1
    # message = PACKET_SIZE.to_bytes(10, "little") #bytes([ct >> 8, (ct % 256), *STD_MESSAGE_PAYLOAD])
    message = bytes([ct >> 8, ct % 256, *STD_MESSAGE_PAYLOAD])
    udp_sent_time_list[j] = datetime.now().timestamp()
    udp_sock.sendto(message, addr)
    time.sleep(SOCKET_RESTING_TIME)

print('fim envio')
udp_sock.close()


#Início TCP
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind(SERVER_ADDRESS)
tcp_socket.listen(1)
conn, addr = tcp_socket.accept()
#tcp_socket.send()

#tcp_socket.connect(SERVER_ADDRESS)
info = {
    'upload_timestamps': udp_received_time_list,
    'download_timestamps': udp_sent_time_list
}
info_string = json.dumps(info)
info_bytes = bytes(info_string, FORMAT)
conn.sendall(info_bytes)

analytics_bytes = conn.recv(BUFFERSIZE)
analytics_string = analytics_bytes.decode(FORMAT)
analytics = json.loads(analytics_bytes)

var_1 = f"Taxa de perda do upload: {analytics['upload_loss_rate'] * 100}%"
var_2 = f"Taxa de perda do download: {analytics['download_loss_rate'] * 100}%"
var_3 = f"Vazão de upload: {analytics['upload_throughput'] * 8}bps%"
var_4 = f"Vazão de download: {analytics['download_throughput'] * 8}bps%"
var_5 = f"Tempo total de upload: {analytics['upload_total_time']}"
var_6 = f"Tempo total de download: {analytics['download_total_time']}"

result_data = f"{var_1}\n{var_2}\n{var_3}\n{var_4}\n{var_5}\n{var_6}"
print(result_data)

conn.close()