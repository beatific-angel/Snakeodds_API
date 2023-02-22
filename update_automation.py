from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from twocaptcha import TwoCaptcha
from threading import Thread

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


# import codecs
def getConnection():
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="betting"
    )
    return mydb


def unserialize_array(serialized_array):
    return dict(enumerate(re.findall(r'"((?:[^"\\]|\\.)*)"', serialized_array)))


def get_online_users():
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = "SELECT * FROM users where login_status ='1'"
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


def get_bkdata(param_item):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = "SELECT id FROM bookmakers_arbs WHERE bk_id = '{}'".format(param_item)
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


def get_valuebet_prematch(event_ID, parent):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = "SELECT * FROM valuebet_prematch WHERE event_id = '{}' and parent = '{}'".format(event_ID, parent)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    if len(myresult) > 0:
        return False
    else:
        return True


def get_valuebet_prematch_child(arbid, event_ID, child):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = "SELECT * FROM valuebet_prematch WHERE arbid = '{}' and event_id = '{}' and child = '{}'".format(arbid,
                                                                                                           event_ID,
                                                                                                           child)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    if len(myresult) > 0:
        return False
    else:
        return True


def get_valuebet_parent(bet1_id, parent):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = "SELECT * FROM valuebet_prematch WHERE bet1_id = '{}' and parent = '{}'".format(bet1_id, parent)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    if len(myresult) > 0:
        return True
    else:
        return False


def get_valuebet_child(bet1_id, child):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = "SELECT * FROM valuebet_prematch WHERE bet1_id = '{}' and child = '{}'".format(bet1_id, child)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    if len(myresult) > 0:
        return True
    else:
        return False


def get_valuebet_lists(event_ID, bookmaker_id, event_name):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = "select * from valuebet_lists where event_id = '{}' and bookmaker_id = '{}' and event_name = '{}'".format(
        event_ID, bookmaker_id, event_name)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    if len(myresult) > 0:
        return False
    else:
        return True


def get_valuebet_childs(bookmaker, event_id, bc_id):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = "select * from valuebet_childs where bookmaker = '{}' and event_id = '{}' and bc_id = '{}'".format(bookmaker,
                                                                                                             event_id,
                                                                                                             bc_id)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    if len(myresult) > 0:
        return False
    else:
        return True


def set_prematch_main(arbs_multi):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = 'INSERT INTO surebet_prematch (arbid,event_id,percent,bet1_id,bet2_id,bet3_id,arb_type,min_koef,max_koef,roi,event_updated,middle_value,parent,arb_formula_id,created_at,updated_at) ' \
          'VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s, %s,%s, %s,%s, %s,%s) ON DUPLICATE KEY UPDATE arbid=VALUES(arbid), percent=VALUES(percent), bet1_id=VALUES(bet1_id),bet2_id=VALUES(bet2_id), bet3_id=VALUES(bet3_id),arb_type=VALUES(arb_type), min_koef=VALUES(min_koef),max_koef=VALUES(max_koef),roi=VALUES(roi),event_updated=VALUES(event_updated),middle_value=VALUES(middle_value),arb_formula_id=VALUES(arb_formula_id), updated_at=VALUES(updated_at) ;'
    with mycursor as cursor:
        try:
            cursor.executemany(sql, arbs_multi)
            mydb.commit()
        except Exception as e:
            print('f', f'set_prematch Exception: {repr(e)}')
    cursor.close()


def set_prematch_child(arbs_multi_child):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = 'INSERT INTO surebet_prematch_child (arbid,event_id,percent,bet1_id,bet2_id,bet3_id,arb_type,min_koef,max_koef,roi,event_updated,middle_value,child,arb_formula_id,created_at,updated_at) ' \
          'VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s,%s) ON DUPLICATE KEY UPDATE arbid=VALUES(arbid), percent=VALUES(percent), bet1_id=VALUES(bet1_id),bet2_id=VALUES(bet2_id), bet3_id=VALUES(bet3_id),arb_type=VALUES(arb_type), min_koef=VALUES(min_koef),max_koef=VALUES(max_koef),roi=VALUES(roi),event_updated=VALUES(event_updated),middle_value=VALUES(middle_value),arb_formula_id=VALUES(arb_formula_id), updated_at=VALUES(updated_at) ;'
    with mycursor as cursor:
        try:
            cursor.executemany(sql, arbs_multi_child)
            mydb.commit()
        except Exception as e:
            print('f', f'set_prematch Exception: {repr(e)}')
    cursor.close()


def set_list(bets_lists):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = 'INSERT INTO surebet_lists (event_id,sport_id,bookmaker_id,bookmaker,bettime,event_name,league,koef,commission,period_id,bc_id,koef_lay,market_and_bet_type,market_and_bet_type_param,access_token,created_at,updated_at) ' \
          'VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s) ON DUPLICATE KEY UPDATE sport_id=VALUES(sport_id), bookmaker=VALUES(bookmaker),bettime=VALUES(bettime),league=VALUES(league),koef=VALUES(koef), commission=VALUES(commission), period_id=VALUES(period_id), bc_id=VALUES(bc_id), koef_lay=VALUES(koef_lay),market_and_bet_type=VALUES(market_and_bet_type), market_and_bet_type_param=VALUES(market_and_bet_type_param),access_token=VALUES(access_token),updated_at=VALUES(updated_at) ;'
    with mycursor as cursor:
        try:
            cursor.executemany(sql, bets_lists)
            mydb.commit()
        except Exception as e:
            print('f', f'set_list Exception: {repr(e)}')
    cursor.close()


def set_vprematch_main(varbs_multi):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = 'INSERT INTO valuebet_prematch (arbid,event_id,percent,bet1_id,arb_type,roi,event_updated,middle_value,parent,created_at,updated_at) ' \
          'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE arbid=VALUES(arbid),event_id=VALUES(event_id), percent=VALUES(percent), bet1_id=VALUES(bet1_id),arb_type=VALUES(arb_type),roi=VALUES(roi),event_updated=VALUES(event_updated),middle_value=VALUES(middle_value), updated_at=VALUES(updated_at) ;'
    with mycursor as cursor:
        try:
            cursor.executemany(sql, varbs_multi)
            mydb.commit()
        except Exception as e:
            print('f', f'set_vprematch_main Exception: {repr(e)}')
    cursor.close()


def set_vprematch_child(varbs_multi_child):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = 'INSERT INTO valuebet_prematch_child (arbid,event_id,percent,bet1_id,arb_type,roi,event_updated,middle_value,child,created_at,updated_at) ' \
          'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE arbid=VALUES(arbid),event_id=VALUES(event_id), percent=VALUES(percent), bet1_id=VALUES(bet1_id),arb_type=VALUES(arb_type),roi=VALUES(roi),event_updated=VALUES(event_updated),middle_value=VALUES(middle_value), updated_at=VALUES(updated_at) ;'
    with mycursor as cursor:
        try:
            cursor.executemany(sql, varbs_multi_child)
            mydb.commit()
        except Exception as e:
            print('f', f'set_vprematch_child Exception: {repr(e)}')
    cursor.close()


def set_vlist(vlists_array):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = 'INSERT INTO valuebet_lists (event_id,sport_id,bookmaker_id,bookmaker,bettime,event_name,league,koef,commission,period_id,bc_id,koef_lay,market_and_bet_type,market_and_bet_type_param,access_token,created_at,updated_at) ' \
          'VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s) ON DUPLICATE KEY UPDATE sport_id=VALUES(sport_id), bookmaker=VALUES(bookmaker),bettime=VALUES(bettime),league=VALUES(league), koef=VALUES(koef), commission=VALUES(commission), period_id=VALUES(period_id), bc_id=VALUES(bc_id), koef_lay=VALUES(koef_lay),market_and_bet_type=VALUES(market_and_bet_type), market_and_bet_type_param=VALUES(market_and_bet_type_param),access_token=VALUES(access_token),updated_at=VALUES(updated_at) ;'
    with mycursor as cursor:
        try:
            cursor.executemany(sql, vlists_array)
            mydb.commit()
        except Exception as e:
            print('f', f'set_vlist Exception: {repr(e)}')
    cursor.close()


def set_vsource_parent(source_array):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = 'UPDATE valuebet_prematch SET percent=%s WHERE bet1_id=%s and parent=%s;'
    with mycursor as cursor:
        try:
            cursor.executemany(sql, source_array)
            mydb.commit()
        except Exception as e:
            print('f', f'set_vsource_parent Exception: {repr(e)}')
    cursor.close()


def set_vsource_child(sources_child_array):
    mydb = getConnection()
    mycursor = mydb.cursor()
    sql = 'UPDATE valuebet_prematch_child SET percent=%s WHERE bet1_id=%s and child=%s;'
    with mycursor as cursor:
        try:
            cursor.executemany(sql, sources_child_array)
            mydb.commit()
        except Exception as e:
            print('f', f'set_vsource_child Exception: {repr(e)}')
    cursor.close()


url = 'https://www.betburger.com/arbs'
url2 = 'https://www.betburger.com/valuebets'
login_url = 'https://www.betburger.com/users/sign_in'

options = webdriver.FirefoxOptions()
options.add_argument("--start-maximized")
# profile = webdriver.FirefoxProfile(r"C:\Users\Administrator\AppData\Roaming\Mozilla\Firefox\Profiles\vn34s8al.default-release")
# profile = webdriver.FirefoxProfile(r"c:\Users\Administrator\AppData\Roaming\Mozilla\Firefox\Profiles\x7bl29te.default-release")
profile = webdriver.FirefoxProfile(
    r"C:\Users\Administrator\AppData\Roaming\Mozilla\Firefox\Profiles\m5nrup07.default-release")
# profile = webdriver.FirefoxProfile(r"c:\Users\Beatific Angel\AppData\Roaming\Mozilla\Firefox\Profiles\ng6fhe8g.default-release")

driver = webdriver.Firefox(executable_path="geckodriver.exe", options=options, firefox_profile=profile)
mainWin = driver.current_window_handle

print('Sucessfully the webdriver runned.')



def login():
    print("login")
    driver.get(login_url)
    time.sleep(1)
    try:
        cookieallow = driver.find_elements_by_class_name('cc-allow')[0].click()
    except:
        pass
    driver.find_element_by_id('betburger_user_email').send_keys(user_email)
    driver.find_element_by_id('betburger_user_password').send_keys(password)
    # driver.find_element_by_id('betburger_user_password').send_keys(Keys.RETURN)

    if (len(driver.find_elements_by_xpath('//div[contains(@class, "g-recaptcha")]'))) > 0:
        solver = TwoCaptcha('')
        sitekey = driver.find_element_by_xpath('//div[contains(@class, "g-recaptcha")]').get_attribute('data-sitekey')

        while 1:
            try:
                result = solver.solve_captcha(sitekey, driver.current_url)
            except Exception as e:
                print(str(e))
            else:
                print('solved: ' + str(result))
                break

        driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "%s"' % result)
        try:
            # driver.find_element_by_xpath('//button[@type="submit" and contains(@class, "btn-submit")]').click()
            driver.find_element_by_xpath('//form[@id="new_session"]').submit()
        except:
            pass

        time.sleep(1)


def init():
    login()
    print('get url')


def get_ageTime(time):
    if "minutes" in time:
        return str(datetime.utcnow() + timedelta(minutes=time.split()[0]))
    elif "hours" in time:
        return str(datetime.utcnow() + timedelta(hours=time.split()[0]))
    else:
        return str(datetime.utcnow() + timedelta(minutes=time.split()[0]))


def get_list(result, access_token, s, data):
    try:
        arbs_multi = []
        for arbs in result['arbs']:
            arb_id = arbs['id']
            event_id = int(arbs['event_id'])
            event_percent = arbs['percent']
            event_bet1_id = arbs['bet1_id']
            event_bet2_id = arbs['bet2_id']
            event_bet3_id = arbs['bet3_id']
            event_arb_type = arbs['arb_type']
            event_min_koef = arbs['min_koef']
            event_max_koef = arbs['max_koef']
            event_arb_formula_id = arbs['arb_formula_id']
            event_roi = arbs['roi']
            event_updated_at = arbs['updated_at']
            event_updated_at = datetime.fromtimestamp(event_updated_at)
            event_middle_value = arbs['middle_value']
            created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            event_parent = '1'
            params_main = (arb_id, event_id, event_percent, event_bet1_id, event_bet2_id, event_bet3_id, \
                           event_arb_type, event_min_koef, event_max_koef, event_roi, \
                           event_updated_at, event_middle_value, event_parent, event_arb_formula_id,
                           created_at, updated_at)
            arbs_multi.append(params_main)
        set_prematch_main(arbs_multi)
        event_arbs_cnt = len(result['event_arbs'])
        arbs_multi_child = []
        if event_arbs_cnt > 0:
            for event_arbs in result['event_arbs']:
                event_arbid = event_arbs['id']
                event_arbs_child = '1'
                event_eventid = int(event_arbs['event_id'])
                event_arbs_percent = event_arbs['percent']
                event_arbs_bet1_id = event_arbs['bet1_id']
                event_arbs_bet2_id = event_arbs['bet2_id']
                event_arbs_bet3_id = event_arbs['bet3_id']
                event_arb_formula_id = event_arbs['arb_formula_id']
                event_arbs_arb_type = event_arbs['arb_type']
                event_arbs_min_koef = event_arbs['min_koef']
                event_arbs_max_koef = event_arbs['max_koef']
                event_arbs_roi = event_arbs['roi']
                event_arbs_updated_at = event_arbs['updated_at']
                event_arbs_updated_at = datetime.fromtimestamp(event_arbs_updated_at)
                event_arbs_middle_value = event_arbs['middle_value']
                created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                params_main = (event_arbid, event_eventid, event_arbs_percent, event_arbs_bet1_id, event_arbs_bet2_id,
                               event_arbs_bet3_id, \
                               event_arbs_arb_type, event_arbs_min_koef, event_arbs_max_koef, event_arbs_roi, \
                               event_arbs_updated_at, event_arbs_middle_value, event_arbs_child, \
                               event_arb_formula_id, created_at, updated_at)
                arbs_multi_child.append(params_main)
            set_prematch_child(arbs_multi_child)
        bets_cnt = len(result['bets'])
        bets_lists = []
        if bets_cnt > 0:
            for real_bet in result['bets']:
                event_bets_id = real_bet['id']
                event_bets_event_id = real_bet['event_id']
                event_bets_koef = real_bet['koef']
                event_bets_commission = real_bet['commission']
                event_bets_name = real_bet['event_name'].replace("'", "\\'")
                event_bets_league = real_bet['league'].replace("'", "\\'")
                event_bets_bookmaker = real_bet['bookmaker_id']
                event_bets_koef_lay = real_bet['koef_lay']
                event_bets_bc_id = real_bet['bc_id']
                event_bets_bettime = real_bet['started_at']
                event_bets_bettime = datetime.fromtimestamp(event_bets_bettime)
                event_bets_sport_id = real_bet['sport_id']
                event_bets_market_and_bet_type = real_bet['market_and_bet_type']
                event_bets_market_and_bet_type_param = real_bet['market_and_bet_type_param']
                event_bets_period_id = real_bet['period_id']
                event_bets_access_token = access_token
                created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

                params = (event_bets_event_id, event_bets_sport_id, event_bets_id, \
                          event_bets_bookmaker, event_bets_bettime, event_bets_name, event_bets_league, \
                          event_bets_koef, event_bets_commission, event_bets_period_id, event_bets_bc_id, \
                          event_bets_koef_lay, event_bets_market_and_bet_type, event_bets_market_and_bet_type_param,
                          event_bets_access_token, \
                          created_at, updated_at)
                bets_lists.append(params)
            set_list(bets_lists)

    except Exception as e:
        pass


def get_list_valuebet(result, access_token, s, data):
    try:
        varbs_multi = []
        for arbs in result['arbs']:
            arb_id = arbs['id']
            event_id = int(arbs['event_id'])
            event_percent = arbs['percent']
            event_bet1_id = arbs['bet1_id']
            event_arb_type = arbs['arb_type']
            event_roi = arbs['roi']
            event_updated_at = arbs['updated_at']
            event_updated_at = datetime.fromtimestamp(event_updated_at)
            event_middle_value = arbs['middle_value']
            created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            event_parent = '1'
            params_main = (arb_id, event_id, event_percent, event_bet1_id, event_arb_type, event_roi, event_updated_at,
                           event_middle_value, event_parent, created_at, updated_at)
            varbs_multi.append(params_main)
        set_vprematch_main(varbs_multi)

        varbs_multi_child = []
        event_arbs_cnt = len(result['event_arbs'])
        if event_arbs_cnt > 0:
            for event_arbs in result['event_arbs']:
                event_arbid = event_arbs['id']
                event_arbs_child = '1'
                event_eventid = int(event_arbs['event_id'])
                event_arbs_percent = event_arbs['percent']
                event_arbs_bet1_id = event_arbs['bet1_id']
                event_arbs_arb_type = event_arbs['arb_type']
                event_arbs_roi = event_arbs['roi']
                event_arbs_updated_at = event_arbs['updated_at']
                event_arbs_updated_at = datetime.fromtimestamp(event_arbs_updated_at)
                event_arbs_middle_value = event_arbs['middle_value']
                created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                params_main = (event_arbid, event_eventid, event_arbs_percent, event_arbs_bet1_id, event_arbs_arb_type,
                               event_arbs_roi, event_arbs_updated_at, event_arbs_middle_value, event_arbs_child,
                               created_at, updated_at)
                varbs_multi_child.append(params_main)
            set_vprematch_child(varbs_multi_child)

        source_array = []
        sources_cnt = len(result['source']['value_bets'])
        if sources_cnt > 0:
            for source in result['source']['value_bets']:
                source_bets_id = source['bet_id']
                source_percent = source['percent']
                source_parent = '1'
                params = (source_percent, source_bets_id, source_parent)
                source_array.append(params)
            set_vsource_parent(source_array)
        sources_child_array = []
        sources_child_cnt = len(result['source']['event_value_bets'])
        if sources_child_cnt > 0:
            for source in result['source']['event_value_bets']:
                source_bets_id = source['bet_id']
                source_percent = source['percent']
                source_child = '1'
                params = (source_percent, source_bets_id, source_child)
                sources_child_array.append(params)
            set_vsource_child(sources_child_array)

        vlists_array = []
        bets_cnt = len(result['bets'])
        if bets_cnt > 0:
            for real_bet in result['bets']:
                event_bets_id = real_bet['id']
                event_bets_event_id = real_bet['event_id']
                event_bets_koef = real_bet['koef']
                event_bets_commission = real_bet['commission']
                event_bets_name = real_bet['event_name'].replace("'", "\\'")
                event_bets_league = real_bet['league'].replace("'", "\\'")
                event_bets_bookmaker = real_bet['bookmaker_id']
                event_bets_koef_lay = real_bet['koef_lay']
                event_bets_bc_id = real_bet['bc_id']
                event_bets_bettime = real_bet['started_at']
                event_bets_bettime = datetime.fromtimestamp(event_bets_bettime)
                event_bets_sport_id = real_bet['sport_id']
                event_bets_market_and_bet_type = real_bet['market_and_bet_type']
                event_bets_market_and_bet_type_param = real_bet['market_and_bet_type_param']
                event_bets_period_id = real_bet['period_id']
                event_bets_access_token = access_token
                created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

                params = (
                event_bets_event_id, event_bets_sport_id, event_bets_id, event_bets_bookmaker, event_bets_bettime,
                event_bets_name, event_bets_league, \
                event_bets_koef, event_bets_commission, event_bets_period_id, event_bets_bc_id, event_bets_koef_lay,
                event_bets_market_and_bet_type, event_bets_market_and_bet_type_param,
                event_bets_access_token, created_at, updated_at)
                vlists_array.append(params)
            set_vlist(vlists_array)

    except Exception as e:
        pass


def surebet_get_data(s, access_token, userid, bookie_id_lists, bstart):
    data = {
        'auto_update': False,
        'notification_sound': False,
        'notification_popup': False,
        'show_event_arbs': True,
        'grouped': True,
        'per_page': 20,
        'sort_by': 'valuebet_percent',
        'event_id': '',
        'koef_format': 'decimal',
        'q': '',
        'event_arb_types': [1, 2, 3, 4, 5, 6, 7, 8, 9],
        'bk_ids': bookie_id_lists,
        'is_live': False,
        'search_filter': [449539]
    }
    while True:
        event_url = f'https://rest-api-pr.betburger.com/api/v1/arbs/pro_search?access_token={access_token}&locale=en'
        response = s.post(event_url, data)
        if not bstart:
            time.sleep(4 * (len(getonlineuser_ids)))
        if response.status_code == 200:
            break
        else:
            print(response.status_code, response.text)

    print('get parent')
    filtertype = 'prematch'
    result = response.json()
    for event in result['arbs']:
        event_id = event['event_id']
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
                data = {
                    'auto_update': False,
                    'notification_sound': False,
                    'notification_popup': False,
                    'show_event_arbs': True,
                    'grouped': True,
                    'per_page': 20,
                    'sort_by': 'valuebet_percent',
                    'event_id': event_id,
                    'koef_format': 'decimal',
                    'q': '',
                    'event_arb_types': [1, 2, 3, 4, 5, 6, 7, 8, 9],
                    'bk_ids': bookie_id_lists,
                    'is_live': False,
                    'search_filter': [449539]
                }
                while True:
                    event_url = f'https://rest-api-pr.betburger.com/api/v1/arbs/pro_search?access_token={access_token}&locale=en'
                    response = s.post(event_url, data)
                    if not bstart:
                        time.sleep(4 * (len(getonlineuser_ids)))
                    if response.status_code == 200:
                        break
                    else:
                        print(response.status_code, response.text)

                print('get child', event_id)
                result = response.json()
                get_list(result, access_token, s, data)
            else:
                break
        else:
            break
    print('finished')


def valuebet_get_data(s, access_token, userid, vbookie_id_lists, bstart):
    filtertype = 'valuebet'
    vdata = {
        'auto_update': False,
        'notification_sound': False,
        'notification_popup': False,
        'show_event_arbs': True,
        'grouped': True,
        'per_page': 20,
        'sort_by': 'valuebet_percent',
        'event_id': '',
        'koef_format': 'decimal',
        'q': '',
        'event_arb_types': [1, 2, 3, 4, 5, 6, 7, 8, 9],
        'bk_ids': vbookie_id_lists,
        'is_live': False,
        'search_filter': [143580]
    }

    while True:
        vevent_url = f'https://rest-api-pr.betburger.com/api/v1/valuebets/pro_search?access_token={access_token}&locale=en'
        vresponse = s.post(vevent_url, vdata)
        if not bstart:
            time.sleep(4 * (len(getonlineuser_ids)))
        if vresponse.status_code == 200:
            break
        else:
            print(vresponse.status_code, vresponse.text)
    vresult = vresponse.json()
    for vevent in vresult['arbs']:
        vevent_id = vevent['event_id']
        vbookie_temp = ''
        vbookie_id_lists_tp = []
        vunique_list = []
        vbookie_lists_tp = get_bk_lists(userid, filtertype)
        if vbookie_lists_tp != True:

            for vbookie_list in vbookie_lists_tp:
                vprocessing_bklists_tp = vbookie_list[4]
                vprocessing_bklists_tp = unserialize_array(vprocessing_bklists_tp)
                for k, v in vprocessing_bklists_tp.items():
                    v = int(v)
                    vunique_list.append(v)
            for x in vunique_list:
                if x not in vbookie_id_lists_tp:
                    vbookie_id_lists_tp.append(x)
            vbookie_id_lists_tp.sort()

            if np.array_equiv(vbookie_id_lists_tp, vbookie_id_lists) == True:
                vdata = {
                    'auto_update': False,
                    'notification_sound': False,
                    'notification_popup': False,
                    'show_event_arbs': True,
                    'grouped': True,
                    'per_page': 20,
                    'sort_by': 'valuebet_percent',
                    'event_id': vevent_id,
                    'koef_format': 'decimal',
                    'q': '',
                    'event_arb_types': [1, 2, 3, 4, 5, 6, 7, 8, 9],
                    'bk_ids': vbookie_id_lists_tp,
                    'is_live': False,
                    'search_filter': [143580]
                }

                while True:
                    vevent_url = f'https://rest-api-pr.betburger.com/api/v1/valuebets/pro_search?access_token={access_token}&locale=en'
                    vresponse = s.post(vevent_url, vdata)
                    time.sleep(0.5)
                    print('event step')
                    if not bstart:
                        time.sleep(4 * (len(getonlineuser_ids)))
                    if vresponse.status_code == 200:
                        break
                    else:
                        print(vresponse.status_code, vresponse.text)
                print('get vchild', vevent_id)        
                vresult = vresponse.json()
                get_list_valuebet(vresult, access_token, s, vdata)
            else:
                break
        else:
            break


def multi_user_work(request_cookies_browser, access_token, userid, bookie_id_lists, vbookie_id_lists,checked_bet, bstart):
    s = requests.Session()
    c = [s.cookies.set(c['name'], c['value']) for c in request_cookies_browser]


    if checked_bet == '' :
        surebet_get_data(s, access_token, userid, bookie_id_lists, bstart)
        valuebet_get_data(s, access_token, userid, vbookie_id_lists, bstart)
    elif checked_bet == 'surebet':
        surebet_get_data(s, access_token, userid, bookie_id_lists, bstart)
    elif checked_bet == 'valuebet':
        valuebet_get_data(s, access_token, userid, vbookie_id_lists, bstart)
    if userid not in changed_ids:
        getonlineuser_ids.remove(userid)
    else:
        changed_ids.remove(userid)


getonlineuser_ids = []
working_ids = []
changed_ids = []


def main():
    init()
    driver.get(url)
    time.sleep(0.5)
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

    vfiltertype = 'valuebet'
    vuser_bookie_id_lists = {}
    for user in current_online:
        userid = user[0]
        vunique_list = []
        vbookie_id_lists = []
        vbookie_lists = get_bk_lists(userid, vfiltertype)
        if vbookie_lists != True:
            for vbookie_list in vbookie_lists:
                vprocessing_bklists = vbookie_list[4]
                vprocessing_bklists = unserialize_array(vprocessing_bklists)
                for k, v in vprocessing_bklists.items():
                    v = int(v)
                    vunique_list.append(v)
            for x in vunique_list:
                if x not in vbookie_id_lists:
                    vbookie_id_lists.append(x)
            vbookie_id_lists.sort()
        vuser_bookie_id_lists[userid] = vbookie_id_lists        

    while True:
        while True:
            try:
                href = driver.find_element_by_xpath('//a[contains(@href, "access_token=")]').get_attribute('href')
                break
            except:
                time.sleep(0.5)
        start_pos = href.find('access_token=') + len('access_token=')
        end_pos = href.find('&', start_pos)
        access_token = href[start_pos:end_pos]
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
                                          request_cookies_browser, access_token, userid, user_bookie_id_lists[userid],vuser_bookie_id_lists[userid],checked_bet,
                                          start))
                workers.append(worker)
                worker.start()
                print('thread created')
                checked_bet = ''

            else:
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

                    if np.array_equiv(bookie_id_lists_tp, user_bookie_id_lists[userid]) == False:
                        print('changed_filter', bookie_id_lists_tp)
                        user_bookie_id_lists[userid] = bookie_id_lists_tp
                        getonlineuser_ids.remove(userid)
                        working_ids.remove(userid)
                        changed_ids.append(userid)
                        checked_bet = 'surebet'


                vbookie_lists_tp = get_bk_lists(userid, vfiltertype)
                if vbookie_lists_tp != True:
                    bookie_temp = ''
                    vunique_list_tp = []
                    vbookie_id_lists_tp = []
                    for bookie_lists_tp_cel in vbookie_lists_tp:
                        vprocessing_bklists_tp = bookie_lists_tp_cel[4]
                        vprocessing_bklists_tp = unserialize_array(vprocessing_bklists_tp)
                        for k, v in vprocessing_bklists_tp.items():
                            v = int(v)
                            vunique_list_tp.append(v)
                    for x in vunique_list_tp:
                        if x not in vbookie_id_lists_tp:
                            vbookie_id_lists_tp.append(x)
                    vbookie_id_lists_tp.sort()

                    if np.array_equiv(vbookie_id_lists_tp, vuser_bookie_id_lists[userid]) == False:
                        print('changed_valuebet_filter', bookie_id_lists_tp)
                        vuser_bookie_id_lists[userid] = vbookie_id_lists_tp
                        getonlineuser_ids.remove(userid)
                        working_ids.remove(userid)
                        changed_ids.append(userid)                        
                        checked_bet = 'valuebet'

        # if getonlineuser_ids != True:
        #     for selected_user in getonlineuser_ids:
        #         worker = threading.Thread(target=multi_user_work, daemon=True, args=(request_cookies_browser, access_token, selected_user))
        #         workers.append(worker)
        #         worker.start()
        #     for worker in workers:
        #         worker.join()


if __name__ == "__main__":
    main()
