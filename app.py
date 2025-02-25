import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import pandas as pd  
import re

GOOGLE_API_KEY = "AIzaSyBfEACHY99TLkwX9wjKzb-TGhLsECfhpGc"

# Configure the google.generativeai client with the API key
genai.configure(api_key=GOOGLE_API_KEY)

## Function to load Google Gemini Pro Vision API And get response
def get_gemini_repsonse(input, image, prompt):
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

## Initialize our streamlit app
st.set_page_config(page_title="Gemini Health App")

st.header("OCR APP")
input = st.text_input("Input Prompt: ", key="input")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
image = ""   
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

submit = st.button("Check")

input_prompt = """
You are an expert ocr auditing documents and invoices, extract all the text and format it according to the image.

ONLY CHECK IF THE INVOICES ARE VALID OR NOT , BY CHECKING THE PRESENCE OF A STAMP.
"""

## If submit button is clicked
if submit:
    image_data = input_image_setup(uploaded_file)
    response = get_gemini_repsonse(input_prompt, image_data, input)
    st.subheader("")
    st.write(response)