import os
import json
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Load config from config.json safely
try:
    with open("config.json") as f:
        config = json.load(f)
except FileNotFoundError:
    raise RuntimeError("config.json file not found. Please create one before running the app.")

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found in .env file. Make sure it's set correctly.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Build the system prompt from config
def build_system_prompt():
    prompt = f"""
You are a helpful assistant for {config.get('business_name', 'our business')}.
You help users with questions related to our services and operations.

Business hours: {config.get('hours', 'N/A')}
Location: {config.get('location', 'N/A')}
Services:
- {'\n- '.join(config.get('services', []))}

Contact info:
- Phone: {config.get('contact_info', {}).get('phone', 'N/A')}
- Email: {config.get('contact_info', {}).get('email', 'N/A')}

Tone: {config.get('tone', 'friendly')}

If you don't know the answer, say: "{config.get('fallback_response', 'I am not sure. Please contact us directly.')}"

Current promotions: {config.get('offers', 'None')}
Pricing: {config.get('pricing_info', 'Please contact us for pricing.')}
Book here: {config.get('appointment_link', 'No booking link available.')}

Staff:
- {'\n- '.join(config.get('staff', []))}

Notes: {config.get('special_notes', 'No additional notes.')}

Example questions and answers:
"""
    for item in config.get("faq_examples", []):
        prompt += f"\nQ: {item['q']}\nA: {item['a']}"

    return prompt.strip()

# Serve chatbot UI
@app.route("/")
def index():
    return render_template("index.html")

# Handle chat API
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "No message provided."}), 400

        system_prompt = build_system_prompt()

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )

        assistant_reply = response.choices[0].message.content.strip()
        return jsonify({"response": assistant_reply})

    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500

# Run the app locally
if __name__ == "__main__":
    app.run(debug=True)
