import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
import pandas as pd # Replaced csv and codecs with pandas

# -- YOUR EXISTING SCRAPING LOGIC --
id='21602'
username = os.getenv("UEK_LOGIN")
password = os.getenv("UEK_PASSWORD")
is_lecturer=True
session = requests.Session()
session.auth = (username, password)
type_char = 'N' if is_lecturer else 'G'
url = f"https://planzajec.uek.krakow.pl/index.php?typ={type_char}&id={id}&okres=2"

response = session.get(url)


# --- ADD THIS EXACT LINE ---
response.encoding = 'utf-8'
# ---------------------------


soup = BeautifulSoup(response.text, 'html.parser')

excel_data = []

table_rows = soup.find_all('tr')
for row in table_rows[1:]:
    columns = row.find_all('td')
    
    # Student view has 6+ columns, Lecturer view has 5+ columns
    if (not is_lecturer and len(columns) >= 6) or (is_lecturer and len(columns) >= 6):
        date_str = columns[0].text.strip()
        if not date_str: continue # Skip empty rows
        
        # Logic for Group vs Lecturer tables
        if not is_lecturer:
            teacher = columns[4].text.strip()
            location = columns[5].text.strip()
        else:
            location = columns[4].text.strip()
            group=columns[5].text.strip()
        time=columns[2].text.strip()
        day_of_week, st_en=time.split(' ')
        if "(" in time:
                time_info, duration_str = time.split("(")
                start,end=time_info.split('-')
        start=1
        end=3
        print(day_of_week)
        entry = {
            "Date": date_str,
            "Day": day_of_week,
            "Starting": start,
            "Ending": end,
            "Subject": columns[2].text.strip(),
            "Type": columns[3].text.strip(),
            "Teacher": teacher if not is_lecturer else None,
            "Location": location,
            "Group": group if is_lecturer else None
        }
        excel_data.append(entry)
        
