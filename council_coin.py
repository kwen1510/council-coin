## streamlit_app.py

# Libraries for connection
import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect

# Libraries for QR Code
from PIL import Image
import numpy as np
import cv2
import qrcode


# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)

# Perform SQL query on the Google Sheet.
# Uses st.cache to only rerun when the query changes or after 10 min.
# @st.cache(ttl=60)
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows

sheet_url = st.secrets["private_gsheets_url"]

# Get all data from the sheet
rows = run_query(f'SELECT * FROM "{sheet_url}"')

# Function to decode QR code
@st.cache
def qr_code_dec(image):
    
    decoder = cv2.QRCodeDetector()
    
    data, vertices, rectified_qr_code = decoder.detectAndDecode(image)
    
    if len(data) > 0:
        # print("Decoded Data: '{}'".format(data))
        
        rectified_image = np.uint8(rectified_qr_code)
        
        decoded_data = data
        
        rectified_image = cv2.putText(rectified_image,decoded_data,(50,350),fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale = 2,
            color = (250,225,100),thickness =  3, lineType=cv2.LINE_AA)
                
    return decoded_data

######### Generate QR Code ############

# Get colour
def colour_picker(house):

    colour_dictionary = {"BB": "green", "BW":"black", "HH":"purple", "MR":"blue", "MT":"red"}

    background_dictionary = {"BB": "white", "BW":"yellow", "HH":"white", "MR":"white", "MT":"white"}

    colour = colour_dictionary[house]

    background = background_dictionary[house]

    # print(colour)

    return colour, background

# Function to generate QR code
def generate_qr_code(studentID, colour, background):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,
        border=4,
    )
    qr.add_data(studentID)
    qr.make(fit=True)

    img = qr.make_image(fill_color=colour, back_color=background)
    img.save(f'./{studentID}.png')
    image = Image.open(f'./{studentID}.png')

    st.image(image, width=300)

    return

def create_qr_code(user):

    student_id = row.student_id
    house = user.house

    colour, background = colour_picker(house)

    generate_qr_code(student_id, colour, background)

    return

# Streamlit stuff
st.title("Griffles Feathers")
st.subheader("Key in your student ID to get your points and QR Code")
st.image("feather.png", width=200)

with st.form("Student ID Form", clear_on_submit=False):
    student_id = st.text_input("Please key in your student ID", placeholder="Student ID")
    submitted = st.form_submit_button("Generate QR Code")

    # Initialise state
    state = "none"

    if submitted:
        # Find student ID in database and return coins and house
        for row in rows:
            if student_id.lower() == row.student_id.lower():
                
                # Get total coins
                st.subheader(f"Number of Points: {round(row.number_of_coins)}")
                state = "yes"

                # Generate QR code
                qr_code = create_qr_code(row)

                break

        # If cannot find
        if state == "none":
            st.error("Cannot find user. Please check your student ID")
