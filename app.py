import streamlit as st
from google import genai
from groq import Groq
from PIL import Image, ExifTags
import io

# 1. REMOVE SPLASH SCREEN (JavaScript Hook)
js = "document.getElementById('splash').style.opacity = '0'; setTimeout(() => document.getElementById('splash').remove(), 1000);"
st.components.v1.html(f"<script>{js}</script>", height=0)

st.set_page_config(page_title="Truth Lens Pro", layout="centered")

# 2. CUSTOM CSS FOR MOBILE "APP" FEEL
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .report-card { 
        background: #161b22; border-radius: 15px; border: 1px solid #30363d; 
        padding: 20px; margin-top: 20px;
    }
    .status-badge {
        padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ TRUTH LENS PRO")

# 3. SIDEBAR CONFIG (Stored in session so you don't re-type)
with st.sidebar:
    st.header("🔑 API Access")
    g_key = st.text_input("Gemini API Key", type="password", key="gkey")
    gr_key = st.text_input("Groq API Key", type="password", key="grkey")
    st.markdown("---")
    st.caption("v2.0.0-Mobile | 2026 Edition")

# 4. UPI FRAUD CHECKLIST (New Feature)
with st.expander("📝 Manual UPI Check Guide"):
    st.write("Before AI scan, check these:")
    st.checkbox("Is the Font consistent? (Check '₹' symbol)")
    st.checkbox("Is the Transaction ID 12 digits?")
    st.checkbox("Are the clock and battery icons blurred?")

uploaded_file = st.file_uploader("📤 Upload Screenshot", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Forensic Target", use_container_width=True)

    if st.button("🚀 RUN FULL AUDIT"):
        if not g_key or not gr_key:
            st.error("Missing API Keys! Swipe right to add them.")
        else:
            with st.status("Performing Deep Forensic Analysis...") as status:
                # --- PHASE 1: LOCAL METADATA SCAN (Replaces Cloudinary) ---
                st.write("Scanning Image Metadata (EXIF)...")
                exif_data = img.getexif()
                meta_summary = "No Metadata Found (Likely a WhatsApp forward or Edited)."
                if exif_data:
                    meta_summary = {ExifTags.TAGS.get(k, k): v for k, v in exif_data.items()}
                
                # --- PHASE 2: VISION SCAN (Gemini 2.0) ---
                st.write("Detecting UI Artifacts & Font Tampering...")
                client_g = genai.Client(api_key=g_key)
                # We send the image bytes directly to Gemini
                vision_prompt = """
                Analyze this Indian Payment (UPI) screenshot. 
                1. Look for 'Ghosting' around text. 
                2. Verify if the 'Transaction Successful' green color is the correct hex. 
                3. Check for overlapping fonts in the Transaction ID.
                Provide a technical summary.
                """
                response_v = client_g.models.generate_content(model="gemini-2.0-flash", contents=[vision_prompt, img])
                
                # --- PHASE 3: VERDICT (Groq Llama 3.3) ---
                st.write("Cross-referencing with Fraud Patterns...")
                client_gr = Groq(api_key=gr_key)
                logic_prompt = f"""
                Act as a Digital Forensic Expert. Based on this Metadata: {meta_summary} 
                And this Vision Report: {response_v.text}
                Give a verdict: 'SAFE', 'SUSPICIOUS', or 'HIGH RISK'. 
                Keep it under 100 words for mobile reading.
                """
                final_verdict = client_gr.chat.completions.create(
                    messages=[{"role": "user", "content": logic_prompt}],
                    model="llama-3.3-70b-versatile"
                )
                
                status.update(label="Audit Complete!", state="complete")

            # --- 5. THE RESULT UI ---
            st.markdown("<div class='report-card'>", unsafe_allow_html=True)
            st.subheader("🏁 Final Verdict")
            st.write(final_verdict.choices[0].message.content)
            
            # Risk Indicator
            risk_color = "🔴" if "HIGH RISK" in final_verdict.choices[0].message.content.upper() else "🟢"
            st.metric("Risk Level", f"{risk_color} Verified")
            st.markdown("</div>", unsafe_allow_html=True)
