import streamlit as st
import requests
from bs4 import BeautifulSoup
import io
import pandas as pd # Replaced csv and codecs with pandas

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
    
    excel_data = []
    
    table_rows = soup.find_all('tr')
    for row in table_rows[1:]:
        columns = row.find_all('td')
        
        # Student view has 6+ columns, Lecturer view has 5+ columns
        if (not is_lecturer and len(columns) >= 6) or (is_lecturer and len(columns) >= 5):
            date_str = columns[0].text.strip()
            if not date_str: continue # Skip empty rows
            
            # Logic for Group vs Lecturer tables
            if not is_lecturer:
                teacher = columns[4].text.strip()
                location = columns[5].text.strip()
            else:
                teacher = "N/A"
                location = columns[4].text.strip()
            
            entry = {
                "Date": date_str,
                "Time": columns[1].text.strip(),
                "Subject": columns[2].text.strip(),
                "Type": columns[3].text.strip(),
                "Teacher": teacher,
                "Location": location
            }
            excel_data.append(entry)
            
    return excel_data, None

# -- STREAMLIT UI --
st.set_page_config(page_title="UEK Schedule Exporter", page_icon="🎓")

# I moved your picture to the top so it acts like a nice header banner!
st.image("picture.png", caption="UEK Schedule Exporter", use_container_width=True)

st.title("🎓 UEK Schedule to Excel")

st.markdown("""
Enter your ID and choose your type to generate a downloadable Excel file (.xlsx).
""")

# User Inputs
user_type = st.radio("I am a:", ["Student/Group", "Lecturer"])
group_id = st.text_input("Enter ID (e.g., 188141)", placeholder="Look at your plan URL for 'id='")

if st.button("Generate Schedule"):
    username = st.secrets["UEK_LOGIN"]
    password = st.secrets["UEK_PASSWORD"]
    
    is_lecturer = True if user_type == "Lecturer" else False
    
    with st.spinner("Scraping UEK Portal..."):
        data, error = scrape_data(group_id, username, password, is_lecturer)
        
        if error:
            st.error(error)
        elif not data:
            st.warning("No schedule found for this ID.")
        else:
            # 1. Convert the list into a Pandas DataFrame
            df = pd.DataFrame(data)
            
            # 2. Create a memory buffer for the Excel file
            buffer = io.BytesIO()
            
            # 3. Create the true .xlsx file using openpyxl
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Schedule')
                
                # Auto-adjust column widths so it looks perfect instantly
                for column in df:
                    column_width = max(df[column].astype(str).map(len).max(), len(column))
                    col_idx = df.columns.get_loc(column)
                    writer.sheets['Schedule'].column_dimensions[chr(65 + col_idx)].width = column_width + 2
            
            st.success("Schedule successfully formatted!")
            
            # 4. Provide the Download Button
            st.download_button(
                label="📥 Download Excel File (.xlsx)",
                data=buffer.getvalue(),
                file_name=f"uek_schedule_{group_id}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")