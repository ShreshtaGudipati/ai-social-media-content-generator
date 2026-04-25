from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from fpdf import FPDF
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re
import traceback

# =====================================
# APP
# =====================================
app = Flask(__name__)

# CORS
CORS(
    app,
    resources={r"/*": {"origins": "*"}}
)

# =====================================
# LOAD ENV
# =====================================
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found")

# =====================================
# GEMINI
# =====================================
genai.configure(api_key=GEMINI_API_KEY)

# KEEP GEMMA MODEL
model = genai.GenerativeModel("models/gemma-3-4b-it")
@app.route("/check-key")
def check_key():
    key = os.getenv("GEMINI_API_KEY", "")
    return {"starts_with": key[:6], "length": len(key)}
# =====================================
# HELPERS
# =====================================
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


def ask_ai(prompt):
    try:
        response = model.generate_content(prompt)

        print("RAW RESPONSE:", response)

        if hasattr(response, "text") and response.text:
            return response.text.strip()

        return "No content generated."

    except Exception:
        traceback.print_exc()
        raise


# =====================================
# AGENTS
# =====================================
def instagram_agent(topic, tone, audience):
    prompt = f"""
Create one Instagram caption.

Topic: {topic}
Tone: {tone}
Audience: {audience}

Add emojis and hashtags.
"""
    return clean_output(ask_ai(prompt))


def linkedin_agent(topic, tone, audience):
    prompt = f"""
Create one LinkedIn post.

Topic: {topic}
Tone: {tone}
Audience: {audience}

Professional tone.
"""
    return clean_output(ask_ai(prompt))


def article_agent(topic, tone, audience):
    prompt = f"""
Write one LinkedIn article.

Topic: {topic}
Tone: {tone}
Audience: {audience}

Use title and headings.
"""
    return clean_output(ask_ai(prompt))


def twitter_agent(topic, tone, audience):
    prompt = f"""
Create one Twitter/X thread.

Topic: {topic}
Tone: {tone}
Audience: {audience}

5 tweets.
"""
    return clean_output(ask_ai(prompt))


# =====================================
# HOME
# =====================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Backend Running"})


# =====================================
# GENERATE
# =====================================
@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json(force=True)

        topic = data.get("topic", "")
        tone = data.get("tone", "")
        audience = data.get("audience", "")

        print("REQUEST:", topic, tone, audience)

        result = {
            "instagram": instagram_agent(topic, tone, audience),
            "linkedin": linkedin_agent(topic, tone, audience),
            "article": article_agent(topic, tone, audience),
            "twitter": twitter_agent(topic, tone, audience)
        }

        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# =====================================
# PDF
# =====================================
@app.route("/download-pdf", methods=["POST"])
def download_pdf():
    try:
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

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# =====================================
# RUN
# =====================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)