# Libraries for connection
import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect

# Libraries for QR Code
from PIL import Image
import numpy as np
import cv2


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
# @st.cache(ttl=600)
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


# Streamlit stuff
st.title("Points Tracker")
st.subheader("Take a screenshot of your QR code and upload it to get your points. Taking photos with the camera will not work.")


#uploading the imges
img_file_buffer = st.file_uploader("Upload an image which you want to Decode", type=[ "jpg", "jpeg",'png'])

if img_file_buffer is not None:
    image = np.array(Image.open(img_file_buffer))

    try:
        student_id = qr_code_dec(image)
        st.markdown(f"Student ID: **{student_id}**")      

    # Initialise state
    state = "none"

    # Check each row to see if student_id matches, then return the 
    for row in rows:
        if student_id == row.student_id:
            st.markdown(f"Number of Points: **{round(row.number_of_coins)}**")
            state = "yes"
            break
    # If cannot find
    if state == "none":
        st.error("Student not found. Please scan the correct QR code")

    except:
        st.error("QR code cannot be detected. Please take a screenshot of the QR code instead.")


# References
# https://medium.com/analytics-vidhya/create-a-qr-code-decoder-web-application-using-opencv-and-streamlit-b0656146e2d1
# https://docs.streamlit.io/knowledge-base/tutorials/databases/private-gsheet
