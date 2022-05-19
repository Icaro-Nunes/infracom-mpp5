import socket
import time
import threading
import select
import datetime
import json

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

udp_received_time_list = [None for _ in range(NUM_MESSAGES)] # [0, 1, ..., 51200]


print('Server online.')
bytes_recv = 0 #variável auxiliar

while(True):

    ready = select.select([udp_sock], [], [], TIMEOUT) #Conta TIMEOUT(60) segundos
    
    if len(ready[0]) == 0: #Se ready >= 60seg, break while
        break

    data, addr = udp_sock.recvfrom(1024) #recebe msg -> data and addr
    tempo = time.strftime("%H:%M:%S") #pega hora, minutos e segundos
    client_msg = data.decode(FORMAT) #decodifica msg de data
    received_ct = int(data[0] << 8) + int(data[1])
    received_index = received_ct - 1
    print('Msg from {addr}: {data}') #printa msg (data) enviada do addr
    bytes_recv += len(data) #soma bytes dos dados recebidos
    udp_received_time_list[received_index] = datetime.now()

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


#Início TCP
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind(())
tcp_socket.listen()
tcp_socket.send()

tcp_socket.connect(SERVER_ADDRESS)
info_bytes = tcp_socket.recv(BUFFERSIZE)
info_string = info_bytes.decode(FORMAT)
info = json.loads(info_string)

# calcular os tempos e valores
failed_uploads = 0
total_data_uploaded = 0
total_time_upload = 0

failed_downloads = 0
total_data_downloaded = 0
total_time_download = 0

for i, tmstp in enumerate(info["upload_timestamps"]):
    if tmstp == None:
        failed_uploads += 1
        continue

    total_data_uploaded += PACKET_SIZE
    total_time_upload += tmstp - udp_sent_time_list[i]

for i, tmstp in enumerate(udp_received_time_list):
    if tmstp == None:
        failed_downloads += 1
        continue

    total_data_downloaded += PACKET_SIZE
    total_time_download += tmstp - info["download_timestamps"][i]

upload_loss_rate = failed_uploads / NUM_MESSAGES
download_loss_rate = failed_uploads / NUM_MESSAGES

upload_throughput = total_data_uploaded / total_time_upload
download_throughput = total_data_downloaded / total_time_download

upload_total_time = total_time_upload
download_total_time = total_time_download

var_1 = f"Taxa de perda do upload: {upload_loss_rate * 100}%"
var_2 = f"Taxa de perda do download: {download_loss_rate * 100}%"
var_3 = f"Vazão de upload: {upload_throughput * 8}bps%"
var_4 = f"Vazão de download: {download_throughput * 8}bps%"
var_5 = f"Tempo total de upload: {upload_total_time}"
var_6 = f"Tempo total de download: {download_total_time}"

connection_data = f"{var_1}\n{var_2}\n{var_3}\n{var_4}\n{var_5}\n{var_6}"

tcp_socket.send()






"""
Cálculo de taxa de perda:
taxa de perda = (1 - pacotes recebidos/50) * 100
"""

"""
Ao final da conexão UDP nós precisaremos utilizar
a conexão TCP para enviar do servidor para o cliente
e do cliente para o servidor as seguintes informações:
- taxa de perda no upload
- taxa de perda no download
- vazão de upload
- vazão de download
- tempo total de download
- tempo total de upload. 

Obs.: O tamanho em bytes do contador deverá
ser levado em conta na computação da vazão
"""








    






