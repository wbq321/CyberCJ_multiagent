"""
CyberCJ Website Server - Serves both the main website and multi-agent chat
"""

# Set environment variables for better stability
import os
os.environ['TOKENIZERS_PARALLELISM'] = 'false'  # Prevent tokenizer warnings
os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers'  # Use tmp for cache

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
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


tutor_system = None

from threading import Lock
tutor_system_lock = Lock()

def get_tutor_system():
    """
    This function gets the tutor system, initializing it on the first call.
    It uses a lock to ensure thread-safety during initialization.
    """
    global tutor_system

    if tutor_system is None:
        with tutor_system_lock:
            if tutor_system is None:
                print("🚀 First request received. Initializing CJ-Mentor system now...")
                try:
                    tutor_system = create_tutor_system()
                    print("✅ CJ-Mentor system initialized successfully!")
                    print(f"📊 Tutor system type: {type(tutor_system)}")
                except Exception as e:
                    print(f"❌ Failed to initialize CJ-Mentor system: {e}")
                    import traceback
                    print(f"📋 Full initialization error: {traceback.format_exc()}")
                    raise e
    return tutor_system

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
    """Handle chat requests with lazy loading of the tutor system."""
    print("=== ASK ENDPOINT CALLED ===")
    try:
        current_tutor_system = get_tutor_system()
        print("📥 Receiving request...")
        data = request.get_json()
        print(f"📊 Request data: {data}")

        if not data or ('question' not in data and 'message' not in data):
            return jsonify({'error': 'Question or message is required'}), 400

        user_message = data.get('question') or data.get('message', '')
        session_id = data.get('session_id', 'default')

        print(f"📝 User message: {user_message}")
        print(f"🔑 Session ID: {session_id}")
        print("🤖 Calling tutor_system.chat()...")

        # Use the instance returned by our function
        response_data = current_tutor_system.chat(user_message, session_id)

        print(f"✅ Got response: {type(response_data)}")
        return jsonify({
            'answer': response_data.get('response'),
            'response': response_data.get('response'),
            'agent_type': response_data.get('agent_type'),
            'scaffolding_level': response_data.get('scaffolding_level'),
            'learning_plan': response_data.get('learning_plan'),
            'current_plan_step': response_data.get('current_plan_step'),
            'total_plan_steps': response_data.get('total_plan_steps'),
            'session_id': session_id
        })

    except Exception as e:
        print(f"💥 ERROR in ask endpoint: {str(e)}")
        import traceback
        print(f"📋 Full traceback: {traceback.format_exc()}")
        return jsonify({
            'error': 'An error occurred while processing your message.',
            'answer': f'I apologize, but I encountered a technical issue: {str(e)}. Please try asking your question again.',
            'response': f'Technical error: {str(e)}'
        }), 500

@app.route('/chat_multi_agent', methods=['POST'])
def chat_multi_agent():
    return ask()

@app.route('/new_topic', methods=['POST'])
def new_topic():
    """Handle new topic requests"""
    try:
        current_tutor_system = get_tutor_system()
        data = request.get_json()
        session_id = data.get('session_id', 'default')

        if current_tutor_system and hasattr(current_tutor_system, 'conversations'):
            if session_id in current_tutor_system.conversations:
                del current_tutor_system.conversations[session_id]

        return jsonify({'status': 'success', 'message': 'New topic session started', 'session_id': session_id})
    except Exception as e:
        print(f"Error in new_topic: {str(e)}")
        return jsonify({'error': 'Failed to start new topic'}), 500

@app.route('/set_profile', methods=['POST'])
def set_profile():
    """Handle profile setting requests"""
    try:
        current_tutor_system = get_tutor_system()

        data = request.get_json()
        session_id = data.get('session_id', 'default')
        profile = data.get('profile', 'general')

        if current_tutor_system and hasattr(current_tutor_system, 'conversations'):
            if session_id in current_tutor_system.conversations:
                profile_mapping = {'student': 'cj_student', 'criminal_justice_professional': 'cj_professional', 'general': 'general'}
                current_tutor_system.conversations[session_id].user_profile = profile_mapping.get(profile, 'general')

        return jsonify({'status': 'success', 'profile': profile, 'session_id': session_id})
    except Exception as e:
        print(f"Error in set_profile: {str(e)}")
        return jsonify({'error': 'Failed to set profile'}), 500

@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    try:
        data = request.get_json()
        if not data: return jsonify({'error': 'No data provided'}), 400
        SURVEY_DIR = os.path.join(parent_dir, 'survey_data')
        os.makedirs(SURVEY_DIR, exist_ok=True)
        SURVEY_FILE = os.path.join(SURVEY_DIR, 'cybercj_surveys.jsonl')
        survey_record = {'timestamp': datetime.now().isoformat(), 'survey_version': '1.0', 'source': 'cybercj_tutor_survey', **data}
        with open(SURVEY_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(survey_record, ensure_ascii=False) + '\n')
        print(f"📊 New survey response recorded: {len(data)} fields")
        return jsonify({'status': 'success', 'message': 'Survey submitted successfully', 'response_id': f"survey_{int(datetime.now().timestamp())}"})
    except Exception as e:
        print(f"Error submitting survey: {str(e)}")
        return jsonify({'error': 'Failed to submit survey'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check endpoint"""
    print("🏥 Health check requested")
    status = {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
    try:
        current_tutor_system = get_tutor_system()
        status['tutor_system'] = 'available'
        test_response = current_tutor_system.chat("Hello", "health_check")
        status['tutor_test'] = 'passed'
        status['test_response_type'] = type(test_response).__name__
    except Exception as e:
        status['tutor_system'] = 'unavailable'
        status['tutor_test'] = 'failed'
        status['tutor_error'] = str(e)
        print(f"🚨 Health check tutor test failed: {e}")
    print(f"🏥 Health status: {status}")
    return jsonify(status)

if __name__ == '__main__':
    print("🚀 Starting CyberCJ Website with Multi-Agent Chat Integration...")

    # Get port from environment variable (Render sets this automatically)
    port = int(os.environ.get('PORT', 5000))
    print(f"📍 CyberCJ Website: http://127.0.0.1:{port}")
    print(f"💬 Multi-Agent Chat: http://127.0.0.1:{port}/multi_agent_chat.html")
    print(f"🔧 Health Check: http://127.0.0.1:{port}/health")

    app.run(host='0.0.0.0', port=port, debug=False)