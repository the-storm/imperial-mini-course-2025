from flask import Flask, render_template, request, jsonify, session, redirect
from admin_bot import AdminBot
from db import Database
import hashlib
from functools import wraps
import os


app = Flask(__name__)
db = Database()
admin_bot = AdminBot()
app.secret_key = os.urandom(32)

def authenticated_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('notes.html')
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return render_template('index.html')

@app.route('/note/new')
@authenticated_only
def new_note():
    return render_template('new_note.html')

@app.route('/note/<string:note_id>/<string:view_type>')
@authenticated_only
def view_note(note_id, view_type):
    note = db.get_note_by_id(note_id, session.get('user_id'))

    if not note:
        return redirect('/')
    if note["user_id"] != session.get('user_id'):
       return redirect("/")
    if view_type == "short":
        return render_template('view_note_short.html',note=note)
    elif view_type == "long":
        return render_template('view_note_long.html',note=note,username=db.get_username_from_id(session.get('user_id')))
    # I guess we just return the long view as default
    else:
        return render_template('view_note_long.html',note=note,username=db.get_username_from_id(session.get('user_id')))
    
@app.route('/notes')
@authenticated_only
def notes():
    return render_template('notes.html')


### APIS ###

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    password_hashed = hashlib.sha256(password.encode()).hexdigest()
    user = db.authenticate_user(username, password_hashed)
    if user:
        session['user_id'] = user.get('id')
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
@authenticated_only
def api_logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'})

@app.route('/api/register', methods=['POST'])
def api_create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    password_hashed = hashlib.sha256(password.encode()).hexdigest()
    
    user = db.create_new_user(username, password_hashed)
    if user:
        return jsonify({'message': 'User created successfully'})
    else:
        return jsonify({'error': 'User creation failed'}), 400

@app.route('/api/note/new', methods=['POST'])
@authenticated_only
def api_create_note():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    
    note = db.create_new_note(title, content, session.get('user_id'))
    if note:
        return jsonify({'message': 'Note created successfully'})
    else:
        return jsonify({'error': 'Note creation failed'}), 400

@app.route('/api/note/<int:note_id>', methods=['DELETE'])
@authenticated_only
def api_delete_note(note_id):
    success = db.delete_note_by_id(note_id, session.get('user_id'))
    if success:
        return jsonify({'message': 'Note deleted successfully'})
    else:
        return jsonify({'error': 'Note deletion failed'}), 400

@app.route('/api/note/<int:note_id>', methods=['GET'])
@authenticated_only
def api_get_note(note_id):
    note = db.get_note_by_id(note_id, session.get('user_id'))
    if note:
        return jsonify({'note': note})
    else:
        return jsonify({'error': 'Note not found'}), 404
    
@app.route('/api/notes', methods=['GET'])
@authenticated_only
def api_get_notes():
    notes = db.get_all_notes_for_user(session.get('user_id'))
    return jsonify({'notes': notes})


@app.route('/api/report', methods=['POST'])
def report_note():
    data = request.get_json()
    url = data.get('url')
    cookie_data = data.get('cookie')

    if not url.startswith('http://') and not url.startswith('https://'):
        return jsonify({'error': 'Invalid URL format'}), 400

    if cookie_data and isinstance(cookie_data, dict) and 'name' in cookie_data and 'value' in cookie_data:
        success = admin_bot.visit_with_cookie(url, cookie_data)
    else:
        success = admin_bot.visit(url)
    
    if success:
        return jsonify({'message': 'Report submitted successfully'})
    else:
        return jsonify({'error': 'Failed to process report'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)