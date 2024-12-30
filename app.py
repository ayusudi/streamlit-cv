import streamlit as st
import pandas as pd 
import os 
from io import BytesIO

from langchain_mistralai.chat_models import ChatMistralAI
from pydantic import BaseModel, Field
from langchain_community.document_loaders import PyPDFLoader
from typing import List
import ssl

# Streamlit app setup
st.title("CV Data Extraction with AI")

# Upload PDF via Streamlit file uploader
uploaded_file = st.file_uploader("Upload a CV (PDF format)", type=["pdf"])

if uploaded_file is not None:
    # Display OpenSSL version
    st.write("OpenSSL Version:", ssl.OPENSSL_VERSION)

    # Save the uploaded file to a temporary path
    with open("uploaded_cv.pdf", "wb") as f:
        f.write(uploaded_file.read())
    
    # Load and process the PDF
    loader = PyPDFLoader("uploaded_cv.pdf")
    pages = loader.load_and_split()

    # Combine text content from all pages
    text = " ".join([page.page_content for page in pages])

    # Define CV Data Extraction model schema
    class CVDataExtraction(BaseModel):
        full_name: str = Field(description="The full name of the candidate, used as their username in the system.")
        email: str = Field(description="The candidate's email address for identification and communication purposes.")
        job_titles: str = Field(description="A summary of the candidate's current or most recent job titles.")
        promotion_years: int = Field(description="The year the candidate started their professional career.")
        profile: str = Field(description="A brief overview of the candidate's professional profile, including their key attributes and expertise.")
        skills: List[str] = Field(description="A list of the candidate's soft and technical skills, showcasing their capabilities.")
        professional_experiences: List[str] = Field(description="Detailed information about the candidate's professional work experiences, including roles, responsibilities, and achievements.")
        educations: List[str] = Field(description="Educational qualifications of the candidate, including degrees, institutions, and graduation years.")
        publications: List[str] = Field(description="Any publications authored or co-authored by the candidate, such as articles, papers, or books.")
        distinctions: List[str] = Field(description="Awards, honors, or recognitions received by the candidate throughout their career or education.")
        certifications: List[str] = Field(description="Professional certifications achieved by the candidate, indicating their specialized knowledge and qualifications.")

    # Initialize the model
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
      st.error("API key for Mistral AI is not set. Please set the MISTRAL_API_KEY environment variable.")
    model = ChatMistralAI(api_key=api_key, model='mistral-large-latest')

    # Use the structured output model
    structured_llm = model.with_structured_output(CVDataExtraction)

    # Extract data using the model
    try:
        extracted_data = structured_llm.invoke(text)
        st.write("Extracted CV Data:")
        st.json(extracted_data.dict())
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Please upload a PDF file to extract CV data.")
