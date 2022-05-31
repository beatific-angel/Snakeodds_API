from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        host="127.0.0.1",
        user="remote_betmanager",
        password="6Ov@4xg6",
        database="betting"
    )
    return mydb


url = 'https://www.finderbet.it/surebet'
url2 = 'https://www.finderbet.it/valuebet'
url3 = 'https://www.finderbet.it/exchange'
login_url = 'https://www.finderbet.it/login/'

options = webdriver.FirefoxOptions()
options.add_argument("--start-maximized")
profile = webdriver.FirefoxProfile(
    r"C:\Users\Administrator\AppData\Roaming\Mozilla\Firefox\Profiles\m5nrup07.default-release")

driver = webdriver.Firefox(executable_path="geckodriver.exe", options=options, firefox_profile=profile)
mainWin = driver.current_window_handle

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
            element  = driver.find_elements_by_xpath('//div[contains(@class, "grecaptcha-logo")]')
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

def set_surebet_main(surebet_lists):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = 'INSERT INTO finder_surebets (surebet_id, cha_id, formula_id, createtime, percent, sport,event_name, group_name, bet_time, bet1_event_name, \
        bet1_group_name, bet_bk1, bet_market_val1, bet_koef1,bet2_event_name, bet2_group_name, bet_bk2, bet_market_val2, bet_koef2,bet3_event_name, \
            bet3_group_name, bet_bk3, bet_market_val3, bet_koef3,parent, created_at, updated_at) ' \
          'VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s, %s,%s, %s,%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s) ON DUPLICATE KEY UPDATE cha_id=VALUES(cha_id), \
                formula_id=VALUES(formula_id),createtime=VALUES(createtime),percent=VALUES(percent),sport=VALUES(sport),event_name=VALUES(event_name),group_name=VALUES(group_name), \
                bet_time=VALUES(bet_time),bet1_event_name=VALUES(bet1_event_name),bet1_group_name=VALUES(bet1_group_name),bet_bk1=VALUES(bet_bk1),bet_market_val1=VALUES(bet_market_val1), \
                bet_koef1=VALUES(bet_koef1),bet2_event_name=VALUES(bet2_event_name),bet2_group_name=VALUES(bet2_group_name),bet_bk2=VALUES(bet_bk2),bet_market_val2=VALUES(bet_market_val2), \
                bet_koef2=VALUES(bet_koef2),bet3_event_name=VALUES(bet3_event_name),bet3_group_name=VALUES(bet3_group_name),bet_bk3=VALUES(bet_bk3),bet_market_val3=VALUES(bet_market_val3), \
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
    sql = 'INSERT INTO finder_surebet_childs (surebet_id, cha_id, formula_id, createtime, percent, sport,event_name, group_name, bet_time, bet1_event_name, \
        bet1_group_name, bet_bk1, bet_market_val1, bet_koef1,bet2_event_name, bet2_group_name, bet_bk2, bet_market_val2, bet_koef2,bet3_event_name, \
            bet3_group_name, bet_bk3, bet_market_val3, bet_koef3, child, created_at, updated_at) ' \
          'VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s, %s, %s,%s, %s, %s, %s) ON DUPLICATE KEY UPDATE cha_id=VALUES(cha_id), \
                formula_id=VALUES(formula_id),createtime=VALUES(createtime),percent=VALUES(percent),sport=VALUES(sport),event_name=VALUES(event_name),group_name=VALUES(group_name), \
                bet_time=VALUES(bet_time),bet1_event_name=VALUES(bet1_event_name),bet1_group_name=VALUES(bet1_group_name),bet_bk1=VALUES(bet_bk1),bet_market_val1=VALUES(bet_market_val1), \
                bet_koef1=VALUES(bet_koef1),bet2_event_name=VALUES(bet2_event_name),bet2_group_name=VALUES(bet2_group_name),bet_bk2=VALUES(bet_bk2),bet_market_val2=VALUES(bet_market_val2), \
                bet_koef2=VALUES(bet_koef2),bet3_event_name=VALUES(bet3_event_name),bet3_group_name=VALUES(bet3_group_name),bet_bk3=VALUES(bet_bk3),bet_market_val3=VALUES(bet_market_val3), \
                bet_koef3=VALUES(bet_koef3),updated_at=VALUES(updated_at) ;'
    with mycursor as cursor:
        try:
            cursor.executemany(sql, alt_surebet_lists)
            mydb.commit()
        except Exception as e:
            print('f', f'set_surebet Exception: {repr(e)}')
    cursor.close()    

def set_valuebet_main(valuebet_lists):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = 'INSERT INTO valuebets (cha_id, percent, sport,event_name, group_name, bet_time, bet_bk, bet_market_val, bet_koef, created_at, updated_at) ' \
          'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE percent=VALUES(percent), \
                sport=VALUES(sport),event_name=VALUES(event_name),group_name=VALUES(group_name), \
                bet_time=VALUES(bet_time),bet_bk=VALUES(bet_bk),bet_market_val=VALUES(bet_market_val), \
                bet_koef=VALUES(bet_koef),updated_at=VALUES(updated_at) ;'
    with mycursor as cursor:
        try:
            cursor.executemany(sql, valuebet_lists)
            mydb.commit()
        except Exception as e:
            print('f', f'set_surebet Exception: {repr(e)}')
    cursor.close()

def set_exchange_main(exchange_lists):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = 'INSERT INTO exchange_lists (surebet_id, cha_id, hash_id_book, hash_id_exchange,tipo_exchange, desc_tipo, sport_id,bookmakers_id_exchange, \
                percent, sport,event_name, group_name, bet_time,bet1_event_name, bet1_group_name, bet_bk1, bet_market_val1, bet_koef1, \
                bet2_event_name, bet2_group_name, bet_bk2, bet_market_val2, bet_koef2, exchange_title, exchange_fund, exchange_commision, created_at, updated_at) ' \
          'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE surebet_id=VALUES(surebet_id), cha_id=VALUES(cha_id), \
                hash_id_book=VALUES(hash_id_book),hash_id_exchange=VALUES(hash_id_exchange),tipo_exchange=VALUES(tipo_exchange),desc_tipo=VALUES(desc_tipo), sport_id=VALUES(sport_id), \
                bookmakers_id_exchange=VALUES(bookmakers_id_exchange),percent=VALUES(percent),sport=VALUES(sport),event_name=VALUES(event_name),group_name=VALUES(group_name), \
                bet_time=VALUES(bet_time),bet1_event_name=VALUES(bet1_event_name),bet1_group_name=VALUES(bet1_group_name),bet_bk1=VALUES(bet_bk1),bet_market_val1=VALUES(bet_market_val1), \
                bet_koef1=VALUES(bet_koef1),bet2_event_name=VALUES(bet2_event_name),bet2_group_name=VALUES(bet2_group_name),bet_bk2=VALUES(bet_bk2),bet_market_val2=VALUES(bet_market_val2), \
                bet_koef2=VALUES(bet_koef2),exchange_title=VALUES(exchange_title),exchange_fund=VALUES(exchange_fund), \
                exchange_commision=VALUES(exchange_commision),updated_at=VALUES(updated_at) ;'
    with mycursor as cursor:
        try:
            cursor.executemany(sql, exchange_lists)
            #cursor.execute(sql)
            mydb.commit()
        except Exception as e:
            print('f', f'set_surebet Exception: {repr(e)}')
    cursor.close()

def init():
    login()

def get_data_api():
    driver.get(url)
    time.sleep(0.5)
    s = requests.Session()
    request_cookies_browser = driver.get_cookies()
    c = [s.cookies.set(c['name'], c['value']) for c in request_cookies_browser]
    nonce_site = driver.find_element_by_id("action-set-filtri_nonce").get_attribute('value')
    while True:
        event_url = f'https://www.finderbet.it/wp-json/bet/v1/getItems?surebet_do_set_filter=NOPE&action-set-filtri_nonce={nonce_site}&_wp_http_referer=%2Fsurebet%2F&data_evento_da=&data_evento_a=&profitto_min=0&puntate=tutti&orderBy=profitto&order=desc&page=1'
        response = s.get(event_url)
        if response.status_code == 200:
            break
        else:
            print(response.status_code, response.text)
    result = response.json()
    bet_items = result['items']
    decrypt_item_res = base64.b64decode(bet_items)
    decrypt_item = decrypt_item_res.json()
    print(decrypt_item)


def get_surebet_data():
    print('get surebet page')
    driver.get(url)
    time.sleep(1)
    print('get data')
    s = requests.Session()
    request_cookies_browser = driver.get_cookies()
    c = [s.cookies.set(c['name'], c['value']) for c in request_cookies_browser]
    scroll_cnt = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        scroll_end_status =driver.find_elements_by_xpath('//div[@class="scroll-status"]')[0].value_of_css_property('display')
        if scroll_end_status == 'block':
            break
        else:
            if scroll_cnt > 5:
                break
            else:
                scroll_cnt = scroll_cnt +1
                print(scroll_cnt)
                continue

    result = driver.find_elements_by_xpath('//div[@class="rigaSurebet"]')
    surebet_lists = []
    for i in range(len(result)):
        time.sleep(1)
        print('Select number: ', i)
        try:
            current_ele = result[i]
            
            surebet_id = current_ele.get_attribute("data-surebet_id")
            cha_id = current_ele.get_attribute("data-cha_id")
            formula_id = current_ele.get_attribute("data-formula_id")
            createtime = current_ele.get_attribute("data-timestamp")
            #createtime = datetime.fromtimestamp(createtime)

            percent = current_ele.find_element_by_xpath('div[@class="contenitoreValoreSure padding-top-riga-surebet"]/div[1]').text
            sport = current_ele.find_element_by_xpath('div[@class="contenitoreSport padding-top-riga-surebet"]/div').text
            event_name = current_ele.find_element_by_xpath('div[@class="contenitoreInfoEv padding-top-riga-surebet"]/div[1]').text
            group_name = current_ele.find_element_by_xpath('div[@class="contenitoreInfoEv padding-top-riga-surebet"]/div[2]').text

            clickalternative = current_ele.find_element_by_css_selector('.icon_sure.iconAlternativa')
            driver.execute_script("arguments[0].click();",clickalternative)
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@class="contenitoreAlternative"]')))  
            alternative_lists = driver.find_element_by_xpath('//div[@class="contenitoreAlternative"]')
            alternative_part = alternative_lists.find_elements_by_xpath('div[@class="rigaSurebet"]')
            alt_surebet_lists = []
            for i in range(len(alternative_part)):
                time.sleep(0.5)
                try:
                    right_ele = alternative_part[i]
                    
                    surebet_id = right_ele.get_attribute("data-surebet_id")
                    cha_id = right_ele.get_attribute("data-cha_id")
                    formula_id = right_ele.get_attribute("data-formula_id")
                    createtime = right_ele.get_attribute("data-timestamp")
                    #createtime = datetime.fromtimestamp(createtime)

                    percent = right_ele.find_element_by_xpath('div[@class="contenitoreValoreSure padding-top-riga-surebet"]/div[1]').text
                    sport = right_ele.find_element_by_xpath('div[@class="contenitoreSport padding-top-riga-surebet"]/div').text
                    event_name = right_ele.find_element_by_xpath('div[@class="contenitoreInfoEv padding-top-riga-surebet"]/div[1]').text
                    group_name = right_ele.find_element_by_xpath('div[@class="contenitoreInfoEv padding-top-riga-surebet"]/div[2]').text

                    clicktarget = right_ele.find_element_by_css_selector('.icon_sure.iconCalcolatore')
                    driver.execute_script("arguments[0].click();",clicktarget)
                    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@class="rigaCalcolatore rigaCalcolatoreConBookmaker"]')))  
                    rightbet_details = driver.find_elements_by_xpath('//div[@class="rigaCalcolatore rigaCalcolatoreConBookmaker"]')
                    betdetail_cnt = len(rightbet_details)
                    if betdetail_cnt > 0:
                        bet1_event_name = rightbet_details[0].find_element_by_xpath('div[1]/div[1]').text
                        bet1_group_name = rightbet_details[0].find_element_by_xpath('div[1]/div[2]').text
                        bet_bk1 = rightbet_details[0].find_element_by_xpath('div[2]/div[2]').text
                        bet_market_val1 = rightbet_details[0].find_element_by_xpath('div[2]/div[3]').text
                        bet_koef1 = rightbet_details[0].find_element_by_xpath('div[3]/div[1]/input').get_attribute('value')

                        bet2_event_name = rightbet_details[1].find_element_by_xpath('div[1]/div[1]').text
                        bet2_group_name = rightbet_details[1].find_element_by_xpath('div[1]/div[2]').text
                        bet_bk2 = rightbet_details[1].find_element_by_xpath('div[2]/div[2]').text
                        bet_market_val2 = rightbet_details[1].find_element_by_xpath('div[2]/div[3]').text
                        bet_koef2 = rightbet_details[1].find_element_by_xpath('div[3]/div[1]/input').get_attribute('value')

                        bet_time = rightbet_details[0].find_element_by_xpath('div[@class="contSoloCellulare"]/div[1]').text
                        if betdetail_cnt == 2:
                            bet3_event_name = ' '
                            bet3_group_name = ' '
                            bet_bk3 = ' '
                            bet_market_val3 = ' '
                            bet_koef3 = ' '

                        elif betdetail_cnt == 3:
                            
                            bet3_event_name = rightbet_details[2].find_element_by_xpath('div[1]/div[1]').text
                            bet3_group_name = rightbet_details[2].find_element_by_xpath('div[1]/div[2]').text
                            bet_bk3 = rightbet_details[2].find_element_by_xpath('div[2]/div[2]').text
                            bet_market_val3 = rightbet_details[2].find_element_by_xpath('div[2]/div[3]').text
                            bet_koef3 = rightbet_details[2].find_element_by_xpath('div[3]/div[1]/input').get_attribute('value')

                    created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    child = 1
                    right_params = (surebet_id, cha_id, formula_id, createtime, percent, sport,event_name, group_name, bet_time, \
                    bet1_event_name, bet1_group_name, bet_bk1, bet_market_val1, bet_koef1, bet2_event_name, bet2_group_name, bet_bk2, \
                    bet_market_val2, bet_koef2, bet3_event_name, bet3_group_name, bet_bk3, bet_market_val3, bet_koef3, child, created_at, updated_at)
            
                    alt_surebet_lists.append(right_params)
                except Exception as e:
                    print('f', f' Exception: {repr(e)}')
                    pass 
            set_surebet_child(alt_surebet_lists)


                
            clicktarget = current_ele.find_element_by_css_selector('.icon_sure.iconCalcolatore')
            driver.execute_script("arguments[0].click();",clicktarget)
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@class="rigaCalcolatore rigaCalcolatoreConBookmaker"]')))  
            bet_details = driver.find_elements_by_xpath('//div[@class="rigaCalcolatore rigaCalcolatoreConBookmaker"]')
            betdetail_cnt = len(bet_details)
            if betdetail_cnt > 0:
                bet1_event_name = bet_details[0].find_element_by_xpath('div[1]/div[1]').text
                bet1_group_name = bet_details[0].find_element_by_xpath('div[1]/div[2]').text
                bet_bk1 = bet_details[0].find_element_by_xpath('div[2]/div[2]').text
                bet_market_val1 = bet_details[0].find_element_by_xpath('div[2]/div[3]').text
                bet_koef1 = bet_details[0].find_element_by_xpath('div[3]/div[1]/input').get_attribute('value')

                bet2_event_name = bet_details[1].find_element_by_xpath('div[1]/div[1]').text
                bet2_group_name = bet_details[1].find_element_by_xpath('div[1]/div[2]').text
                bet_bk2 = bet_details[1].find_element_by_xpath('div[2]/div[2]').text
                bet_market_val2 = bet_details[1].find_element_by_xpath('div[2]/div[3]').text
                bet_koef2 = bet_details[1].find_element_by_xpath('div[3]/div[1]/input').get_attribute('value')

                bet_time = bet_details[0].find_element_by_xpath('div[@class="contSoloCellulare"]/div[1]').text
                if betdetail_cnt == 2:
                    bet3_event_name = ' '
                    bet3_group_name = ' '
                    bet_bk3 = ' '
                    bet_market_val3 = ' '
                    bet_koef3 = ' '

                elif betdetail_cnt == 3:
                    
                    bet3_event_name = bet_details[2].find_element_by_xpath('div[1]/div[1]').text
                    bet3_group_name = bet_details[2].find_element_by_xpath('div[1]/div[2]').text
                    bet_bk3 = bet_details[2].find_element_by_xpath('div[2]/div[2]').text
                    bet_market_val3 = bet_details[2].find_element_by_xpath('div[2]/div[3]').text
                    bet_koef3 = bet_details[2].find_element_by_xpath('div[3]/div[1]/input').get_attribute('value')

            created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            parent = 1
            main_params = (surebet_id, cha_id, formula_id, createtime, percent, sport,event_name, group_name, bet_time, \
                bet1_event_name, bet1_group_name, bet_bk1, bet_market_val1, bet_koef1, bet2_event_name, bet2_group_name, bet_bk2, \
                bet_market_val2, bet_koef2, bet3_event_name, bet3_group_name, bet_bk3, bet_market_val3, bet_koef3,parent, created_at, updated_at)
            surebet_lists.append(main_params)

        except Exception as e:
            print('f', f' Exception: {repr(e)}')
            pass 
    set_surebet_main(surebet_lists)
    time.sleep(1)
    #driver.find_element_by_xpath('//*[@id="aggiorna_ora"]').click()

def get_valuebet_data():
    driver.get(url2)
    time.sleep(1)
    s = requests.Session()
    request_cookies_browser = driver.get_cookies()
    c = [s.cookies.set(c['name'], c['value']) for c in request_cookies_browser]
    scroll_cnt = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        scroll_end_status =driver.find_elements_by_xpath('//div[@class="scroll-status"]')[0].value_of_css_property('display')
        if scroll_end_status == 'block':
            break
        else:
            if scroll_cnt > 10:
                break
            else:
                scroll_cnt =  scroll_cnt + 1
                print(scroll_cnt)
                continue

    result = driver.find_elements_by_xpath('//div[@class="rigaSurebet"]')
    valuebet_lists = []
    for i in range(len(result)):
        time.sleep(0.5)
        print('Select number: ', i)
        try:
            current_ele = result[i]
            
            cha_id = current_ele.get_attribute("data-cha_id")

            percent = current_ele.find_element_by_xpath('div[@class="contenitoreValoreSure padding-top-riga-surebet"]/div[1]').text
            sport = current_ele.find_element_by_xpath('div[@class="contenitoreSport padding-top-riga-surebet"]/div').text
            event_name = current_ele.find_element_by_xpath('div[@class="contenitoreInfoEv padding-top-riga-surebet"]/div[1]').text
            group_name = current_ele.find_element_by_xpath('div[@class="contenitoreInfoEv padding-top-riga-surebet"]/div[2]').text
            bet_time = current_ele.find_element_by_xpath('div[@class="contenitoreDataSure padding-top-riga-surebet"]').text
            
            bet_bk = current_ele.find_element_by_xpath('div[@class="contenitoreDestraValue"]/div/div[1]').text
            bet_koef = current_ele.find_element_by_xpath('div[@class="contenitoreDestraValue"]/div/div[2]').text
            bet_market_val = current_ele.find_element_by_xpath('div[@class="contenitoreDestraValue"]/div/div[3]').text

            created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

            val_params = (cha_id,percent, sport,event_name, group_name, bet_time, bet_bk, bet_market_val , bet_koef, created_at, updated_at)
            valuebet_lists.append(val_params)

        except Exception as e:
            print('f', f' Exception: {repr(e)}')
            pass 
    set_valuebet_main(valuebet_lists)
    time.sleep(1)
    #driver.find_element_by_xpath('//*[@id="aggiorna_ora"]').click()


def get_exchange_data():
    driver.get(url3)
    time.sleep(1)
    s = requests.Session()
    request_cookies_browser = driver.get_cookies()
    c = [s.cookies.set(c['name'], c['value']) for c in request_cookies_browser]
    scroll_cnt = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        scroll_end_status =driver.find_elements_by_xpath('//div[@class="scroll-status"]')[0].value_of_css_property('display')
        if scroll_end_status == 'block':
            time.sleep(3)
            print('last')
            break
        else:
            scroll_cnt = scroll_cnt + 1
            if scroll_cnt > 5:
                break
            else:        
                print(scroll_cnt)        
                continue

    result = driver.find_elements_by_xpath('//div[@class="rigaSurebet"]')


    for i in range(len(result)):
        time.sleep(0.5)
        print('Select number: ', i)
        if i > 100:
            break
        else:
            try:
                exchange_lists = []
                current_ele = result[i]
                surebet_id = current_ele.get_attribute("data-cha_id")
                cha_id = current_ele.get_attribute("data-cha_id")
                hash_id_book = current_ele.get_attribute("data-hash_id_book")
                hash_id_exchange = current_ele.get_attribute("data-hash_id_exchange")
                tipo_exchange = current_ele.get_attribute("data-tipo_exchange")
                desc_tipo = current_ele.get_attribute("data-desc_tipo")
                sport_id = current_ele.get_attribute("data-sport_id")
                bookmakers_id_exchange = current_ele.get_attribute("data-bookmakers_id_exchange")
                #createtime = datetime.fromtimestamp(createtime)
                percent = current_ele.find_element_by_xpath('div[@class="contenitoreValoreSure padding-top-riga-surebet"]/div[1]').text
                sport = current_ele.find_element_by_xpath('div[@class="contenitoreSport padding-top-riga-surebet"]/div').text
                event_name = current_ele.find_element_by_xpath('div[@class="contenitoreInfoEv padding-top-riga-surebet"]/div[1]').text
                group_name = current_ele.find_element_by_xpath('div[@class="contenitoreInfoEv padding-top-riga-surebet"]/div[2]').text

                clicktarget = current_ele.find_element_by_css_selector('.icon_sure.iconCalcolatore')
                driver.execute_script("arguments[0].click();",clicktarget)
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@class="contenitoreCalcolatore"]')))  
                bet_details = driver.find_elements_by_xpath('//div[@class="contenitoreCalcolatore"]')
                betdetail_cnt = len(bet_details)
                if betdetail_cnt > 0:
                    bet1_event_name = bet_details[0].find_element_by_xpath('div[2]/div[1]/div[1]').text
                    bet1_group_name = bet_details[0].find_element_by_xpath('div[2]/div[1]/div[2]').text
                    bet_bk1 = bet_details[0].find_element_by_xpath('div[2]/div[2]/div[2]').text
                    bet_market_val1 = bet_details[0].find_element_by_xpath('div[2]/div[2]/div[3]').text
                    bet_koef1 = bet_details[0].find_element_by_xpath('div[2]/div[3]/div[1]/input').get_attribute('value')

                    bet2_event_name = bet_details[0].find_element_by_xpath('div[3]/div[1]/div[1]').text
                    bet2_group_name = bet_details[0].find_element_by_xpath('div[3]/div[1]/div[2]').text
                    bet_bk2 = bet_details[0].find_element_by_xpath('div[3]/div[2]/div[2]').text
                    bet_market_val2 = bet_details[0].find_element_by_xpath('div[3]/div[2]/div[3]').text
                    bet_koef2 = bet_details[0].find_element_by_xpath('div[3]/div[3]/div[1]/input').get_attribute('value')

                    bet_time = bet_details[0].find_element_by_xpath('div[2]/div[2]/div[1]').text

                    exchange_title = bet_details[0].find_element_by_xpath('div[4]/div[1]').text
                    exchange_fund = bet_details[0].find_element_by_xpath('div[4]/div[2]/div[2]/span').text
                    exchange_commision = bet_details[0].find_element_by_xpath('div[5]/div[1]/div[2]/div[1]/input').get_attribute('value')

                created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

                main_params = (surebet_id, cha_id, hash_id_book, hash_id_exchange,tipo_exchange, desc_tipo, sport_id,bookmakers_id_exchange, \
                    percent, sport,event_name, group_name, bet_time,bet1_event_name, bet1_group_name, bet_bk1, bet_market_val1, bet_koef1, \
                    bet2_event_name, bet2_group_name, bet_bk2, bet_market_val2, bet_koef2, exchange_title, exchange_fund, exchange_commision, created_at, updated_at)
                exchange_lists.append(main_params)
                print(exchange_lists)
                set_exchange_main(exchange_lists)
            except Exception as e:
                print('f', f' Exception: {repr(e)}')
                pass 




def main():
    init()
    while True:
        get_surebet_data()
        time.sleep(1.5)
        #get_valuebet_data()
        time.sleep(1.5)
        #get_exchange_data()
        time.sleep(1.5)

    

if __name__ == "__main__":
    main()
