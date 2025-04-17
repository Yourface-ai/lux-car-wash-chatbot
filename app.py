import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Initialize OpenAI client with API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Route to serve the chatbot HTML page
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

        # Send message to OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant for Lux Car Wash. "
                        "You help users book appointments, explain services like Interior Detailing, "
                        "Exterior Wash, Full-Service Wax, and Stain Removal. "
                        "You know the business hours: 9am–6pm, Mon–Sat. "
                        "If you're unsure, suggest contacting customer service."
                    ),
                },
                {"role": "user", "content": user_message},
            ],
        )

        assistant_reply = response.choices[0].message.content.strip()
        return jsonify({"response": assistant_reply})

    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)