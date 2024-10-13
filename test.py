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
from discord.ext import commands, tasks
import re
from datetime import datetime, timedelta
import schedule

CHANNEL_ID = "1294151296667881483"

# 試合データを取得する関数
def check():
    global nowtime
    global driver
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.get('https://soccer.yahoo.co.jp/jleague/category/j1')

    time.sleep(3)
   
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

            # 日付と時間のパース
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

# 試合結果を取得し、Discordに送信する関数
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

    for onelink in linkss:
        res = requests.get(onelink)
        global soup
        soup = BeautifulSoup(res.text, 'html.parser')

        # 現在の時間（仮）
        nowtime = "202410111148"
        global twohourslater
        twohourslater = datetime.strptime(nowtime, '%Y%m%d%H%M') + timedelta(hours=2, minutes=30)
        print(twohourslater)
        global twohourslater_str
        twohourslater_str = twohourslater.strftime('%H:%M')
        print(nowtime)

        # 試合結果の取得
        findscorehome = soup.find_all(class_=['sc-scoreBoard__data--totalHome'])
        findscoreaway = soup.find_all(class_=['sc-scoreBoard__data--totalAway'])
        findscorepoint = soup.find_all(class_=['sc-scoreBoard__data--point'])
        findscoreteamname = soup.find_all(class_=['sc-scoreBoard__teamName'])

        home_score = findscorehome[0].text if findscorehome else 'N/A'
        away_score = findscoreaway[0].text if findscoreaway else 'N/A'
        home_team = findscoreteamname[0].text if len(findscoreteamname) > 0 else 'N/A'
        away_team = findscoreteamname[1].text if len(findscoreteamname) > 1 else 'N/A'

        result = f"{home_team} {home_score} - {away_score} {away_team}"
        print(result)
        
        return result

# スケジュールされたタスク
schedule.every().day.at("14:17").do(check)

# Discord Bot設定
token = os.getenv('TOKEN')
intents = discord.Intents.none()
intents.reactions = True
intents.guilds = True
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('ログインしました')

    @tasks.loop(seconds=60)
    async def loop():
        now = datetime.now().strftime('%H:%M')
        if twohourslater_str == now:
            channel = client.get_channel(int(CHANNEL_ID))
            score_result = await scoreget()  # 非同期に試合結果を取得
            await channel.send(score_result)

    loop.start()
    
    while True:
        schedule.run_pending()  # スケジュール処理を実行
        await asyncio.sleep(1)  # 1秒待機

client.run(token)
