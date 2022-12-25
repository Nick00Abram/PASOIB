import socket
import ssl
import os
import win32com.client
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from tkinter import filedialog as fd
import tkinter.messagebox as mb
import hashlib
import logging
from datetime import *
import shutil

dir = os.path.abspath(os.curdir)
today = datetime.now().strftime(("%Y-%m-%d-%H.%M.%S"))
logging.basicConfig(filename=dir + "\\log\\"+ today +".txt", level=logging.INFO,filemode='a',format='%(asctime)s %(levelname)s:%(message)s')
logging.info('Запущена программа')

hash = os.path.basename(__file__)
with open(hash,"rb") as f:
    bytes = f.read() # read file as bytes
    readable_hash = hashlib.md5(bytes).hexdigest()
    logging.info(readable_hash)

window = tk.Tk()
window.resizable(False, False)
window.geometry('300x150')
FLASH = mb.askokcancel(message='Вставьте флешку и нажмите окей')
flash = ''
if FLASH:
	wmi = win32com.client.GetObject("winmgmts:")
	# accept = False
	# while accept==False:
	for usb in wmi.InstancesOf("Win32_USBHub"):
		if (usb.DeviceID == "USB\VID_058F&PID_6387\\64FD2634"):
			showinfo(message='Флешка считана.')
			logging.info('Флешка считана. Вход в систему.')
			# accept = True
			flash = usb.PNPDeviceID
		
else:
	logging.warning('Отмена. Закрытие программы.') 
	quit()
if flash == '':
	logging.warning('Флешка не распознана. Закрытие программы.') 
	quit()	

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

def CONNECTION():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	s.bind(('',11719))
	con = False
	if not (os.path.exists(dir + '\privkey.pem') and  os.path.exists(dir + '\certificate.pem')):
		logging.warning('Не обнаружен(ы) сертификат(ы).Закрытые программы.')
		showinfo(message='Не обнаружен(ы) сертификат(ы).\nЗакрытые программы.')
		quit()
	f = open(dir+'\certificate.pem','rb')
	logging.info('Отправка сертификата на проверку предполагаемому серверу')
	l = f.read(4096)
	while con == False:
		data,addr = s.recvfrom(60)
		if data == b'CONNECTION':
			SERVER = addr[0]
			con = True
			logging.info('Предполагаемый IP сервера:'+SERVER)
	s.sendto(l,(SERVER,11719))
	s.close()
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client = ssl.wrap_socket(client, keyfile=dir + '\privkey.pem', certfile=dir + '\certificate.pem', server_side=False)
	client.connect((SERVER, 4443))
	logging.info('Сертификат верен, соединение с сервером установлено, идет прием файла.')
	showinfo(message='Подключение установлено.\nИдет приём файла.')
	filename = str(client.recv(1024),encoding = 'utf-8')
	file = open(filename,'wb')
	while True:
		from_server = client.recv(1024)
		print(from_server)
		while from_server:
			file.write(from_server)
			from_server = client.recv(1024)
		file.close()
		logging.info('Файл получен. Закрытие соединения.')
		client.close()
		break
btn_con = ttk.Button(
	window,
	text='Подключение к серверу(КЛИЕНТ)',
	command=CONNECTION,
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
btn_con.pack(pady=10)
label = ttk.Label(text='IP этого компьютера:' + getMyIp())
save_btn.pack(pady=5)
label.pack(pady=5)
window.mainloop()
logging.info('Закрытие программы.')