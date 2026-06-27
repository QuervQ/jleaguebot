import asyncio
import hashlib
import io
import os
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

import aiohttp
import discord
import tweepy
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

BSD_BASE_URL = os.getenv("BSD_BASE_URL", "https://sports.bzzoiro.com").rstrip("/")
BSD_API_KEY = os.getenv("BSD_API_KEY")
BSD_TIMEZONE = os.getenv("BSD_TIMEZONE", "Asia/Tokyo")
BSD_LEAGUE_IDS = os.getenv("BSD_LEAGUE_IDS", "").strip()
BSD_EXTRA_LEAGUE_IDS = os.getenv("BSD_EXTRA_LEAGUE_IDS", "27").strip()
BSD_MATCH_STATUSES = os.getenv(
    "BSD_MATCH_STATUSES",
    "finished,inprogress,1st_half,halftime,2nd_half,extratime,penalties,aet",
)

CHANNEL_ID = int(os.getenv("CHANNEL_ID", "1294151296667881483"))

FONT_PATH = "ヒラギノ角ゴシック_W9.ttc"
font4 = ImageFont.truetype(FONT_PATH, 15)
font2 = ImageFont.truetype(FONT_PATH, 30)
font = ImageFont.truetype(FONT_PATH, 30)
font1 = ImageFont.truetype(FONT_PATH, 60)
font3 = ImageFont.truetype(FONT_PATH, 25)
font5 = ImageFont.truetype(FONT_PATH, 12)

CANVAS_SIZE = (1600, 900)
CENTER_X = CANVAS_SIZE[0] // 2

sentfile = set()
image_memory_cache = {}


def _create_twitter_clients():
    required = [
        "Bearertoken",
        "api_key",
        "api_keysecret",
        "accseestoken",
        "accseestokensecret",
    ]
    if not all(os.getenv(key) for key in required):
        return None, None

    clientx = tweepy.Client(
        bearer_token=os.getenv("Bearertoken"),
        consumer_key=os.getenv("api_key"),
        consumer_secret=os.getenv("api_keysecret"),
        access_token=os.getenv("accseestoken"),
        access_token_secret=os.getenv("accseestokensecret"),
    )
    auth = tweepy.OAuthHandler(os.getenv("api_key"), os.getenv("api_keysecret"))
    auth.set_access_token(os.getenv("accseestoken"), os.getenv("accseestokensecret"))
    return clientx, tweepy.API(auth)


twitter_client, twitter_api = _create_twitter_clients()


def _bsd_headers():
    if not BSD_API_KEY:
        raise RuntimeError("BSD_API_KEY が .env に設定されていません")
    return {"Authorization": f"Token {BSD_API_KEY}"}


def _today_range_utc():
    local_tz = ZoneInfo(BSD_TIMEZONE)
    today = datetime.now(local_tz).date()
    start_local = datetime.combine(today, time.min, tzinfo=local_tz)
    end_local = datetime.combine(today, time.max, tzinfo=local_tz)
    return (
        start_local.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        end_local.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
    )


def _parse_int_list(value: str):
    if not value:
        return []
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def _target_statuses():
    return [status.strip() for status in BSD_MATCH_STATUSES.split(",") if status.strip()]


def _target_league_ids():
    league_ids = _parse_int_list(BSD_LEAGUE_IDS)
    extra_ids = _parse_int_list(BSD_EXTRA_LEAGUE_IDS)
    if not league_ids:
        return [None]
    return list(dict.fromkeys([*league_ids, *extra_ids]))


async def bsd_get(session: aiohttp.ClientSession, path: str, params=None):
    async with session.get(f"{BSD_BASE_URL}{path}", headers=_bsd_headers(), params=params) as response:
        text = await response.text()
        if response.status >= 400:
            raise RuntimeError(f"BSD API error {response.status}: {text[:300]}")
        return await response.json()


def _extract_items(payload, key="results"):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        items = payload.get(key)
        if isinstance(items, list):
            return items
        events = payload.get("events")
        if isinstance(events, list):
            return events
    return []


async def fetch_target_events(session: aiohttp.ClientSession):
    date_from, date_to = _today_range_utc()
    events_by_id = {}

    for league_id in _target_league_ids():
        for status in _target_statuses():
            params = {
                "status": status,
                "date_from": date_from,
                "date_to": date_to,
                "limit": 200,
            }
            if league_id is not None:
                params["league_id"] = league_id

            payload = await bsd_get(session, "/api/v2/events/", params)
            for event in _extract_items(payload):
                events_by_id[event["id"]] = event

    return sorted(events_by_id.values(), key=lambda event: event.get("event_date") or "")


async def fetch_event_stats(session: aiohttp.ClientSession, event_id: int):
    payload = await bsd_get(session, f"/api/v2/events/{event_id}/stats/")
    return payload.get("stats") or {}


async def fetch_event_incidents(session: aiohttp.ClientSession, event_id: int):
    payload = await bsd_get(session, f"/api/v2/events/{event_id}/incidents/")
    return payload.get("incidents") or []


async def fetch_event_lineups(session: aiohttp.ClientSession, event_id: int):
    try:
        payload = await bsd_get(session, f"/api/v2/events/{event_id}/lineups/")
    except Exception as e:
        print(f"ラインナップ取得エラー: {event_id} {e}")
        return {}
    return payload.get("lineups") or {}


async def fetch_image_cached(url: str, session: aiohttp.ClientSession):
    if not url:
        return None

    if url in image_memory_cache:
        return image_memory_cache[url]

    try:
        async with session.get(url, headers=_bsd_headers()) as response:
            if response.status != 200:
                print(f"画像取得失敗: {response.status} {url}")
                return None
            data = await response.read()
    except Exception as e:
        print(f"画像取得エラー: {e}")
        return None

    image_memory_cache[url] = data
    return data


async def open_cached_image(url: str, session: aiohttp.ClientSession):
    data = await fetch_image_cached(url, session)
    if data is None:
        return None
    return Image.open(io.BytesIO(data)).convert("RGBA")


async def fetch_team_logo(session: aiohttp.ClientSession, team_id):
    if team_id is None:
        return None
    return await open_cached_image(f"{BSD_BASE_URL}/img/team/{team_id}/", session)


async def fetch_venue_image(session: aiohttp.ClientSession, venue_id):
    if venue_id is None:
        return None
    return await open_cached_image(f"{BSD_BASE_URL}/img/venue/{venue_id}/", session)


async def fetch_player_image(session: aiohttp.ClientSession, player_id):
    if player_id is None:
        return None
    return await open_cached_image(f"{BSD_BASE_URL}/img/player/{player_id}/", session)


async def fetch_lineup_player_images(session: aiohttp.ClientSession, lineups):
    players = []
    for side in ("home", "away"):
        lineup = lineups.get(side) or {}
        players.extend(lineup.get("players") or [])

    tasks = {
        player.get("id"): fetch_player_image(session, player.get("id"))
        for player in players
        if player.get("id") is not None
    }
    if not tasks:
        return {}

    images = await asyncio.gather(*tasks.values())
    return dict(zip(tasks.keys(), images))


def _value(data, key, suffix="", default="-"):
    value = data.get(key)
    if value is None:
        return default
    return f"{value}{suffix}"


def _pass_text(data):
    passes = data.get("passes")
    accurate = data.get("accurate_passes")
    pct = data.get("pass_accuracy_pct")
    if passes is None:
        return "-"

    if accurate is not None and pct is not None:
        return f"{accurate}/{passes}\n{pct:.0f}%"
    if accurate is not None:
        return f"{accurate}/{passes}"
    return str(passes)


def _count_cards(incidents, side: str, card_type: str):
    is_home = side == "home"
    total = 0
    for incident in incidents:
        if incident.get("type") != "card" or incident.get("is_home") is not is_home:
            continue
        if incident.get("card_type") == card_type:
            total += 1
    return total


def _stat_rows(stats, incidents):
    home = stats.get("home") or {}
    away = stats.get("away") or {}
    home_yellow = home.get("yellow_cards")
    away_yellow = away.get("yellow_cards")
    home_red = home.get("red_cards")
    away_red = away.get("red_cards")
    if home_yellow is None:
        home_yellow = _count_cards(incidents, "home", "yellow")
    if away_yellow is None:
        away_yellow = _count_cards(incidents, "away", "yellow")
    if home_red is None:
        home_red = _count_cards(incidents, "home", "red")
    if away_red is None:
        away_red = _count_cards(incidents, "away", "red")

    return [
        (_value(home, "ball_possession", "%"), "ボール支配率", _value(away, "ball_possession", "%")),
        (_value(home, "total_shots"), "シュート", _value(away, "total_shots")),
        (_value(home, "shots_on_target"), "枠内シュート", _value(away, "shots_on_target")),
        (_value(home, "distance_covered"), "走行距離", _value(away, "distance_covered")),
        (_value(home, "sprints"), "スプリント", _value(away, "sprints")),
        (_pass_text(home), "パス（成功率）", _pass_text(away)),
        (_value(home, "offsides"), "オフサイド", _value(away, "offsides")),
        (_value(home, "free_kicks"), "フリーキック", _value(away, "free_kicks")),
        (_value(home, "corner_kicks"), "コーナーキック", _value(away, "corner_kicks")),
        (_value(home, "penalty_kicks"), "ペナルティキック", _value(away, "penalty_kicks")),
        (str(home_yellow), "警告", str(away_yellow)),
        (str(home_red), "退場", str(away_red)),
    ]


def _score(value):
    return "-" if value is None else str(value)


def _second_half_score(total, halftime):
    if total is None or halftime is None:
        return "-"
    return str(total - halftime)


def _paste_logo(canvas, logo, box):
    if logo is None:
        return
    logo = logo.copy()
    logo.thumbnail((120, 120))
    x, y, w, h = box
    pos = (x + (w - logo.width) // 2, y + (h - logo.height) // 2)
    canvas.paste(logo, pos, logo)


def _cover_image(source, size):
    width, height = size
    scale = max(width / source.width, height / source.height)
    resized = source.resize((int(source.width * scale), int(source.height * scale)))
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def _make_background(venue_image):
    template = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 255))
    if venue_image is None:
        return template

    img = _cover_image(venue_image.convert("RGBA"), CANVAS_SIZE)
    shade = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 185))
    return Image.alpha_composite(img, shade)


def _draw_center(draw, x, y, text, text_font, fill="white", stroke_width=3):
    text = str(text)
    if "\n" in text:
        draw.multiline_text(
            (x, y),
            text,
            fill=fill,
            font=text_font,
            anchor="mm",
            align="center",
            spacing=0,
            stroke_width=stroke_width,
            stroke_fill="black",
        )
        return

    draw.text((x, y), text, fill=fill, font=text_font, anchor="mm", stroke_width=stroke_width, stroke_fill="black")


def _draw_left(draw, x, y, text, text_font, fill="white", stroke_width=3):
    draw.text(
        (x, y),
        str(text),
        fill=fill,
        font=text_font,
        anchor="lm",
        stroke_width=stroke_width,
        stroke_fill="black",
    )


def _draw_fit_center(draw, x, y, text, max_width, fonts, fill="white", stroke_width=3):
    text = str(text)
    for candidate in fonts:
        bbox = draw.textbbox((0, 0), text, font=candidate, stroke_width=stroke_width)
        if bbox[2] - bbox[0] <= max_width:
            _draw_center(draw, x, y, text, candidate, fill=fill, stroke_width=stroke_width)
            return
    _draw_center(draw, x, y, text, fonts[-1], fill=fill, stroke_width=stroke_width)


def _circle_image(source, size):
    if source is None:
        return None
    img = _cover_image(source.convert("RGBA"), (size, size))
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size - 1, size - 1), fill=255)
    output = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    output.paste(img, (0, 0), mask)
    return output


def _draw_pitch(draw, box, side):
    x, y, w, h = box
    line = (255, 255, 255, 120)
    fill = (16, 96, 52, 88)
    draw.rounded_rectangle((x, y, x + w, y + h), radius=18, fill=fill, outline=line, width=3)
    draw.line((x + w, y, x + w, y + h), fill=line, width=3)
    if side == "home":
        draw.rectangle((x, y + h * 0.28, x + w * 0.18, y + h * 0.72), outline=line, width=2)
        draw.rectangle((x, y + h * 0.40, x + w * 0.07, y + h * 0.60), outline=line, width=2)
        draw.arc((x + w * 0.06, y + h * 0.37, x + w * 0.30, y + h * 0.63), -65, 65, fill=line, width=2)
        draw.line((x + w - 1, y, x + w - 1, y + h), fill=line, width=2)
    else:
        draw.rectangle((x + w * 0.82, y + h * 0.28, x + w, y + h * 0.72), outline=line, width=2)
        draw.rectangle((x + w * 0.93, y + h * 0.40, x + w, y + h * 0.60), outline=line, width=2)
        draw.arc((x + w * 0.70, y + h * 0.37, x + w * 0.94, y + h * 0.63), 115, 245, fill=line, width=2)
        draw.line((x, y, x, y + h), fill=line, width=2)


def _formation_rows(lineup):
    formation = (lineup.get("formation") or "").replace(" ", "")
    parts = [int(part) for part in formation.split("-") if part.isdigit()]
    players = list(lineup.get("players") or [])

    if not players:
        return []

    goalkeeper = players[:1]
    field_players = players[1:]
    rows = [goalkeeper]
    start = 0
    for count in parts:
        rows.append(field_players[start:start + count])
        start += count
    if start < len(field_players):
        rows.append(field_players[start:])
    return rows


def _player_initials(player):
    name = (player.get("short_name") or player.get("name") or "?").strip()
    parts = name.replace(".", " ").split()
    if not parts:
        return "?"
    return "".join(part[0] for part in parts[:2]).upper()


def _draw_player(draw, img, player, cx, cy, player_images):
    size = 42
    player_img = _circle_image(player_images.get(player.get("id")), size)
    left = int(cx - size / 2)
    top = int(cy - size / 2)
    if player_img is not None:
        img.paste(player_img, (left, top), player_img)
    else:
        draw.ellipse((left, top, left + size, top + size), fill=(24, 24, 24, 230), outline="white", width=2)
        _draw_center(draw, cx, cy, _player_initials(player), font5, stroke_width=1)

    number = player.get("jersey_number")
    if number is not None:
        draw.ellipse((left - 4, top - 4, left + 14, top + 14), fill=(0, 0, 0, 220), outline="white", width=1)
        _draw_center(draw, left + 5, top + 5, number, font5, stroke_width=1)

    name = (player.get("short_name") or player.get("name") or "-").strip()
    _draw_fit_center(draw, cx, cy + 32, name, 92, [font4, font5], stroke_width=2)


def _draw_lineup_half(draw, img, box, lineup, side, player_images):
    _draw_pitch(draw, box, side)
    x, y, w, h = box
    team_name = lineup.get("team_name") or "-"
    formation = lineup.get("formation") or "-"
    title_y = y - 34
    _draw_fit_center(draw, x + w / 2, title_y, f"{team_name}  {formation}", w - 20, [font3, font4, font5])

    rows = _formation_rows(lineup)
    if not rows:
        _draw_center(draw, x + w / 2, y + h / 2, "LINEUP N/A", font3)
        return

    columns = len(rows)
    for col, row in enumerate(rows):
        if side == "home":
            cx = x + 52 + col * ((w - 104) / max(columns - 1, 1))
        else:
            cx = x + w - 52 - col * ((w - 104) / max(columns - 1, 1))

        gap = h / (len(row) + 1)
        for index, player in enumerate(row):
            cy = y + gap * (index + 1)
            _draw_player(draw, img, player, cx, cy, player_images)


def build_score_image(event, stats, incidents, home_logo, away_logo, venue_image=None, lineups=None, player_images=None):
    img = _make_background(venue_image)
    draw = ImageDraw.Draw(img)
    lineups = lineups or {}
    player_images = player_images or {}

    home_score = _score(event.get("home_score"))
    away_score = _score(event.get("away_score"))
    home_ht = event.get("home_score_ht")
    away_ht = event.get("away_score_ht")
    home_total = event.get("home_score")
    away_total = event.get("away_score")

    home_name = event.get("home_team") or (lineups.get("home") or {}).get("team_name") or "-"
    away_name = event.get("away_team") or (lineups.get("away") or {}).get("team_name") or "-"

    _draw_fit_center(draw, 360, 55, home_name, 440, [font3, font4, font5])
    _draw_fit_center(draw, 1240, 55, away_name, 440, [font3, font4, font5])

    _draw_lineup_half(draw, img, (30, 145, 500, 700), lineups.get("home") or {"team_name": home_name}, "home", player_images)
    _draw_lineup_half(draw, img, (1070, 145, 500, 700), lineups.get("away") or {"team_name": away_name}, "away", player_images)

    _draw_center(draw, 720, 52, _score(home_ht), font)
    _draw_center(draw, CENTER_X, 52, "前半", font)
    _draw_center(draw, 880, 52, _score(away_ht), font)
    _draw_center(draw, 720, 92, _second_half_score(home_total, home_ht), font)
    _draw_center(draw, CENTER_X, 92, "後半", font)
    _draw_center(draw, 880, 92, _second_half_score(away_total, away_ht), font)
    _draw_center(draw, 690, 165, home_score, font1)
    _draw_center(draw, 910, 165, away_score, font1)

    rows = _stat_rows(stats, incidents)
    for index, (home_value, label, away_value) in enumerate(rows):
        y = 240 + index * 44
        label_font = font3
        value_font = font3 if label in {"走行距離", "パス（成功率）"} and home_value != "-" else font3
        away_font = font3 if label in {"走行距離", "パス（成功率）"} and away_value != "-" else font3
        if label == "パス（成功率）":
            home_x = 655
            label_x = CENTER_X
            away_x = 945
            value_font = font4
            away_font = font4
        else:
            home_x = 670
            label_x = CENTER_X
            away_x = 930

        _draw_center(draw, home_x, y, home_value, value_font)
        _draw_center(draw, label_x, y, label, label_font)
        _draw_center(draw, away_x, y, away_value, away_font)

    _draw_left(draw, 24, 875, "Create By @Quervo9e", font)

    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    _paste_logo(overlay, home_logo, (555, 20, 110, 110))
    _paste_logo(overlay, away_logo, (935, 20, 110, 110))

    result = Image.alpha_composite(img, overlay)
    buffer = io.BytesIO()
    result.save(buffer, format="png")
    return buffer.getvalue()


async def scoreget():
    images = []
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        events = await fetch_target_events(session)
        for event in events:
            try:
                event_id = event["id"]
                stats, incidents, home_logo, away_logo, venue_image, lineups = await asyncio.gather(
                    fetch_event_stats(session, event_id),
                    fetch_event_incidents(session, event_id),
                    fetch_team_logo(session, event.get("home_team_id")),
                    fetch_team_logo(session, event.get("away_team_id")),
                    fetch_venue_image(session, event.get("venue_id")),
                    fetch_event_lineups(session, event_id),
                )
                player_images = await fetch_lineup_player_images(session, lineups)
                images.append(
                    build_score_image(
                        event,
                        stats,
                        incidents,
                        home_logo,
                        away_logo,
                        venue_image,
                        lineups,
                        player_images,
                    )
                )
            except Exception as e:
                print(f"試合データの処理エラー: {event.get('id')} {e}")
    return images


token = os.getenv("TOKEN")
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(name="cs", description="世界中のサッカー試合情報を返します")
async def check(interaction: discord.Interaction):
    await interaction.response.defer()
    messages = await scoreget()
    if not messages:
        await interaction.followup.send("今日の対象試合はまだありません。")
        return

    for message in messages:
        await interaction.followup.send(file=discord.File(io.BytesIO(message), filename="football.png"))


@client.event
async def on_ready():
    await tree.sync()
    print("ログインしました")
    if not loop.is_running():
        loop.start()


@tasks.loop(seconds=60)
async def loop():
    try:
        channel = client.get_channel(CHANNEL_ID)
        if channel is None:
            print(f"チャンネルが見つかりません: {CHANNEL_ID}")
            return

        messages = await scoreget()
        for message in messages:
            message_key = hashlib.md5(message).hexdigest()
            if message_key in sentfile:
                continue

            await channel.send(file=discord.File(io.BytesIO(message), filename="football.png"))
            sentfile.add(message_key)
            await asyncio.sleep(3)

            if twitter_client and twitter_api:
                try:
                    media = twitter_api.media_upload(filename="image.png", file=io.BytesIO(message))
                    twitter_client.create_tweet(media_ids=[media.media_id])
                except Exception as e:
                    print(f"Twitter API Error: {e}")

            await asyncio.sleep(10)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    client.run(token)
