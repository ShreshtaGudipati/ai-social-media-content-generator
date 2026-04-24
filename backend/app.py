from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from fpdf import FPDF
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re

# =====================================
# APP
# =====================================
app = Flask(__name__)

# Allow Localhost + Vercel Frontend
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:3000",
                "https://ai-social-media-content-generator-ecru.vercel.app"
            ]
        }
    },
    supports_credentials=True
)

# =====================================
# API KEY
# =====================================
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("models/gemma-3-4b-it")

# =====================================
# HELPERS
# =====================================
def ask_ai(prompt):
    response = model.generate_content(prompt)
    return response.text.strip()


def clean_output(text):
    text = re.sub(r"\*\*|##|---", "", text)
    text = re.sub(r"Option\s*\d+:?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def pdf_safe(text):
    text = text.replace("’", "'")
    text = text.replace("‘", "'")
    text = text.replace("“", '"')
    text = text.replace("”", '"')
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("…", "...")
    return text.encode("latin-1", "ignore").decode("latin-1")

# =====================================
# AGENTS
# =====================================
def instagram_agent(topic, tone, audience):
    prompt = f"""
    Create one final Instagram caption.

    Topic: {topic}
    Tone: {tone}
    Audience: {audience}

    Add emojis and hashtags.
    """
    return clean_output(ask_ai(prompt))


def linkedin_agent(topic, tone, audience):
    prompt = f"""
    Create one professional LinkedIn post.

    Topic: {topic}
    Tone: {tone}
    Audience: {audience}
    """
    return clean_output(ask_ai(prompt))


def article_agent(topic, tone, audience):
    prompt = f"""
    Write one professional LinkedIn article.

    Topic: {topic}
    Tone: {tone}
    Audience: {audience}
    """
    return clean_output(ask_ai(prompt))


def twitter_agent(topic, tone, audience):
    prompt = f"""
    Create one Twitter/X thread.

    Topic: {topic}
    Tone: {tone}
    Audience: {audience}
    """
    return clean_output(ask_ai(prompt))

# =====================================
# GENERATE
# =====================================
@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)

    topic = data.get("topic", "")
    tone = data.get("tone", "")
    audience = data.get("audience", "")

    return jsonify({
        "instagram": instagram_agent(topic, tone, audience),
        "linkedin": linkedin_agent(topic, tone, audience),
        "article": article_agent(topic, tone, audience),
        "twitter": twitter_agent(topic, tone, audience)
    })

# =====================================
# DOWNLOAD PDF
# =====================================
@app.route("/download-pdf", methods=["POST"])
def download_pdf():
    data = request.get_json(force=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, pdf_safe("AI SOCIAL MEDIA CONTENT REPORT\n\n"))

    pdf.multi_cell(0, 10, pdf_safe("Instagram:\n"))
    pdf.multi_cell(0, 10, pdf_safe(data.get("instagram", "") + "\n\n"))

    pdf.multi_cell(0, 10, pdf_safe("LinkedIn:\n"))
    pdf.multi_cell(0, 10, pdf_safe(data.get("linkedin", "") + "\n\n"))

    pdf.multi_cell(0, 10, pdf_safe("Article:\n"))
    pdf.multi_cell(0, 10, pdf_safe(data.get("article", "") + "\n\n"))

    pdf.multi_cell(0, 10, pdf_safe("Twitter:\n"))
    pdf.multi_cell(0, 10, pdf_safe(data.get("twitter", "") + "\n\n"))

    filename = "content_report.pdf"
    pdf.output(filename)

    return send_file(
        filename,
        as_attachment=True,
        download_name="content_report.pdf",
        mimetype="application/pdf"
    )

# =====================================
# RUN
# =====================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)