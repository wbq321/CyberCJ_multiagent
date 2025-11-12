# app.py - CyberJustice Multi-Agent Flask API

import os
import json
import time
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()

# Import our multi-agent system
from multi_agent_tutor import create_tutor_system, UserProfile

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app)

# --- Global Variables ---
tutor_system = None
is_loading = False
loading_lock = threading.Lock()

# --- Response Cleaning Function ---
def clean_response(response_text):
    """Clean the response by removing any unwanted formatting"""
    if not response_text:
        return response_text

    # Additional cleaning can be added here if needed
    return response_text.strip()

# --- System Initialization ---
def initialize_tutor_system():
    global tutor_system, is_loading

    with loading_lock:
        if tutor_system or is_loading:
            return
        is_loading = True

    print("Initializing CyberJustice Multi-Agent Tutor System...")

    try:
        tutor_system = create_tutor_system()
        print("CyberJustice Multi-Agent Tutor System initialized successfully!")

    except Exception as e:
        import traceback
        print(f"FATAL ERROR during system initialization: {e}")
        traceback.print_exc()
        raise
    finally:
        with loading_lock:
            is_loading = False

# --- API Endpoint for Chat ---
@app.route('/ask', methods=['POST'])
def ask_question():
    global tutor_system

    if tutor_system is None:
        if is_loading:
            return jsonify({"error": "Multi-agent system is still initializing. Please try again in a moment."}), 503
        else:
            print("Multi-agent system not ready, attempting re-initialization...")
            try:
                initialize_tutor_system()
                if tutor_system is None:
                    return jsonify({"error": "Multi-agent system initialization failed. Check server logs."}), 500
            except Exception as e_reinit:
                print(f"Error during re-initialization attempt: {e_reinit}")
                return jsonify({"error": "Multi-agent system failed to initialize on demand. Check server logs."}), 500

    data = request.get_json()
    user_question = data.get('question')
    session_id = data.get('session_id', 'default')
    user_profile = data.get('user_profile', 'general')  # 'cj_student', 'police_officer', or 'general'

    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    print(f"Received question: {user_question} (session: {session_id}, profile: {user_profile})")

    try:
        # Get response from multi-agent system
        result = tutor_system.chat(
            user_input=user_question,
            session_id=session_id,
            user_profile=user_profile
        )

        if "error" in result:
            return jsonify({"error": result["error"]}), 500

        response_data = {
            "answer": result["response"],
            "agent_type": result["agent_type"],
            "user_profile": result["user_profile"],
            "session_id": result["session_id"]
        }

        print(f"Sending response from {result['agent_type']} agent: {result['response'][:100]}...")
        return jsonify(response_data)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in /ask route: {e}\n{error_details}")
        return jsonify({"error": f"An error occurred while processing: {str(e)}"}), 500

# --- API Endpoint for Setting User Profile ---
@app.route('/set_profile', methods=['POST'])
def set_profile():
    """Allow users to set or change their profile mid-conversation"""
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    user_profile = data.get('user_profile', 'general')

    if user_profile not in ['cj_student', 'police_officer', 'general']:
        return jsonify({"error": "Invalid user profile. Must be 'cj_student', 'police_officer', or 'general'"}), 400

    # Update the conversation context
    if tutor_system and session_id in tutor_system.conversations:
        tutor_system.conversations[session_id].user_profile = UserProfile(user_profile)
        return jsonify({"message": f"Profile updated to {user_profile}", "session_id": session_id})
    else:
        return jsonify({"message": f"Profile will be set to {user_profile} for new conversations", "session_id": session_id})

# --- API Endpoint for Getting Conversation Status ---
@app.route('/status', methods=['GET'])
def get_status():
    """Get conversation status and learning progress"""
    session_id = request.args.get('session_id', 'default')

    if tutor_system and session_id in tutor_system.conversations:
        context = tutor_system.conversations[session_id]
        return jsonify({
            "session_id": session_id,
            "user_profile": context.user_profile.value,
            "current_topic": context.current_topic,
            "last_agent": context.last_agent_type.value if context.last_agent_type else None,
            "conversation_length": len(context.conversation_history)
        })
    else:
        return jsonify({
            "session_id": session_id,
            "message": "No active conversation found",
            "user_profile": "general"
        })

# --- API Endpoint for Starting New Topic ---
@app.route('/new_topic', methods=['POST'])
def start_new_topic():
    """Reset learning progress for a new topic while maintaining profile"""
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    topic_name = data.get('topic', '')

    if tutor_system and session_id in tutor_system.conversations:
        context = tutor_system.conversations[session_id]
        # Reset learning progress but keep profile
        context.current_topic = topic_name
        context.last_question = ""
        # Keep some conversation history but mark new topic
        context.conversation_history.append({
            'action': 'new_topic_started',
            'topic': topic_name,
            'timestamp': time.time()
        })

        return jsonify({
            "message": f"Started new topic: {topic_name}",
            "session_id": session_id
        })
    else:
        return jsonify({"message": "Session not found, will start fresh", "session_id": session_id})

# --- Feedback Collection Endpoint ---
@app.route('/feedback', methods=['POST'])
def collect_feedback():
    """Collect user feedback on AI responses for human-in-the-loop improvement"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['message_id', 'feedback_type', 'user_query', 'ai_response', 'session_id']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Create feedback record
        feedback_record = {
            "message_id": data['message_id'],
            "feedback_type": data['feedback_type'],  # 'helpful' or 'flag'
            "user_query": data['user_query'],
            "ai_response": data['ai_response'],
            "session_id": data['session_id'],
            "user_profile": data.get('user_profile', 'general'),
            "timestamp": data.get('timestamp', time.strftime('%Y-%m-%d %H:%M:%S')),
            "collected_at": time.strftime('%Y-%m-%d %H:%M:%S')
        }

        # Save feedback to file (you can change this to database later)
        feedback_file = 'feedback_data.jsonl'
        with open(feedback_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(feedback_record, ensure_ascii=False) + '\n')

        # Log feedback for monitoring
        feedback_type_emoji = "👍" if data['feedback_type'] == 'helpful' else "🚩"
        print(f"Feedback collected: {feedback_type_emoji} {data['feedback_type']} | Session: {data['session_id']}")
        print(f"Query: {data['user_query'][:100]}...")

        return jsonify({
            "success": True,
            "message": "Feedback collected successfully",
            "feedback_id": data['message_id']
        })

    except Exception as e:
        print(f"Error collecting feedback: {e}")
        return jsonify({"error": "Failed to collect feedback"}), 500

# --- Health Check Endpoint ---
@app.route('/health', methods=['GET'])
def health_check():
    if tutor_system and not is_loading:
        return jsonify({
            "status": "ready",
            "system": "multi-agent",
            "agents": ["orchestrator", "tutor", "technical_explainer", "assessment"]
        }), 200
    elif is_loading:
        return jsonify({"status": "initializing", "message": "Multi-agent tutor system is initializing"}), 503
    else:
        return jsonify({"status": "not_ready", "message": "Multi-agent tutor system not initialized"}), 503

# --- Serve HTML Interface ---
@app.route('/')
def serve_interface():
    """Serve the multi-agent chat interface"""
    try:
        with open('multi_agent_chat.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>CyberJustice Multi-Agent Tutor</h1>
        <p>Interface file not found. Please ensure multi_agent_chat.html exists in the project directory.</p>
        <p>Available endpoints:</p>
        <ul>
            <li>POST /ask - Send questions to the multi-agent system</li>
            <li>POST /set_profile - Set user profile</li>
            <li>GET /status - Get conversation status</li>
            <li>POST /new_topic - Start a new topic</li>
            <li>GET /health - System health check</li>
        </ul>
        """, 200

# --- Background Initialization ---
def start_background_initialization():
    def init_wrapper():
        try:
            initialize_tutor_system()
        except Exception as e_thread_init:
            print(f"FATAL ERROR in background initialization thread: {e_thread_init}")
            global tutor_system, is_loading
            tutor_system = None
            with loading_lock:
                is_loading = False

    init_thread = threading.Thread(target=init_wrapper, daemon=True)
    init_thread.start()

# --- Main Execution ---
if __name__ == '__main__':
    print("Starting CyberJustice Multi-Agent Tutor Flask app...")
    start_background_initialization()
    app.run(host='0.0.0.0', port=5000, debug=False)