"""
CyberCJ Website Server - Serves both the main website and multi-agent chat
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime

# Add the current directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)

from multi_agent_tutor import create_tutor_system

app = Flask(__name__)
CORS(app)

# Initialize the CJ-Mentor system
try:
    tutor_system = create_tutor_system()
    print("✅ CJ-Mentor system initialized successfully!")
except Exception as e:
    print(f"❌ Failed to initialize CJ-Mentor system: {e}")
    tutor_system = None

# Feedback storage
FEEDBACK_DIR = os.path.join(parent_dir, 'feedback_data')
os.makedirs(FEEDBACK_DIR, exist_ok=True)
FEEDBACK_FILE = os.path.join(FEEDBACK_DIR, 'cybercj_feedback.jsonl')

@app.route('/')
def index():
    """Serve the main CyberCJ website"""
    return send_from_directory('CyberCJ', 'index.html')

@app.route('/CyberCJ/<path:filename>')
def serve_cybercj_static(filename):
    """Serve CyberCJ static files"""
    return send_from_directory('CyberCJ', filename)

@app.route('/multi_agent_chat.html')
def serve_chat():
    """Serve the multi-agent chat interface"""
    return send_from_directory('.', 'multi_agent_chat.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve other static files"""
    # Try to serve from current directory first
    if os.path.exists(os.path.join('.', filename)):
        return send_from_directory('.', filename)
    # Then try CyberCJ directory
    elif os.path.exists(os.path.join('CyberCJ', filename)):
        return send_from_directory('CyberCJ', filename)
    else:
        return "File not found", 404

@app.route('/ask', methods=['POST'])
def ask():
    """Handle chat requests - compatible with existing multi_agent_chat.html"""
    if not tutor_system:
        return jsonify({'error': 'Tutor system not available'}), 500

    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required'}), 400

        user_message = data['question']
        session_id = data.get('session_id', 'default')

        # Get response from CJ-Mentor system
        response_data = tutor_system.chat(user_message, session_id)

        return jsonify({
            'answer': response_data.get('response'),
            'agent_type': response_data.get('agent_type'),
            'scaffolding_level': response_data.get('scaffolding_level'),
            'learning_plan': response_data.get('learning_plan'),
            'current_plan_step': response_data.get('current_plan_step'),
            'total_plan_steps': response_data.get('total_plan_steps'),
            'session_id': session_id
        })

    except Exception as e:
        print(f"Error in ask endpoint: {str(e)}")
        return jsonify({
            'error': 'An error occurred while processing your message.',
            'answer': 'I apologize, but I encountered a technical issue. Please try asking your question again.'
        }), 500

@app.route('/chat_multi_agent', methods=['POST'])
def chat_multi_agent():
    """Handle multi-agent chat requests - alternative endpoint"""
    return ask()  # Redirect to the same handler

@app.route('/new_topic', methods=['POST'])
def new_topic():
    """Handle new topic requests"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')

        # Clear the conversation for this session
        if tutor_system and hasattr(tutor_system, 'conversations'):
            if session_id in tutor_system.conversations:
                del tutor_system.conversations[session_id]

        return jsonify({
            'status': 'success',
            'message': 'New topic session started',
            'session_id': session_id
        })

    except Exception as e:
        print(f"Error in new_topic: {str(e)}")
        return jsonify({'error': 'Failed to start new topic'}), 500

@app.route('/set_profile', methods=['POST'])
def set_profile():
    """Handle profile setting requests"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        profile = data.get('profile', 'general')

        # Update profile in the conversation context if it exists
        if tutor_system and hasattr(tutor_system, 'conversations'):
            if session_id in tutor_system.conversations:
                # Map profile values
                profile_mapping = {
                    'student': 'cj_student',
                    'officer': 'police_officer',
                    'general': 'general'
                }
                tutor_system.conversations[session_id].user_profile = profile_mapping.get(profile, 'general')

        return jsonify({
            'status': 'success',
            'profile': profile,
            'session_id': session_id
        })

    except Exception as e:
        print(f"Error in set_profile: {str(e)}")
        return jsonify({'error': 'Failed to set profile'}), 500

@app.route('/survey.html')
def serve_survey():
    """Serve the survey page"""
    return send_from_directory('.', 'survey.html')

@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    """Handle survey submission"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Create survey data directory
        SURVEY_DIR = os.path.join(parent_dir, 'survey_data')
        os.makedirs(SURVEY_DIR, exist_ok=True)
        SURVEY_FILE = os.path.join(SURVEY_DIR, 'cybercj_surveys.jsonl')

        # Add metadata
        survey_record = {
            'timestamp': datetime.now().isoformat(),
            'survey_version': '1.0',
            'source': 'cybercj_tutor_survey',
            **data  # Include all survey responses
        }

        # Save to JSONL file
        with open(SURVEY_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(survey_record, ensure_ascii=False) + '\n')

        print(f"📊 New survey response recorded: {len(data)} fields")

        return jsonify({
            'status': 'success',
            'message': 'Survey submitted successfully',
            'response_id': f"survey_{int(datetime.now().timestamp())}"
        })

    except Exception as e:
        print(f"Error submitting survey: {str(e)}")
        return jsonify({'error': 'Failed to submit survey'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'tutor_system': 'available' if tutor_system else 'unavailable',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting CyberCJ Website with Multi-Agent Chat Integration...")
    
    # Get port from environment variable (Render sets this automatically)
    port = int(os.environ.get('PORT', 5000))
    print(f"📍 CyberCJ Website: http://127.0.0.1:{port}")
    print(f"💬 Multi-Agent Chat: http://127.0.0.1:{port}/multi_agent_chat.html")
    print(f"🔧 Health Check: http://127.0.0.1:{port}/health")

    app.run(host='0.0.0.0', port=port, debug=False)