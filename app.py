import streamlit as st
from google import genai
from groq import Groq
import cloudinary
import cloudinary.uploader
import requests
from PIL import Image
import io

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Truth Lens Pro", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .report-card { background: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 10px; margin-bottom: 15px; }
    .metric { color: #58a6ff; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTHENTICATION ---
genai_client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
groq_client = Groq(api_key=st.secrets["GROQ_KEY"])

# Cloudinary Config
cloudinary.config(
    cloud_name = st.secrets["CLOUDINARY_NAME"],
    api_key = st.secrets["CLOUDINARY_API_KEY"],
    api_secret = st.secrets["CLOUDINARY_API_SECRET"],
    secure = True
)

HF_TOKEN = st.secrets["HUGGINGFACE_KEY"]

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Truth Lens Lab")
    st.info("Status: All Systems Active (2026)")
    st.divider()
    st.markdown("### 📖 About\nTruth Lens uses a **Jury of AIs** (Google, Meta, Cloudinary) to verify digital integrity.")

# --- 4. MAIN UI ---
st.title("🕵️‍♂️ Digital Forensic Terminal")
uploaded_file = st.file_uploader("Upload Evidence (Image/Screenshot)", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    col1, col2 = st.columns([1, 1.2])
    img = Image.open(uploaded_file)
    
    with col1:
        st.image(img, caption="Forensic Sample", use_container_width=True)
        run_scan = st.button("🚀 EXECUTE FULL SPECTRUM AUDIT")

    if run_scan:
        with col2:
            st.subheader("📑 Forensic Report")
            
            # --- STAGE 1: CLOUDINARY (Metadata) ---
            with st.spinner("Extracting Metadata..."):
                upload_res = cloudinary.uploader.upload(uploaded_file, image_metadata=True)
                metadata = upload_res.get("image_metadata", {})
                st.markdown("<div class='report-card'><b>📡 Metadata Scan:</b><br>", unsafe_allow_html=True)
                if metadata:
                    st.write(f"Camera: {metadata.get('Make', 'Unknown')} {metadata.get('Model', '')}")
                    st.write(f"Timestamp: {metadata.get('DateTimeOriginal', 'Hidden/Stripped')}")
                else:
                    st.warning("⚠️ Metadata has been stripped (common in WhatsApp/Facebook images).")
                st.markdown("</div>", unsafe_allow_html=True)

            # --- STAGE 2: HUGGING FACE (Pixel Anomaly) ---
            with st.spinner("Hugging Face: Scanning for Deepfakes..."):
                # Using a specialized forgery detection model
                API_URL = "https://api-inference.huggingface.co/models/umm-maybe/Deepfake-detection"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                uploaded_file.seek(0)
                response = requests.post(API_URL, headers=headers, data=uploaded_file.read())
                
                st.markdown("<div class='report-card'><b>🧪 Pixel Anomaly Audit (HF):</b><br>", unsafe_allow_html=True)
                if response.status_code == 200:
                    st.json(response.json())
                else:
                    st.write("Specialized scan pending (Model loading...)")
                st.markdown("</div>", unsafe_allow_html=True)

            # --- STAGE 3: GEMINI 2.0 (Vision reasoning) ---
            with st.spinner("Gemini: Visual Analysis..."):
                v_prompt = "Identify any font mismatches, copy-paste artifacts, or shadow inconsistencies. Be very critical."
                vision_res = genai_client.models.generate_content(model="gemini-2.0-flash", contents=[v_prompt, img])
                st.markdown(f"<div class='report-card'><b>🔍 Visual Findings:</b><br>{vision_res.text}</div>", unsafe_allow_html=True)

            # --- STAGE 4: GROQ (Final Verdict) ---
            with st.spinner("Groq: Final Jury Verdict..."):
                final_prompt = f"Vision Report: {vision_res.text}. Metadata: {metadata}. Give a final Fraud Risk Score (0-100%) and 1 reason."
                logic_res = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": final_prompt}],
                    model="llama-3.3-70b-versatile"
                )
                st.error(f"🏁 FINAL VERDICT: {logic_res.choices[0].message.content}")

# --- 5. FOOTER ---
st.divider()
st.caption("© 2026 Truth Lens | Digital Integrity Guaranteed.")
