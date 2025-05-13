from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime, timedelta

# Initialize Flask application and configurations
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # Use a secure random key for session management
socketio = SocketIO(app)
login_manager = LoginManager(app)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('chat.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database
def init_db():
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT,
            username TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
init_db()

# User model
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user_data = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return User(user_data['id'], user_data['username'], user_data['password']) if user_data else None

# Function to format timestamp
def format_timestamp(timestamp):
    now = datetime.now()
    timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

    if timestamp.date() == now.date():
        return f'Today at {timestamp.strftime("%I:%M %p")}'
    elif timestamp.date() == now.date() - timedelta(days=1):
        return f'Yesterday at {timestamp.strftime("%I:%M %p")}'
    else:
        return timestamp.strftime('%B %d, %Y at %I:%M %p')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return "Username and password are required", 400

        hashed_password = generate_password_hash(password)

        # Insert user into database
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Username already exists", 400
        finally:
            conn.close()

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user_data = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data['id'], user_data['username'], user_data['password'])
            login_user(user)
            return redirect(url_for('chat'))
        else:
            return "Invalid username or password", 401
    
    return render_template('login.html')

@app.route('/chat')
@login_required
def chat():
    conn = get_db_connection()
    messages = conn.execute('SELECT * FROM messages ORDER BY timestamp DESC').fetchall()
    conn.close()
    return render_template('chat.html', username=current_user.username, messages=messages)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# SocketIO events
@socketio.on('send_message')
def handle_send_message(data):
    message = data['message']
    username = current_user.username
    room = data['room']

    # Store message in database
    conn = get_db_connection()
    conn.execute('INSERT INTO messages (room, username, message) VALUES (?, ?, ?)', (room, username, message))
    conn.commit()
    
    # Get the current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    formatted_time = format_timestamp(timestamp)  # Format timestamp

    conn.close()

    emit('receive_message', {'message': message, 'username': username, 'timestamp': formatted_time}, broadcast=True)

@socketio.on('typing')
def handle_typing(data):
    emit('user_typing', {'username': current_user.username}, broadcast=True)

# Run the app
if __name__ == '__main__':
    socketio.run(app, port=5000, debug=True)
