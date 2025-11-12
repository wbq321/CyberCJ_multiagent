"""
CyberCJ Website Flask Server with Integrated CJ-Mentor Chatbot
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime

# Add the parent directory to sys.path to import multi_agent_tutor
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from multi_agent_tutor import UnifiedTutorAgent

app = Flask(__name__)
CORS(app)

# Initialize the CJ-Mentor agent
tutor_agent = UnifiedTutorAgent()

# Feedback storage directory
FEEDBACK_DIR = os.path.join(parent_dir, 'feedback_data')
os.makedirs(FEEDBACK_DIR, exist_ok=True)
FEEDBACK_FILE = os.path.join(FEEDBACK_DIR, 'cybercj_feedback.jsonl')

@app.route('/')
def index():
    """Serve the main CyberCJ website"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, images, etc.)"""
    return send_from_directory('.', filename)

@app.route('/chat_multi_agent', methods=['POST'])
def chat_multi_agent():
    """Handle chat requests from the CJ-Mentor chatbot"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message']
        conversation_id = data.get('conversation_id', 'default')
        
        # Get response from CJ-Mentor
        response_data = tutor_agent.process_message(user_message, conversation_id)
        
        # Format the response for the frontend
        response = {
            'response': response_data.get('response', 'I apologize, but I encountered an error processing your request.'),
            'conversation_id': conversation_id
        }
        
        # Add system message if present (e.g., learning plan updates)
        if 'system_message' in response_data:
            response['system_message'] = response_data['system_message']
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error in chat_multi_agent: {str(e)}")
        return jsonify({
            'error': 'An error occurred while processing your message. Please try again.',
            'response': 'I apologize, but I encountered a technical issue. Please try asking your question again.'
        }), 500

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """Handle feedback submission from users"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Prepare feedback record
        feedback_record = {
            'timestamp': datetime.now().isoformat(),
            'message_id': data.get('message_id'),
            'conversation_id': data.get('conversation_id'),
            'rating': data.get('rating'),  # 'positive' or 'negative'
            'response_text': data.get('response_text'),
            'user_agent': request.headers.get('User-Agent'),
            'source': 'cybercj_website'
        }
        
        # Append to feedback file
        with open(FEEDBACK_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(feedback_record) + '\n')
        
        return jsonify({'status': 'success', 'message': 'Feedback recorded'})
    
    except Exception as e:
        print(f"Error recording feedback: {str(e)}")
        return jsonify({'error': 'Failed to record feedback'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'CyberCJ CJ-Mentor Integration',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status', methods=['GET'])
def api_status():
    """API status endpoint"""
    return jsonify({
        'chatbot_status': 'operational',
        'agent_type': 'UnifiedTutorAgent',
        'features': ['strategic_planning', 'scaffolding', 'feedback_system'],
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("Starting CyberCJ Website with CJ-Mentor Integration...")
    print("Available at: http://127.0.0.1:5001")
    print("Chatbot API: http://127.0.0.1:5001/chat_multi_agent")
    print("Feedback API: http://127.0.0.1:5001/feedback")
    
    app.run(host='127.0.0.1', port=5001, debug=True)