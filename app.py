import streamlit as st
from google import genai
from groq import Groq
from PIL import Image, ExifTags
import io

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Truth Lens Ultra", layout="wide", page_icon="🕵️‍♂️")
st.markdown("<style>.stApp {background-color: #0b0e14; color: #ffffff;}</style>", unsafe_allow_html=True)

# --- 2. SECRETS CHECK ---
GEMINI_KEY = st.secrets.get("GEMINI_KEY")
GROQ_KEY = st.secrets.get("GROQ_KEY")

if not GEMINI_KEY or not GROQ_KEY:
    st.error("🔑 API Keys are missing in Streamlit Secrets!")
    st.stop()

# Initialize AI Clients
gen_client = genai.Client(api_key=GEMINI_KEY)
groq_client = Groq(api_key=GROQ_KEY)

# --- 3. UI LAYOUT ---
st.title("🕵️‍♂️ Truth Lens Ultra: Forensic Hub")
st.write("Upload any image or document. Gemini scans the pixels; Groq audits the logic.")

# User Command Input
user_query = st.text_input("🔍 What should I search for?", placeholder="e.g., 'Is the QR code safe?', 'Find text about payment'...")

# File Uploader
uploaded_file = st.file_uploader("Upload Evidence", type=['jpg', 'png', 'jpeg', 'txt'])

if uploaded_file and st.button("🚀 EXECUTE MULTI-AI SCAN"):
    col1, col2 = st.columns([1, 1.5])
    
    # CASE A: IMAGE UPLOADED
    if uploaded_file.type.startswith('image'):
        img = Image.open(uploaded_file)
        with col1:
            st.image(img, caption="Evidence Preview", use_container_width=True)
            
            # FEATURE: METADATA (EXIF) AUDIT
            st.subheader("📁 Hidden Metadata Audit")
            exif_data = img._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    tag_name = ExifTags.TAGS.get(tag, tag)
                    st.write(f"**{tag_name}:** {value}")
            else:
                st.warning("⚠️ No Metadata found. (Image has been stripped/edited!)")

        with col2:
            st.subheader("🧠 Multi-AI Jury Results")
            
            # Step 1: Gemini Vision Analysis
            with st.spinner("Gemini is auditing pixels..."):
                v_prompt = f"Forensic Task: {user_query}. Check for Photoshop artifacts, font mismatches, and shadow logic."
                vision_resp = gen_client.models.generate_content(model='gemini-2.0-flash', contents=[v_prompt, img])
                st.markdown(f"**🔴 Gemini Forensic Verdict:**\n{vision_resp.text}")

            # Step 2: Groq Logical Audit (Fast Analysis)
            with st.spinner("Groq is auditing logic..."):
                g_prompt = f"Analyze this forensic report: '{vision_resp.text}'. Based on the user's query '{user_query}', is this likely fraud? Be brutally honest."
                chat_completion = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": g_prompt}],
                    model="llama-3.3-70b-versatile",
                )
                st.success(f"**⚡ Groq Logic Audit:** {chat_completion.choices[0].message.content}")

    # CASE B: TEXT FILE UPLOADED
    else:
        text_content = uploaded_file.read().decode("utf-8")
        st.subheader("📄 Document Logic Scan")
        with st.spinner("Groq is scanning text..."):
            doc_prompt = f"In this document, perform the task: '{user_query}'. \n\n Content: {text_content}"
            doc_resp = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": doc_prompt}],
                model="llama-3.3-70b-versatile",
            )
            st.info(doc_resp.choices[0].message.content)
