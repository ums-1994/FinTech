from flask import Flask, render_template, request, redirect, session, flash, jsonify, make_response, Response
import os
from datetime import timedelta  # used for setting session timeout
import pandas as pd
import plotly
import plotly.express as px
import json
import warnings
import support
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO
from reportlab.lib.utils import ImageReader
import tempfile
import plotly.io as pio

warnings.filterwarnings("ignore")

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def login():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)
    if 'user_id' in session:  # if logged-in
        flash("Already a user is logged-in!")
        return redirect('/home')
    else:  # if not logged-in
        return render_template("login.html")


@app.route('/login_validation', methods=['POST'])
def login_validation():
    if 'user_id' not in session:  # if user not logged-in
        email = request.form.get('email')
        passwd = request.form.get('password')
        query = """SELECT * FROM user_login WHERE email LIKE '{}' AND password LIKE '{}'""".format(email, passwd)
        users = support.execute_query("search", query)
        if len(users) > 0:  # if user details matched in db
            session['user_id'] = users[0][0]
            return redirect('/home')
        else:  # if user details not matched in db
            flash("Invalid email and password!")
            return redirect('/')
    else:  # if user already logged-in
        flash("Already a user is logged-in!")
        return redirect('/home')


@app.route('/reset', methods=['POST'])
def reset():
    if 'user_id' not in session:
        email = request.form.get('femail')
        pswd = request.form.get('pswd')
        userdata = support.execute_query('search', """select * from user_login where email LIKE '{}'""".format(email))
        if len(userdata) > 0:
            try:
                query = """update user_login set password = '{}' where email = '{}'""".format(pswd, email)
                support.execute_query('insert', query)
                flash("Password has been changed!!")
                return redirect('/')
            except:
                flash("Something went wrong!!")
                return redirect('/')
        else:
            flash("Invalid email address!!")
            return redirect('/')
    else:
        return redirect('/home')


@app.route('/register')
def register():
    if 'user_id' in session:  # if user is logged-in
        flash("Already a user is logged-in!")
        return redirect('/home')
    else:  # if not logged-in
        return render_template("register.html")


@app.route('/registration', methods=['POST'])
def registration():
    if 'user_id' not in session:  # if not logged-in
        name = request.form.get('name')
        email = request.form.get('email')
        passwd = request.form.get('password')
        if len(name) > 5 and len(email) > 10 and len(passwd) > 5:  # if input details satisfy length condition
            try:
                query = """INSERT INTO user_login(username, email, password) VALUES('{}','{}','{}')""".format(name,
                                                                                                              email,
                                                                                                              passwd)
                support.execute_query('insert', query)

                user = support.execute_query('search',
                                             """SELECT * from user_login where email LIKE '{}'""".format(email))
                session['user_id'] = user[0][0]  # set session on successful registration
                flash("Successfully Registered!!")
                return redirect('/home')
            except:
                flash("Email id already exists, use another email!!")
                return redirect('/register')
        else:  # if input condition length not satisfy
            flash("Not enough data to register, try again!!")
            return redirect('/register')
    else:  # if already logged-in
        flash("Already a user is logged-in!")
        return redirect('/home')


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/feedback', methods=['POST'])
def feedback():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    sub = request.form.get("sub")
    message = request.form.get("message")
    flash("Thanks for reaching out to us. We will contact you soon.")
    return redirect('/')


@app.route('/home')
def home():
    if 'user_id' in session:  # if user is logged-in
        query = """select * from user_login where user_id = {} """.format(session['user_id'])
        userdata = support.execute_query("search", query)

        table_query = """select * from user_expenses where user_id = {} order by pdate desc""".format(
            session['user_id'])
        table_data = support.execute_query("search", table_query)
        df = pd.DataFrame(table_data, columns=['#', 'User_Id', 'Date', 'Expense', 'Amount', 'Note'])

        df = support.generate_df(df)
        try:
            earning, spend, invest, saving = support.top_tiles(df)
        except:
            earning, spend, invest, saving = 0, 0, 0, 0

        try:
            bar, pie, line, stack_bar = support.generate_Graph(df)
        except:
            bar, pie, line, stack_bar = None, None, None, None
        try:
            monthly_data = support.get_monthly_data(df, res=None)
        except:
            monthly_data = []
        try:
            card_data = support.sort_summary(df)
        except:
            card_data = []

        try:
            goals = support.expense_goal(df)
        except:
            goals = []
        try:
            size = 240
            pie1 = support.makePieChart(df, 'Earning', 'Month_name', size=size)
            pie2 = support.makePieChart(df, 'Spend', 'Day_name', size=size)
            pie3 = support.makePieChart(df, 'Investment', 'Year', size=size)
            pie4 = support.makePieChart(df, 'Saving', 'Note', size=size)
            pie5 = support.makePieChart(df, 'Saving', 'Day_name', size=size)
            pie6 = support.makePieChart(df, 'Investment', 'Note', size=size)
        except:
            pie1, pie2, pie3, pie4, pie5, pie6 = None, None, None, None, None, None

        return render_template('home.html',
                               user_name=userdata[0][1],
                               df_size=df.shape[0],
                               df=jsonify(df.to_json()),
                               earning=earning,
                               spend=spend,
                               invest=invest,
                               saving=saving,
                               monthly_data=monthly_data,
                               card_data=card_data,
                               goals=goals,
                               table_data=table_data[:4],
                               bar=bar,
                               line=line,
                               stack_bar=stack_bar,
                               pie1=pie1,
                               pie2=pie2,
                               pie3=pie3,
                               pie4=pie4,
                               pie5=pie5,
                               pie6=pie6,
                               )
    else:  # if not logged-in
        return redirect('/')


@app.route('/home/add_expense', methods=['POST'])
def add_expense():
    if 'user_id' in session:
        user_id = session['user_id']
        if request.method == 'POST':
            date = request.form.get('e_date')
            expense = request.form.get('e_type')
            amount = request.form.get('amount')
            notes = request.form.get('notes')
            try:
                query = """insert into user_expenses (user_id, pdate, expense, amount, pdescription) values 
                ({}, '{}','{}',{},'{}')""".format(user_id, date, expense, amount, notes)
                support.execute_query('insert', query)
                flash("Saved!!")
            except:
                flash("Something went wrong.")
                return redirect("/home")
            return redirect('/home')
    else:
        return redirect('/')


@app.route('/analysis')
def analysis():
    if 'user_id' in session:
        # Fetch user data
        query = """SELECT * FROM user_login WHERE user_id = {}""".format(session['user_id'])
        userdata = support.execute_query('search', query)
        
        # Fetch expense data
        query2 = """SELECT pdate, expense, pdescription, amount FROM user_expenses WHERE user_id = {}""".format(
            session['user_id'])
        data = support.execute_query('search', query2)
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=['Date', 'Expense', 'Note', 'Amount(R)'])
        df = support.generate_df(df)

        if df.shape[0] > 0:
            # Generate visualizations with explanations
            # Expense Distribution (Pie Chart)
            pie = support.meraPie(df=df, names='Expense', values='Amount(R)', hole=0.7, hole_text='Expense',
                                  hole_font=20, height=400, width=400, margin=dict(t=1, b=1, l=1, r=1))
            pie_explanation = "This pie chart shows the distribution of your expenses across different categories."

            # Monthly Trends (Line Chart)
            line = support.meraLine(df=df, x='Date', y='Amount(R)', color='Expense', 
                                   slider=False, show_legend=True, height=400, title="Monthly Spending Trends")
            line_explanation = "This line chart tracks your spending trends over time, showing how your expenses vary month by month."

            # Category Breakdown (Bar Chart)
            bar = support.meraBarChart(df=df.groupby(['Note', "Expense"]).sum().reset_index(), 
                                      x='Note', y='Amount(R)', color="Expense", height=400, 
                                      x_label="Category", y_label="Amount (R)", show_xtick=True, title="Category Breakdown")
            bar_explanation = "This bar chart breaks down your expenses by subcategories, showing where your money is being spent."

            # Spending Heatmap (Heatmap)
            heat = support.meraHeatmap(df, 'Day_name', 'Month_name', height=400, 
                                      title="Transaction count Day vs Month")
            heat_explanation = "This heatmap shows your spending patterns by day and month, highlighting when you spend the most."

            # Calculate insights
            total_spent = df['Amount(R)'].sum()
            avg_monthly_spending = df.groupby('Month')['Amount(R)'].sum().mean()
            largest_expense = df['Amount(R)'].max()
            most_frequent_category = df['Expense'].mode()[0]

            return render_template('analysis.html',
                                 user_name=userdata[0][1],
                                 pie=json.dumps(pie),
                                 bar=json.dumps(bar),
                                 line=json.dumps(line),
                                 heat=json.dumps(heat),
                                 pie_explanation=pie_explanation,
                                 line_explanation=line_explanation,
                                 bar_explanation=bar_explanation,
                                 heat_explanation=heat_explanation,
                                 total_spent=total_spent,
                                 avg_monthly_spending=avg_monthly_spending,
                                 largest_expense=largest_expense,
                                 most_frequent_category=most_frequent_category)
        else:
            flash("No data records to analyze.")
            return redirect('/home')
    else:
        return redirect('/')


@app.route('/profile')
def profile():
    if 'user_id' in session:  # if logged-in
        query = """select * from user_login where user_id = {} """.format(session['user_id'])
        userdata = support.execute_query('search', query)
        return render_template('profile.html', user_name=userdata[0][1], email=userdata[0][2])
    else:  # if not logged-in
        return redirect('/')


@app.route("/updateprofile", methods=['POST'])
def update_profile():
    name = request.form.get('name')
    email = request.form.get("email")
    query = """select * from user_login where user_id = {} """.format(session['user_id'])
    userdata = support.execute_query('search', query)
    query = """select * from user_login where email = "{}" """.format(email)
    email_list = support.execute_query('search', query)
    if name != userdata[0][1] and email != userdata[0][2] and len(email_list) == 0:
        query = """update user_login set username = '{}', email = '{}' where user_id = '{}'""".format(name, email,
                                                                                                      session[
                                                                                                          'user_id'])
        support.execute_query('insert', query)
        flash("Name and Email updated!!")
        return redirect('/profile')
    elif name != userdata[0][1] and email != userdata[0][2] and len(email_list) > 0:
        flash("Email already exists, try another!!")
        return redirect('/profile')
    elif name == userdata[0][1] and email != userdata[0][2] and len(email_list) == 0:
        query = """update user_login set email = '{}' where user_id = '{}'""".format(email, session['user_id'])
        support.execute_query('insert', query)
        flash("Email updated!!")
        return redirect('/profile')
    elif name == userdata[0][1] and email != userdata[0][2] and len(email_list) > 0:
        flash("Email already exists, try another!!")
        return redirect('/profile')

    elif name != userdata[0][1] and email == userdata[0][2]:
        query = """update user_login set username = '{}' where user_id = '{}'""".format(name, session['user_id'])
        support.execute_query('insert', query)
        flash("Name updated!!")
        return redirect("/profile")
    else:
        flash("No Change!!")
        return redirect("/profile")


@app.route('/logout')
def logout():
    try:
        session.pop("user_id")  # delete the user_id in session (deleting session)
        return redirect('/')
    except:  # if already logged-out but in another tab still logged-in
        return redirect('/')


@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    if 'user_id' in session:
        try:
            # First verify the expense belongs to the logged-in user
            verify_query = """SELECT * FROM user_expenses WHERE id = {} AND user_id = {}""".format(
                expense_id, session['user_id'])
            expense = support.execute_query('search', verify_query)
            
            if len(expense) > 0:  # If expense exists and belongs to user
                delete_query = """DELETE FROM user_expenses WHERE id = {}""".format(expense_id)
                support.execute_query('insert', delete_query)
                flash("Expense deleted successfully!")
            else:
                flash("Expense not found or unauthorized!")
        except Exception as e:
            print(e)
            flash("Something went wrong while deleting the expense!")
        return redirect('/home')
    else:
        return redirect('/')


@app.route('/export/csv')
def export_csv():
    if 'user_id' in session:
        query = """select pdate, expense, amount, pdescription from user_expenses where user_id = {}""".format(
            session['user_id'])
        data = support.execute_query('search', query)
        df = pd.DataFrame(data, columns=['Date', 'Expense', 'Amount', 'Note'])
        
        # Create CSV in memory
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=expenses.csv'
        response.headers['Content-type'] = 'text/csv'
        return response
    else:
        return redirect('/')

@app.route('/export/excel')
def export_excel():
    if 'user_id' in session:
        query = """select pdate, expense, amount, pdescription from user_expenses where user_id = {}""".format(
            session['user_id'])
        data = support.execute_query('search', query)
        df = pd.DataFrame(data, columns=['Date', 'Expense', 'Amount', 'Note'])
        
        # Create Excel in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Expenses')
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=expenses.xlsx'
        response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return response
    else:
        return redirect('/')

@app.route('/export/pdf')
def export_pdf():
    if 'user_id' in session:
        query = """select pdate, expense, amount, pdescription from user_expenses where user_id = {}""".format(
            session['user_id'])
        data = support.execute_query('search', query)
        df = pd.DataFrame(data, columns=['Date', 'Expense', 'Amount', 'Note'])
        
        # Create PDF in memory
        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Convert DataFrame to list of lists
        data = [df.columns.to_list()] + df.values.tolist()
        
        # Create table
        table = Table(data)
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ])
        table.setStyle(style)
        elements.append(table)
        
        # Build PDF
        pdf.build(elements)
        buffer.seek(0)
        
        response = make_response(buffer.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=expenses.pdf'
        response.headers['Content-type'] = 'application/pdf'
        return response
    else:
        return redirect('/')

@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    if 'user_id' in session:
        if request.method == 'GET':
            # Fetch the expense record to edit
            query = """SELECT * FROM user_expenses WHERE id = {} AND user_id = {}""".format(
                expense_id, session['user_id'])
            expense = support.execute_query('search', query)
            
            if len(expense) > 0:  # If expense exists and belongs to user
                return render_template('edit_expense.html', expense=expense[0])
            else:
                flash("Expense not found or unauthorized!")
                return redirect('/home')
        
        elif request.method == 'POST':
            # Update the expense record
            date = request.form.get('e_date')
            expense_type = request.form.get('e_type')
            amount = request.form.get('amount')
            notes = request.form.get('notes')
            
            try:
                update_query = """UPDATE user_expenses SET 
                    pdate = '{}', 
                    expense = '{}', 
                    amount = {}, 
                    pdescription = '{}' 
                    WHERE id = {} AND user_id = {}""".format(
                    date, expense_type, amount, notes, expense_id, session['user_id'])
                support.execute_query('insert', update_query)
                flash("Expense updated successfully!")
            except Exception as e:
                print(e)
                flash("Something went wrong while updating the expense!")
            return redirect('/home')
    else:
        return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
