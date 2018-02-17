import pymysql
import socket
import datetime
import time
import pickle
import os.path
import thread
from time import gmtime, strftime

nama_file = strftime("%d-%m-%Y-%H-%M-%S", gmtime())
print("Default Nama File '%s'" %nama_file)


def image_capture():
	db = pymysql.connect(host='127.0.0.1',user='root',password='',database='gammu')
	cursor = db.cursor()

	serversocket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	host1 = '192.168.43.97'
	port1 = 9999
	serversocket1.bind((host1, port1))
	serversocket1.listen(5)
	clientsocket1,addr = serversocket1.accept()
	print("berhasil konek", addr)

	i=1
	save_path = 'C:/Users/Eka Suweantara/Desktop/FlaskApp/serving_static/static/img/'
	while True:
		msg = clientsocket1.recv(1000000)
		a = datetime.datetime.now()
		waktu_sekarang = a.hour, a.minute, a.second
		completeName = os.path.join(save_path, 'gambar'+str(i)+str(waktu_sekarang)+'.jpg')
		with open(completeName,'wb') as f:
			if not msg:
				break
			print("waktu gambar ", waktu_sekarang)
			time.sleep(5)
			f.write(msg)
			# path_gbr = '/static/img/gambar'+str(waktu_sekarang)+'.jpg'
			# sql = "INSERT INTO gambar (id, waktu, path_gbr) VALUES ('%s', '%s', '%s')" % (i, waktu_sekarang, path_gbr)
			# cursor.execute(sql)
			# db.commit()
			i=i+1
			time.sleep(15)


def image_capture2():
	serversocket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	host1 = '192.168.43.162'
	port1 = 8888
	serversocket1.bind((host1, port1))
	serversocket1.listen(5)
	clientsocket1,addr = serversocket1.accept()
	print("berhasil konek", addr)

	i=1
	save_path = 'C:/Users/Eka Suweantara/Desktop/FlaskApp/serving_static/static/img/'
	while True:
		msg = clientsocket1.recv(1000000)
		a = datetime.datetime.now()
		waktu_sekarang = a.hour, a.minute, a.second
		completeName = os.path.join(save_path, 'gambar_bw_'+str(waktu_sekarang)+'.jpg')
		with open(completeName,'wb') as f:
			if not msg:
				break
			print("waktu gambar ", waktu_sekarang)
			time.sleep(5)
			f.write(msg)
			i=i+1
			time.sleep(15)


try:
	thread.start_new_thread(image_capture,())
	# thread.start_new_thread(image_capture2,())
	# thread.start_new_thread(ketinggian_air,())
except Exception as e:
	print("Ada error "+e)
while 1:
	pass
