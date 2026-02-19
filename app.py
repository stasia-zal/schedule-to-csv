import streamlit as st
import requests
from bs4 import BeautifulSoup
import csv
import io
import codecs

# -- YOUR EXISTING SCRAPING LOGIC --
def scrape_data(id, username, password, is_lecturer):
    session = requests.Session()
    session.auth = (username, password)
    type_char = 'N' if is_lecturer else 'G'
    url = f"https://planzajec.uek.krakow.pl/index.php?typ={type_char}&id={id}&okres=2"
    
    response = session.get(url)
    if response.status_code == 401:
        return None, "Login Failed: Check Credentials"
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # --- THIS IS THE MISSING PART ---
    excel_data = []  # Initialize the list here!
    
    table_rows = soup.find_all('tr')
    for row in table_rows[1:]:
        columns = row.find_all('td')
        if len(columns) >= 5:
            # Your logic to extract data from columns...
            entry = {
                "Date": columns[0].text.strip(),
                "Time": columns[1].text.strip(),
                "Subject": columns[2].text.strip(),
                "Type": columns[3].text.strip(),
                "Location": columns[4].text.strip()
            }
            excel_data.append(entry) # Add the entry to the list
            
    return excel_data, None # Now excel_data exists!

# -- STREAMLIT UI --
st.set_page_config(page_title="UEK Schedule Exporter")
st.title("🎓 UEK Schedule to Excel")

st.markdown("""
Enter your ID and choose your type to generate a downloadable Excel/CSV file.
""")

# User Inputs
user_type = st.radio("I am a:", ["Student/Group", "Lecturer"])
group_id = st.text_input("Enter ID (e.g., 188141)", placeholder="Look at your plan URL for 'id='")

if st.button("Generate Schedule"):
    # We use a 'service' account login stored in YOUR GitHub Secrets
    # so the public users don't need their own login to use the app
    username = st.secrets["UEK_LOGIN"]
    password = st.secrets["UEK_PASSWORD"]
    
    is_lecturer = True if user_type == "Lecturer" else False
    
    with st.spinner("Scraping UEK Portal..."):
        data, error = scrape_data(group_id, username, password, is_lecturer)
        
        if error:
            st.error(error)
        if data:
            # 1. Use a StringIO buffer
            output = io.StringIO()
            
            # 2. Write the CSV
            writer = csv.DictWriter(output, fieldnames=data[0].keys(), delimiter=';')
            writer.writeheader()
            writer.writerows(data)
            
            # 3. THE FIX: Encode as 'utf-8-sig' specifically for Excel
            excel_ready_data = output.getvalue().encode('utf-8-sig')

            st.download_button(
                label="📥 Download for Excel",
                data=excel_ready_data,
                file_name=f"schedule_{group_id}.csv",
                mime="text/csv"
    )
st.image("picture.png", caption="UEK Schedule Exporter", width=700)