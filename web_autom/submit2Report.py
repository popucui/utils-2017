#!/usr/bin/env python
#coding=utf-8
'''
login and post data to TianFu report system: http://192.168.0.16:8088/genius/login/auth
params:
    patientId
    snpResult
'''
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
#from bs4 import BeautifulSoup
import requests, ConfigParser, sys
import logging

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.CRITICAL)

patientId = sys.argv[1]
snpResult = sys.argv[2]

display = Display(visible=0, size=(1024, 768))
display.start()

config = ConfigParser.ConfigParser()
config.readfp(open('allgftType.cfg') )
#prepare data for submit
patientData = {
    '_action_save': 'Save',
    'barcode': patientId,
    'id': patid,
    'patientId': patid,
    'version': '0',
    'type' : []
}
with open(snpResult) as f:
    for line in f:
        tmp = line.strip().split()
        snp = tmp[3]
        gftid = tmp[5]
        logging.debug(config.get(gftid, snp))
        patientData['type'].append(config.get(gftid, snp) )

#login
browser = webdriver.Firefox()
browser.get('http://192.168.0.16:8088/genius/login/auth')
username = browser.find_element_by_name("j_username")
password = browser.find_element_by_name("j_password")
username.send_keys("user")
password.send_keys("passwd")
browser.find_element_by_id("field-submit").click()

#select a patient
url = 'http://192.168.0.16:8088/genius/testResult/listPatient?name=&barcode={0}&consentId=&offset=&max=2'.format(patientId)
browser.get(url)
browser.find_element_by_link_text(patientId).click()
patid = browser.current_url.split('/')[-1]


currentCookie = browser.get_cookies()
logging.info(currentCookie[0]['value'])
postPatientInfo = requests.post(browser.current_url, data = patientData, cookies={'JSESSIONID' : currentCookie[0]['value']} )
logging.info( postPatientInfo.text )
logging.info(postPatientInfo.status_code)
if postPatientInfo.status_code == 200:
    print '{0} done!'.format(patientId)

browser.close()
display.stop()
