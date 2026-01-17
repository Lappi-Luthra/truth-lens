from fastapi import FastAPI, UploadFile, File
from google import genai
from groq import Groq
import cloudinary.uploader
import uvicorn

app = FastAPI(title="Truth Lens API")

# Clients
genai_client = genai.Client(api_key="YOUR_GEMINI_KEY")
groq_client = Groq(api_key="YOUR_GROQ_KEY")

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    # 1. Technical Scan (Cloudinary)
    upload_res = cloudinary.uploader.upload(file.file, image_metadata=True)
    metadata = upload_res.get("image_metadata", {})

    # 2. Vision Scan (Gemini 2.0)
    # Note: In a real API, you'd pass the file bytes to Gemini
    v_res = genai_client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=["Scan for fraud artifacts.", file.file.read()]
    )

    # 3. Final Logic (Groq)
    logic_res = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": f"Audit this: {v_res.text}"}],
        model="llama-3.3-70b-versatile"
    )

    return {
        "fraud_score": logic_res.choices[0].message.content,
        "metadata_found": bool(metadata),
        "verdict": "Flagged" if "high risk" in logic_res.choices[0].message.content.lower() else "Clear"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
