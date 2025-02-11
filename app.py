from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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