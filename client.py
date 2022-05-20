import socket
import time
import json
import select
from datetime import datetime

SERVER = '127.0.0.1'
SERVERPORT = 9090
SERVER_ADDRESS = (SERVER, SERVERPORT)

CLIENT_IP = '127.0.0.1'
CLIENT_PORT = 9091
CLIENT_ADDRESS = (CLIENT_IP, CLIENT_PORT)

BUFFERSIZE = 524288
NUM_MESSAGES = 1024
FORMAT = 'utf-8'
TIMEOUT = 30
EDGE_TIMEOUT = 120
PACKET_SIZE = 1026
PAYLOAD_SIZE = 1024
TOTAL_DATA_SIZE = NUM_MESSAGES*PACKET_SIZE
TOTAL_CONTENT_SIZE = NUM_MESSAGES*PAYLOAD_SIZE

STD_MESSAGE_PAYLOAD = [(i % 256) for i in range(PAYLOAD_SIZE)]

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

udp_sent_time_list = [None for _ in range(NUM_MESSAGES)]
udp_received_time_list = [None for _ in range(NUM_MESSAGES)]

for j in range(NUM_MESSAGES):
    ct = j + 1
    message = bytes([ct >> 8, ct % 256, *STD_MESSAGE_PAYLOAD])
    udp_sent_time_list[j] = datetime.now().timestamp()
    udp_socket.sendto(message, SERVER_ADDRESS)
    time.sleep(0.1)


bytes_recv = 0
first_receiving = True

while(True):
    ready = select.select([udp_socket], [], [], TIMEOUT if not first_receiving else EDGE_TIMEOUT) #Conta TIMEOUT(60) segundos
    if first_receiving == True:
        first_receiving = False

    if len(ready[0]) == 0:
        print('to no break do select 8')
        break

    data, addr = udp_socket.recvfrom(BUFFERSIZE)
    bytes_recv += len(data)

    received_ct = int(data[0] << 8) + int(data[1])
    received_index = received_ct - 1
    udp_received_time_list[received_index] = datetime.now().timestamp()

    if bytes_recv >= TOTAL_DATA_SIZE:
        print('entrei no break')
        break

    print(bytes_recv, "/", TOTAL_DATA_SIZE)


udp_socket.close()

time.sleep(TIMEOUT/6)

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind(CLIENT_ADDRESS)

tcp_socket.connect(SERVER_ADDRESS)
print("linha 72")
info_bytes = tcp_socket.recv(BUFFERSIZE)
print('linhas 74')
info_string = info_bytes.decode(FORMAT)
info = json.loads(info_string)
tcp_socket.close()


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


var_1 = f"Taxa de perda do upload: {upload_loss_rate * 100:.2f}%"
var_2 = f"Taxa de perda do download: {download_loss_rate * 100:.2f}%"
var_3 = f"Vazão de upload: {upload_throughput * 8:.2f} bps%" # *1000 porque os tempos vem em microssegundos
var_4 = f"Vazão de download: {download_throughput * 8:.2f} bps%" # *1000 porque os tempos vem em microssegundos
var_5 = f"Tempo total de upload: {upload_total_time:.2f} s"
var_6 = f"Tempo total de download: {download_total_time:.2f} s"

connection_data = f"{var_1}\n{var_2}\n{var_3}\n{var_4}\n{var_5}\n{var_6}"

print(connection_data)
# tcp_socket.send()