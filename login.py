from flask import Flask, request, redirect, url_for, session, flash
from markupsafe import Markup

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# In-memory user store (for demo)
# Store full user details as dict: {username: {details}}
users = {}

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
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if username in users:
            flash('Username already exists. Please choose another.', 'error')
            return redirect(url_for('signup'))

        # Save full user details
        users[username] = {
            'first_name': first_name,
            'last_name': last_name,
            'dob': dob,
            'email': email,
            'password': password
        }
        flash('Signup successful! Please login.', 'success')
        return redirect(url_for('login'))

    messages_html = get_flash_messages_html()
    return f"""
        <h1>Signup</h1>
        <form method='post'>
            <label>First Name:</label>
            <input type='text' name='first_name' required><br><br>
            <label>Last Name:</label>
            <input type='text' name='last_name' required><br><br>
            <label>DOB:</label>
            <input type='date' name='dob' required><br><br>
            <label>Email:</label>
            <input type='email' name='email' required><br><br>
            <label>Username:</label>
            <input type='text' name='username' required><br><br>
            <label>Password:</label>
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
            <label>Username:</label>
            <input type='text' name='username' required><br><br>
            <label>Password:</label>
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

def get_flash_messages_html():
    messages_html = ""
    for category, message in get_flashed_messages(with_categories=True):
        color = "red" if category == "error" else "green"
        messages_html += f"<p style='color: {color};'>{message}</p>"
    return Markup(messages_html)

from flask import get_flashed_messages

if __name__ == '__main__':
    app.run(debug=True)
