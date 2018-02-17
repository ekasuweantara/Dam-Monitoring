from __future__ import print_function # In python 2.7

from flask import Flask, redirect
from flask import render_template, url_for
from flask import request, flash
from flask import json, abort, jsonify
from flask import session
from flask import Markup
# import MySQLdb
import pymysql
import md5
import hashlib
import os, gc
import sys
import socket, time
import pickle
import random
import datetime
import sys
import thread
import time

app = Flask(__name__)
app.secret_key = "super secret key"

db = pymysql.connect(host='127.0.0.1',user='root',password='',database='gammu')
cursor = db.cursor()

#
db_pi = pymysql.connect(host='192.168.1.7',user='root',password='root',database='bendungan')
cursor_pi = db_pi.cursor()



@app.route("/tinggi_air")
def tinggi_air():
    sql = "SELECT * FROM tinggi_air ORDER BY id DESC LIMIT 1;"
    cursor.execute(sql)
    results = cursor.fetchall()
    db.commit()
    for row in results:
        tinggi = row[1]
        waktu = row[2]
        # print("ini data air ",results)

    # a = datetime.datetime.now()
    # waktu = a.hour, a.minute, a.second
    # tinggi = random.uniform(3.5, 6.5)
    # tinggi = str(round(tinggi,2))
    return render_template('tinggi_air.html', waktu = waktu, tinggi = tinggi)

@app.route("/image_capture")
def image_capture():
    sql = "SELECT * FROM gambar ORDER BY id DESC LIMIT 1;"
    cursor.execute(sql)
    results = cursor.fetchall()
    db.commit()
    for row in results:
        waktu = row[1]
        path = row[2]
    return render_template('image_capture.html', data_waktu = waktu, data_path = path)

@app.route("/")
def user():
    message = "The Flask Shop"
    return render_template('index.html')

@app.route("/login_admin")
def login_admin():
    return render_template('/admin/login_admin.html')

@app.route("/cek_login", methods = ["POST"])
def cek_login():
    try:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            md5Password = hashlib.md5()
            md5Password.update(password)
            md5Password = md5Password.hexdigest()

            if email and password:
                sql = "SELECT * FROM admin WHERE email = ('%s')" % (email)
                #try:
                email_db = 1
                cursor.execute(sql)
                results = cursor.fetchall()
                for row in results:
                    nama_db = row[1]
                    email_db = row[2]
                    password_db = row[3]
                    jenis_db = row[4]

                if email == email_db:
                    if md5Password == password_db:
                        if jenis_db > 0:
                            nama = nama_db
                            jenis = jenis_db
                            session['logged_in'] = True
                            session['nama'] = nama
                            session['jenis'] = jenis
                            return redirect('/dashboard')
                        else:
                            pesan = 'Anda belum diverifikasi'
                            return render_template('/admin/login_admin.html', pesan = pesan)
                    else:
                        pesan = 'Password salah'
                        return render_template('/admin/login_admin.html', pesan = pesan)

                else:
                    pesan = 'Email salah'
                    return render_template('/admin/login_admin.html', pesan = pesan)

    except Exception as e:
        return(str(e))

@app.route("/register_admin")
def register_admin():
    return render_template('/admin/register.html')

@app.route("/register", methods = ["GET", "POST"])
def register():
    try:
        if request.method == "POST":
            print("mau masuk")
            name = request.form['nama']
            email = request.form['email']
            password = request.form['password']
            md5 = hashlib.md5()
            md5.update(password)
            md5 = md5.hexdigest()


            query = "SELECT COUNT(*) FROM admin WHERE email = '%s'" % (email)
            cursor.execute(query)
            results = cursor.fetchone()
            if str(results) == '(0,)':
                sql = "INSERT INTO admin (nama, email, password) VALUES ('%s', '%s', '%s')" % (name, email, md5)
                try:
                    cursor.execute(sql)
                    db.commit()
                    return redirect('/login_admin')

                except:
                    db.rollback()

    except Exception as e:
        alert = 'Email sudah digunakan'
        return render_template('/admin/login_admin.html', pesan = alert)
    return render_template('/admin/register.html')

@app.route("/dashboard")
def dashboard():
    try:
        return render_template('/admin/dashboard.html')


    except Exception as e:
        return(str(e))
    return render_template('/admin/dashboard.html')

@app.route("/ketinggian_air")
def ketinggian_air():
    return render_template('/admin/data_ketinggian_air.html')

@app.route("/kontak")
def kontak():
    try:
        sql = "SELECT * FROM orang;"
        cursor.execute(sql)
        results = cursor.fetchall()
        data = results
        return render_template('/admin/kontak.html', data = data)

    except Exception as e:
        return(str(e))

    # try:
    #     sql = "SELECT * FROM orang;"
    #     cursor.execute(sql)
    #     results = cursor.fetchall()
    #     data = results
    #     return render_template('/admin/kontak.html', data = data)
    #
    # except Exception as e:
    #     return(str(e))

@app.route("/hapus_kontak", methods = ["GET", "POST"])
def hapus_kontak():
    data=0
    if request.method == "GET":
        data = request.args.get('data_id', 1, type=int)
    try:
        sql = "DELETE FROM orang WHERE id = %s;" % (data)
        cursor.execute(sql)
        db.commit()
        return str('success')

    except Exception as e:
        return(str(e))

@app.route("/lihat_kontak", methods = ["GET", "POST"])
def lihat_kontak():
    data=0
    if request.method == "GET":
        data = request.args.get('data_id', 1, type=int)
    # try:
    sql = "SELECT * FROM orang WHERE id = %s;" % (data)
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        id_kontak2 = row[0]
        no_hp = row[1]
        nama = row[2]
        alamat = row[3]
    id_kontak = id_kontak2
    no_hp_kontak = no_hp
    nama_kontak = nama
    alamat_kontak = alamat
    data = {'id':id_kontak, 'no_hp': no_hp_kontak, 'nama': nama_kontak, 'alamat': alamat_kontak}

    return jsonify(json.dumps(data))

        # return jsonify(data)

    # except Exception as e:
    #     return(str(e))


    # data=0
    # if request.method == "GET":
    #     data = request.args.get('data_id', 1, type=int)
    # # try:
    # print(data)
    # sql = "SELECT * FROM orang WHERE id = %s;" % (data)
    # cursor.execute(sql)
    # results = cursor.fetchall()
    # for row in results:
    #     id_kontak2 = row[0]
    #     no_hp = row[2]
    #     nama = row[1]
    #     alamat = row[3]
    # id_kontak = id_kontak2
    # no_hp_kontak = no_hp
    # nama_kontak = nama
    # alamat_kontak = alamat
    # print("id", id_kontak,"no hp", no_hp_kontak, "nama", nama_kontak, "alamat", alamat_kontak)
    # data = {'id':id_kontak, 'no_hp': no_hp_kontak, 'nama': nama_kontak, 'alamat': alamat_kontak}
    #
    # return jsonify(json.dumps(data))


@app.route("/update_kontak", methods = ["GET", "POST"])
def update_kontak():
    try:
        if request.method == "POST":
            id_kontak = request.form['id_kontak']
            nama = request.form['nama_kontak2']
            no_hp = request.form['no_hp_kontak2']
            no_hp2 = str(no_hp)
            alamat = request.form['alamat_kontak2']

            # print('Nama: ' + nama, file=sys.stderr)
            # print('No Hp.: ' + no_hp, file=sys.stderr)
            # print('Alamat: ' + alamat, file=sys.stderr)


            if nama and no_hp and alamat:
                sql = "UPDATE orang SET nama = '%s', no_hp = '%s', alamat = '%s' WHERE id = '%s'" % (nama, no_hp2, alamat, id_kontak)
                try:
                    cursor.execute(sql)
                    db.commit()
                except:
                    db.rollback()
    except Exception as e:
        return(str(e))
    return redirect('/kontak')

@app.route("/tambah_kontak", methods = ["GET", "POST"])
def tambah_kontak():
    try:
        if request.method == "POST":
            nama = request.form['nama_kontak']
            no_hp = request.form['no_hp_kontak']
            alamat = request.form['alamat_kontak']

            print('Nama: ' + nama, file=sys.stderr)
            print('No Hp.: ' + no_hp, file=sys.stderr)
            print('Alamat: ' + alamat, file=sys.stderr)


            if nama and no_hp and alamat:
                sql = "INSERT INTO orang (nama, no_hp, alamat) VALUES ('%s', '%s', '%s')" % (nama, no_hp, alamat)
                try:
                    cursor.execute(sql)
                    db.commit()
                except:
                    db.rollback()
    except Exception as e:
        return(str(e))
    return redirect('/kontak')

@app.route("/verifikasi")
def verifikasi():
    try:
        sql = "SELECT * FROM admin WHERE NOT status = 2;"
        cursor.execute(sql)
        results = cursor.fetchall()
        data = results
        return render_template('/admin/verifikasi.html', data = data)


    except Exception as e:
        return(str(e))

@app.route("/verifikasi_diterima", methods = ["GET", "POST"])
def verifikasi_diterima():
    data=0
    if request.method == "GET":
        data = request.args.get('data_id', 1, type=int)
    try:
        sql = "UPDATE admin SET status = 1 WHERE id_pegawai = %s;" % (data)
        cursor.execute(sql)
        db.commit()
        return str('success')

    except Exception as e:
        return(str(e))

@app.route("/verifikasi_ditolak", methods = ["GET", "POST"])
def verifikasi_ditolak():
    data=0
    if request.method == "GET":
        data = request.args.get('data_id', 1, type=int)
    try:
        sql = "DELETE FROM admin WHERE id_pegawai = %s;" % (data)
        cursor.execute(sql)
        db.commit()
        return str('success')

    except Exception as e:
        return(str(e))

@app.route("/pengaturan")
def pengaturan():
    return render_template('/admin/pengaturan.html', data=[{'jenis':'Waspada'}, {'jenis':'Siaga'}, {'jenis':'Awas'}, {'jenis':'Citra Bendungan'}])

@app.route("/atur", methods = ["GET"])
def atur():
    normal = request.args.get('myRange')
    waspada = request.args.get('myRange2')
    siaga = request.args.get('myRange3')
    awas = request.args.get('myRange4')
    threshold = request.args.get('myRange5', type=float)
    threshold = threshold/100
    text = request.args.get('text')
    jenis_pesan = request.args.get('jenis')
    dalam = request.args.get('myRange6')
    # if jenis_pesan == 'Normal':
    #     jenis_pesan = 1
    if jenis_pesan == 'Waspada':
        jenis_pesan = 1
    if jenis_pesan == 'Siaga':
        jenis_pesan = 2
    if jenis_pesan == 'Awas':
        jenis_pesan = 3
    if jenis_pesan == 'Citra Bendungan':
        jenis_pesan = 4

    # print('Normal: ' + normal, file=sys.stderr)
    # print('Waspada: ' + waspada, file=sys.stderr)
    # print('Siaga: ' + siaga, file=sys.stderr)
    # print('Awas: ' + awas, file=sys.stderr)
    # print('Threshold: ' + str(threshold), file=sys.stderr)
    # print('Text: ' + text, file=sys.stderr)
    # print('Jenis Pesan: ' + str(jenis_pesan), file=sys.stderr)
    try:
        try:
            sql1 = "UPDATE threshold SET threshold=%s WHERE id='1';" % (threshold)
            cursor_pi.execute(sql1)
            db_pi.commit()

            sql2 = "UPDATE tinggi SET tinggi=%s WHERE id='1';" % (normal)
            cursor_pi.execute(sql2)
            db_pi.commit()

            sql3 = "UPDATE tinggi SET tinggi=%s WHERE id='2';" % (waspada)
            cursor_pi.execute(sql3)
            db_pi.commit()

            sql4 = "UPDATE tinggi SET tinggi=%s WHERE id='3';" % (siaga)
            cursor_pi.execute(sql4)
            db_pi.commit()

            sql5 = "UPDATE tinggi SET tinggi=%s WHERE id='4';" % (awas)
            cursor_pi.execute(sql5)
            db_pi.commit()

            nama_admin = session['nama']
            sql6 = "UPDATE pesan SET isi_pesan='%s', admin='%s' WHERE id=%s;" % (text, nama_admin, jenis_pesan)
            cursor.execute(sql6)
            db.commit()

            sql7 = "UPDATE dalam SET dalam=%s WHERE id='1';" % (dalam)
            cursor_pi.execute(sql7)
            db_pi.commit()


        except Exception as e:
            db_pi.rollback()
    except Exception as e:
        return str(e)


    return redirect('/pengaturan')

@app.route("/logout")
def logout():
    try:



        sql = "DELETE FROM tinggi_air"
        cursor.execute(sql)
        db.commit()

        sql2 = "DELETE FROM gambar"
        cursor.execute(sql2)
        db.commit()

    except Exception as e:
        return(str(e))


    session['logged_in'] = False
    return redirect('/login_admin')

if __name__ == "__main__":
    app.run(debug=True)
