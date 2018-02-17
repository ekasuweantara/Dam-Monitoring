from __future__ import division

import cv2
import numpy as np
import picamera
import RPi.GPIO as GPIO
import time
import datetime
import MySQLdb as mdb
import sys
import thread
import socket
from socket import error as SocketError
import errno
import pickle

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#deklarasi dan konekting
con = mdb.connect('localhost', 'root', 'root', 'bendungan');
cur = con.cursor()

con_win = mdb.connect('192.168.43.162', 'root', 'password', 'gammu');
cur_win = con_win.cursor()

TRIG = 4
ECHO = 17
print "jarak sedang diproses"
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.output(TRIG, False)
print "menunggu sensor"
time.sleep(2)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '192.168.43.162'
port = 9999



def send_data_pic():
	try:
		with open("gambar.jpg", "rb") as fh:
			time.sleep(5)
			s.send(fh.read())
			time.sleep(5)
	except SocketError as e:
		if e.errno != errno.ECONNRESET:
			raise
		pass

def threshold():
	try:
		sql = "SELECT *FROM threshold"
		cur.execute(sql)
		data = cur.fetchall()
		for row in data:
			thres = row[1]
		return thres
	except mdb.Error, e:
		print "Select Data Gagal1"

def capture():
    #ambil gbr set resolusi 120x90
	with picamera.PiCamera() as camera:
		camera.resolution = (180, 150)
		camera.capture('gambar.jpg')

def aslitobw():
    #ambil gbr dan convert ke binary
    im_gray = cv2.imread('gambar.jpg', 0)
    #print im_gray.shape
    (thresh, im_bw) = cv2.threshold(im_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    thresh = 127
    im_bw = cv2.threshold(im_gray, thresh, 255, cv2.THRESH_BINARY)[1]
    #cv2.imwrite('gambar_bw1.png', im_bw)
    return im_bw
    
def konversi(im_bw):
    #ambil gbr dan mengubah ke array data
    x = im_bw.reshape(1, np.prod(im_bw.shape))
    img_data = np.asarray(x)

    #cek RGB tiap pixel
    for i in range(len(img_data)):
        for j in range(len(img_data[0])):
            if img_data[i][j] == 255:
                img_data[i][j] = 1
            #print(img_data[i][j])
    return img_data
    
def jaccard_similarity(x,y):
	xy = np.dot(x, y)
	xx = np.sum(x)
	yy = np.sum(y)
	return xy/(xx+yy-xy)


def ambil_tinggi():
	try:
		sql = "SELECT *FROM tinggi"
		cur.execute(sql)
		con.commit()
		data = cur.fetchall()
		return data
	except mdb.Error, e:
		print "Select Data Gagal"

		
def ambil_kedalaman():
	try:
		sql = "SELECT *FROM dalam"
		cur.execute(sql)
		con.commit()
		data = cur.fetchall()
		return data
	except mdb.Error, e:
		print "Select Data Gagal"

def sms_gateway(jenis):
	sql = "INSERT INTO outbox (CreatorID, DestinationNumber, TextDecoded) SELECT pesan.admin, orang.no_hp, pesan.isi_pesan FROM pesan, orang WHERE pesan.id = ('%s')" %(jenis)
	cur_win.execute(sql)
	con_win.commit()


thres = ambil_tinggi()

tinggi_normal = thres[0][1]
tinggi_waspada = thres[1][1]
tinggi_siaga = thres[2][1]
tinggi_awas = thres[3][1]

#print 'normal: ', tinggi_normal, 'waspada: ', tinggi_waspada, 'siaga: ', tinggi_siaga, 'awas: ', tinggi_awas


status_normal = thres[0][2]
status_waspada = thres[1][2]
status_siaga = thres[2][2]
status_awas = thres[3][2]

dal = ambil_kedalaman()
dalam = dal[0][1]


def ketinggian_air():
	i = 1
	while True:
		a = datetime.datetime.now()
		waktu_sekarang_air = a.hour, a.minute, a.second
		GPIO.output(TRIG, True)
		time.sleep(0.00001)
		GPIO.output(TRIG, False)

		while GPIO.input(ECHO) == 0:
			pulse_start = time.time()

		while GPIO.input(ECHO) == 1:
			pulse_end = time.time()

		pulse_duration = pulse_end - pulse_start
		jarak = pulse_duration * 17150
		jarak = round(jarak, 2)
		tinggi = dalam - jarak
		#tinggi air 3,3
		
		if tinggi <= tinggi_normal:
			print "keadaan air ", status_normal
			
		elif tinggi <= tinggi_waspada:
			print "keadaan air ", status_waspada
			sms_gateway(1)
			
		elif tinggi <= tinggi_siaga:
			print "keadaan air ", status_siaga
			sms_gateway(2)
			
		else:
			print "keadaan air ", status_awas
			sms_gateway(3)
		#print "jarak : ", jarak, "cm"
		
		
		#send_data_air(tinggi, waktu_sekarang_air)
		sql = "INSERT INTO tinggi_air(id, tinggi, waktu) VALUES ('%s', '%s', '%s')" % (i, tinggi, waktu_sekarang_air)
		cur_win.execute(sql)
		con_win.commit()
		print "tinggi : ", tinggi, "cm waktu ke : ", waktu_sekarang_air
		i = i + 1
		 
		time.sleep(1)
	GPIO.cleanup()


def image_capture():
	s.connect((host, port))
	thres = threshold()
	capture()
	send_data_pic()
	im_bw = aslitobw()
	x = konversi(im_bw)
	x = x.tolist()[0]
	capture()
	send_data_pic()
	im_bw = aslitobw()
	y = konversi(im_bw)
	y = y.tolist()[0]
	img1 = jaccard_similarity(x,y)
	while True:
		capture()
		send_data_pic()
		im_bw = aslitobw()
		y = konversi(im_bw)
		y = y.tolist()[0]
		print('gambar 1 ' + str(np.sum(x)))
		print('gambar 2 ' + str(np.sum(y)))

		img2 = jaccard_similarity(x,y)
		selisih = float(abs(img2 - img1))
		img1 = img2
		if selisih > float(thres):
			sms_gateway(4)

		print("%.2f" % jaccard_similarity(x,y))
		print("%.2f" % selisih)
	
		x = y
		time.sleep(10)
	cv2.waitKey(0)                 # Waits forever for user to press any key
	cv2.destroyAllWindows()        # Closes displayed windows


# Create two threads as follows
try:
   thread.start_new_thread(image_capture,())
   thread.start_new_thread(ketinggian_air,())
except:
   print "Error: unable to start thread"

while 1:
   pass
