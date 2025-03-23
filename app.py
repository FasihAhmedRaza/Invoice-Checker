import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import fitz  # PyMuPDF

GOOGLE_API_KEY = "AIzaSyBfEACHY99TLkwX9wjKzb-TGhLsECfhpGc"

# Configure the Google Generative AI client
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize session state for responses
if "responses" not in st.session_state:
    st.session_state.responses = []

# Function to get Gemini API response
def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, image[0], prompt])
    return response.text

# Function to process uploaded image
def input_image_setup(uploaded_file):
    if uploaded_file:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{"mime_type": uploaded_file.type, "data": bytes_data}]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Function to extract images from a PDF
def pdf_to_images(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    images = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.open(BytesIO(pix.tobytes()))
        images.append(img)
    return images


import streamlit as st

# Set custom page title and favicon
st.set_page_config(page_title="Invoice Check", page_icon="logo.jpeg")

# Hide Streamlit's default logo and add your custom logo
st.markdown(
    """
    <style>
        /* Hide the default Streamlit menu and watermark */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* Custom logo placement */
        .custom-logo {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)




col1, col2 = st.columns([1, 5])  # Adjust the ratio as needed

with col1:
    st.image("logo.jpeg", width=100)  # Adjust width as needed

with col2:
    st.header("Invoice Check APP")



# Dropdown for file type selection
file_type = st.selectbox("Select file type:", ["Image", "PDF"])

# File uploader based on selection
if file_type == "Image":
    uploaded_files = st.file_uploader(
        "Upload up to 5 images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True
    )
    if uploaded_files and len(uploaded_files) > 5:
        st.error("You can upload a maximum of 5 images.")
        uploaded_files = uploaded_files[:5]  # Limit to 5 images
elif file_type == "PDF":
    uploaded_file = st.file_uploader(
        "Upload a PDF file...", type=["pdf"]
    )

input_prompt = """
You are an expert ocr auditing documents and invoices, extract all the text and format it according to the image.

ONLY CHECK IF THE INVOICES ARE VALID OR NOT , BY CHECKING THE PRESENCE OF A STAMP, INVOICE NO, if invoice no is not present then it invalid as well .

THE INVOICE SHOULD BE ONLY FROM 'AJMAN MANICIPALITY', 'Darwish Engineering' or 'AIMSGROUP'

if (company = ajman manicipality or darwish engineering or AIMSGROUP ) && (invoice number=true) && (stamp=true)
    then invoice is valid

else not valid.

Return only the name of the company if present,the name of the sender(company name is sender) and reciever if present,  the invoice number if present, total amount with correct or incorrect calculation status and taxes if any,  and VALID OR NOT VALID. write in tabular form.
VERIFY THE TOTAL AMOUNT IF IT IS CORRECTLY CALCULATED, AND RETURN CORRECT, IF IT CORRECTLY CALCULATED ALONG WITH THE AMOUNT. 

do not write anything else provide only the table!.
"""
# Submit button
if st.button("Check"):
    new_responses = []  # Temporary storage for new responses

    if file_type == "Image" and uploaded_files:
        for idx, uploaded_file in enumerate(uploaded_files):
            image = Image.open(uploaded_file)
            st.image(image, caption=f"Uploaded Image {idx+1}.", width=500)

            image_data = input_image_setup(uploaded_file)
            response = get_gemini_response(input_prompt, image_data, "hi")

            # Display response immediately after the image
            st.subheader(f"Response for Image {idx+1}")
            st.write(response)

            # Store response
            new_responses.append({"type": f"Image {idx+1}", "response": response})

    elif file_type == "PDF" and uploaded_file:
        images = pdf_to_images(uploaded_file)
        for i, img in enumerate(images):
            st.image(img, caption=f"Page {i+1} of PDF", width=500)

            
            # Convert image to bytes for Gemini API
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            image_data = [{"mime_type": "image/png", "data": img_byte_arr}]
            response = get_gemini_response(input_prompt, image_data, "hi")

            # Display response immediately after each page
            st.subheader(f"Response for Page {i+1}")
            st.write(response)

            # Store response
            new_responses.append({"type": f"PDF - Page {i+1}", "response": response})

    # Append new responses to session state
    st.session_state.responses.extend(new_responses)



# Display all previous responses at the end
if st.session_state.responses:
    st.subheader("History")
    for idx, res in enumerate(st.session_state.responses):
        st.markdown(f"### {res['type']}")
        st.write(res['response'])

