import requests
from bs4 import BeautifulSoup
import os
import csv
from dotenv import load_dotenv

# 1. Load credentials from .env
load_dotenv()

def scrape_to_excel(id, session, is_lecturer=False):
    """Scrapes data and returns a list of dictionaries for Excel"""
    type_char = 'N' if is_lecturer else 'G'
    url = f"https://planzajec.uek.krakow.pl/index.php?typ={type_char}&id={id}&okres=2"

    response = session.get(url)
    response.raise_for_status()
    response.encoding = "utf-8"
    
    soup = BeautifulSoup(response.text, 'html.parser')
    excel_data = []
    
    table_rows = soup.find_all('tr')

    for row in table_rows[1:]:
        columns = row.find_all('td')
        if len(columns) >= 6:
            date_str = columns[0].text.strip()
            if not date_str: continue # Skip empty rows
            
            day_time_str = columns[1].text.strip()
            subject = columns[2].text.strip()
            class_type = columns[3].text.strip()
            
            # Logic for Group vs Lecturer tables
            if not is_lecturer:
                teacher = columns[4].text.strip()
                location_td = columns[5]
            else:
                location_td = columns[4]
                teacher = "N/A"

            # Extract location text or link
            link = location_td.find("a")
            location = link["href"] if link and link.get("href") else location_td.text.strip()

            # Clean up the time string (e.g., "08:00-09:30")
            time_only = day_time_str.split('(')[0].strip() if '(' in day_time_str else day_time_str

            excel_data.append({
                "Date": date_str,
                "Time": time_only,
                "Subject": subject,
                "Type": class_type,
                "Location": location,
                "Teacher": teacher
            })

    return excel_data

def run_update():
    username = os.getenv("UEK_LOGIN")
    password = os.getenv("UEK_PASSWORD")
    
    if not username or not password:
        print("Error: UEK_LOGIN or UEK_PASSWORD not set in .env")
        return

    session = requests.Session()
    session.auth = (username, password)
    
    # PUT YOUR GROUP ID HERE
    my_group_id = "252671" 
    
    print(f"Fetching data for {my_group_id}...")
    data = scrape_to_excel(my_group_id, session)

    if data:
        filename = 'uek_schedule.csv'
        # utf-8-sig makes Polish characters work in Excel
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter=';')
            writer.writeheader()
            writer.writerows(data)
        print(f"Done! Created {filename}")
    else:
        print("No data found. Check your Group ID or credentials.")

if __name__ == "__main__":
    run_update()