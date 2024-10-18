import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests
from bs4 import BeautifulSoup
import discord
from dotenv import load_dotenv
load_dotenv()
import os
from discord.ext import commands,tasks
import re
import datetime
import schedule
from lxml import html
from datetime import datetime, timedelta
from collections import OrderedDict
from PIL import Image,ImageDraw,ImageFont


CHANNEL_ID =1294151296667881483
# twohourslater_str = None
url="https://soccer.yahoo.co.jp/jleague/"
matchtimes=[
    
]

global nowtime
global driver
driver = webdriver.Chrome()
driver.implicitly_wait(10)
scoreandmatchtime={}
font = ImageFont.truetype('ヒラギノ角ゴシック W9.ttc', 50)
async def scoreget():
    results = []
    linkss = []
    imagess= []
    background_image_urls=[]
    driver.get(url)
    global flag
    flag = True
    # now =datetime.now().strftime('%H:%M')
    now = datetime.strptime('16:30', '%H:%M').strftime('%H:%M')#仮
    try:
        hrefs = driver.find_elements(By.CLASS_NAME, "sc-tableGame__score--hasLink")
        # OrderedDict でリンクの順番を保持しつつ重複を排除
        unique_links = OrderedDict()

        for link in hrefs:
            href = link.get_attribute('href')
            if href:
                unique_links[href] = link  # 重複を排除しつつリンクを保持
        
        linkss = list(unique_links.keys())  # 重複のないリンクのリストを取得
        print(linkss)
    except:
        print('リンクが取得できませんでした')

    if flag:
      for onelink in linkss:
        res = requests.get(onelink)
        
        global soup

        soup = BeautifulSoup(res.text, 'html.parser')
        cnvrtdate=html.fromstring(str(soup))
           #/html/body/div/main/div[2]/section[2]/div/div/div/div[2]/div[1]/div[1]/a/span
                                              #/html/body/div/main/div[2]/section[2]/div/div/div/div[2]/div[1]/div[1]/a/span
        findscore = soup.find_all(class_=['sc-scoreBoard__time'])
        findscorehome = soup.find_all(class_=['sc-scoreBoard__data--totalHome'])
        findscoreaway = soup.find_all(class_=['sc-scoreBoard__data--totalAway'])
        findscoreteamname = soup.find_all(class_=['sc-scoreBoard__teamName'])
        global findstats
        # findstats=soup.find_all("td",class_=['sc-tableVersus__data--away'])
        logo = cnvrtdate.xpath('/html/body/div/main/div[2]/section[2]/div/div/div/div[2]/div[1]/div[1]/a/span')
        findstatshome1=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[1]/td[1]')
        findstatshome2=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[2]/td[1]')
        findstatshome3=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[3]/td[1]')
        findstatshome4=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[4]/td[1]')
        findstatshome5=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[5]/td[1]')
        findstatshome6=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[6]/td[1]')
        findstatshome7=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[7]/td[1]')
        findstatshome8=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[8]/td[1]')
        findstatshome9=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[9]/td[1]')
        findstatshome10=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[10]/td[1]')
        findstatcardyshome11=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[11]/td[1]/p[1]')
        findstatcardrhome12=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[11]/td[1]/p[2]')

        findstatsaway1=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[1]/td[2]')
        findstatsaway2=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[2]/td[2]')
        findstatsaway3=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[3]/td[2]')
        findstatsaway4=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[4]/td[2]')
        findstatsaway5=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[5]/td[2]')
        findstatsaway6=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[6]/td[2]')
        findstatsaway7=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[7]/td[2]')
        findstatsaway8=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[8]/td[2]')
        findstatsaway9=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[9]/td[2]')
        findstatsaway10=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[10]/td[2]')
        findstatcardyaway11=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[11]/td[2]/p[1]')
        findstatcardraway11=cnvrtdate.xpath('/html/body/div/main/div[2]/div[4]/section/table/tbody/tr[11]/td[2]/p[2]')

        for p in findscore:
            img = Image.open('stats.png')
            draw = ImageDraw.Draw(img)
            
            time_str = p.text

            date_match = re.search(r'(\d{1,2})/(\d{1,2})', time_str)
            time_match = re.search(r'(\d{1,2}):(\d{2})', time_str)
            

            if date_match and time_match:
                month = date_match.group(1).zfill(2)  # 月をゼロ埋め
                day = date_match.group(2).zfill(2)    # 日をゼロ埋め
                hour = time_match.group(1).zfill(2)   # 時間をゼロ埋め
                minute = time_match.group(2)          # 分

                # 現在の年を取得
                now_year = datetime.now().year
                match_datetime = datetime(year=now_year, month=int(month), day=int(day), hour=int(hour), minute=int(minute))
                nowtime = match_datetime.strftime('%Y%m%d%H%M')
                global twohourslatersss
                twohourslatersss = datetime.strptime(nowtime, '%Y%m%d%H%M') + timedelta(hours=2, minutes=30)
                twohourslater_str = twohourslatersss.strftime('%H:%M')
                matchtimes.append(twohourslatersss)
                
                
                print(nowtime)
                # print(f"テスト{homestats1}")
        
              
                if twohourslater_str == now:
                          
                          draw = ImageDraw.Draw(img)
                          
                          home_score = findscorehome[0].text.strip() if findscorehome else 'N/A'
                          away_score = findscoreaway[0].text.strip() if findscoreaway  else'N/A'
                          home_team = findscoreteamname[0].text.strip() if len(findscoreteamname) > 0 else 'N/A'
                          away_team = findscoreteamname[1].text.strip() if len(findscoreteamname) > 1 else 'N/A'
                          homestats1=findstatshome1[0].text.strip() if len(findstatshome1) > 0 else 'N/A'
                          homestats2=findstatshome2[0].text.strip() if len(findstatshome2) > 0 else 'N/A'
                          homestats3=findstatshome3[0].text.strip() if len(findstatshome3) > 0 else 'N/A'
                          homestats4=findstatshome4[0].text.strip() if len(findstatshome4) > 0 else 'N/A'
                          homestats5=findstatshome5[0].text.strip() if len(findstatshome5) > 0 else 'N/A'
                          homestats6=findstatshome6[0].text.strip() if len(findstatshome6) > 0 else 'N/A'
                          homestats7=findstatshome7[0].text.strip() if len(findstatshome7) > 0 else 'N/A'
                          homestats8=findstatshome8[0].text.strip() if len(findstatshome8) > 0 else 'N/A'
                          homestats9=findstatshome9[0].text.strip() if len(findstatshome9) > 0 else 'N/A'
                          homestats10=findstatshome10[0].text.strip() if len(findstatshome10) > 0 else 'N/A'
                          homestats11=findstatcardyaway11[0].text.strip() if len(findstatcardyshome11) > 0 else 'N/A'
                          homestats12=findstatcardraway11[0].text.strip() if len(findstatcardyshome11) > 0 else 'N/A'
                                                                                  
                  
                          awaystats1=findstatsaway1[0].text.strip() if len(findstatsaway1)> 0 else 'N/A'
                          awaystats2=findstatsaway2[0].text.strip() if len(findstatsaway2)> 0 else 'N/A'
                          awaystats3=findstatsaway3[0].text.strip() if len(findstatsaway3)> 0 else 'N/A'
                          awaystats4=findstatsaway4[0].text.strip() if len(findstatsaway4)> 0 else 'N/A'
                          awaystats5=findstatsaway5[0].text.strip() if len(findstatsaway5)> 0 else 'N/A'
                          awaystats6=findstatsaway6[0].text.strip() if len(findstatsaway6)> 0 else 'N/A'
                          awaystats7=findstatsaway7[0].text.strip() if len(findstatsaway7)> 0 else 'N/A'
                          awaystats8=findstatsaway8[0].text.strip() if len(findstatsaway8) > 0 else 'N/A'
                          awaystats9=findstatsaway9[0].text.strip() if len(findstatsaway9) > 0 else 'N/A'
                          awaystats10=findstatsaway10[0].text.strip() if len(findstatsaway10) > 0 else 'N/A'
                          awaystats11=findstatcardyshome11[0].text.strip() if len(findstatcardyshome11) > 0 else 'N/A'
                          awaystats12=findstatcardrhome12[0].text.strip() if len(findstatcardyshome11) > 0 else 'N/A'
                          homestats6.replace('\n', '')
                          awaystats6.replace('\n','') 
                          draw.text((50,300),home_team,'black',font=font,align='center')
                          draw.text((500,300),away_team,'black',font=font,align='center')
                          result_message = f"{home_team} {home_score} - {away_score} {away_team}\n{homestats1+'ボール支配率'+awaystats1}\n{homestats2+'シュート'+awaystats2}\n{homestats3+'枠内シュート'+awaystats3}\n{homestats4+'走行距離'+awaystats4}\n{homestats5+'スプリント'+awaystats5}\n{homestats6+'パス（成功率）' + awaystats6}\n{homestats7+'オフサイド'+awaystats7}\n{homestats8+'フリーキック'+awaystats8}\n{homestats9+'コーナーキック'+awaystats9}\n{homestats10+'ペナルティキック'+awaystats10}\n{'ホームイエローカード'+homestats11}\n{'ホームレッドカード'+homestats12}\n{'アウェイイエローカード'+awaystats11}\n{'アウェイレッドカード'+awaystats12}\n"
                          results.append(result_message)  # 各試合結果をリストに追
                          global image_filename
                          image_filename = f"{home_team}.png".replace(' ', '_')
                          imagess.append(image_filename)
                          img.save(image_filename)
                          flag = False
                          # img.save("result.jpg")
                          # return image_filename
                flag=False
        # for result in results:
        #    if twohourslater_str == now:
    return imagess
                
      
token=os.getenv('TOKEN')
intents=discord.Intents.none()
intents.reactions = True
intents.guilds = True
intents=discord.Intents.default()
intents.message_content=True
bot=commands.Bot(command_prefix='!', intents=intents)
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    
    print('ログインしました')
    @tasks.loop(seconds=60)
    async def loop():
        # print(f"現在の時間: {now}, 2時間半後の時間: {twohourslater_str}")
          # now =datetime.now().strftime('%H:%M')
          channel = client.get_channel(CHANNEL_ID)
          # message=await scoreget()
          # for messages in message:  # 各試合ごとにメッセージを送信
          messages = await scoreget()  # 全試合結果を取得
          for message in messages:  # 各試合ごとにメッセージを
            await channel.send(file=discord.File(message))

            await asyncio.sleep(1)  
          # if "11:00" == now:
          #       await check()
          #       print("check() が実行されました")
    loop.start()
client.run(token)