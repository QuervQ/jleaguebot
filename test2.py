import asyncio
import io
import aiohttp
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
from selenium.webdriver.chrome.options import Options
import re
import datetime
import urllib.request
from lxml import html
from datetime import datetime, timedelta
from collections import OrderedDict
from PIL import Image,ImageDraw,ImageFont
from discord import app_commands
import tweepy
from keep_alive import keep_alive

CHANNEL_ID =1294151296667881483
# twohourslater_str = None
url="https://soccer.yahoo.co.jp/jleague/"
matchtimes=[
    
]
clientx = tweepy.Client(bearer_token=os.getenv('Bearertoken'),
                        consumer_key=os.getenv('api_key'),
                        consumer_secret=os.getenv('api_keysecret'),
                        access_token=os.getenv('accseestoken'),
                        access_token_secret=os.getenv('accseestokensecret'))
auth = tweepy. OAuthHandler (os.getenv('api_key'), os.getenv('api_keysecret'))
auth. set_access_token(os.getenv('accseestoken'), os.getenv('accseestokensecret'))
api = tweepy.API (auth)
options = Options()
options.add_argument('--headless')
global nowtime
global driver
driver = webdriver.Chrome(options=options)#
driver.implicitly_wait(10)
scoreandmatchtime={}
font4=ImageFont.truetype('ヒラギノ角ゴシック_W9.ttc', 15)
font2 = ImageFont.truetype('ヒラギノ角ゴシック_W9.ttc', 30)
font = ImageFont.truetype('ヒラギノ角ゴシック_W9.ttc', 30)#HackNerdFontMono-Bold.ttf
font1 = ImageFont.truetype('ヒラギノ角ゴシック_W9.ttc', 60)
font3 = ImageFont.truetype('ヒラギノ角ゴシック_W9.ttc', 25)
sentfile=set()
async def fetch_image(url: str, filename: str):
    try:
      """非同期で画像をダウンロードする"""
      async with aiohttp.ClientSession() as session:
           async with session.get(url) as response:
             if response.status == 200:
                with open(filename, 'wb') as f:
                    f.write(await response.read())
                    print(f"画像 {filename} をダウンロードしました。")
    except Exception as e:
        print(e)
async def scoreget():
      results = []
      linkss = []
      imagess= []
      background_image_urls=[]
      driver.get(url)
      
      now =datetime.now().strftime('%H:%M')
      # now = datetime.strptime('21:30', '%H:%M').strftime('%H:%M')#仮
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
      except Exception as e:
          print(e)
      try:    
        for onelink in linkss:
          res = requests.get(onelink)
          soup = BeautifulSoup(res.text, 'html.parser')
          cnvrtdate=html.fromstring(str(soup))
          soup = BeautifulSoup(res.text, 'html.parser')
          driver.get(onelink)
          cnvrtdate=html.fromstring(str(soup))
             #/html/body/div/main/div[2]/section[2]/div/div/div/div[2]/div[1]/div[1]/a/span
                                                #/html/body/div/main/div[2]/section[2]/div/div/div/div[2]/div[1]/div[1]/a/span
          findscore = soup.find_all(class_=['sc-scoreBoard__time'])
          findscorehome = soup.find_all(class_=['sc-scoreBoard__data--totalHome'])
          findscoreaway = soup.find_all(class_=['sc-scoreBoard__data--totalAway'])
          findscoreteamname = soup.find_all(class_=['sc-scoreBoard__teamName'])
          global findstats
          # findstats=soup.find_all("td",class_=['sc-tableVersus__data--away']
              
          logohome=driver.find_element(By.XPATH,"/html/body/div/main/div[2]/section[2]/div/div/div/div[2]/div[1]/div[1]/a/span").value_of_css_property('background-image')
          
          logoaway = driver.find_element(By.XPATH,"/html/body/div/main/div[2]/section[2]/div/div/div/div[2]/div[3]/div[1]/a/span").value_of_css_property('background-image')
  
          homematch= re.search(r'url\("(.*?)"\)', logohome)
          if homematch:
              logourlh=homematch.group(1)
              print(logourlh)
  
          awaymatch = re.search(r'url\("(.*?)"\)', logoaway)
          if awaymatch:
              logourla=awaymatch.group(1)
              print(logourla)
  
  
          responseh = requests.get(logourlh)
          responsea = requests.get(logourla)
  
          imageh=responseh.content
          imagea=responsea.content
                                                                  #  /html/body/div/main/div[2]/div[3]/section/table/tbody/tr[1]/td[1]
          findstatshome1=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[1]/td[1]')
          findstatshome2=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[2]/td[1]')
          findstatshome3=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[3]/td[1]')
          findstatshome4=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[4]/td[1]')
          findstatshome5=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[5]/td[1]')
          findstatshome6=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[6]/td[1]')
          findstatshome7=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[7]/td[1]')
          findstatshome8=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[8]/td[1]')
          findstatshome9=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[9]/td[1]')
          findstatshome10=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[10]/td[1]')
          findstatcardyshome11=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[11]/td[1]/p[1]')
          findstatcardrhome12=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[11]/td[1]/p[2]')
  
          findstatsaway1=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[1]/td[2]')
          findstatsaway2=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[2]/td[2]')
          findstatsaway3=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[3]/td[2]')
          findstatsaway4=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[4]/td[2]')
          findstatsaway5=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[5]/td[2]')
          findstatsaway6=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[6]/td[2]')
          findstatsaway7=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[7]/td[2]')
          findstatsaway8=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[8]/td[2]')
          findstatsaway9=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[9]/td[2]')
          findstatsaway10=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[10]/td[2]')
          findstatcardyaway11=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[11]/td[2]/p[1]')
          findstatcardraway12=cnvrtdate.xpath('/html/body/div/main/div[2]/div[3]/section/table/tbody/tr[11]/td[2]/p[2]')
  
          zennhannhomescore=cnvrtdate.xpath('/html/body/div/main/div[2]/section[2]/div/div/div/div[2]/div[2]/table/tbody/tr[1]/td[2]')
          zennhannawayscore=cnvrtdate.xpath('/html/body/div/main/div[2]/section[2]/div/div/div/div[2]/div[2]/table/tbody/tr[1]/td[4]')
          kouhanhomescore=cnvrtdate.xpath('/html/body/div/main/div[2]/section[2]/div/div/div/div[2]/div[2]/table/tbody/tr[2]/td[1]')
          kouhanawayscore=cnvrtdate.xpath('/html/body/div/main/div[2]/section[2]/div/div/div/div[2]/div[2]/table/tbody/tr[2]/td[3]')
          info=cnvrtdate.xpath('/html/body/div/main/div[2]/section[2]/div/div/div/div[2]/div[2]/div/p')
          studium = cnvrtdate.xpath('/html/body/div/main/div[2]/section[13]/table/tbody/tr[1]/td')
          human=cnvrtdate.xpath('/html/body/div/main/div[2]/section[13]/table/tbody/tr[2]/td[1]')

          for p in findscore:
              img = Image.open('stats.png').convert('RGBA')
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
                  
                  infos=info[0].text.strip() if info else '-'
                  print(nowtime)
                  # print(f"テスト{homestats1}")
          
                  
                  if infos == '試合終了':
                    draw = ImageDraw.Draw(img)
                    home_image = f"{logourlh.split('/')[-1]}"
                    away_image = f"{logourla.split('/')[-1]}"
                    await fetch_image(logourlh, home_image)
                    await fetch_image(logourla, away_image)
                    imglistsh=Image.open(home_image).convert('RGBA')
                    imglistsa=Image.open(away_image).convert('RGBA')
                    ycard = Image.open('yellowcard.png')
                    rcard=Image.open('redcard.png')
                    ycard2 = Image.open('yellowcard.png')
                    rcard2=Image.open('redcard.png')
                    
                    home_score = findscorehome[0].text.strip() if findscorehome else '-'
                    away_score = findscoreaway[0].text.strip() if findscoreaway  else'-'
                    home_team = findscoreteamname[0].text.strip() if len(findscoreteamname) > 0 else '-'
                    away_team = findscoreteamname[1].text.strip() if len(findscoreteamname) > 1 else '-'
                    studiums = studium[0].text.strip() if studium else '-'
                    zennhannhome_score = zennhannhomescore[0].text.strip() if  zennhannhomescore else '-'
                    zenhannaway_score = zennhannawayscore[0].text.strip() if zennhannawayscore  else'-'
                    kouhannhome_score = kouhanhomescore[0].text.strip() if kouhanhomescore  else '-'
                    kouhannaway_score = kouhanawayscore[0].text.strip() if kouhanawayscore else '-'
                    humas = human[0].text.strip() if human else '-'
                    homestats1=findstatshome1[0].text.strip() if len(findstatshome1) > 0 else '-'
                    homestats2=findstatshome2[0].text.strip() if len(findstatshome2) > 0 else '-'
                    homestats3=findstatshome3[0].text.strip() if len(findstatshome3) > 0 else '-'
                    homestats4=findstatshome4[0].text.strip() if len(findstatshome4) > 0 else '-'
                    homestats5=findstatshome5[0].text.strip() if len(findstatshome5) > 0 else '-'
                    homestats6=findstatshome6[0].text.strip() if len(findstatshome6) > 0 else '-'
                    homestats7=findstatshome7[0].text.strip() if len(findstatshome7) > 0 else '-'
                    homestats8=findstatshome8[0].text.strip() if len(findstatshome8) > 0 else '-'
                    homestats9=findstatshome9[0].text.strip() if len(findstatshome9) > 0 else '-'
                    homestats10=findstatshome10[0].text.strip() if len(findstatshome10) > 0 else '-'
                    homestats11=findstatcardyshome11[0].text.strip() if len(findstatcardyshome11) > 0 else '-'
                    homestats12=findstatcardrhome12[0].text.strip() if len(findstatcardyshome11) > 0 else '-'
                                                                            
                    
                    
                    awaystats1=findstatsaway1[0].text.strip() if len(findstatsaway1)> 0 else '-'
                    awaystats2=findstatsaway2[0].text.strip() if len(findstatsaway2)> 0 else '-'
                    awaystats3=findstatsaway3[0].text.strip() if len(findstatsaway3)> 0 else '-'
                    awaystats4=findstatsaway4[0].text.strip() if len(findstatsaway4)> 0 else '-'
                    awaystats5=findstatsaway5[0].text.strip() if len(findstatsaway5)> 0 else '-'
                    awaystats6=findstatsaway6[0].text.strip() if len(findstatsaway6)> 0 else '-'
                    awaystats7=findstatsaway7[0].text.strip() if len(findstatsaway7)> 0 else '-'
                    awaystats8=findstatsaway8[0].text.strip() if len(findstatsaway8) > 0 else '-'
                    awaystats9=findstatsaway9[0].text.strip() if len(findstatsaway9) > 0 else '-'
                    awaystats10=findstatsaway10[0].text.strip() if len(findstatsaway10) > 0 else '-'
                    awaystats11=findstatcardyaway11[0].text.strip() if len(findstatcardyshome11) > 0 else '-'
                    awaystats12=findstatcardraway12[0].text.strip() if len(findstatcardyshome11) > 0 else '-'
                    homestats6=homestats6.replace('\n', '').strip()
                    awaystats6=awaystats6.replace('\n', '').strip()
                    homestats6=homestats6.replace(' ', '').strip()
                    awaystats6= awaystats6.replace(' ', '')
                    draw.text((210,20),f"{zennhannhome_score}    前半    {zenhannaway_score}",'white',font=font,align='center')
                    draw.text((210,60),f"{kouhannhome_score}    後半    {kouhannaway_score}",'white',font=font,align='center')
                    draw.text((70,140),home_score,'white',font=font1,align='center')
                    draw.text((490,140),away_score,'white',font=font1,align='center')
                    draw.text((80,240),homestats1,'white',font=font,align='center')
                    draw.text((210,240),"ボール支配率",'white',font=font,align='center')
                    draw.text((470,240),awaystats1,'white',font=font,align='center')

                    draw.text((80,290),homestats2,'white',font=font,align='center')
                    draw.text((240,290),"シュート",'white',font=font,align='center')
                    draw.text((470,290),awaystats2,'white',font=font,align='center')

                    draw.text((80,340),homestats3,'white',font=font,align='center')
                    draw.text((220,340),"枠内シュート",'white',font=font,align='center')
                    draw.text((470,340),awaystats3,'white',font=font,align='center')
                    if homestats4=='-':
                        draw.text((80,390),homestats4,'white',font=font3,align='center')#
                    else:
                      draw.text((20,390),homestats4,'white',font=font3,align='center')#
                    draw.text((240,390),"走行距離",'white',font=font,align='center')
                    if awaystats4=='-':
                        draw.text((470,390),awaystats4,'white',font=font3,align='center')#
                    else:
                      draw.text((410,390),awaystats4,'white',font=font3,align='center')#


                    draw.text((80,440),homestats5,'white',font=font,align='center')
                    draw.text((230,440),"スプリント",'white',font=font,align='center')
                    draw.text((470,440),awaystats5,'white',font=font,align='center')

                    if homestats6=='-':
                      draw.text((80,490),homestats6,'white',font=font3,align='center')#
                    else:
                      draw.text((20,490),homestats6,'white',font=font3,align='center')#
                    draw.text((210,490),"パス（成功率）",'white',font=font,align='center')
                    if awaystats6=='-':
                      draw.text((470,490),awaystats6,'white',font=font3,align='center')#
                    else:
                      draw.text((420,490),awaystats6,'white',font=font3,align='center')#

                    draw.text((80,540),homestats7,'white',font=font,align='center')
                    draw.text((230,540),"オフサイド",'white',font=font,align='center')
                    draw.text((470,540),awaystats7,'white',font=font,align='center')

                    draw.text((80,590),homestats8,'white',font=font,align='center')
                    draw.text((220,590),"フリーキック",'white',font=font,align='center')
                    draw.text((470,590),awaystats8,'white',font=font,align='center')

                    draw.text((80,640),homestats9,'white',font=font,align='center')
                    draw.text((200,640),"コーナーキック",'white',font=font,align='center')
                    draw.text((470,640),awaystats9,'white',font=font,align='center')

                    draw.text((80,690),homestats10,'white',font=font,align='center')
                    draw.text((190,690),"ペナルティキック",'white',font=font,align='center')
                    draw.text((470,690),awaystats10,'white',font=font,align='center')

                    draw.text((60,740),homestats11,'white',font=font,align='center')
                    draw.text((240,740),"警告 退場",'white',font=font,align='center')
                    draw.text((450,740),awaystats11,'white',font=font,align='center')
                    draw.text((130,740),homestats12,'white',font=font,align='center')
                    draw.text((520,740),awaystats12,'white',font=font,align='center')
                    draw.text((10,950),'Create By @Quervo9e','white',font=font,align='center')
                    result_message = f"{home_team} {home_score} - {away_score} {away_team}\n{homestats1+'ボール支配率'+awaystats1}\n{homestats2+'シュート'+awaystats2}\n{homestats3+'枠内シュート'+awaystats3}\n{homestats4+'走行距離'+awaystats4}\n{homestats5+'スプリント'+awaystats5}\n{homestats6+'パス（成功率）' + awaystats6}\n{homestats7+'オフサイド'+awaystats7}\n{homestats8+'フリーキック'+awaystats8}\n{homestats9+'コーナーキック'+awaystats9}\n{homestats10+'ペナルティキック'+awaystats10}\n{'ホームイエローカード'+homestats11}\n{'ホームレッドカード'+homestats12}\n{'アウェイイエローカード'+awaystats11}\n{'アウェイレッドカード'+awaystats12}\n"
                    results.append(result_message)  # 各試合結果をリストに追
                    global image_filename
                    image_filename = f"{match_datetime}{home_team}{away_team}.png".replace(' ', '_')
                    
                    
                    
                    #背景と同サイズの透明な画像を生成
                    imgclearb = Image.new("RGBA", img.size, (255, 255, 255, 0))
                    # img_clearh = Image.new("RGBA", imglistsh.size, (255, 255, 255, 0))
                    # img_cleara =Image.new("RGBA", imglistsa.size, (255, 255, 255, 0))
                    #透明画像の上にペースト
                    imgclearb.paste(imglistsh, (30, 10))
                    imgclearb.paste(imglistsa, (450, 10))
                    imgclearb.paste(ycard,(30,750))
                    imgclearb.paste(ycard2,(420,750))
                    imgclearb.paste(rcard,(100,750))
                    imgclearb.paste(rcard2,(490,750))

                    
                    #重ね合わせる
                    imgs = Image.alpha_composite(img, imgclearb)
                    num_byteio = io.BytesIO()
                    imgs.save(num_byteio, format='png')# 仮にpngにしている
                    num_bytes = num_byteio.getvalue()
                    imagess.append(num_bytes)
                    
                    # imgs.save(image_filename)
                    # img.save("result.jpg")
                    # return image_filename
      except Exception as e:
        print(e)
      return imagess
                            
                  
      
token=os.getenv('TOKEN')
intents=discord.Intents.none()
intents.reactions = True
intents.guilds = True
intents=discord.Intents.default()
intents.message_content=True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name='cs',description='Jリーグの試合結果を返します')
async def check (interaction:discord.Interaction):
   messages= await scoreget()
   for message in messages:
      await interaction.response.defer()
      await interaction.followup.send(file=discord.File(io.BytesIO(message),filename='unko.png'))
@client.event
async def on_ready():
    await tree.sync()
    print('ログインしました')
    @tasks.loop(seconds=60)
    async def loop():
          try:
            # print(f"現在の時間: {now}, 2時間半後の時間: {twohourslater_str}")
            # now =datetime.now().strftime('%H:%M')
            channel = client.get_channel(CHANNEL_ID)
            # message=await scoreget()
            # for messages in message:  # 各試合ごとにメッセージを送信
            messages = await scoreget()  # 全試合結果を取得
            for message in messages:  # 各試合ごとにメッセージを
               if message not in sentfile:
                 await channel.send(file=discord.File(io.BytesIO(message),filename='unko.png'))
                 await asyncio.sleep(3)
                 try:
                    media = api.media_upload(filename='image.png', file=io.BytesIO(message))
                    clientx.create_tweet(media_ids=[media.media_id])
                 except Exception as e:
                    print(f"Twitter API Error: {e}")
                 sentfile.add(message)
                #  messages.remove(message)




                 await asyncio.sleep(10)
          except Exception as e:
              print(e)
          # if "11:00" == now:
          #       await check()
          #       print("check() が実行されました")
    loop.start()
keep_alive()
client.run(token)