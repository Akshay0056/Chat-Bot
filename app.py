from flask import Flask, request, jsonify, render_template, session
import google.generativeai as genai
import os
from dotenv import load_dotenv
import re
from flask_session import Session

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Flask session
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecretkey")
Session(app)

# Configure Gemini API
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not found in environment variables")

genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-2.0-flash"

def simple_addiction_check(user_input):
    """
    Basic rule-based gadget addiction detection based on keywords and hours.
    """
    matches = re.findall(r'(\d+)\s*hours', user_input.lower())
    total_hours = sum(int(hour) for hour in matches)

    print("Detected total gadget hours from input:", total_hours)

    if total_hours >= 8:
        return "High Risk 🚨 (You may need to limit your gadget time!)"
    elif total_hours >= 5:
        return "Moderate Risk ⚠️ (Try to balance gadget usage and rest.)"
    elif total_hours >= 2:
        return "Low Risk ✅ (Your usage seems fine, keep monitoring!)"
    else:
        return None

def run_chat(user_input):
    user_name = session.get("user_name")

    # If name not in session, ask for it
    if not user_name:
        # Detect if the input is a name (e.g., "Akshay")
        if len(user_input.split()) == 1 and user_input.isalpha():
            user_name = user_input.capitalize()
            session["user_name"] = user_name
            return f"👋 Nice to meet you, {user_name}! I'm ElectroFree ⚡😊. What would you like help with today?"

        # If name not provided yet, ask for it
        return "👋 Hi there! I'm ElectroFree ⚡😊. Before we begin, may I know your **first name**?"

    # Gadget addiction check
    addiction_result = simple_addiction_check(user_input)
    if addiction_result:
        return f"🧠 **Gadget Addiction Analysis Result:** {addiction_result}"

    # Set up chat
    model = genai.GenerativeModel(MODEL_NAME)
    chat = model.start_chat(history=[
        {
            "role": "user",
            "parts": [
                {
                    "text": (
                        "You are ElectroFree, an AI health assistant. "
                        "Detect gadget overuse, give basic health tips and hospital info. "
                        "Respond in short, clear sentences. Be friendly and simple."
                    )
                }
            ]
        },
        {
            "role": "model",
            "parts": [
                {
                    "text": f"Hi {user_name}! 😊 I'm ElectroFree ⚡. How can I help?"
                }
            ]
        }
    ])

    generation_config = {
        "temperature": 0.4,
        "top_k": 1,
        "top_p": 0.9,
        "max_output_tokens": 100
    }

    response = chat.send_message(user_input, generation_config=generation_config)

    print("Bot response:", response.text)
    return response.text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return "This is ElectroFree's about page."

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('userInput')
    if not user_input:
        return jsonify({"error": "Invalid request body"}), 400

    try:
        response = run_chat(user_input)
        return jsonify({"response": response})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(port=int(os.getenv('PORT', 5000)), debug=True)
