import os
import sys
import json
import time
import random
import requests
import webbrowser
import subprocess
def log(text):
    print(text)
def readfile(path):
 with open (path, 'r') as file:
        return file.read()
def writefile(path, data):
    with open (path, 'w') as file:
        file.write(data)
def deletefile(path):
    if os.path.exists(path):
        os.remove(path)
def exit():
    sys.exit()
def exists(path):
    return os.path.exists(path)
def create(path, data=""):
    with open (path, 'w') as file:
        file.write(data)
def read_json(path):
    with open (path, 'r') as file:
        return json.load(file)
def write_json(path, data):
    with open (path, 'w') as file:
        json.dump(data, file)
def delete(path):
    if os.path.exists(path):
        os.remove(path)
def readtime():
    return time.time()
def wait(seconds):
    time.sleep(seconds)
def format_time(t):
    return time.strftime("%I%M", time.localtime(t))
def current_time():
    return time.strftime("%I%M", time.localtime())
def current_time_int():
    return int(current_time())
def random(minimum, maximum):
    return random.randint(minimum, maximum)
def openurl(url):
    webbrowser.open(url)
def newtab(url):
    webbrowser.open_new_tab(url)
def opennew(url):
    webbrowser.open_new(url)
def newwindow(url):
    webbrowser.open_new_window(url)
def geturl(url):
    response = requests.get(url)
    return response.text
def clearlog():
    os.system('cls' if os.name == 'nt' else 'clear')
def cmd(command):
    return subprocess.run(command, shell=True, capture_output=True, text=True).stdout
