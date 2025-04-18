import os
import json
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Load config.json safely
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

# Build the system prompt from config.json
def build_system_prompt():
    business_name = config.get('business_name', 'our business')
    services = "\n".join(config.get("services", []))
    hours = config.get('hours', 'N/A')
    location = config.get('location', 'N/A')
    contact = config.get('contact_info', {})
    tone = config.get('tone', 'friendly')
    fallback = config.get('fallback_response', 'I am not sure. Please contact us directly.')
    offers = config.get('offers', 'None')

    prompt = (
        f"You are a helpful assistant for {business_name}.\n"
        f"You help users with the following services:\n{services}\n\n"
        f"Business hours: {hours}\n"
        f"Location: {location}\n"
        f"Contact info: Phone - {contact.get('phone', 'N/A')}, Email - {contact.get('email', 'N/A')}\n"
        f"Tone: {tone}\n\n"
        f"If unsure how to answer, say: \"{fallback}\"\n"
        f"Promotions: {offers}\n"
    )

    faq_examples = config.get("faq_examples", [])
    if faq_examples:
        prompt += "\nHere are some example questions and answers:\n"
        for item in faq_examples:
            prompt += f"Q: {item['q']}\nA: {item['a']}\n"

    return prompt.strip()

# Route to serve the chatbot UI
@app.route("/")
def index():
    return render_template("index.html")

# Route to handle chat API
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        system_prompt = build_system_prompt()

        # Send message to OpenAI
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

# Run the app
if __name__ == "__main__":
    app.run(debug=True)