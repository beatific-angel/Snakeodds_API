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

def init():
    login()


def surebet_get_data(s, request_cookies_browser, userid, bookie_id_lists, bstart):
    # go to filter page and save filters
    driver.get(saveurl)
    WebDriverWait(driver, 120).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="mepr-account-payments"]')))
    filtertype = 'prematch'
    mepr_nonce = driver.find_element_by_xpath('//input[@id="mepr_profile-filtri_nonce"]').get_attribute('value')
    filtersavedata = {
        'mepr-process-profile-filtri': 'Y',
        'mepr_profile-filtri_nonce': mepr_nonce,
        '_wp_http_referer': '/account/?action=profile-filtri',
        'importo_default':'100',
        'arrotontamento_dafault': '1',
        'bookmakers[]': [bookie_id_lists],
        'sports[]': [2,1,4,5,23]
    }
    driver.delete_cookie('__cf_bm')
    driver.delete_cookie('wfwaf-authcookie-71f47a747fbb7b6570a859ec7a006d6d')
    driver.delete_cookie('wordpress_sec_165b92c533db78e0b8c7972d9effad21')
    while True:
        event_url = f'https://www.finderbet.it/account/?action=profile-filtri'
        
        response = s.post(event_url, data=filtersavedata)
        if response.status_code == 200:          
            break
        else:
            print(response.status_code, response.text)

    time.sleep(2)
    driver.get('https://www.finderbet.it/')
    time.sleep(1)
    request_cookies_browser = driver.get_cookies()
    # go to surebet page
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="action-set-filtri_nonce"]')))
    nonce_site = driver.find_element_by_id("action-set-filtri_nonce").get_attribute('value')

    wp_nonce_string = driver.find_element_by_xpath('//script[@id="wp-api-request-js-extra"]').get_attribute('innerHTML')
    wp_nonce_temp = wp_nonce_string.split('"')
    wp_nonce = wp_nonce_temp[7]
    cookie_cnt = len(request_cookies_browser)
    header_cookie = ''
    for i in range(cookie_cnt):
        header_cookie += request_cookies_browser[i]['name'] + '=' + request_cookies_browser[i]['value'] + '; '

    get_surebetdata_api(s, nonce_site, wp_nonce, bookie_id_lists, header_cookie, userid, filtertype)


def get_surebetdata_api(s, nonce_site, wp_nonce, bookie_id_lists, header_cookie, userid, filtertype):
    print('surebet loop started')
    surebet_lists = []
    alt_surebet_lists = []
    headers = {
        "x-wp-nonce": wp_nonce,
        "cookie": header_cookie
    }
    while True:
        s = requests.Session()
        cnt_bk_lists = len(bookie_id_lists)
        bk_url_header = ''
        for m in range(cnt_bk_lists):
            bk_url_header += f'&bookmakers[]={bookie_id_lists[m]}'

        event_url = f'https://www.finderbet.it/wp-json/bet/v1/getItems?surebet_do_set_filter=YEPPA&action-set-filtri_nonce={nonce_site}&_wp_http_referer=/surebet/{bk_url_header}&data_evento_da=&data_evento_a=&profitto_min=0&puntate=tutti&orderBy=profitto&order=desc&page=1'

        response = s.get(event_url, headers=headers)
        if response.status_code == 200:
            break
        else:
            print(response.status_code, response.text)
    result = response.json()
    bet_items = result['items']
    decrypt_item_res = base64.b64decode(bet_items)
    items = decrypt_item_res.decode()
    surebet_result = json.loads(items)

    if len(surebet_result) > 0:
       
        for i in range(len(surebet_result)):
            bookie_lists_tp = get_bk_lists(userid, filtertype)
            if bookie_lists_tp != True:
                unique_list_tp = []
                bookie_id_lists_tp = []
                for bookie_lists_tp_cel in bookie_lists_tp:
                    processing_bklists_tp = bookie_lists_tp_cel[4]
                    processing_bklists_tp = unserialize_array(
                        processing_bklists_tp)
                    for k, v in processing_bklists_tp.items():
                        v = int(v)
                        unique_list_tp.append(v)
                for x in unique_list_tp:
                    if x not in bookie_id_lists_tp:
                        bookie_id_lists_tp.append(x)
                bookie_id_lists_tp.sort()
                if np.array_equiv(bookie_id_lists_tp, bookie_id_lists) == True:
                    selected_ele = surebet_result[i]
                    surebet_id = selected_ele['bet_id']
                    cha_id = selected_ele['cha_id']
                    percent = selected_ele['valore_surebet']

                    group_name = selected_ele['gruppo_evento']
                    event_name = selected_ele['nome_evento']
                    bet_time = selected_ele['datetime']
                    sport = selected_ele['sport']
                    formula_id = selected_ele['formula_id']
                    timestamp = selected_ele['timestamp']
                    created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

                    bet_cnt = len(selected_ele['bookmakers'])
                    bookmakers = selected_ele['bookmakers']
                    bet_koef1 = bookmakers[0]['value']
                    bet_bk1 = bookmakers[0]['bname']
                    bet_market_val1 = bookmakers[0]['sigla']
                    bet_desc1 = bookmakers[0]['desc']
                    bet_koef2 = bookmakers[1]['value']
                    bet_bk2 = bookmakers[1]['bname']
                    bet_market_val2 = bookmakers[1]['sigla']
                    bet_desc2 = bookmakers[1]['desc']
                    if bet_cnt == 2:
                        bet_koef3 = ' '
                        bet_bk3 = ' '
                        bet_market_val3 = ' '
                        bet_desc3 = ''
                    elif bet_cnt == 3:
                        bet_koef3 = bookmakers[2]['value']
                        bet_bk3 = bookmakers[2]['bname']
                        bet_market_val3 = bookmakers[2]['sigla']
                        bet_desc3 = bookmakers[2]['desc']

                    while True:
                        event_url = f'https://www.finderbet.it/wp-json/bet/v1/getItem/{surebet_id}'
                        response = s.post(event_url, headers=headers)
                        if response.status_code == 200:
                            break
                        else:
                            print(response.status_code, response.text)
                    post_result = response.json()
                    post_data = post_result['data']
                    post_data_decrypt = base64.b64decode(post_data)
                    postitems = post_data_decrypt.decode()
                    each_bets_res = json.loads(postitems)
                    cnt_bets = len(each_bets_res)

                    bet1_event_name = each_bets_res[0]['gruppo_evento']
                    bet1_group_name = each_bets_res[0]['nome_evento']
                    bet2_event_name = each_bets_res[1]['gruppo_evento']
                    bet2_group_name = each_bets_res[1]['nome_evento']

                    if cnt_bets == 2:
                        bet3_event_name = ' '
                        bet3_group_name = ' '
                    elif cnt_bets == 3:
                        bet3_event_name = each_bets_res[2]['gruppo_evento']
                        bet3_group_name = each_bets_res[2]['nome_evento']

                    main_params = (surebet_id, cha_id, percent, sport, event_name, group_name, bet_time, \
                                   bet1_event_name, bet1_group_name, bet_bk1, bet_desc1, bet_market_val1, bet_koef1,
                                   bet2_event_name,
                                   bet2_group_name, bet_bk2, bet_desc2, \
                                   bet_market_val2, bet_koef2, bet3_event_name, bet3_group_name, bet_bk3, bet_desc3,
                                   bet_market_val3,
                                   bet_koef3, created_at, updated_at)
                    surebet_lists.append(main_params)
                else:
                    return
            else:
                return
        set_surebet_main(surebet_lists)

        for i in range(len(surebet_result)):
            selected_ele = surebet_result[i]
            surebet_id = selected_ele['bet_id']
            cha_id = selected_ele['cha_id']
            formula_id = selected_ele['formula_id']
            timestamp = selected_ele['timestamp']
            postdata = {
                'surebet_do_set_filter': 'NOPE',
                'action-set-filtri_nonce': nonce_site,
                '_wp_http_referer': '/surebet/',
                'data_evento_da': '',
                'data_evento_a': '',
                'profitto_min': 0,
                'puntate': 'tutti',
                'surebet_id': surebet_id,
                'cha_id': cha_id,
                'formula_id': formula_id,
                'timestamp': timestamp
            }
            s.headers = headers

            while True:
                event_url = f'https://www.finderbet.it/wp-json/bet/v1/getClosestItemsCount'
                response = s.post(event_url, json=postdata)
                if response.status_code == 200:
                    break
                else:
                    print(response.status_code, response.text)
            child_result = response.json()
            child_data = child_result['data']
            child_data_decrypt = base64.b64decode(child_data)
            childitems = child_data_decrypt.decode()
            childlists = json.loads(childitems)
            cnt_childlists = len(childlists)
            if cnt_childlists > 0:
                parent_id = surebet_id
                for i in range(cnt_childlists):
                    if i < 3:
                        child_item = childlists[i]
                        csurebet_id = child_item['bet_id']
                        cpercent = child_item['valore_surebet']
                        cgroup_name = child_item['gruppo_evento']
                        cevent_name = child_item['nome_evento']
                        csport = child_item['sport']
                        ccha_id = child_item['cha_id']
                        cbet_time = child_item['datetime']
                        child_bookmakers = child_item['bookmakers']
                        child_bk_cnt = len(child_bookmakers)
                        cbet_bk1 = child_bookmakers[0]['bname']
                        cbet_koef1 = child_bookmakers[0]['value']
                        cbet_market_val1 = child_bookmakers[0]['sigla']
                        cbet_desc1 = child_bookmakers[0]['desc']
                        cbet_bk2 = child_bookmakers[1]['bname']
                        cbet_koef2 = child_bookmakers[1]['value']
                        cbet_market_val2 = child_bookmakers[1]['sigla']
                        cbet_desc2 = child_bookmakers[1]['desc']

                        if child_bk_cnt == 2:
                            cbet_koef3 = ' '
                            cbet_bk3 = ' '
                            cbet_market_val3 = ' '
                            cbet_desc3 = ' '
                        else:
                            cbet_koef3 = child_bookmakers[2]['value']
                            cbet_bk3 = child_bookmakers[2]['bname']
                            cbet_market_val3 = child_bookmakers[2]['sigla']
                            cbet_desc3 = child_bookmakers[2]['desc']

                        created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                        updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

                        right_params = (
                            csurebet_id, ccha_id, cpercent, csport, cevent_name, cgroup_name, cbet_time, \
                            cevent_name, cgroup_name, cbet_bk1, cbet_desc1, cbet_market_val1, cbet_koef1,
                            cevent_name,
                            cgroup_name, cbet_bk2, cbet_desc2, \
                            cbet_market_val2, cbet_koef2, cevent_name, cgroup_name, cbet_bk3, cbet_desc3,
                            cbet_market_val3,
                            cbet_koef3, parent_id, created_at, updated_at)
                        alt_surebet_lists.append(right_params)
        set_surebet_child(alt_surebet_lists)

    else:
        return
    print('surebet loop finished.will start valuebet loop soon.')


def valuebet_get_data(s, request_cookies_browser, userid, vbookie_id_lists, bstart):
    #go to filter page and save filters
    driver.get(saveurl)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="mepr-account-payments"]')))

    mepr_nonce = driver.find_element_by_xpath('//input[@id="mepr_profile-filtri_nonce"]').get_attribute('value')
    filtersavedata = {
        'mepr-process-profile-filtri': 'Y',
        'mepr_profile-filtri_nonce': mepr_nonce,
        '_wp_http_referer': '/account/?action=profile-filtri',
        'importo_default':'100',
        'arrotontamento_dafault': '1',
        'bookmakers[]': [vbookie_id_lists],
        'sports[]': [2,1,4,5,23]
    }
    driver.delete_cookie('__cf_bm')
    driver.delete_cookie('wfwaf-authcookie-71f47a747fbb7b6570a859ec7a006d6d')
    driver.delete_cookie('wordpress_sec_165b92c533db78e0b8c7972d9effad21')

    while True:
        event_url = f'https://www.finderbet.it/account/?action=profile-filtri'
        
        response = s.post(event_url, data=filtersavedata)
        if response.status_code == 200:          
            break
        else:
            print(response.status_code, response.text)

    # go to surebet page
    time.sleep(2)
    driver.get('https://www.finderbet.it/')
    time.sleep(1)
    request_cookies_browser = driver.get_cookies() 
    # go to valuebet page
    driver.get(url2)
    WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="contenitoreSurebet"]')))
    nonce_site = driver.find_element_by_id("action-set-filtri_nonce").get_attribute('value')

    wp_nonce_string = driver.find_element_by_xpath('//script[@id="wp-api-request-js-extra"]').get_attribute('innerHTML')
    wp_nonce_temp = wp_nonce_string.split('"')
    wp_nonce = wp_nonce_temp[7]
    cookie_cnt = len(request_cookies_browser)
    header_cookie = ''
    for i in range(cookie_cnt):
        header_cookie += request_cookies_browser[i]['name'] + '=' + request_cookies_browser[i]['value'] + '; '

    get_valuebetdata_api(s, nonce_site, wp_nonce, vbookie_id_lists, header_cookie)

def get_valuebetdata_api(s, nonce_site, wp_nonce, bookie_id_lists, header_cookie):
    while True:
        s = requests.Session()
        headers = {
            "x-wp-nonce": wp_nonce,
            "cookie": header_cookie
        }
        cnt_bk_lists = len(bookie_id_lists)
        bk_url_header = ''
        for m in range(cnt_bk_lists):
            bk_url_header += f'&bookmakers[]={bookie_id_lists[m]}'

        event_url = f'https://www.finderbet.it/wp-json/valuebet/v1/getItems?surebet_do_set_filter=YEPPA&action-set-filtri_nonce=c0e2668683&_wp_http_referer=/valuebet/{bk_url_header}&data_evento_da=&data_evento_a=&profitto_min=&orderBy=profitto&order=desc&page=1'

        response = s.get(event_url, headers=headers)
        if response.status_code == 200:
            break
        else:
            print(response.status_code, response.text)
    result  = response.json()
    bet_items = result['items']
    decrypt_item_res = base64.b64decode(bet_items)
    items = decrypt_item_res.decode()
    valuebet_result = json.loads(items)
    print('valuebet loop started')
    valuebet_lists = []
    if len(valuebet_result) > 0:
        for i in range(len(valuebet_result)):
            try:
                time.sleep(0.2)
                selected_item = valuebet_result[i]
                valuebet_id = selected_item['valuebet_id']
                percent = selected_item['valore_surebet']
                sport = selected_item['sport']
                bet_time = selected_item['datetime']
                cha_id = selected_item['cha_id']
                group_name = selected_item['gruppo_evento']
                event_name = selected_item['nome_evento']
                selected_bookmaker = selected_item['bookmakers']
                bet_koef = selected_bookmaker[0]['value']
                bet_bk = selected_bookmaker[0]['bname']
                bet_market_val = selected_bookmaker[0]['sigla']
                bet_desc = selected_bookmaker[0]['desc']

                created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

                val_params = (valuebet_id, cha_id, percent, sport, event_name, \
                              group_name, bet_time, bet_bk, bet_market_val, bet_koef,bet_desc,
                              created_at, updated_at)
                #valuebet_lists.append(val_params)
                set_valuebet_main(val_params)
            except Exception as e:
                print('f', f' Exception: {repr(e)}')
                pass

        print('valuebet loop finished')
    else:
        return
