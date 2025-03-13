
import streamlit as st
import openai
import os
import fitz  # PyMuPDF
import pdfplumber
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# --- Load API Key Securely from .env ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("⚠️ OpenAI API key is missing! Set the API key in a `.env` file.")
    st.stop()

# --- Initialize OpenAI Client ---
client = openai.OpenAI(api_key=OPENAI_API_KEY)


st.set_page_config(
    page_title="💰 Financial Advisory Assistant",
    page_icon="📊",
    layout="wide"
)

# --- Sidebar for Navigation & Options ---
with st.sidebar:
    st.image("https://img.icons8.com/external-flaticons-flat-flat-icons/64/000000/external-finance-fintech-flaticons-flat-flat-icons-5.png", width=100)
    st.title("💼 Financial Advisory Assistant")
    st.subheader("Helping you with financial insights!")
    st.divider()

    # Theme Toggle
    theme = st.radio("🌗 Select Theme:", ["Light Mode 🌞", "Dark Mode 🌙"])

    st.divider()
    st.markdown(
        """
        📊 **Features**:  
        - AI-powered **Financial Advice**  
        - **PDF Upload & Analysis**  
        - **Tax Form Assistance**  
        - **Redact Sensitive Data**  
        - **Secure & Private**
        """
    )
    st.divider()


# --- Apply Custom Styling Based on Theme ---
is_dark = theme == "Dark Mode 🌙"
text_color = "#FFFFFF" if is_dark else "#000000"
bg_color = "#1E1E1E" if is_dark else "#F5F5F5"
button_color = "#FF4B4B" if is_dark else "#008080"
button_text_color = "#FFFFFF"
checkbox_text_color = "#FFFFFF" if is_dark else "#000000"

custom_css = f"""
    <style>
        .stApp {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
        }}
        .stTextInput, .stFileUploader, .stTextArea {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
        }}
        .stButton>button {{
            background-color: {button_color} !important;
            color: {button_text_color} !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            padding: 8px 15px !important;
        }}
        .stMarkdown, .stTextArea, .stSuccess {{
            color: {text_color} !important;
        }}
        label, div[data-testid="stCheckbox"] > label {{
            color: {checkbox_text_color} !important;
            font-weight: bold;
        }}
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# --- Function to Query GPT Model ---
def query_finetuned_gpt(prompt):
    response = client.chat.completions.create(
        model="ft:gpt-4o-mini-2024-07-18:personal:cust-support-ft:B61VF7hG",
        messages=[
            {"role": "system", "content": "You are a financial advisory assistant helping users with financial analysis and tax planning."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content

# --- Function to Extract Text from PDFs ---
def extract_text_from_pdf(uploaded_pdf):
    reader = PdfReader(uploaded_pdf)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# --- Redact Sensitive Data Function ---
def redact_sensitive_info(text):
    redacted_text = text.replace("SSN", "[REDACTED]").replace("Account Number", "[REDACTED]")  # Customize as needed
    return redacted_text

# --- Main Application Title ---
st.title("💰 AI-Powered Financial Advisory Assistant")

# --- User Query Input with Button ---
st.subheader("📢 Ask AI About Your Finances")
user_query = st.text_input(
    "Ask me anything related to finance, investments, or tax planning:",
    placeholder="E.g., What are some good investment strategies?"
)

if st.button("🔍 Ask AI"):
    if user_query:
        with st.spinner("🤖 Thinking..."):
            response = query_finetuned_gpt(user_query)
        st.success("✅ Response Received")
        st.markdown(f"**🤖 AI Advisor:** <span style='color: {text_color};'>{response}</span>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Please enter a question before clicking the button.")

st.divider()

# --- File Uploaders ---
st.subheader("📤 Upload Your Financial Documents")
col1, col2 = st.columns(2)

with col1:
    payslip = st.file_uploader("📄 Upload Your Payslip (PDF)", type=["pdf"])
with col2:
    tax_form = st.file_uploader("📜 Upload Your Tax Form (PDF)", type=["pdf"])

# --- Toggle Options (Now Clearly Visible in Light Mode) ---
retain_data = st.checkbox("🔄 Retain Data for Future Queries", key="retain", help="Keep extracted data for future analysis.")
redact_data = st.checkbox("🛑 Redact Sensitive Information", key="redact", help="Mask sensitive data before analysis.")

extracted_text = ""

if payslip or tax_form:
    st.success("✅ File(s) Uploaded Successfully!")

    # Extract text from both documents
    with st.spinner("📄 Extracting text from documents..."):
        if payslip:
            payslip_text = extract_text_from_pdf(payslip)
            if redact_data:
                payslip_text = redact_sensitive_info(payslip_text)
            extracted_text += f"Payslip:\n{payslip_text[:1000]}\n\n"

        if tax_form:
            tax_form_text = extract_text_from_pdf(tax_form)
            if redact_data:
                tax_form_text = redact_sensitive_info(tax_form_text)
            extracted_text += f"Tax Form:\n{tax_form_text[:1000]}\n\n"

    # Display Extracted Text Preview
    st.subheader("📄 Extracted Document Text (Preview)")
    st.text_area("📜 Document Data", extracted_text[:2000], height=250)

    # --- Analyze Document Button ---
    if st.button("📊 Analyze Financial Document"):
        if extracted_text:
            with st.spinner("🤖 Analyzing..."):
                analysis = query_finetuned_gpt(f"Analyze this financial document and provide insights:\n\n{extracted_text[:2000]}")
            st.success("✅ Analysis Completed")
            st.markdown("### 📊 AI-Powered Financial Insights:")
            st.text_area("📋 AI Analysis", analysis, height=300)
        else:
            st.warning("⚠️ No text extracted from the document.")

    # --- AI Assistance for Tax Form Filling ---
    if payslip and tax_form and st.button("📝 Assist in Filling Tax Form"):
        with st.spinner("🤖 Generating tax form suggestions..."):
            analysis_prompt = f"""
            You are an expert tax advisor. A user has provided their payslip details below:
            {payslip_text}

            They also uploaded an empty tax form. Please analyze both and guide them step-by-step on:
            - What values to enter in each field
            - Any missing information they need to fill in
            - Suggestions for tax savings

            Provide a structured, easy-to-follow guide.
            """
            tax_advice = query_finetuned_gpt(analysis_prompt)

        st.success("✅ AI Tax Form Assistance Completed!")
        st.markdown("### 📊 AI-Powered Tax Form Guidance:")
        st.text_area("📋 Suggested Tax Form Entries", tax_advice, height=300)

    # --- Forget Data If Not Retaining ---
    if not retain_data:
        payslip_text = ""
        tax_form_text = ""
        st.warning("🔒 Data is not stored for future use. AI responses will not be retained.")

# --- Footer ---
st.markdown("---")
st.markdown(f"🔒 **Your data is secure & private. AI-generated insights are for informational purposes only.**", unsafe_allow_html=True)