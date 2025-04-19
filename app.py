import os
import json
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv()

# Load config from config.json
with open("config.json", "r") as f:
    config = json.load(f)

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Initialize OpenAI client
try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("Missing OPENAI_API_KEY in .env file")
    client = OpenAI(api_key=openai_api_key)
except Exception as e:
    raise RuntimeError(f"Failed to initialize OpenAI client: {str(e)}")

# Homepage route
@app.route("/")
def index():
    return render_template("index.html")

# Chatbot API route
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Format the system prompt using config
        system_message = {
            "role": "system",
            "content": (
                f"You are a helpful assistant for {config['business_name']}. "
                f"You help users with services like {', '.join(config['services'])}. "
                f"The business hours are: {config['hours']}. "
                f"Your tone should be {config['tone']}. "
                f"If you're unsure, say: '{config['fallback_response']}'"
            ),
        }

        # Send to OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                system_message,
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message.content.strip()
        return jsonify({"response": reply})

    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500

# Run the app locally (Render uses gunicorn)
if __name__ == "__main__":
    app.run(debug=True)