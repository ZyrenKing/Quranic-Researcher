# Quranic-Researcher 📖
A smart tool to retrieve Quranic verses in Uthmani script, Al-Saadi’s Tafsir, and recitation by Sheikh Maher Al-Muaiqly. It generates ready-made images of verses for content creators, with options to copy text, download audio, and export all assets as a single ZIP file. 📖🎧
---
## Tech Stack 🛠
- Language: Python 3.10 <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="Python" width="25" height="25"/>
- Framework: Flask <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/flask/flask-original.svg" alt="Flask" width="25" height="25"/>
- Moduls: requests, pandas, BeautifulSoup, base64, random, fake_useragent, etc.
---
## Features 🚀
### Programming Advantages
  - Caching: Stores results after the first search, reducing server load and speeding up repeat responses.
  - Base64 Embedding: Embeds audio and images directly into the page, avoiding CORS issues and broken external links.
  - Smart Protection: Uses rate limiting and random user-agents to prevent the script from being blocked by the source website.
### User Advantages
  - All-in-One Page: Provides the text, Tafsir (interpretation), image, and audio together without navigating multiple sites.
  - Blazing Fast Repetition: Re-searching a previously viewed verse loads instantly due to caching.
  - Extremely Easy to Use: Only requires selecting a Surah name and entering a verse number; everything else appears automatically.
---
## Prerequisites 📋
Before starting, ensure that the following is installed on your device:
- `Python 3.10` or Latest
- `pip` for manage the Moduls
---
## Installation & Setup 💻
1. clone this is repo:
```Bash
git clone https://github.com/ZyrenKing/Quranic-Researcher
```
2. Create and activate a virtual environment:
```Bash
python -m venv venv
source venv/bin/activate  # on the Linux/macOS
```
3. Installs the required libraries:
```Bash
pip install -r requirements.txt
```
4. Project Operation:
```Bash
python app.py
```
