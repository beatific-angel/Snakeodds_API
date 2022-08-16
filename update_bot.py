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


def set_surebet_main(surebet_lists):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = 'INSERT INTO finder_surebets (surebet_id, cha_id, percent, sport,event_name, group_name, bet_time, bet1_event_name, \
        bet1_group_name, bet_bk1, bet_desc1, bet_market_val1, bet_koef1,bet2_event_name, bet2_group_name, bet_bk2, bet_desc2, bet_market_val2, bet_koef2,bet3_event_name, \
            bet3_group_name, bet_bk3, bet_desc3, bet_market_val3, bet_koef3, created_at, updated_at) ' \
          'VALUES (%s, %s,%s, %s,%s, %s,%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s,%s, %s, %s) ON DUPLICATE KEY UPDATE \
                percent=VALUES(percent),sport=VALUES(sport),event_name=VALUES(event_name),group_name=VALUES(group_name), \
                bet_time=VALUES(bet_time),bet1_event_name=VALUES(bet1_event_name),bet1_group_name=VALUES(bet1_group_name),bet_bk1=VALUES(bet_bk1),bet_desc1=VALUES(bet_desc1),bet_market_val1=VALUES(bet_market_val1), \
                bet_koef1=VALUES(bet_koef1),bet2_event_name=VALUES(bet2_event_name),bet2_group_name=VALUES(bet2_group_name),bet_bk2=VALUES(bet_bk2),bet_desc2=VALUES(bet_desc2),bet_market_val2=VALUES(bet_market_val2), \
                bet_koef2=VALUES(bet_koef2),bet3_event_name=VALUES(bet3_event_name),bet3_group_name=VALUES(bet3_group_name),bet_bk3=VALUES(bet_bk3),bet_desc3=VALUES(bet_desc3),bet_market_val3=VALUES(bet_market_val3), \
                bet_koef3=VALUES(bet_koef3),updated_at=VALUES(updated_at) ;'
    with mycursor as cursor:
        try:
            cursor.executemany(sql, surebet_lists)
            mydb.commit()
        except Exception as e:
            print('f', f'set_surebet Exception: {repr(e)}')
    cursor.close()


def set_surebet_child(alt_surebet_lists):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = 'INSERT INTO finder_surebets_child (surebet_id, cha_id, percent, sport,event_name, group_name, bet_time, bet1_event_name, \
        bet1_group_name, bet_bk1, bet_desc1, bet_market_val1, bet_koef1,bet2_event_name, bet2_group_name, bet_bk2, bet_desc2, bet_market_val2, bet_koef2,bet3_event_name, \
            bet3_group_name, bet_bk3, bet_desc3, bet_market_val3, bet_koef3, parent_id, created_at, updated_at) ' \
          'VALUES (%s, %s,%s, %s,%s, %s,%s, %s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s) ON DUPLICATE KEY UPDATE cha_id=VALUES(cha_id), \
                percent=VALUES(percent),sport=VALUES(sport),event_name=VALUES(event_name),group_name=VALUES(group_name), \
                bet_time=VALUES(bet_time),bet1_event_name=VALUES(bet1_event_name),bet1_group_name=VALUES(bet1_group_name),bet_bk1=VALUES(bet_bk1),bet_desc1=VALUES(bet_desc1),bet_market_val1=VALUES(bet_market_val1), \
                bet_koef1=VALUES(bet_koef1),bet2_event_name=VALUES(bet2_event_name),bet2_group_name=VALUES(bet2_group_name),bet_bk2=VALUES(bet_bk2),bet_desc2=VALUES(bet_desc2),bet_market_val2=VALUES(bet_market_val2), \
                bet_koef2=VALUES(bet_koef2),bet3_event_name=VALUES(bet3_event_name),bet3_group_name=VALUES(bet3_group_name),bet_bk3=VALUES(bet_bk3),bet_desc3=VALUES(bet_desc3),bet_market_val3=VALUES(bet_market_val3), \
                bet_koef3=VALUES(bet_koef3),updated_at=VALUES(updated_at) ;'
    with mycursor as cursor:
        try:
            cursor.executemany(sql, alt_surebet_lists)
            mydb.commit()
        except Exception as e:
            print('f', f'set_surebet Exception: {repr(e)}')
    cursor.close()


def set_valuebet_main(val_params):
    mydb = getConnection()
    mycursor = mydb.cursor()
    # sql = 'INSERT INTO valuebets (valuebet_id,cha_id, percent, sport,event_name, group_name, bet_time, bet_bk, bet_market_val, bet_koef, bet_desc, created_at, updated_at) ' \
    #       'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE percent=VALUES(percent), \
    #             sport=VALUES(sport),event_name=VALUES(event_name),group_name=VALUES(group_name), \
    #             bet_time=VALUES(bet_time),bet_bk=VALUES(bet_bk),bet_market_val=VALUES(bet_market_val), \
    #             bet_koef=VALUES(bet_koef),bet_desc=VALUES(bet_desc),updated_at=VALUES(updated_at) ;'

    sql = "INSERT INTO valuebets (valuebet_id,cha_id, percent, sport,event_name, group_name, bet_time, bet_bk, bet_market_val, bet_koef, bet_desc, created_at, updated_at)\
            VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(\
                val_params[0],val_params[1],val_params[2],val_params[3],val_params[4],val_params[5],val_params[6],val_params[7]\
                ,val_params[8],val_params[9],val_params[10],val_params[11],val_params[12])                
    mycursor.execute(sql)
    mydb.commit()
    mycursor.close()


def set_exchange_main(exchange_lists):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = 'INSERT INTO finder_exchangelists (exchange_id, cha_id, percent, sport,event_name, group_name, bet_time, evento_book, \
            gruppo_book, nome_book, valore_book, hash_id_book, sigla_hash_book,desc_hash_book, datetime_book, url_desktop_book, evento_exchange, gruppo_exchange, \
            url_desktop_exchange,book_exchange, nome_exchange, valore_exchange, hash_id_exchange, sigla_hash_exchange, desc_hash_exchange, tipo_exchange, \
            desc_tipo, datetime_exchange, created_at, updated_at) ' \
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE \
                percent=VALUES(percent),sport=VALUES(sport),event_name=VALUES(event_name),group_name=VALUES(group_name), \
                bet_time=VALUES(bet_time),evento_book=VALUES(evento_book),gruppo_book=VALUES(gruppo_book),nome_book=VALUES(nome_book),valore_book=VALUES(valore_book),hash_id_book=VALUES(hash_id_book), \
                sigla_hash_book=VALUES(sigla_hash_book),desc_hash_book=VALUES(desc_hash_book),datetime_book=VALUES(datetime_book),url_desktop_book=VALUES(url_desktop_book),evento_exchange=VALUES(evento_exchange),gruppo_exchange=VALUES(gruppo_exchange), \
                url_desktop_exchange=VALUES(url_desktop_exchange),book_exchange=VALUES(book_exchange),nome_exchange=VALUES(nome_exchange),valore_exchange=VALUES(valore_exchange),hash_id_exchange=VALUES(hash_id_exchange),sigla_hash_exchange=VALUES(sigla_hash_exchange), \
                desc_hash_exchange=VALUES(desc_hash_exchange),tipo_exchange=VALUES(tipo_exchange),desc_tipo=VALUES(desc_tipo),datetime_exchange=VALUES(datetime_exchange),updated_at=VALUES(updated_at) ;'
    with mycursor as cursor:
        try:
            cursor.executemany(sql, exchange_lists)
            mydb.commit()
        except Exception as e:
            print('f', f'set_exchange Exception: {repr(e)}')
    cursor.close()    

def set_exchange_child(alt_exchange_childlists):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = 'INSERT INTO finder_exchange_childlists (exchange_id, cha_id, parent_id, percent, sport,event_name, group_name, bet_time, evento_book, \
            gruppo_book, nome_book, valore_book, hash_id_book, sigla_hash_book,desc_hash_book, datetime_book, url_desktop_book, evento_exchange, gruppo_exchange, \
            url_desktop_exchange,book_exchange, nome_exchange, valore_exchange, hash_id_exchange, sigla_hash_exchange, desc_hash_exchange, tipo_exchange, \
            desc_tipo, datetime_exchange, created_at, updated_at) ' \
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE \
                percent=VALUES(percent),sport=VALUES(sport),event_name=VALUES(event_name),group_name=VALUES(group_name), \
                bet_time=VALUES(bet_time),evento_book=VALUES(evento_book),gruppo_book=VALUES(gruppo_book),nome_book=VALUES(nome_book),valore_book=VALUES(valore_book),hash_id_book=VALUES(hash_id_book), \
                sigla_hash_book=VALUES(sigla_hash_book),desc_hash_book=VALUES(desc_hash_book),datetime_book=VALUES(datetime_book),url_desktop_book=VALUES(url_desktop_book),evento_exchange=VALUES(evento_exchange),gruppo_exchange=VALUES(gruppo_exchange), \
                url_desktop_exchange=VALUES(url_desktop_exchange),book_exchange=VALUES(book_exchange),nome_exchange=VALUES(nome_exchange),valore_exchange=VALUES(valore_exchange),hash_id_exchange=VALUES(hash_id_exchange),sigla_hash_exchange=VALUES(sigla_hash_exchange), \
                desc_hash_exchange=VALUES(desc_hash_exchange),tipo_exchange=VALUES(tipo_exchange),desc_tipo=VALUES(desc_tipo),datetime_exchange=VALUES(datetime_exchange),updated_at=VALUES(updated_at) ;'
    with mycursor as cursor:
        try:
            cursor.executemany(sql, alt_exchange_childlists)
            mydb.commit()
        except Exception as e:
            print('f', f'set_exchange Exception: {repr(e)}')
    cursor.close()  
