#==========================================
# Imports
#==========================================
import re
import base64
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from flask import Flask, flash, redirect, render_template, request, url_for, session, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from fake_useragent import UserAgent
from dotenv import load_dotenv
import os

#==========================================
# Server Configuration & Setup
#==========================================
app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")
ua = UserAgent()
dataset = pd.read_csv("dataset/quran.csv")
options = dataset["sora_name"]
dataset.set_index("sora_name", inplace=True)

#==========================================
# Rate Limiting Configuration
#==========================================
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute", "40 per hour", "200 per day"]
)

#==========================================
# Caching Definitions
#==========================================
data_cache = {}

def generate_cache_key(sora_num, aya_num):
    return f"{sora_num}-{aya_num}"

#==========================================
# Functions & Business Logic
#==========================================
def get_random_headers():
    return {
        "User-Agent": ua.random,
        "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://surahquran.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

def fetch_image_as_base64(url):
    try:
        resp = requests.get(url, headers=get_random_headers(), timeout=10)
        if resp.status_code == 200:
            encoded = base64.b64encode(resp.content).decode('utf-8')
            return f"data:image/png;base64,{encoded}"
    except Exception:
        pass
    return None

def fetch_audio_as_base64(url):
    try:
        resp = requests.get(url, headers=get_random_headers(), timeout=10)
        if resp.status_code == 200:
            encoded = base64.b64encode(resp.content).decode('utf-8')
            return f"data:audio/mpeg;base64,{encoded}"
    except Exception:
        pass
    return None

def extract_aya_data(sora_num, aya_num):
    aya_page_url = f"https://surahquran.com/aya-{aya_num}-sora-{sora_num}.html"
    tafsir_page_url = f"https://surahquran.com/aya-tafsir-{aya_num}-{sora_num}.html#saadi"
    image_url = f"https://surahquran.com/img/ayah/{sora_num}-{aya_num}.png"

    aya_text = "لم يتم العثور على النص."
    tafsir_text = "لم يتم العثور على التفسير."
    audio_url = None

    try:
        aya_resp = requests.get(aya_page_url, headers=get_random_headers(), timeout=10)
        if aya_resp.status_code == 200:
            soup = bs(aya_resp.content, "html.parser")
            sound_tag = soup.find("source", id="mp3ppl")
            if sound_tag:
                audio_url = sound_tag.get("src")
            h3_othmani = soup.find("h3", id="othmani")
            if h3_othmani:
                next_h3 = h3_othmani.find_next("h3")
                if next_h3:
                    raw = next_h3.get_text(strip=True)
                    aya_text = re.sub(r"\[.*?\]", "", raw).strip()
        else:
            aya_text = f"خطأ في الاتصال بالموقع: {aya_resp.status_code}"

        tafsir_resp = requests.get(tafsir_page_url, headers=get_random_headers(), timeout=10)
        if tafsir_resp.status_code == 200:
            soup = bs(tafsir_resp.content, "html.parser")
            h3_saadi = soup.find("h3", id="saadi")
            if h3_saadi:
                blockquote = h3_saadi.find_next("blockquote")
                if blockquote:
                    tafsir_text = blockquote.get_text(strip=True)
        else:
            tafsir_text = f"خطأ في الاتصال بصفحة التفسير: {tafsir_resp.status_code}"

    except Exception as e:
        aya_text = f"حدث خطأ أثناء جلب البيانات: {str(e)}"
        tafsir_text = f"حدث خطأ أثناء جلب التفسير: {str(e)}"

    return {
        "aya_text": aya_text,
        "tafsir_text": tafsir_text,
        "image_url": image_url,
        "audio_url": audio_url,
        "aya_page_url": aya_page_url,
        "tafsir_page_url": tafsir_page_url,
    }

#==========================================
# Routes / API Endpoints
#==========================================
@app.route("/")
def home():
    cache_key = session.get("cache_key")
    result = data_cache.get(cache_key) if cache_key else None

    if cache_key and not result:
        session.pop("cache_key", None)
        result = None

    return render_template(
        "index.html",
        options=options,
        result=result
    )

@app.route("/search", methods=["POST"])
def search():
    if request.method == "POST":
        sora_name = request.form.get("sora_name", "").strip()
        aya_num = request.form.get("aya_num", "").strip()

        if not sora_name or not aya_num:
            flash("الرجاء إدخال اسم السورة ورقم الآية.")
            return redirect(url_for("home"))

        try:
            sora_num = dataset.loc[sora_name, "sora_num"]
        except KeyError:
            flash("اسم السورة غير موجود في قاعدة البيانات.")
            return redirect(url_for("home"))

        try:
            aya_num = int(aya_num)
        except ValueError:
            flash("رقم الآية يجب أن يكون رقماً صحيحاً.")
            return redirect(url_for("home"))

        cache_key = generate_cache_key(sora_num, aya_num)

        if cache_key not in data_cache:
            raw_data = extract_aya_data(sora_num, aya_num)

            image_b64 = fetch_image_as_base64(raw_data["image_url"])
            audio_b64 = fetch_audio_as_base64(raw_data["audio_url"]) if raw_data["audio_url"] else None

            final_data = {
                "sora_name": sora_name,
                "sora_num": sora_num,
                "aya_num": aya_num,
                "aya_text": raw_data["aya_text"],
                "tafsir_text": raw_data["tafsir_text"],
                "aya_image": image_b64,
                "aya_sound": audio_b64,
            }
            data_cache[cache_key] = final_data

        session["cache_key"] = cache_key

    return redirect(url_for("home"))

@app.route("/clear", methods=['POST','GET'])
def clear():
    session.pop("cache_key", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)