from flask import Flask, request, redirect, url_for, session, flash, get_flashed_messages
from markupsafe import Markup
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import secrets
import time
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Secure secret key

# In-memory user store: {username: {first_name, last_name, dob, email, password_hash, created_at, failed_attempts, lockout_until}}
users = {}

# Session timeout (30 minutes)
SESSION_TIMEOUT = 30 * 60

# Account lockout settings
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 15 * 60  # 15 minutes

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, "Password is valid"

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def login_required(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        
        # Check session timeout
        if 'login_time' in session:
            if time.time() - session['login_time'] > SESSION_TIMEOUT:
                session.clear()
                flash('Session expired. Please log in again.', 'error')
                return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

def is_account_locked(username):
    """Check if account is currently locked"""
    if username not in users:
        return False
    
    user = users[username]
    if 'lockout_until' in user and user['lockout_until']:
        if time.time() < user['lockout_until']:
            return True
        else:
            # Lockout expired, reset attempts
            user['failed_attempts'] = 0
            user['lockout_until'] = None
    
    return False

def lock_account(username):
    """Lock user account after too many failed attempts"""
    if username in users:
        users[username]['lockout_until'] = time.time() + LOCKOUT_DURATION

def get_flash_messages_html():
    """Generate HTML for flash messages"""
    messages_html = ""
    for category, message in get_flashed_messages(with_categories=True):
        color = "red" if category == "error" else "green"
        messages_html += f"<p style='color: {color}; padding: 10px; border: 1px solid {color}; border-radius: 4px; margin: 10px 0;'>{message}</p>"
    return Markup(messages_html)

@app.route('/')
@login_required
def index():
    username = session['username']
    user_data = users.get(username, {})
    full_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
    
    return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>FinSight Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
                .logout-btn {{ background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; }}
                .logout-btn:hover {{ background: #c82333; }}
                .user-info {{ background: #f8f9fa; padding: 20px; border-radius: 4px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome, {full_name or username}!</h1>
                    <a href='/logout' class="logout-btn">Logout</a>
                </div>
                <p>You are successfully logged in to FinSight.</p>
                <div class="user-info">
                    <h3>Account Information</h3>
                    <p><strong>Username:</strong> {username}</p>
                    <p><strong>Name:</strong> {full_name}</p>
                    <p><strong>Email:</strong> {user_data.get('email', 'N/A')}</p>
                    <p><strong>Date of Birth:</strong> {user_data.get('dob', 'N/A')}</p>
                    <p><strong>Account Created:</strong> {user_data.get('created_at', 'Unknown')}</p>
                    <p><strong>Last Login:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
    """

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        dob = request.form['dob']
        email = request.form['email'].strip().lower()
        username = request.form['username'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validation
        if not all([first_name, last_name, dob, email, username, password]):
            flash('All fields are required.', 'error')
            return redirect(url_for('register'))
        
        if not validate_email(email):
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))
        
        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('register'))

        if username in users:
            flash('Username already exists. Please choose another.', 'error')
            return redirect(url_for('register'))
        
        # Check if email already exists
        for user_data in users.values():
            if user_data['email'] == email:
                flash('Email already registered. Please use another email.', 'error')
                return redirect(url_for('register'))

        # Create user account
        users[username] = {
            'first_name': first_name,
            'last_name': last_name,
            'dob': dob,
            'email': email,
            'password_hash': generate_password_hash(password),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'failed_attempts': 0,
            'lockout_until': None
        }
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))

    # GET request, show registration form
    messages_html = get_flash_messages_html()
    return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Register - FinSight</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 500px; margin: 20px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .form-group {{ margin-bottom: 20px; }}
                label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                input {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
                button {{ width: 100%; padding: 12px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }}
                button:hover {{ background: #218838; }}
                .password-requirements {{ font-size: 12px; color: #666; margin-top: 5px; }}
                .form-row {{ display: flex; gap: 15px; }}
                .form-row .form-group {{ flex: 1; }}
                .links {{ text-align: center; margin-top: 20px; }}
                .links a {{ color: #007bff; text-decoration: none; }}
                .links a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Create Account</h1>
                <form method='post'>
                    <div class="form-row">
                        <div class="form-group">
                            <label>First Name:</label>
                            <input type='text' name='first_name' required>
                        </div>
                        <div class="form-group">
                            <label>Last Name:</label>
                            <input type='text' name='last_name' required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Date of Birth:</label>
                        <input type='date' name='dob' required>
                    </div>
                    <div class="form-group">
                        <label>Email:</label>
                        <input type='email' name='email' required>
                    </div>
                    <div class="form-group">
                        <label>Username:</label>
                        <input type='text' name='username' required minlength="3">
                    </div>
                    <div class="form-group">
                        <label>Password:</label>
                        <input type='password' name='password' required>
                        <div class="password-requirements">
                            Password must be at least 8 characters with uppercase, lowercase, number, and special character.
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Confirm Password:</label>
                        <input type='password' name='confirm_password' required>
                    </div>
                    <button type='submit'>Create Account</button>
                </form>
                <div class="links">
                    <p>Already have an account? <a href='/login'>Login here</a></p>
                </div>
                {messages_html}
            </div>
        </body>
        </html>
    """

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if not username or not password:
            flash('Username and password are required.', 'error')
            return redirect(url_for('login'))

        if username not in users:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))

        # Check if account is locked
        if is_account_locked(username):
            lockout_time = users[username]['lockout_until']
            remaining_time = int((lockout_time - time.time()) / 60)
            flash(f'Account locked due to too many failed attempts. Try again in {remaining_time} minutes.', 'error')
            return redirect(url_for('login'))

        user = users[username]
        
        if check_password_hash(user['password_hash'], password):
            # Successful login
            session['username'] = username
            session['login_time'] = time.time()
            user['failed_attempts'] = 0  # Reset failed attempts
            user['lockout_until'] = None
            flash(f'Welcome back, {user["first_name"]}!', 'success')
            return redirect(url_for('index'))
        else:
            # Failed login
            user['failed_attempts'] = user.get('failed_attempts', 0) + 1
            
            if user['failed_attempts'] >= MAX_LOGIN_ATTEMPTS:
                lock_account(username)
                flash(f'Account locked due to {MAX_LOGIN_ATTEMPTS} failed login attempts. Please try again in 15 minutes.', 'error')
            else:
                remaining_attempts = MAX_LOGIN_ATTEMPTS - user['failed_attempts']
                flash(f'Invalid username or password. {remaining_attempts} attempts remaining.', 'error')
            
            return redirect(url_for('login'))

    messages_html = get_flash_messages_html()
    return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login - FinSight</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 400px; margin: 50px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .form-group {{ margin-bottom: 20px; }}
                label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                input {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
                button {{ width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }}
                button:hover {{ background: #0056b3; }}
                .links {{ text-align: center; margin-top: 20px; }}
                .links a {{ color: #007bff; text-decoration: none; }}
                .links a:hover {{ text-decoration: underline; }}
                h1 {{ text-align: center; color: #333; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Login to FinSight</h1>
                <form method='post'>
                    <div class="form-group">
                        <label>Username:</label>
                        <input type='text' name='username' required>
                    </div>
                    <div class="form-group">
                        <label>Password:</label>
                        <input type='password' name='password' required>
                    </div>
                    <button type='submit'>Login</button>
                </form>
                <div class="links">
                    <p>Don't have an account? <a href='/register'>Create Account</a></p>
                </div>
                {messages_html}
            </div>
        </body>
        </html>
    """

@app.route('/logout')
def logout():
    username = session.get('username', 'User')
    session.clear()
    flash(f'Goodbye, {username}! You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

# Security headers middleware
@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)