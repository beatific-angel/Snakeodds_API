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




chromeOptions = webdriver.ChromeOptions()
#adding specific Chrome Profile Path
chromeOptions.add_argument("user-data-dir=C:\\Users\\sh225\\AppData\\Local\\Google\\Chrome Beta\\User Data\\\Default")
#set chromedriver.exe path
chromeOptions.add_argument("--headless")
chromeOptions.add_argument("--disable-gpu")
chromeOptions.add_argument("--no-sandbox")
chromeOptions.binary_location = "C:/Program Files/Google/Chrome Beta/Application/chrome.exe"
driver = webdriver.Chrome(executable_path="chromedriver.exe", options=chromeOptions)
#maximize browser
driver.set_window_size(1366, 768)


print('Sucessfully the webdriver runned.')

user_email = "filomenasalaris375@gmail.com"
password = "Gimbo123"


def login():
    print("login")
    driver.get(login_url)
    time.sleep(1)

    driver.find_element_by_id('user_login').send_keys(user_email)
    driver.find_element_by_id('user_pass').send_keys(password)
    visibilitytag = driver.find_elements_by_xpath('//div[contains(@class, "grecaptcha-badge")]')
    if visibilitytag[0].is_displayed():
        if (len(driver.find_elements_by_xpath('//div[contains(@class, "grecaptcha-logo")]'))) > 0:
            solver = TwoCaptcha('aacf25b9da54ec379de9c1d4c4aee92c')
            element = driver.find_elements_by_xpath('//div[contains(@class, "grecaptcha-logo")]')
            sitekeyurl = element[0].find_element_by_xpath('//iframe').get_attribute("src")
            parsed_url = urlparse(sitekeyurl)
            keygetparam = parse_qs(parsed_url.query)
            print(keygetparam)
            getsitekey = keygetparam['k']
            sitekey = getsitekey[0]
            while 1:
                try:
                    result = solver.solve_captcha(sitekey, driver.current_url)
                except Exception as e:
                    print(str(e))
                else:
                    print('solved: ' + str(result))
                    break

            driver.execute_script('document.getElementById("g-recaptcha-response-100000").innerHTML = "%s"' % result)
            try:
                # driver.find_element_by_xpath('//button[@type="submit" and contains(@class, "btn-submit")]').click()
                driver.find_element_by_xpath('//form[@id="wp-submit"]').submit()
            except:
                pass

            time.sleep(1)
    else:
        driver.find_element_by_xpath('//input[@id="wp-submit"]').click()
        time.sleep(3)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="nav-menu-item-4846"]')))


def unserialize_array(serialized_array):
    return dict(enumerate(re.findall(r'"((?:[^"\\]|\\.)*)"', serialized_array)))


def get_online_users():
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = "SELECT * FROM users AS e INNER JOIN paypal_subscriptions AS u ON e.id = u.user_id WHERE e.login_status='1' and (u.status = 'ACTIVE' or ( u.status = 'CANCELLED' AND now() < u.end_at ))"
    # "SELECT * FROM users where login_status ='1' and subscription_status = 'ACTIVE' "
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    if len(myresult) > 0:
        return myresult
    else:
        return True


def get_focus(userid):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = "SELECT * FROM users WHERE id = '{}'".format(userid)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    if len(myresult) > 0:
        return myresult
    else:
        return True


def get_bk_lists(userid, filtertype):
    if (userid != ''):
        if (filtertype == 'prematch'):
            mydb = getConnection()
            mycursor = mydb.cursor()
            sql = "SELECT * FROM filterlists WHERE userid = '{}' and filtertype = 'prematch' and check_status = '1'".format(
                userid)
            mycursor.execute(sql)
            myresult = mycursor.fetchall()
            mycursor.close()
            mydb.close()
            if len(myresult) > 0:
                return myresult
            else:
                return True

        elif (filtertype == 'valuebet'):
            mydb = getConnection()
            mycursor = mydb.cursor()
            sql = "SELECT * FROM filterlists WHERE userid = '{}' and filtertype = 'valuebet' and check_status = '1'".format(
                userid)
            mycursor.execute(sql)
            myresult = mycursor.fetchall()
            mycursor.close()
            mydb.close()
            if len(myresult) > 0:
                return myresult
            else:
                return True

        elif (filtertype == 'oddsmatcher'):
            mydb = getConnection()
            mycursor = mydb.cursor()
            sql = "SELECT * FROM filterlists WHERE userid = '{}' and filtertype = 'oddsmatcher' and check_status = '1'".format(
                userid)
            mycursor.execute(sql)
            myresult = mycursor.fetchall()
            mycursor.close()
            mydb.close()
            if len(myresult) > 0:
                return myresult
            else:
                return True
    else:
        return True

