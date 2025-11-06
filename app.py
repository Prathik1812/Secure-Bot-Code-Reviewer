import streamlit as st
from google import genai
from google.genai import types

# --- 1. CONFIGURATION ---
MODEL_NAME = "gemini-2.5-flash"

SECURITY_SYSTEM_PROMPT = """
You are an expert Cyber Security Architect and Code Auditor specializing in detecting and fixing security vulnerabilities in code.
Your task is to perform a detailed security review of the user-provided code snippet.

Your analysis MUST adhere to the following steps:
1. Identify all security-related flaws (e.g., SQL Injection, XSS, insecure input validation, hardcoded secrets, insecure cryptography, buffer overflows).
2. For each flaw, provide a clear explanation of the vulnerability and its potential impact.
3. Provide a secure, refactored version of the code snippet that fully remediates the identified flaw(s).
4. If no security flaws are found, state "Security Status: CLEAN."

Your output MUST be formatted clearly using Markdown.
"""

# --- 2. GEMINI API CALL FUNCTION ---
def get_gemini_client(api_key):
    """Initializes and returns the Gemini client."""
    try:
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"Error initializing Gemini client: {e}. Please check your API key.")
        return None

def analyze_and_remediate_code(client, code_to_analyze, language):
    try:
        full_content = [
            types.Part(text=f"Code to analyze (Language: {language}):"),
            types.Part(text=f"```\n{code_to_analyze}\n```")
        ]

        config = types.GenerateContentConfig(
            temperature=0.2,
            system_instruction=SECURITY_SYSTEM_PROMPT
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_content,
            config=config
        )
        return response.text

    except Exception as e:
        if "API_KEY_INVALID" in str(e):
            return "ERROR: The Gemini API Key is invalid. Please get a valid key from Google AI Studio."
        elif "RESOURCE_EXHAUSTED" in str(e):
            return "ERROR: Rate limit exceeded. Please wait a moment and try again."
        else:
            return f"An unexpected error occurred: {e}"

# --- 3. STREAMLIT LAYOUT ---
st.set_page_config(page_title="Secure Code Review Bot", layout="wide")
st.title("🤖 Secure Code Review and Remediation Bot")

st.markdown("APP INIT OK")

# API Key & language selection
col1, col2 = st.columns([2,1])
with col1:
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
with col2:
    if 'language' not in st.session_state:
        st.session_state.language = 'Python'
    st.session_state.language = st.selectbox("Select Code Language:", ['Python','JavaScript','Java','Go','Other'])

# Code input
st.subheader("Paste Your Code")
default_code = """
import requests
import sys

def fetch_data(url):
    # Potential security flaw: No input validation
    response = requests.get(url)
    return response.text

if __name__ == '__main__':
    user_url = sys.argv[1]
    data = fetch_data(user_url)
    print(data)
"""
code_input = st.text_area(f"Paste your {st.session_state.language} code here:", height=300, value=default_code)

# Analyze button
st.subheader("Review Results")
if st.button("🔍 Analyze and Remediate Code"):
    if not api_key:
        st.error("🛑 Please enter your Gemini API Key.")
    elif not code_input.strip():
        st.warning("⚠️ Please paste some code to analyze.")
    else:
        client = get_gemini_client(api_key)
        if client:
            with st.spinner("Analyzing code with Gemini..."):
                gemini_output = analyze_and_remediate_code(client, code_input, st.session_state.language)

            if gemini_output.startswith("ERROR"):
                st.error(gemini_output)
            else:
                st.markdown(gemini_output)
                st.success("✅ Analysis and Remediation Complete!")

# Responsible AI note
st.markdown("---")
st.markdown("### 🔒 Responsible AI Note")
st.info("""
The suggested remediation is AI-generated. Always human-review and test all AI-suggested code fixes
before deploying to ensure correctness and security.
""")
