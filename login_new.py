from flask import Flask, request, redirect, url_for, session, flash, get_flashed_messages
from markupsafe import Markup
import smtplib
import random
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# In-memory user store: {username: {first_name, last_name, dob, email, password}}
users = {}

# Temporary storage for signup OTPs: {email: otp}
signup_otps = {}

def send_otp_email(to_email, otp):
    EMAIL_ADDRESS = "your_email@gmail.com"      # <-- Replace with your email
    EMAIL_PASSWORD = "your_app_password"        # <-- Replace with your app password or SMTP password

    msg = EmailMessage()
    msg['Subject'] = "Your OTP for FinSight Signup"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(f"Your OTP for signup verification is: {otp}")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

def get_flash_messages_html():
    messages_html = ""
    for category, message in get_flashed_messages(with_categories=True):
        color = "red" if category == "error" else "green"
        messages_html += f"<p style='color: {color};'>{message}</p>"
    return Markup(messages_html)

@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        user_data = users.get(username, {})
        full_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
        return f"""
            <h1>Welcome, {full_name or username}!</h1>
            <p>You are now logged in.</p>
            <a href='/logout'>Logout</a>
        """
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Step 1: If OTP form submitted
        if 'otp' in request.form:
            email = session.get('signup_email')
            entered_otp = request.form['otp']
            real_otp = signup_otps.get(email)
            if real_otp and entered_otp == real_otp:
                # OTP correct: create user from saved session info
                user_info = session.get('signup_data')
                if user_info:
                    username = user_info['username']
                    users[username] = user_info
                    flash('Signup successful! Please login.', 'success')
                    # Clear temporary signup data
                    signup_otps.pop(email, None)
                    session.pop('signup_data', None)
                    session.pop('signup_email', None)
                    return redirect(url_for('login'))
                else:
                    flash('Session expired. Please signup again.', 'error')
                    return redirect(url_for('signup'))
            else:
                flash('Invalid OTP. Please try again.', 'error')
                return redirect(url_for('signup'))

        # Step 2: If signup form submitted (no OTP yet)
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if username in users:
            flash('Username already exists. Please choose another.', 'error')
            return redirect(url_for('signup'))

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        signup_otps[email] = otp
        session['signup_email'] = email
        session['signup_data'] = {
            'first_name': first_name,
            'last_name': last_name,
            'dob': dob,
            'email': email,
            'username': username,
            'password': password
        }

        # Send OTP email
        try:
            send_otp_email(email, otp)
            flash('OTP sent to your email. Please verify.', 'success')
        except Exception as e:
            flash(f'Failed to send OTP email: {e}', 'error')
            return redirect(url_for('signup'))

        # Show OTP input form
        messages_html = get_flash_messages_html()
        return f"""
            <h1>Verify OTP</h1>
            <form method='post'>
                <label>Enter OTP sent to {email}:</label><br>
                <input type='text' name='otp' required><br><br>
                <button type='submit'>Verify</button>
            </form>
            {messages_html}
        """

    # GET request, show signup form
    messages_html = get_flash_messages_html()
    return f"""
        <h1>Signup</h1>
        <form method='post'>
            <label>First Name:</label><br>
            <input type='text' name='first_name' required><br><br>
            <label>Last Name:</label><br>
            <input type='text' name='last_name' required><br><br>
            <label>DOB:</label><br>
            <input type='date' name='dob' required><br><br>
            <label>Email:</label><br>
            <input type='email' name='email' required><br><br>
            <label>Username:</label><br>
            <input type='text' name='username' required><br><br>
            <label>Password:</label><br>
            <input type='password' name='password' required><br><br>
            <button type='submit'>Signup</button>
        </form>
        <p>Already have an account? <a href='/login'>Login here</a></p>
        {messages_html}
    """

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username]['password'] == password:
            session['username'] = username
            flash(f'Welcome, {username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))

    messages_html = get_flash_messages_html()
    return f"""
        <h1>Login</h1>
        <form method='post'>
            <label>Username:</label><br>
            <input type='text' name='username' required><br><br>
            <label>Password:</label><br>
            <input type='password' name='password' required><br><br>
            <button type='submit'>Login</button>
        </form>
        <p>Don’t have an account? <a href='/signup'>Signup here</a></p>
        {messages_html}
    """

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
