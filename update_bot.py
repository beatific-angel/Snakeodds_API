from contextlib import suppress
from operator import index
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests.auth import HTTPBasicAuth
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from twocaptcha import TwoCaptcha
from threading import Thread
from urllib.parse import urlparse, parse_qs
import sys
import time
import csv
import requests
import json
import re
import numpy as np
import threading
from multiprocessing import Process
import mysql.connector
from datetime import datetime, timedelta
import base64


def getConnection():
    mydb = mysql.connector.connect(
        host="178.62.242.69",
        user="root",
        password="qazQAZ123@@",
        database="betting"
    )
    return mydb


url = 'https://www.finderbet.it/surebet'
url2 = 'https://www.finderbet.it/valuebet'
url3 = 'https://www.finderbet.it/exchange'
login_url = 'https://www.finderbet.it/login/'
saveurl = 'https://www.finderbet.it/account/?action=profile-filtri'


