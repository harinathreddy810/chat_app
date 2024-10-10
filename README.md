Project Title: Real-Time Chat Application with Authentication

Description
This project is a web-based chat application designed with user authentication and real-time messaging using Flask and Flask-SocketIO. Users can register, log in, and join a general chat room where they can send messages, view other users’ messages, and see typing indicators. The app is designed to be interactive and user-friendly, featuring a responsive interface built with HTML, CSS, and JavaScript. Messages and user data are securely stored in a SQLite database.

Core Libraries
Flask - Main web framework for building the server-side of the application.
Flask-SocketIO - Enables real-time communication between the client and server.
Flask-Login - Manages user session and authentication.
Werkzeug Security - Provides password hashing and verification for secure login.
SQLite3 - Lightweight database for user data and message storage.
Jinja2 - Flask’s templating engine for rendering HTML templates dynamically.

Key Components and Functions
app.py - Main Application File
Application Initialization: Configures the Flask app with a secret key for session management and initializes the SocketIO instance.
Database Connection (get_db_connection): Connects to the SQLite database and sets the row factory for easy row access.
Database Initialization (init_db): Creates two tables, users for user information and messages for storing chat messages.
User Class (User): Defines a user model compatible with Flask-Login, allowing easy session management.
User Loader (load_user): Loads a user from the database based on their user ID.


Routes
/ (index) - Renders the homepage with options to log in or register.
/register - Handles new user registration, validating input and storing hashed passwords in the database.
/login - Authenticates users by verifying credentials and logs them in.
/chat - Main chatroom interface, requiring users to be logged in. Displays past messages and allows new messages to be sent.
/logout - Logs out the current user, ending their session.


SocketIO Events
send_message: Listens for new messages from users, saves them to the database, and broadcasts them to all connected clients.
typing: Emits a typing indicator when a user is typing, displayed for all connected clients.

HTML Templates
index.html: Main page with links to login and register.
login.html: User login form.
register.html: User registration form.
chat.html: Chat room interface displaying past messages, a message input box, a send button, and typing indicators.

Styles
Custom CSS styling for all HTML templates creates a visually appealing and responsive design. The chat messages are styled distinctly based on the sender, with unique background colors for messages sent by the user versus others in the chat room.

Summary of Features
User Registration and Login: Secure registration with hashed passwords and user login.
Real-Time Chatting: Users can communicate in real-time with message updates visible immediately.
Message History: Persistent message history stored in the database, shown on login.
Typing Indicator: Visual cue showing when another user is typing, enhancing real-time interaction.
