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


CHANNEL_ID =1294151296667881483
twohourslater_str = None
url=""
async def check():
    await asyncio.sleep(3)
    global nowtime
    global driver
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.get('https://soccer.yahoo.co.jp/jleague/category/j1')
  
    
    await asyncio.sleep(3)
    linkss = []
    try:
        hrefs = driver.find_elements(By.CLASS_NAME, "sc-tableGame__score--hasLink")
        for link in hrefs:
            href = link.get_attribute('href')
            if href:
                linkss.append(href)
            else:
                print("hrefがない")
        print(linkss)
    except:
        print('そもそもない')

    for onelink in linkss:
        res = requests.get(onelink)
        global soup
        soup = BeautifulSoup(res.text, 'html.parser')


        findscore = soup.find_all(class_=['sc-scoreBoard__time'])
        for p in findscore:
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
                nowtime="202410120649"#仮
                global twohourslater
                twohourslater = datetime.strptime(nowtime, '%Y%m%d%H%M') + timedelta(hours=2, minutes=30)
                print(twohourslater)
                global twohourslater_str
                twohourslater_str = twohourslater.strftime('%H:%M')
                print(nowtime)



        # target = '/'
        # idx = time_str.find(target) 
        # month = time_str[:idx]

        # target = '/'
        # idx = time_str.find(target)
        # day = time_str[idx + 1]

        # sep = '）'
        # t = time_str.split(sep)  # 半角空白文字で文字列を分割
        # matchtime = t[1]  # 日付はインデックス0に含まれている
async def scoreget():
    linkss = []
    driver.get('https://soccer.yahoo.co.jp/jleague/category/j1')
    try:
        hrefs = driver.find_elements(By.CLASS_NAME, "sc-tableGame__score--hasLink")
        for link in hrefs:
            href = link.get_attribute('href')
            if href:
                linkss.append(href)
            else:
                print("hrefがない")
        print(linkss)
    except:
        print('そもそもない')

    result_messages = []  # 結果を格納するリスト
    for onelink in linkss:
        res = requests.get(onelink)
        
        global soup
        soup = BeautifulSoup(res.text, 'html.parser')
        cnvrtdate=html.fromstring(str(soup))


        # 現在の時間（仮）
        global twohourslater
        twohourslater = datetime.strptime(nowtime, '%Y%m%d%H%M') + timedelta(hours=2, minutes=30)
        print(twohourslater)
        global twohourslater_str
        twohourslater_str = twohourslater.strftime('%H:%M')
        print(twohourslater)
        print(twohourslater_str)
        print(nowtime)

        # 試合結果の取得
        findscorehome = soup.find_all(class_=['sc-scoreBoard__data--totalHome'])
        findscoreaway = soup.find_all(class_=['sc-scoreBoard__data--totalAway'])
        findscoreteamname = soup.find_all(class_=['sc-scoreBoard__teamName'])
        global findstats
        # findstats=soup.find_all("td",class_=['sc-tableVersus__data--away'])
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
        print(f"テスト{homestats1}")
        homestats6.replace('\n', '')
        awaystats6.replace('\n','')
        result_message = f"{home_team} {home_score} - {away_score} {away_team}\n{homestats1+'ボール支配率'+awaystats1}\n{homestats2+'シュート'+awaystats2}\n{homestats3+'枠内シュート'+awaystats3}\n{homestats4+'走行距離'+awaystats4}\n{homestats5+'スプリント'+awaystats5}\n{homestats6+'パス（成功率）' + awaystats6}\n{homestats7+'オフサイド'+awaystats7}\n{homestats8+'フリーキック'+awaystats8}\n{homestats9+'コーナーキック'+awaystats9}\n{homestats10+'ペナルティキック'+awaystats10}\n{'ホームイエローカード'+homestats11}\n{'ホームレッドカード'+homestats12}\n{'アウェイイエローカード'+awaystats11}\n{'アウェイレッドカード'+awaystats12}\n"

        # statsmassagehome=f"homeSTATS\n{home_stats1}{home_stats2}{home_stats3}{home_stats4}{home_stats5}{home_stats6}{home_stats7}{home_stats8}{home_stats9}{home_stats10}{home_stats11}"
        # statsmassageaway=f"awaySTATS\n{away_stats1}{away_stats2}{away_stats3}{away_stats4}{away_stats5}{away_stats6}{away_stats7}{away_stats8}{away_stats9}{away_stats10}{away_stats11}"
        
        result_messages.append(result_message)  
        # result_messages.append(statsmassagehome)

    if result_messages:
        return "\n".join(result_messages)  
    return "試合結果はありません。" 
      
# scoreget()





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
    await check()
    print(twohourslater_str)
    @tasks.loop(seconds=30)
    async def loop():
        global now
        
        # print(f"現在の時間: {now}, 2時間半後の時間: {twohourslater_str}")


        while True:
          now =datetime.now().strftime('%H:%M')
          print(twohourslater_str)
          print(f"現在の時間: {now}, 2時間半後の時間: {twohourslater_str}")
          if twohourslater_str is not None:  # twohourslater_str が None でないことを確認
           
            if twohourslater_str == now:
                channel = client.get_channel(CHANNEL_ID)
                score_result = await scoreget() 
                await channel.send(score_result)

          if "09:17" == now:
                await check()
                print("check() が実行されました")
          # if twohourslater_str==now:
          #     channel = client.get_channel(CHANNEL_ID)
          #     score_result = await scoreget() 
          #     await channel.send(score_result)
          # if "08:55"==now:
          #     await check()
          #     print("check() が実行されました")
          await asyncio.sleep(60)
    loop.start()
      


    # schedule.every().day.at("14:50").do(check)
    # while True:
    #   schedule.run_pending()  # 3. 指定時間が来てたら実行、まだなら何もしない
      
    #   await asyncio.sleep(1)  # 待ち


client.run(token)
# schedule.every().day.at(twohourslater_str).do(scores)#仮



