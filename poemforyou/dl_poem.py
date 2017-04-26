#!/home/reboot/software/envs/p3k/bin/python3.5

import os,sys
import time,random
import requests
from bs4 import BeautifulSoup

i = 0
with open(sys.argv[1]) as f:
    for line in f:
        html = requests.get(line).text
        soup = BeautifulSoup(html, 'html.parser')
        poem_title = soup.title.get_text()
        mpvoice = soup.find_all('mpvoice')
        
        if i % 5 == 0: #wait for few seconds
            time.sleep( random.sample(range(6), 1)[0] )
        if mpvoice:
            audio_id = mpvoice[0].get('voice_encode_fileid')
            os.system('wget https://res.wx.qq.com/voice/getvoice\?mediaid\={m_id} -O "./audio/{name}.mp3"'.format(
                m_id = audio_id, name = poem_title ) )
            i += 1
        else:
            pass
        