import pymysql
import socket
import datetime
import time
import pickle
import os.path
import thread
from time import gmtime, strftime

nama_file = strftime("%d-%m-%Y", gmtime())
print("Default Nama File '%s'" %nama_file)
#nama_file = raw_input("Masukkan nama file untuk penyimpanan tinggi air: ")

def image_capture():
	db = pymysql.connect(host='127.0.0.1',user='root',password='',database='gammu')
	cursor = db.cursor()

	serversocket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	host1 = '192.168.1.4'
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
		completeName = os.path.join(save_path, 'gambar'+str(waktu_sekarang)+'.jpg')
		with open(completeName,'wb') as f:
			if not msg:
				break
			print("waktu gambar ", waktu_sekarang)
			f.write(msg)
			path_gbr = '/static/img/gambar'+str(waktu_sekarang)+'.jpg'
			sql = "INSERT INTO gambar (id, waktu, path_gbr) VALUES ('%s', '%s', '%s')" % (i, waktu_sekarang, path_gbr)
			cursor.execute(sql)
			db.commit()
			i=i+1
			time.sleep(10)
def ketinggian_air():
	# db = pymysql.connect(host='127.0.0.1',user='root',password='',database='gammu')
	# cursor = db.cursor()
    #
	# serversocket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# host2 = '192.168.1.11'
	# port2 = 8888
	# port = 6666
    #
	# serversocket2.bind((host2, port2))
	# serversocket2.listen(5)
    #
	# serversocket.bind((host2, port))
	# serversocket.listen(5)
    #
	# clientsocket2,addr = serversocket2.accept()
	# print("berhasil konek2", addr)
	# clientsocket,addr = serversocket.accept()
	# print("berhasil konek3", addr)
	waktu_db = 0

	file = open(str(nama_file)+ ".txt","w")
	i=1
	while True:
		# tinggi = clientsocket2.recv(4096)
		# waktu = clientsocket.recv(4096)
		# data_tinggi = pickle.loads(tinggi)
		# data_waktu = pickle.loads(waktu)
		sql = "SELECT * FROM tinggi_air ORDER BY id DESC LIMIT 1;"
	    cursor.execute(sql)
	    results = cursor.fetchall()
	    db.commit()
	    for row in results:
	        tinggi = row[1]
	        waktu = row[2]

		waktu_db = waktu
		tinggi_db = tinggi
		if waktu_db != 0:
			print "tinggi: ", tinggi, "cm waktu ke: ", waktu
			# sql = "INSERT INTO tinggi_air (id, tinggi, waktu) VALUES ('%s', '%s', '%s')" % (i, data_tinggi, data_waktu)
			# cursor.execute(sql)
			# db.commit()
			# i=i+1
			file.write("%s, %s, %s" % (i, data_waktu, data_tinggi))
			file.write("\n")
			i=i+1
		time.sleep(1)

# def sms_gateway():
# 	db = pymysql.connect(host='127.0.0.1',user='root',password='',database='gammu')
# 	cursor = db.cursor()
#
# 	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 	host1 = '192.168.1.11'
# 	port = 7777
# 	serversocket.bind((host1, port))
# 	serversocket.listen(5)
# 	clientsocket,addr = serversocket.accept()
# 	print("berhasil konek4", addr)
# 	while True:
# 		jenis = clientsocket.recv(4096)
# 		print("jenis = ", jenis)
# 		if not jenis:
# 			break
# 		sql = "INSERT INTO outbox (CreatorID, DestinationNumber, TextDecoded) SELECT pesan.admin, orang.no_hp, pesan.isi_pesan FROM pesan, orang WHERE pesan.id = ('%s')" %(jenis)
# 		cursor.execute(sql)
# 		db.commit()

try:
	thread.start_new_thread(image_capture,())
	thread.start_new_thread(ketinggian_air,())
	# thread.start_new_thread(sms_gateway,())
except Exception as e:
	print("Ada error "+e)
while 1:
	pass
