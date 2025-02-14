from openai import OpenAI # type: ignore
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import openai  # type: ignore # Example: Using OpenAI for NLP
from flask_sqlalchemy import SQLAlchemy # type: ignore

load_dotenv()  # Load environment variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budgetbuddy.db'
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    notifications = db.Column(db.String(50), default='Enable all notifications')

# Models
class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(10), nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(10), nullable=False)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(10), nullable=False)

# Create Database
with app.app_context():
    db.create_all()

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

@app.route('/')
def home():
    incomes = Income.query.all()
    expenses = Expense.query.all()
    budgets = Budget.query.all()

    # Prepare data for charts
    income_dates = [income.date for income in incomes]
    income_amounts = [income.amount for income in incomes]
    expense_dates = [expense.date for expense in expenses]
    expense_amounts = [expense.amount for expense in expenses]

    return render_template('home.html', incomes=incomes, expenses=expenses, budgets=budgets,
                           income_dates=income_dates, income_amounts=income_amounts,
                           expense_dates=expense_dates, expense_amounts=expense_amounts)

def filter_expenses(search_query, category, start_date, end_date):
    expenses = []  # Replace with your actual data source (e.g., database query)
    filtered = expenses
    if search_query:
        filtered = [e for e in filtered if search_query.lower() in e['description'].lower()]
    if category:
        filtered = [e for e in filtered if e['category'] == category]
    if start_date:
        filtered = [e for e in filtered if e['date'] >= start_date]
    if end_date:
        filtered = [e for e in filtered if e['date'] <= end_date]
    return filtered

# Settings Route
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        notifications = request.form.get('notifications')

        # Update user settings (example: fetch user from session or database)
        user = User.query.filter_by(username='current_user').first()
        if user:
            user.username = username
            user.email = email
            user.password = password
            user.notifications = notifications
            db.session.commit()
            flash('Settings updated successfully!', 'success')
        else:
            flash('User not found!', 'error')

        return redirect(url_for('home'))

    return render_template('home.html')

# Help Route
@app.route('/help', methods=['GET', 'POST'])
def help():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Save the help request (example: store in database or send email)
        flash('Your message has been sent! We will get back to you soon.', 'success')
        return redirect(url_for('home'))

    return render_template('home.html')

# Add Record Route
@app.route('/add-record', methods=['POST'])
def add_record():
    if request.method == 'POST':
        record_type = request.form.get('record_type')
        amount = float(request.form.get('amount'))
        description = request.form.get('description')
        category = request.form.get('category')
        date = request.form.get('date')

        if record_type == 'Income':
            new_record = Income(amount=amount, description=description, date=date)
        elif record_type == 'Expense':
            new_record = Expense(amount=amount, description=description, category=category, date=date)
        elif record_type == 'Budget':
            new_record = Budget(amount=amount, category=category, date=date)

        db.session.add(new_record)
        db.session.commit()
        flash(f'{record_type} added successfully!', 'success')
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True) 