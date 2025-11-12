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

        user_message = data.get('question', '').strip()
        if not user_message:
            return jsonify({'error': 'Question cannot be empty'}), 400

        session_id = data.get('session_id', 'default')

        print(f"[DEBUG] Processing message: {user_message[:50]}... (session: {session_id})")

        # Use threading timeout instead of signal (Render compatible)
        import threading
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
        
        def get_ai_response():
            print(f"[DEBUG] Calling tutor_system.chat...")
            response_data = tutor_system.chat(user_message, session_id)
            print(f"[DEBUG] Got response: {str(response_data)[:100]}...")
            return response_data
        
        try:
            # Use thread pool with timeout (works better on cloud platforms)
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(get_ai_response)
                response_data = future.result(timeout=90)  # 90 second timeout
            
            return jsonify({
                'response': response_data.get('response', 'I apologize, but I encountered an issue generating a response.'),
                'answer': response_data.get('response', 'I apologize, but I encountered an issue generating a response.'),
                'agent_type': response_data.get('agent_type'),
                'scaffolding_level': response_data.get('scaffolding_level'),
                'learning_plan': response_data.get('learning_plan'),
                'current_plan_step': response_data.get('current_plan_step'),
                'total_plan_steps': response_data.get('total_plan_steps'),
                'session_id': session_id
            })
        
        except FutureTimeoutError:
            print(f"[ERROR] Timeout processing message: {user_message}")
            return jsonify({
                'error': 'Request timeout - AI processing took too long',
                'answer': 'I apologize, but my response is taking longer than expected. Please try asking a simpler question or try again later.'
            }), 504
            
    except Exception as e:
        print(f"[ERROR] Exception in ask endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'An error occurred while processing your message.',
            'answer': 'I apologize, but I encountered a technical issue. Please try asking your question again.'
        }), 500

@app.route('/chat_multi_agent', methods=['POST'])
def chat_multi_agent():
    """Handle multi-agent chat requests - alternative endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Handle different message field names
        user_message = data.get('message') or data.get('question')
        if not user_message:
            return jsonify({'error': 'Message or question is required'}), 400
            
        # Create compatible request for ask() function
        compatible_data = {
            'question': user_message,
            'session_id': data.get('session_id', 'default')
        }
        
        # Temporarily replace request data
        original_get_json = request.get_json
        request.get_json = lambda: compatible_data
        
        try:
            result = ask()
            return result
        finally:
            request.get_json = original_get_json
            
    except Exception as e:
        print(f"[ERROR] Exception in chat_multi_agent: {str(e)}")
        return jsonify({
            'error': 'Failed to process chat request',
            'response': 'I apologize, but I encountered a technical issue. Please try again.'
        }), 500

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
    """Health check endpoint with detailed diagnostics"""
    try:
        import psutil
        
        # Basic health info
        health_info = {
            'status': 'healthy',
            'tutor_system': 'available' if tutor_system else 'unavailable',
            'timestamp': datetime.now().isoformat(),
            'memory_usage': f"{psutil.virtual_memory().percent:.1f}%",
            'available_memory_mb': f"{psutil.virtual_memory().available / 1024 / 1024:.1f}",
            'cpu_count': psutil.cpu_count(),
            'groq_api_key_set': bool(os.environ.get('GROQ_API_KEY')),
            'tokenizers_parallelism': os.environ.get('TOKENIZERS_PARALLELISM', 'default')
        }
        
        # Test tutor system
        if tutor_system:
            try:
                # Quick test without actual AI call
                test_context = tutor_system._get_or_create_context("health_check", "test")
                health_info['tutor_context_test'] = 'passed'
            except Exception as e:
                health_info['tutor_context_test'] = f'failed: {str(e)}'
        
        return jsonify(health_info)
    
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/test_ai', methods=['POST'])
def test_ai():
    """Quick AI test endpoint for debugging"""
    try:
        if not tutor_system:
            return jsonify({'error': 'Tutor system not available'}), 500
            
        print("[TEST] Starting AI test...")
        
        # Simple test message
        test_message = "Hello, can you help me learn about cybersecurity?"
        test_session = f"test_{int(time.time())}"
        
        import threading
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
        import time
        
        def quick_ai_test():
            return tutor_system.chat(test_message, test_session)
        
        # Short timeout for testing
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(quick_ai_test)
            response_data = future.result(timeout=30)  # 30 second timeout for testing
        
        print("[TEST] AI test completed successfully")
        
        return jsonify({
            'status': 'success',
            'test_message': test_message,
            'response_received': bool(response_data.get('response')),
            'response_length': len(response_data.get('response', '')),
            'agent_type': response_data.get('agent_type'),
            'timestamp': datetime.now().isoformat()
        })
        
    except FutureTimeoutError:
        return jsonify({
            'status': 'timeout',
            'error': 'AI test timed out after 30 seconds',
            'timestamp': datetime.now().isoformat()
        }), 504
        
    except Exception as e:
        print(f"[TEST ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("🚀 Starting CyberCJ Website with Multi-Agent Chat Integration...")
    
    # Get port from environment variable (Render sets this automatically)
    port = int(os.environ.get('PORT', 5000))
    print(f"📍 CyberCJ Website: http://127.0.0.1:{port}")
    print(f"💬 Multi-Agent Chat: http://127.0.0.1:{port}/multi_agent_chat.html")
    print(f"🔧 Health Check: http://127.0.0.1:{port}/health")

    app.run(host='0.0.0.0', port=port, debug=False)