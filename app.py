import streamlit as st
from google import genai
from groq import Groq
from PIL import Image
import io

# --- 1. SETUP ---
st.set_page_config(page_title="Truth Lens AI", layout="wide", page_icon="🛡️")

# --- 2. AUTHENTICATION ---
# The new SDK is much cleaner with API keys
client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
groq_client = Groq(api_key=st.secrets["GROQ_KEY"])

st.title("🛡️ Truth Lens Intelligence")
st.write("Using the latest **Gemini 3 Flash** & **Groq Llama 3** architecture.")

# --- 3. THE SCANNER ---
uploaded_file = st.file_uploader("Upload image for forensic audit", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Evidence", width=500)
    
    if st.button("🔍 Run Deep Scan"):
        with st.spinner("Analyzing pixels..."):
            # New GenAI Syntax (Faster & Simpler)
            response = client.models.generate_content(
                model="gemini-3-flash-preview", 
                contents=["Perform a forensic audit on this image. Look for edits, inconsistent lighting, or fraud.", img]
            )
            
            st.subheader("🚩 Forensic Verdict")
            st.write(response.text)
            
            # Groq logical cross-check
            audit_prompt = f"Verify this AI claim: {response.text}. Is it logically sound?"
            groq_resp = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": audit_prompt}],
                model="llama-3.3-70b-versatile",
            )
            st.info(f"⚡ Groq Logic Audit: {groq_resp.choices[0].message.content}")
