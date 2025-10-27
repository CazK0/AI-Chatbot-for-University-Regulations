from flask import render_template, request, jsonify, session
from app import app
import uuid
from datetime import datetime
import os

chatbot = None
chatbot_error = None

try:
    from app.chatbot import UniversityChatbot
    chatbot = UniversityChatbot()
except Exception as e:
    chatbot_error = str(e)

@app.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if chatbot is None:
            return jsonify({'error': 'Service unavailable'}), 500

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({'error': 'Please enter a message'}), 400
        if len(user_message) > 1000:
            return jsonify({'error': 'Message too long'}), 400

        try:
            bot_response = chatbot.process_message(user_message)
        except Exception as e:
            bot_response = "I encountered an error. Please try again."

        if not bot_response or not bot_response.strip():
            bot_response = "I couldn't generate a response. Please try rephrasing your question."

        try:
            if 'conversations' not in session:
                session['conversations'] = []
            if len(session['conversations']) >= 10:
                session['conversations'] = session['conversations'][-9:]

            session['conversations'].append({
                'timestamp': datetime.now().isoformat(),
                'user_message': user_message[:200],
                'bot_response': bot_response[:500]
            })
            session.modified = True
        except Exception:
            pass

        return jsonify({
            'response': bot_response,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': 'Server error occurred'}), 500

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/history')
def history():
    try:
        conversations = session.get('conversations', [])
        return render_template('history.html', conversations=conversations)
    except Exception:
        return render_template('history.html', conversations=[])

@app.route('/clear_history', methods=['POST'])
def clear_history():
    try:
        session.pop('conversations', None)
        return jsonify({'success': True})
    except Exception:
        return jsonify({'error': 'Could not clear history'}), 500