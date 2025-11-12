# app.py - CyberJustice Improved Pedagogical Tutor (Fixed Conversation Flow)

import os
import json
import time
import re
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain.chains.question_answering import load_qa_chain
from langchain_core.prompts import PromptTemplate
import threading

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app)

# --- Global Variables for LangChain components ---
primary_faq_chain = None
retriever = None
is_loading = False
loading_lock = threading.Lock()

# --- Simple Conversation Memory (for session management) ---
conversation_memory = {}

# --- Configurations ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
KNOWLEDGE_FILE_PATH = './knowledge.txt'
VECTORSTORE_PATH = "faiss_index_cybersecurity_navigator"

# --- Response Cleaning Function ---
def clean_tutor_response(response_text):
    """Clean the tutor response by removing thinking tags and formatting issues"""
    if not response_text:
        return response_text

    # Remove <think> tags and their content
    response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL | re.IGNORECASE)

    # Remove any remaining angle bracket content that might be thinking
    response_text = re.sub(r'<[^>]*>', '', response_text)

    # Clean up extra whitespace
    response_text = re.sub(r'\n\s*\n', '\n\n', response_text)
    response_text = response_text.strip()

    return response_text

def analyze_input_intent(user_input, previous_question, conversation_context):
    """
    Analyze whether user input is answering previous question or asking new question
    Returns: 'answering', 'new_question', or 'unclear'
    """
    if not previous_question:
        return 'new_question'

    user_input_lower = user_input.lower().strip()

    # Check for question indicators
    question_indicators = ['what', 'how', 'why', 'when', 'where', 'can you', 'could you', 'please', '?']
    is_question = any(indicator in user_input_lower for indicator in question_indicators) or user_input.endswith('?')

    # Check for answer indicators (short responses that don't contain question words)
    if len(user_input.split()) <= 10 and not is_question:
        # Short responses are likely answers
        return 'answering'

    # Check for specific answer patterns
    answer_patterns = [
        r'^(yes|no)\b',
        r'^(confidentiality|integrity|availability)\b',
        r'^(malware|virus|trojan|worm|spyware|ransomware)\b',
        r'^(a|an|the)?\s*(hacker|cybercriminal|attacker)',
        r'(information|data)\s+(is|are)\s+(collected|stolen|modified)',
        r'(type|kind)\s+of\s+(malware|attack|threat)',
    ]

    for pattern in answer_patterns:
        if re.search(pattern, user_input_lower):
            return 'answering'

    # If contains question words, likely a new question
    if is_question:
        return 'new_question'

    # Default to answering if we have a previous question and no clear question indicators
    return 'answering' if previous_question else 'new_question'

# --- LLM Initialization Helper ---
def get_llm(model_name="llama-3.1-8b-instant", temperature=0.4):
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set.")
    return ChatGroq(
        model=model_name,
        groq_api_key=GROQ_API_KEY,
        temperature=temperature,
    )

# --- LangChain Setup Function ---
def initialize_navigator_system():
    global primary_faq_chain, retriever, is_loading

    with loading_lock:
        if primary_faq_chain or is_loading:
            return
        is_loading = True

    print("Initializing CyberJustice Improved Pedagogical Tutor System...")

    try:
        # Initialize LLM
        specialist_llm = get_llm(model_name="llama-3.1-8b-instant", temperature=0.4)
        print(f"Successfully initialized CyberJustice Tutor LLM: llama-3.1-8b-instant")

        # Initialize components
        print("Initializing CyberJustice Tutor components...")
        if not os.path.exists(KNOWLEDGE_FILE_PATH):
            print(f"Error: Knowledge file not found at {KNOWLEDGE_FILE_PATH}")
            raise FileNotFoundError(f"Knowledge file not found: {KNOWLEDGE_FILE_PATH}")

        loader = TextLoader(KNOWLEDGE_FILE_PATH, encoding='utf-8')
        documents = loader.load()
        if not documents:
            print("Error: No documents loaded from knowledge file.")
            raise ValueError("No documents loaded from knowledge file.")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        split_docs = text_splitter.split_documents(documents)
        if not split_docs:
            print("Error: No documents after splitting for FAQ agent.")
            raise ValueError("No documents after splitting for FAQ agent.")

        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        if os.path.exists(VECTORSTORE_PATH):
            print(f"Loading vectorstore from {VECTORSTORE_PATH}")
            vectorstore = FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)
        else:
            print(f"Creating new vectorstore at {VECTORSTORE_PATH}")
            vectorstore = FAISS.from_documents(split_docs, embeddings)
            vectorstore.save_local(VECTORSTORE_PATH)
        print("CyberJustice Tutor Vectorstore initialized.")

        # Store the retriever
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

        # Define the improved pedagogical prompt template
        faq_prompt_template_str = """You are a Senior Cybercrime Analyst with over 15 years of experience in law enforcement and cybersecurity. You are teaching criminal justice students about cybersecurity concepts from the CyberCJ curriculum.

CONVERSATION ANALYSIS:
Previous question I asked: {previous_question}
Student's current input: {question}
Input intent: {input_intent}
Learning progression: Stage {learning_stage}, Correct answers: {correct_answers}

CRITICAL PEDAGOGICAL STRATEGY:
1. RECOGNIZE CONVERSATION FLOW:
   - If input_intent is "answering": Student is responding to my previous question
   - If input_intent is "new_question": Student is asking about a new topic
   - If input_intent is "unclear": Clarify what they mean

2. ADAPTIVE RESPONSE BASED ON PROGRESSION:
   - If learning_stage >= 3 AND correct_answers >= 2: PROVIDE COMPLETION
   - If learning_stage >= 4: Conclude the topic and offer new learning
   - Otherwise: Continue guided discovery

3. RESPONSE TYPES:

   WHEN STUDENT IS ANSWERING (input_intent = "answering"):
   - If answer is good: "Excellent! [quote their answer]. You've grasped [concept]. [COMPLETION or NEXT STEP]"
   - If answer is partial: "Good start with '[quote]'. Now think about [specific refinement]..."
   - If answer is wrong: "I see you're thinking '[quote]'. Let me guide you to [course section]..."

   WHEN STUDENT ASKS NEW QUESTION (input_intent = "new_question"):
   - "Let's explore [topic]. Start by looking at [specific course section]. What does it say about [one aspect]?"

   COMPLETION CRITERIA (when learning_stage >= 3 AND correct_answers >= 2):
   - "Excellent work! You've demonstrated solid understanding of [topic]. You now know: [summarize key points]. Ready to apply this to real scenarios or explore a new cybersecurity topic?"

COURSE GROUNDING RULES:
- Always reference specific course content provided in Context
- Use exact course terminology and examples
- Guide to discovery rather than direct answers
- Keep responses 2-3 sentences maximum

Context from CyberCJ curriculum:
{context}

Your response as Senior Cybercrime Analyst (guide discovery, recognize completion):"""

        FAQ_CHAIN_PROMPT = PromptTemplate(
            input_variables=["context", "question", "previous_question", "input_intent", "learning_stage", "correct_answers"],
            template=faq_prompt_template_str,
        )

        # Create the document chain
        primary_faq_chain = load_qa_chain(
            llm=specialist_llm,
            chain_type="stuff",
            prompt=FAQ_CHAIN_PROMPT
        )

        print("CyberJustice Improved Pedagogical Tutor Chain initialized.")

    except Exception as e:
        import traceback
        print(f"FATAL ERROR during system initialization: {e}")
        traceback.print_exc()
        raise
    finally:
        with loading_lock:
            is_loading = False

    print("CyberJustice Improved Pedagogical Tutor System initialized successfully.")

# --- API Endpoint for Chat ---
@app.route('/ask', methods=['POST'])
def ask_question():
    global primary_faq_chain, retriever

    if primary_faq_chain is None or retriever is None:
        if is_loading:
            return jsonify({"error": "Bot system is still initializing. Please try again in a moment."}), 503
        else:
            print("Core components not ready, attempting re-initialization...")
            try:
                initialize_navigator_system()
                if primary_faq_chain is None or retriever is None:
                    return jsonify({"error": "Bot system initialization failed. Check server logs."}), 500
            except Exception as e_reinit:
                print(f"Error during re-initialization attempt: {e_reinit}")
                return jsonify({"error": "Bot system failed to initialize on demand. Check server logs."}), 500

    data = request.get_json()
    user_question = data.get('question')
    session_id = data.get('session_id', 'default')

    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    print(f"Received question: {user_question} (session: {session_id})")

    try:
        # Get conversation context
        session_memory = conversation_memory.get(session_id, {})
        previous_question = session_memory.get('last_question', '')
        learning_stage = session_memory.get('learning_stage', 0)
        correct_answers = session_memory.get('correct_answers', 0)

        # Analyze input intent
        input_intent = analyze_input_intent(user_question, previous_question, session_memory)

        print(f"  Previous question: {previous_question}")
        print(f"  Input intent: {input_intent}")
        print(f"  Learning stage: {learning_stage}, Correct answers: {correct_answers}")

        # Retrieve relevant documents
        relevant_docs = retriever.get_relevant_documents(user_question)
        context = "\n\n".join([doc.page_content for doc in relevant_docs])

        # Call the chain with enhanced context
        print(f"  Consulting CyberJustice Tutor with improved conversation analysis...")

        faq_response = primary_faq_chain.invoke({
            "input_documents": relevant_docs,
            "context": context,
            "question": user_question,
            "previous_question": previous_question or "None",
            "input_intent": input_intent,
            "learning_stage": learning_stage,
            "correct_answers": correct_answers
        })

        faq_answer = faq_response.get("output_text")

        if faq_answer:
            print(f"  CyberJustice Tutor responded: {faq_answer}")
            final_answer = clean_tutor_response(faq_answer)

            # Update conversation memory with smarter progression tracking
            new_stage = learning_stage
            new_correct = correct_answers

            # Increment stage for any interaction
            if input_intent != 'unclear':
                new_stage += 1

            # Detect correct answers based on response content
            response_lower = final_answer.lower()
            if any(praise in response_lower for praise in ['excellent', 'correct', 'good', 'well done', 'right', 'exactly']):
                if input_intent == 'answering':  # Only count as correct if they were answering
                    new_correct += 1

            # Store what the tutor asked for next interaction
            tutor_question = ""
            if "?" in final_answer:
                questions = [s.strip() + "?" for s in final_answer.split("?") if s.strip()]
                if questions:
                    tutor_question = questions[-1]

            # Update memory
            conversation_memory[session_id] = {
                'last_question': tutor_question,
                'learning_stage': new_stage,
                'correct_answers': new_correct,
                'timestamp': time.time(),
                'last_user_input': user_question,
                'last_intent': input_intent
            }

            print(f"  Updated memory - Stage: {new_stage}, Correct: {new_correct}, Next question: {tutor_question}")

        else:
            final_answer = "I'm having trouble accessing the curriculum materials right now. Let me try to help you think through this concept another way."

        print(f"Sending final answer: {final_answer}")
        return jsonify({
            "answer": final_answer,
            "learning_stage": conversation_memory[session_id].get('learning_stage', 0),
            "correct_answers": conversation_memory[session_id].get('correct_answers', 0),
            "input_intent": input_intent,
            "session_id": session_id
        })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in /ask route: {e}\n{error_details}")
        return jsonify({"error": f"An error occurred while processing: {str(e)}"}), 500

# --- API Endpoint for New Topic ---
@app.route('/new_topic', methods=['POST'])
def new_topic():
    """Reset learning progress for a new topic"""
    data = request.get_json()
    session_id = data.get('session_id', 'default')

    conversation_memory[session_id] = {
        'last_question': '',
        'learning_stage': 0,
        'correct_answers': 0,
        'timestamp': time.time()
    }

    return jsonify({"message": "Started new topic", "session_id": session_id})

# --- Health Check Endpoint ---
@app.route('/health', methods=['GET'])
def health_check():
    if primary_faq_chain and retriever and not is_loading:
        return jsonify({"status": "ready", "system": "improved_pedagogical_tutor"}), 200
    elif is_loading:
        return jsonify({"status": "initializing", "message": "Tutor system is initializing"}), 503
    else:
        return jsonify({"status": "not_ready", "message": "Tutor system not initialized"}), 503

# --- Function to run initialization in a background thread ---
def start_background_initialization():
    def init_wrapper():
        try:
            initialize_navigator_system()
        except Exception as e_thread_init:
            print(f"FATAL ERROR in background initialization thread: {e_thread_init}")
            global primary_faq_chain, retriever, is_loading
            primary_faq_chain = None
            retriever = None
            with loading_lock:
                is_loading = False

    init_thread = threading.Thread(target=init_wrapper, daemon=True)
    init_thread.start()

# --- Main Execution ---
if __name__ == '__main__':
    print("Starting CyberJustice Improved Pedagogical Tutor Flask app...")
    start_background_initialization()
    app.run(host='0.0.0.0', port=5000, debug=False)