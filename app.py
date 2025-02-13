from openai import OpenAI
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
import openai  # type: ignore # Example: Using OpenAI for NLP

load_dotenv()  # Load environment variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# ... existing Flask setup ...

def get_ai_response(user_input):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Keep responses concise."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return "I'm having trouble connecting to the AI service. Please try again later."

@app.route('/chat', methods=['POST'])
def chat_handler():
    user_message = request.json.get('message', '')
    
    # Optional: Add your existing pattern matching as fallback
    bot_response = get_ai_response(user_message)
    
    return jsonify({'response': bot_response})

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    user_message = data['message']
    
    # Example: Use OpenAI to generate a response
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"User: {user_message}\nChatbot:",
        max_tokens=50
    )
    
    return jsonify({"reply": response.choices[0].text.strip()})

@app.route('/home')
def home():
    search_query = request.args.get('search', '')
    category = request.args.get('category', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    # Filter expenses based on query parameters
    expenses = filter_expenses(search_query, category, start_date, end_date)
    savings_progress = 75  # Replace with your logic
    return render_template('home.html', expenses=expenses, savings_progress=savings_progress)

def filter_expenses(search_query, category, start_date, end_date):
    # Assuming 'expenses' is a list of dictionaries with keys like 'description', 'category', 'date'
    filtered = expenses  # Replace 'expenses' with your actual data source
    if search_query:
        filtered = [e for e in filtered if search_query.lower() in e['description'].lower()]
    if category:
        filtered = [e for e in filtered if e['category'] == category]
    if start_date:
        filtered = [e for e in filtered if e['date'] >= start_date]
    if end_date:
        filtered = [e for e in filtered if e['date'] <= end_date]
    return filtered

if __name__ == '__main__':
    app.run(debug=True) 