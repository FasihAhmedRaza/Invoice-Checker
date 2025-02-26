import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import fitz  # PyMuPDF

GOOGLE_API_KEY = "AIzaSyBfEACHY99TLkwX9wjKzb-TGhLsECfhpGc"

# Configure the google.generativeai client with the API key
genai.configure(api_key=GOOGLE_API_KEY)

## Function to load Google Gemini Pro Vision API And get response
def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, image[0], prompt])
    return response.text

def input_image_setup(uploaded_file):
    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

def pdf_to_images(pdf_file):
    # Open the PDF file
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    images = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.open(BytesIO(pix.tobytes()))
        images.append(img)
    return images

## Initialize our streamlit app
st.set_page_config(page_title="Invoice App")

st.header("Invoice verification APP")

# Add a dropdown to select file type
file_type = st.selectbox("Select file type:", ["Image", "PDF"])

# File uploader based on selected file type
if file_type == "Image":
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
elif file_type == "PDF":
    uploaded_file = st.file_uploader("Choose a PDF...", type=["pdf"])

input = st.text_input("Provide additional guidance (optional): ", key="input")
submit = st.button("Check")

input_prompt = """
You are an expert ocr auditing documents and invoices, extract all the text and format it according to the image.

ONLY CHECK IF THE INVOICES ARE VALID OR NOT , BY CHECKING THE PRESENCE OF A STAMP.

Return single word as VALID OR INVALID.
"""

## If submit button is clicked
if submit and uploaded_file is not None:
    if file_type == "Image":
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)
        image_data = input_image_setup(uploaded_file)
        response = get_gemini_response(input_prompt, image_data, input)
        st.subheader("Response")
        st.write(response)
    elif file_type == "PDF":
        images = pdf_to_images(uploaded_file)
        for i, img in enumerate(images):
            st.image(img, caption=f"Page {i+1} of PDF", use_column_width=True)
            # Convert the image to bytes for Gemini API
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            image_data = [{"mime_type": "image/png", "data": img_byte_arr}]
            response = get_gemini_response(input_prompt, image_data, input)
            st.subheader(f"Response for Page {i+1}")
            st.write(response)
