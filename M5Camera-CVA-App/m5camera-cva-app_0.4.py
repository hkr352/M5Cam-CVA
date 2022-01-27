#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python 3.7.4

'''
@file  m5camera-cva-app.py
@brief Object recognition camera
'''

__author__    = 'Mitsuhiro MIYAGUCHI'
__license__   = 'The MIT License'

# reference
# Google Cloud Vison API
# demo: https://cloud.google.com/vision/?hl=ja
# REST API: https://cloud.google.com/vision/docs/reference/rest?hl=ja

#Standard Library
import os
from subprocess import Popen
import time
import datetime
import webbrowser
from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
import json
#ThirdParty Library
import serial
import serial.tools.list_ports

green = '\033[92m'
yellow = '\033[93m'
red = '\033[91m'
end = '\033[0m'

def printg( text = 0):
    print(green + text + end)

def printy( text = 0):
    print(yellow + text + end)

def printr( text = 0):
    print(red + text + end)

class socketThread(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global detectFlag
        #global so
        while True:
            data, addr = so.recvfrom(1024)
            if data == b'detect':
                data = ""
                detectPic()
            elif data == b'con':
                print("CONNECT")
                #change framesize XGA(1024x768)
                text = "curl -s \"" + WEBADDRES + "/control?var=framesize&val=8\""
                popen = Popen(text, shell=True)
                popen.wait()
                print(">>")
            elif data == b'dcon':
                printy("DISCONNECT")
                print(">>")
            else:
                print(data)

# def socketConnect():
#     global so
#     so = socket(AF_INET, SOCK_DGRAM)
#     so.connect((ADDRESS, PORT))   # for client
#     print(so)

class serialThread(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global ser
        #global so
        while True:
            try:
                text = ser.readline()
                print(".", end="")#
                #print(text)
                
                if 'Camera Ready' in str(text):
                    print("")
                    print(text)
                    print("Auto connection")
                    so.sendto("con".encode(), (ADDRESS, PORT))
                    ser.close()
                    break
                elif "192.168" in str(text):
                    ser.close()
                    break
            except:
                print("read error")
                ser.close()
                break
        print("serialClose")
        print(">>")

def _findDevice():
    com = None
    for DEVICE in list(serial.tools.list_ports.comports()):
        if 'USB Serial Port' in DEVICE[1]:
            com = DEVICE[0]
        elif 'Silicon Labs CP210x USB to UART Bridge' in DEVICE[1]:
            com = DEVICE[0]
        else:
            print("None")
            print(DEVICE[1])
    return com

def serialConnect():
    global ser
    try:
        com = _findDevice()
        if not com == "None":
            ser = serial.Serial(com, 115200)
            print("m5camera serial connect")
            st = serialThread()
            st.setDaemon(True)
            st.start()
    except:
        print("serial not connect")

def detectPic():
    now = datetime.datetime.today()
    fileName = "photo/" + PHOTONAME + now.strftime('%Y%m%d_%H%M%S') + '.jpeg'
    print(fileName)
    popen = Popen("curl -s " + WEBADDRES + '/capture -o ' + fileName, shell=True)
    popen.wait()
    text = "cva.sh " + fileName +" "+ APIKEY
    #print(text)
    popen = Popen(text, shell=True)
    popen.wait()

    #path = os.getcwd()
    #webbrowser.open(path + "/" + fileName)

    with open("response.json", encoding="utf-8_sig") as f:
        js = json.load(f)
        print("")
        printy("Detect result:")
        try:
            print("Detect label result:")
            for index in range(len(js["responses"][0]["labelAnnotations"])):
                printg (js["responses"][0]["labelAnnotations"][index]["description"])
            print("")
        except Exception as e:
            print("None")

        try:
            print("Detect object result:")
            for index in range(len(js["responses"][0]["localizedObjectAnnotations"])):
                printg (js["responses"][0]["localizedObjectAnnotations"][index]["name"])
            print("")
        except Exception as e:
            print("None")
            
        try:
            print("Detect text result:")
            for index in range(len(js["responses"][0]["textAnnotations"])):
                printg (js["responses"][0]["textAnnotations"][index]["description"])
            print("")
        except Exception as e:
            print("None")

def jsonSaveLoad(save = False):

    with open("config.json", 'r', encoding="utf-8_sig") as f:
        js = json.load(f)

        global ADDRESS, WEBADDRES, PORT, PHOTONAME
        global SSID, PASSWORD, APIKEY

        if not save:
            ADDRESS =   js["ip-addres"] # M5Stack address
            WEBADDRES = "http://" + ADDRESS
            PORT = int(js["port"])
            PHOTONAME = js["photo-name"]
            SSID =      js["ssid"]
            PASSWORD =  js["password"]
            APIKEY =    js["api-key"]

        if save:
            js["ip-addres"] = ADDRESS
            WEBADDRES = "http://" + ADDRESS
            js['port'] = PORT
            js["photo-name"] = PHOTONAME
            js["ssid"] = SSID
            js["password"] = PASSWORD
 
            with open("config.json", 'w+', encoding="utf-8_sig") as f:
                json.dump(js, f, indent=2)
            print("save param")

if __name__ == "__main__":

    #ADDRESS = "192.168.2.144" # M5Stack address
    ADDRESS = "192.168.2.117" # M5Stack address
    WEBADDRES = "http://" + ADDRESS
    PORT = 50104
    PHOTONAME = "photo_"
    SSID =""
    PASSWORD=""
    APIKEY = ""

    jsonSaveLoad()

    so = socket(AF_INET, SOCK_DGRAM)
    so.connect((ADDRESS, PORT))   # for client

    th = socketThread()
    th.setDaemon(True)
    th.start()

    global ser
    serialConnect()

    print("Auto connection")
    so.sendto("con".encode(), (ADDRESS, PORT))

    menuText =\
    "Key input \r\n"+\
    "\r\n"+\
    "m5ip: change ipAddress\r\n"+\
    "con : connection\r\n"+\
    "dcon: disconnection\r\n"+\
    "str : stream\r\n"+\
    "cap : capture\r\n"+\
    "wcap: webcapture\r\n"+\
    "det : detect\r\n"+\
    "menu: menutext\r\n"+\
    "ssid: change ssid\r\n"+\
    "pass: change pass\r\n"+\
    "name: change photo name\r\n"+\
    "config: M5Camera config\r\n"+\
    "cnw: change net work\r\n"+\
    "exit: close\r\n"
    print(menuText)

    while True:
        key = input('>> ')
        if key == "str":
            url = WEBADDRES + ":81/stream"
            #http://192.168.2.144:81/stream
            webbrowser.open(url)
        elif key == "cap":
            now = datetime.datetime.today()
            fileName = "photo/" + PHOTONAME + now.strftime('%Y%m%d_%H%M%S') + '.jpeg'
            popen = Popen("curl -s " + WEBADDRES + '/capture -o ' + fileName, shell=True)
            popen.wait()
            #print (fileName)
            #im = Image.open(fileName)
            #im.show()
        elif key == "wcap":
            webbrowser.open(WEBADDRES + "/capture")
        elif key == "det":
            detectPic()
        elif key == "con":
            so.sendto(key.encode(), (ADDRESS, PORT))
            #print(so)
        elif key == "dcon":
            so.sendto(key.encode(), (ADDRESS, PORT))
        elif key == "config":
            webbrowser.open(WEBADDRES)
        elif key == "m5ip":
            print("Input m5ip. Example: 192.168.1.255")
            key = input('>> ')
            ADDRESS = key
            print("Change ip")
            jsonSaveLoad(True)
            print("Exit because IPaddres changed.")
            print("Please Reboot App.")
            print("IPアドレスが変更されたため、終了します")
            print("アプリを再起動してください")
            time.sleep(3)
            break
        elif key == "ssid":
            print("Input SSID.")
            key = input('>> ')
            SSID = key
            print("Change SSID")
            jsonSaveLoad(True)
        elif key == "pass":
            print("Input Password.")
            key = input('>> ')
            PASSWORD = key
            print("Change Password")
            jsonSaveLoad(True)
        elif key == "menu":
            print(menuText)
        elif key == "name":
            print("Input photo name to change")
            key = input('>> ')
            PHOTONAME = key
        elif key == "param":
            print(ADDRESS)
            print(WEBADDRES)
            print(PORT)
            print(PHOTONAME)
            print(SSID)
            print(PASSWORD)
            print(APIKEY)
        elif key == "serial":
            serialConnect()
        elif key == "cnw":
            try:
                #ser.write(unicode("SSID\n"))
                ser.write("SSID\n".encode('utf-8'))
                ser.write((SSID+"\n").encode('utf-8'))
                ser.write("PASS\n".encode('utf-8'))
                ser.write((PASSWORD+"\n").encode('utf-8'))
                ser.write("CON\n".encode('utf-8'))
            except:
                print("not connect")
        elif key == "exit":
            break
        else :
            print("Type error")
    so.close()