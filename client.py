import socket
import threading
import time
import json
import select
from datetime import datetime

LOCALHOST = 'localhost'
LOCALPORT = 9090
SERVER = 'localhost'
SERVERPORT = 9091
SERVER_ADDRESS = (SERVER, SERVERPORT)

NUM_MESSAGES = 51200
TOTAL_DATA_SIZE = 52531200
BUFFERSIZE = 4096
FORMAT = 'utf-8'
TIMEOUT = 60
PACKET_SIZE = 1026

STD_MESSAGE_PAYLOAD = [i for i in range(1024)]

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((LOCALHOST, LOCALPORT))

udp_sent_time_list = [None for _ in range(NUM_MESSAGES)] # [0, 1, ..., 51200]
udp_received_time_list = [None for _ in range(NUM_MESSAGES)] # [0, 1, ..., 51200]

for i in range(NUM_MESSAGES):
    ct = i + 1
    message = bytes([ct >> 8, (ct % 256), *STD_MESSAGE_PAYLOAD])
    udp_sent_time_list[i] = datetime.now()
    udp_socket.sendto(message, SERVER_ADDRESS)


bytes_recv = 0
time.sleep(TIMEOUT) #creme de la creme

while(True):
    ready = select.select([udp_socket], [], [], TIMEOUT) #Conta TIMEOUT(60) segundos
    
    if len(ready) == 0: #Se ready >= 60seg, break while
        break

    data, addr = udp_socket.recvfrom(1024) #recebe msg -> data and addr
    bytes_recv += len(data) #soma bytes dos dados recebidos

    received_ct = int(data[0] << 8) + int(data[1])
    received_index = received_ct - 1
    udp_received_time_list[received_index] = datetime.now()

    if bytes_recv >= TOTAL_DATA_SIZE: #se quantidade de dados recebidos for maior que X, break
        break

udp_socket.close()

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind((LOCALHOST, LOCALPORT))

tcp_socket.connect(SERVER_ADDRESS)
info_bytes = tcp_socket.recv(BUFFERSIZE)
info_string = info_bytes.decode(FORMAT)
info = json.loads(info_string)

# info = dict(
#     "upload_timestamps": [0 ... (51200 - 1)],
#     "download_timestamps": [0 ... (51200 - 1)]
# )

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

print(f"Taxa de perda do upload: {upload_loss_rate * 100}%")
print(f"Taxa de perda do download: {download_loss_rate * 100}%")
print(f"Vazão de upload: {upload_throughput * 8}bps%")
print(f"Vazão de download: {download_throughput * 8}bps%")
print(f"Tempo total de upload: {upload_total_time}")
print(f"Tempo total de download: {download_total_time}")
