from operator import index
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
saveurl = 'https://www.finderbet.it/account/?action=profile-filtri'

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
    else:
        return True


def set_surebet_main(surebet_lists):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = 'INSERT INTO finder_surebets (surebet_id, cha_id, percent, sport,event_name, group_name, bet_time, bk_ids, bet1_event_name, \
        bet1_group_name, bet_bk1, bet_desc1, bet_market_val1, bet_koef1,bet2_event_name, bet2_group_name, bet_bk2, bet_desc2, bet_market_val2, bet_koef2,bet3_event_name, \
            bet3_group_name, bet_bk3, bet_desc3, bet_market_val3, bet_koef3, created_at, updated_at) ' \
          'VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s, %s,%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s,%s, %s, %s) ON DUPLICATE KEY UPDATE \
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
    sql = 'INSERT INTO finder_surebets_child (surebet_id, cha_id, percent, sport,event_name, group_name, bet_time, bk_ids, bet1_event_name, \
        bet1_group_name, bet_bk1, bet_desc1, bet_market_val1, bet_koef1,bet2_event_name, bet2_group_name, bet_bk2, bet_desc2, bet_market_val2, bet_koef2,bet3_event_name, \
            bet3_group_name, bet_bk3, bet_desc3, bet_market_val3, bet_koef3, parent_id, created_at, updated_at) ' \
          'VALUES (%s, %s,%s, %s,%s, %s,%s, %s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s) ON DUPLICATE KEY UPDATE cha_id=VALUES(cha_id), \
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


def set_valuebet_main(valuebet_lists):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = 'INSERT INTO valuebets (valuebet_id,cha_id, percent, sport,event_name, group_name, bet_time, bet_bk, bet_market_val, bet_koef, created_at, updated_at) ' \
          'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE percent=VALUES(percent), \
                sport=VALUES(sport),event_name=VALUES(event_name),group_name=VALUES(group_name), \
                bet_time=VALUES(bet_time),bet_bk=VALUES(bet_bk),bet_market_val=VALUES(bet_market_val), \
                bet_koef=VALUES(bet_koef),updated_at=VALUES(updated_at) ;'
    with mycursor as cursor:
        try:
            cursor.executemany(sql, valuebet_lists)
            mydb.commit()
        except Exception as e:
            print('f', f'set_valuebet Exception: {repr(e)}')
    cursor.close()


def init():
    login()


def surebet_get_data(s, request_cookies_browser, userid, bookie_id_lists, bstart):
    # # go to filter page and save filters
    # driver.get(saveurl)
    # WebDriverWait(driver, 120).until(
    #     EC.presence_of_all_elements_located((By.XPATH, '//*[@id="mepr-account-payments"]')))
    filtertype = 'prematch'
    # mepr_nonce = driver.find_element_by_xpath('//input[@id="mepr_profile-filtri_nonce"]').get_attribute('value')
    # bk_lists = driver.find_elements_by_class_name('input-checkbox-bookmaker')
    # bookie_lists_tp = get_bk_lists(userid, filtertype)
    # for j in range(len(bk_lists)):
    #     if bookie_lists_tp != True:
    #         bookie_temp = ''
    #         unique_list_tp = []
    #         bookie_id_lists_tp = []
    #         for bookie_lists_tp_cel in bookie_lists_tp:
    #             processing_bklists_tp = bookie_lists_tp_cel[4]
    #             processing_bklists_tp = unserialize_array(
    #                 processing_bklists_tp)
    #             for k, v in processing_bklists_tp.items():
    #                 v = int(v)
    #                 unique_list_tp.append(v)
    #         for x in unique_list_tp:
    #             if x not in bookie_id_lists_tp:
    #                 bookie_id_lists_tp.append(x)
    #         bookie_id_lists_tp.sort()
    #         if np.array_equiv(bookie_id_lists_tp, bookie_id_lists) == True:
    #             get_check_status = bk_lists[j].get_attribute('checked')
    #             print(get_check_status)
    #             try:
    #                 if get_check_status == 'true':
    #                     bk_lists[j].click()
    #             except Exception as e:
    #                 continue
    #         else:
    #             return
    #     else:
    #         return
    #
    # cnt_bk_lists = len(bookie_id_lists)
    # for m in range(cnt_bk_lists):
    #
    #     if bookie_lists_tp != True:
    #         bookie_temp = ''
    #         unique_list_tp = []
    #         bookie_id_lists_tp = []
    #         for bookie_lists_tp_cel in bookie_lists_tp:
    #             processing_bklists_tp = bookie_lists_tp_cel[4]
    #             processing_bklists_tp = unserialize_array(
    #                 processing_bklists_tp)
    #             for k, v in processing_bklists_tp.items():
    #                 v = int(v)
    #                 unique_list_tp.append(v)
    #         for x in unique_list_tp:
    #             if x not in bookie_id_lists_tp:
    #                 bookie_id_lists_tp.append(x)
    #         bookie_id_lists_tp.sort()
    #         if np.array_equiv(bookie_id_lists_tp, bookie_id_lists) == True:
    #             bk_val = bookie_id_lists[m]
    #             driver.find_element_by_id('gridCheckBook' + str(bk_val)).click()
    #         else:
    #             return
    #     else:
    #         return
    #
    # driver.find_element_by_xpath('//button[@type="submit" and contains(@class, "btn-primary")]').click()
    # time.sleep(1)

    # go to surebet page
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="contenitoreSurebet"]')))
    nonce_site = driver.find_element_by_id("action-set-filtri_nonce").get_attribute('value')

    wp_nonce_string = driver.find_element_by_xpath('//script[@id="wp-api-request-js-extra"]').get_attribute('innerHTML')
    wp_nonce_temp = wp_nonce_string.split('"')
    wp_nonce = wp_nonce_temp[7]
    cookie_cnt = len(request_cookies_browser)
    header_cookie = ''
    for i in range(cookie_cnt):
        header_cookie += request_cookies_browser[i]['name'] + '=' + request_cookies_browser[i]['value'] + '; '

    bookie_lists_tp = get_bk_lists(userid, filtertype)
    if bookie_lists_tp != True:
        bookie_temp = ''
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
        print('filter lists:',bookie_id_lists_tp)
        if np.array_equiv(bookie_id_lists_tp, bookie_id_lists) == True:
            get_surebetdata_api(s, nonce_site, wp_nonce, bookie_id_lists, header_cookie, userid, filtertype)
        else:
            print('finished')
            return
    else:
        return


def get_surebetdata_api(s, nonce_site, wp_nonce, bookie_id_lists, header_cookie, userid, filtertype):
    surebet_lists = []
    for pagenum in range(1, 3):
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

            event_url = f'https://www.finderbet.it/wp-json/bet/v1/getItems?surebet_do_set_filter=YEPPA&action-set-filtri_nonce={nonce_site}&_wp_http_referer=/surebet/{bk_url_header}&data_evento_da=&data_evento_a=&profitto_min=0&puntate=tutti&orderBy=profitto&order=desc&page={pagenum}'

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
                    bookie_temp = ''
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
                        # post_headers={
                        #            "x-wp-nonce": wp_nonce
                        # }
                        s.headers = {"x-wp-nonce": wp_nonce,
                                     "cookie": header_cookie}

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
                            alt_surebet_lists = []
                            parent_id = surebet_id
                            for i in range(cnt_childlists):
                                if i < 5:
                                    child_item = childlists[i]
                                    csurebet_id = child_item['bet_id']
                                    cpercent = child_item['valore_surebet']
                                    cgroup_name = child_item['gruppo_evento']
                                    cevent_name = child_item['nome_evento']
                                    csport = child_item['sport']
                                    ccha_id = child_item['cha_id']
                                    cbk_ids = child_item['book_ids_for_filter']
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
                                        cbet_desc3 = ''
                                    elif child_bk_cnt == 3:
                                        cbet_koef3 = child_bookmakers[2]['value']
                                        cbet_bk3 = child_bookmakers[2]['bname']
                                        cbet_market_val3 = child_bookmakers[2]['sigla']
                                        cbet_desc3 = child_bookmakers[2]['desc']
                                    child_post_headers = {
                                        "x-wp-nonce": wp_nonce,
                                        "cookie": header_cookie
                                    }
                                    while True:
                                        event_url = f'https://www.finderbet.it/wp-json/bet/v1/getItem/{csurebet_id}'
                                        response = s.post(event_url, headers=child_post_headers)
                                        if response.status_code == 200:
                                            break
                                        else:
                                            print(response.status_code, response.text)
                                    cpost_result = response.json()
                                    cpost_data = cpost_result['data']
                                    cpost_data_decrypt = base64.b64decode(cpost_data)
                                    cpostitems = cpost_data_decrypt.decode()
                                    ceach_bets_res = json.loads(cpostitems)
                                    cnt_bets = len(ceach_bets_res)

                                    cbet1_event_name = ceach_bets_res[0]['gruppo_evento']
                                    cbet1_group_name = ceach_bets_res[0]['nome_evento']
                                    cbet2_event_name = ceach_bets_res[1]['gruppo_evento']
                                    cbet2_group_name = ceach_bets_res[1]['nome_evento']

                                    if cnt_bets == 2:
                                        cbet3_event_name = ' '
                                        cbet3_group_name = ' '
                                    elif cnt_bets == 3:
                                        cbet3_event_name = ceach_bets_res[2]['gruppo_evento']
                                        cbet3_group_name = ceach_bets_res[2]['nome_evento']

                                    ccreated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                                    cupdated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

                                    right_params = (
                                        csurebet_id, ccha_id, cpercent, csport, cevent_name, cgroup_name, cbet_time,
                                        cbk_ids, \
                                        cbet1_event_name, cbet1_group_name, cbet_bk1, cbet_desc1, cbet_market_val1,
                                        cbet_koef1, cbet2_event_name,
                                        cbet2_group_name, cbet_bk2, cbet_desc2, \
                                        cbet_market_val2, cbet_koef2, cbet3_event_name, cbet3_group_name, cbet_bk3,
                                        cbet_desc3, cbet_market_val3,
                                        cbet_koef3, parent_id, ccreated_at, cupdated_at)
                                    alt_surebet_lists.append(right_params)
                                elif i > 20:
                                    break
                            set_surebet_child(alt_surebet_lists)

                        bk_ids = selected_ele['book_ids_for_filter']
                        detail_items = json.loads(selected_ele['items'])
                        bet_cnt = len(detail_items)
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

                        post_headers = {
                            "x-wp-nonce": wp_nonce,
                            "cookie": header_cookie
                        }
                        while True:
                            event_url = f'https://www.finderbet.it/wp-json/bet/v1/getItem/{surebet_id}'
                            response = s.post(event_url, headers=post_headers)
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

                        created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                        updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

                        main_params = (surebet_id, cha_id, percent, sport, event_name, group_name, bet_time, bk_ids, \
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

        else:
            break
    set_surebet_main(surebet_lists)

def multi_user_work(request_cookies_browser, userid, bookie_id_lists, vbookie_id_lists, checked_bet, bstart):
    s = requests.Session()
    c = [s.cookies.set(c['name'], c['value']) for c in request_cookies_browser]

    surebet_get_data(s, request_cookies_browser, userid, bookie_id_lists, bstart)
    #valuebet_get_data(s, request_cookies_browser, userid, vbookie_id_lists, bookie_id_lists, bstart)
    if userid not in changed_ids:
        getonlineuser_ids.remove(userid)
    else:
        changed_ids.remove(userid)


getonlineuser_ids = []
working_ids = []
changed_ids = []


def main():
    init()
    while True:
        workers = []
        checked_bet = ''
        user_bookie_id_lists = {}
        filtertype = 'prematch'
        current_online = get_online_users()

        for user in current_online:
            userid = user[0]
            unique_list = []
            bookie_id_lists = []
            bookie_lists = get_bk_lists(userid, filtertype)
            if bookie_lists == True:
                continue
            for bookie_list_lists in bookie_lists:
                processing_bklists = bookie_list_lists[4]
                processing_bklists = unserialize_array(processing_bklists)
                for k, v in processing_bklists.items():
                    v = int(v)
                    unique_list.append(v)
            for x in unique_list:
                if x not in bookie_id_lists:
                    bookie_id_lists.append(x)
            bookie_id_lists.sort()
            user_bookie_id_lists[userid] = bookie_id_lists

        request_cookies_browser = driver.get_cookies()

        current_online = get_online_users()
        for user in current_online:
            userid = user[0]
            if userid not in getonlineuser_ids and userid in user_bookie_id_lists:
                start = True
                if userid in working_ids:
                    start = False
                else:
                    working_ids.append(userid)
                getonlineuser_ids.append(userid)
                worker = threading.Thread(target=multi_user_work, daemon=True,
                                          args=(
                                              request_cookies_browser, userid, user_bookie_id_lists[userid], checked_bet,
                                              start))
                workers.append(worker)
                worker.start()
                print('thread created')
                checked_bet = ''

            bookie_lists_tp = get_bk_lists(userid, filtertype)
            if bookie_lists_tp != True:
                bookie_temp = ''
                unique_list_tp = []
                bookie_id_lists_tp = []
                for bookie_lists_tp_cel in bookie_lists_tp:
                    processing_bklists_tp = bookie_lists_tp_cel[4]
                    processing_bklists_tp = unserialize_array(processing_bklists_tp)
                    for k, v in processing_bklists_tp.items():
                        v = int(v)
                        unique_list_tp.append(v)
                for x in unique_list_tp:
                    if x not in bookie_id_lists_tp:
                        bookie_id_lists_tp.append(x)
                bookie_id_lists_tp.sort()
                if userid not in user_bookie_id_lists:
                    break
                if np.array_equiv(bookie_id_lists_tp, user_bookie_id_lists[userid]) == False:
                    print('changed_filter', bookie_id_lists_tp)
                    user_bookie_id_lists[userid] = bookie_id_lists_tp
                    getonlineuser_ids.remove(userid)
                    working_ids.remove(userid)
                    changed_ids.append(userid)
                    checked_bet = 'surebet'


if __name__ == "__main__":
    main()
