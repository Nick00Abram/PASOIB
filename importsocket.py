import socket
import ssl
import os
import threading
import win32com.client
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import tkinter.messagebox as mb
import hashlib
import logging
from datetime import *
import filecmp
import shutil

today = datetime.now().strftime(("%Y-%m-%d-%H.%M.%S"))
dir = os.path.abspath(os.curdir)
logging.basicConfig(filename=dir + "\\log\\"+ today +".txt", level=logging.INFO,filemode='a',format='%(asctime)s %(levelname)s:%(message)s')
logging.info('Запущена программа')

hash = os.path.basename(__file__)
with open(hash,"rb") as f:
    bytes = f.read() # read file as bytes
    readable_hash = hashlib.md5(bytes).hexdigest()
    logging.info(readable_hash)


def getMyIp(): # Host IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = 'Вы не в локальной сети'
    finally:
        s.close()
    return IP

def scan_Ip(ip): # Ping vsex compov
    addr = net + str(ip)
    comm = "ping -n 1 " + addr
    response = os.popen(comm)
    data = response.readlines()
    for line in data:
        if 'TTL' in line:
            # print(addr, "--> Ping Ok")
            logging.info('В сети компьютер:'+addr)
            adrres.append(addr)
            break

file=b''
adrres=[]
net = getMyIp()
if net == 'Вы не в локальной сети':
    showinfo(message='СЕТЬ НЕ ОБНАРУЖЕНА.\nПерезапустите сеть и программу',title='ВНИМАНИЕ!')
    logging.error('СЕТЬ НЕ ОБНАРУЖЕНА.ЗАКРЫТИЕ ПРОГРАММЫ...')
    quit()
logging.info('IP сервера:' + net)
net_split = net.split('.')
a = '.'
net = net_split[0] + a + net_split[1] + a + net_split[2] + a

t1 = datetime.now()

for ip in range(1, 255):
    if ip == int(net_split[3]):
       continue
    potoc = threading.Thread(target=scan_Ip, args=[ip])
    potoc.start()

potoc.join()
t2 = datetime.now()
total = t2 - t1
logging.info('Время сканирования сети:' + str(total))

window = tk.Tk()
window.resizable(False, False)
window.geometry('300x150')
def select_file():

    file = fd.askopenfilename()
    if file == '': file = 'Файл не выбран!'
    showinfo(
        title='Выбраный файл',
        message=file
    )
    return file


def network():
    showinfo(message = '\n'.join(adrres),title='Время сканирования: ' + str(total))
ips_network_btn = ttk.Button(
    window,
    text='Компьютеры в сети',
    command=network,
    width=200
)

def CONNECT():
    dir = os.path.abspath(os.curdir)
    if not (os.path.exists(dir + '\privkey.pem') and  os.path.exists(dir + '\certificate.pem')):
        logging.warning('Не обнаружен(ы) сертификат(ы).Закрытые программы.')
        showinfo(message='Не обнаружен(ы) сертификат(ы).\nЗакрытые программы.')
        quit()

    file=select_file()
    if file == 'Файл не выбран!':
        logging.info('Отмена выбора файла. Закрытие соединения.')
        showinfo(message='Отмена выбора файла.\nЗакрытие соединения.')
        return
    logging.info('Выбран файл для передачи. Создается подключение')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind(('',11719))
    for i in adrres:
	    s.sendto('CONNECTION'.encode('utf-8'),(i,11719))
    client_cert = open(dir+'\\client\\certificate.pem','wb')
    cert_client = s.recv(4096)
    client_cert.write(cert_client)
    client_cert.close()
    if not filecmp.cmp((dir+'\\client\\certificate.pem'),(dir + '\certificate.pem')):
        logging.warning('Внимание! Сертификат клиента отличается от правильного!')
        showinfo(message='Внимание!\nСертификат клиента отличается от правильного!')
        quit()
    

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s = ssl.wrap_socket(s, keyfile= dir + '\privkey.pem', certfile= dir + '\certificate.pem', server_side=True)
    s.bind((getMyIp(), 4443))
    s.listen(5)
    logging.info('Подключение создается. Ожидание передачи файла.')
    cancel = mb.askokcancel(message='Подключение создается.\nОжидание передачи файла.\nНажмите ОК для продолжения.')
    if cancel == True:    
        conn, addr = s.accept()
        filename = os.path.basename(file)
        print(filename)
        conn.send(filename.encode('utf-8'))
        f = open(file,"rb")
        l = f.read(1024)
        print(l)
        while l:
            conn.send (l)
            l = f.read(1024)
        conn.close()
        logging.info('Передача завершена.')
        showinfo(message='Передача завершена.')
    elif cancel == False:
        logging.error('Подключение разорвано. Файл не передан.')
        s.close()
        return
        
connection_btn = ttk.Button(
    window,
    text = 'Создать подключение(СЕРВЕР)',
    command = CONNECT,
    width=200
)

def save():
    directory = fd.askdirectory()
    if (os.path.exists(dir + '\privkey.pem') and  os.path.exists(dir + '\certificate.pem')):
        shutil.copyfile(dir + '\privkey.pem',directory+ '\privkey.pem')
        shutil.copyfile(dir + '\certificate.pem',directory+ '\certificate.pem')
        logging.info('Файлы скопированы.')
    else:
        logging.warning('Сертификатов не обнаружено в папке программы.')
        showinfo(message='Сертификатов не обнаружено в папке программы.')
        return

save_btn = ttk.Button(
    window,
    command=save,
    text='Резервное копирование сертификaтов',
    width=200
)
label = ttk.Label(text='IP этого компьютера:' + getMyIp())
ips_network_btn.pack(pady=10)
connection_btn.pack(pady=5)
save_btn.pack(pady=5)
label.pack(padx=10)
window.mainloop()
logging.info('Закрытие программы.')
