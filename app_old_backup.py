# app.py - CyberJustice Pedagogical Tutor (Simplified Version)

import os
import json
import time
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
import threading
import re

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

# --- LLM Initialization Helper ---
def get_llm(model_name="openai/gpt-oss-120b", temperature=0.4):
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set.")
    return ChatGroq(
        model=model_name,
        groq_api_key=GROQ_API_KEY,
        temperature=temperature,
    )

# --- LangChain Setup Function ---
def initialize_navigator_system():
    global primary_faq_chain, is_loading

    with loading_lock:
        if primary_faq_chain or is_loading:
            return
        is_loading = True

    print("Initializing CyberJustice Pedagogical Tutor System...")

    try:
        # Initialize LLM
        specialist_llm = get_llm(model_name="openai/gpt-oss-120b", temperature=0.4)
        print(f"Successfully initialized CyberJustice Tutor LLM: openai/gpt-oss-120b")

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

        # Define the pedagogical prompt template
        faq_prompt_template_str = """You are a Senior Cybercrime Analyst with over 15 years of experience in law enforcement and cybersecurity. You are teaching criminal justice students about cybersecurity concepts from the CyberCJ curriculum.

CONVERSATION CONTEXT:
Previous tutor question: {previous_question}
Current student input: {question}

CRITICAL PEDAGOGICAL STRATEGY - PROGRESSIVE LEARNING WITH COMPLETION:
- Give ONLY ONE question OR ONE small exercise per response
- Keep responses short (6-7 sentences maximum)
- Build understanding progressively through multiple exchanges
- RECOGNIZE when learning objective is achieved and provide CLOSURE
- Don't overwhelm with multiple tasks or questions

COMPLETION RECOGNITION:
- If student has answered 2-3 related questions correctly on a topic, CONCLUDE the learning sequence
- Provide a brief summary acknowledgment and suggest moving to a new topic
- Don't drill endlessly - recognize successful learning completion

ADAPTIVE RESPONSE APPROACH:
1. ANALYZE the student's input in context:
   - If previous_question is empty/None: This is a NEW topic (start learning sequence)
   - If previous_question exists: CAREFULLY determine if the student input is:
     a) ANSWERING the previous question (look for factual statements, definitions, explanations)
     b) ASKING a new question (look for question words, request for information)

   ANSWER INDICATORS: Student provides statements like "This type of malware...", "It means...", "The process involves...", definitions, explanations, single-word answers like "confidentiality"
   QUESTION INDICATORS: Student asks "What is...", "How does...", "Can you explain..."

2. RESPOND APPROPRIATELY based on progression:
   - NEW TOPIC: "Let's explore [topic]. Start by looking at [specific section]. What does it say about [one specific aspect]?"
   - FIRST CORRECT ANSWER (0-1 previous correct): "Excellent: '[quote their answer]' Now let's examine [next logical step]."
   - SECOND CORRECT ANSWER (1-2 previous correct): "Perfect: '[quote their answer]' You're building good understanding. One more aspect: [final question]"
   - COMPLETION TRIGGER (2+ previous correct): "Outstanding work! You've demonstrated solid understanding of [topic]: [brief summary]. You're ready to tackle new cybersecurity concepts. What would you like to explore next?"
   - PARTIAL ANSWER: "Good start with '[quote]'. Let me guide you to [specific course section] to complete this."
   - NEW QUESTION (different topic): Start fresh sequence for new topic

3. COURSE GROUNDING:
   - Always reference the specific course content provided in Context
   - Don't invent module numbers not mentioned in Context
   - Guide students to discover answers in the course materials
   - Use course terminology and examples exactly as presented

RESPONSE FORMAT:
- Keep it conversational but professional
- Focus on ONE learning step only per response
- Provide CLOSURE when learning objective is achieved

Context from CyberCJ curriculum:
{context}

Your response as Senior Cybercrime Analyst (recognize completion when appropriate):"""

        FAQ_CHAIN_PROMPT = PromptTemplate(
            input_variables=["context", "question", "previous_question"],
            template=faq_prompt_template_str,
        )

        # Create a custom chain with conversation context
        from langchain.chains.question_answering import load_qa_chain

        # Create the document chain that will handle conversation context
        primary_faq_chain = load_qa_chain(
            llm=specialist_llm,
            chain_type="stuff",
            prompt=FAQ_CHAIN_PROMPT
        )

        # Store the retriever separately for document retrieval
        global retriever
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

        print("CyberJustice Pedagogical Tutor Chain initialized.")

    except Exception as e:
        import traceback
        print(f"FATAL ERROR during system initialization: {e}")
        traceback.print_exc()
        raise
    finally:
        with loading_lock:
            is_loading = False

    print("CyberJustice Pedagogical Tutor System initialized successfully.")

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
    session_id = data.get('session_id', 'default')  # Simple session management

    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    print(f"Received question: {user_question} (session: {session_id})")

    try:
        # Get conversation context
        session_memory = conversation_memory.get(session_id, {})
        previous_question = session_memory.get('last_question', '')
        current_topic = session_memory.get('current_topic', '')
        correct_answers_count = session_memory.get('correct_answers', 0)

        # Simple topic detection (first few words of user's question/answer)
        if not previous_question:  # New conversation or topic
            new_topic = user_question.lower().split()[:3]  # First 3 words as topic indicator
            current_topic = ' '.join(new_topic)
            correct_answers_count = 0

        # Retrieve relevant documents
        relevant_docs = retriever.get_relevant_documents(user_question)

        # Prepare context for the chain
        context = "\n\n".join([doc.page_content for doc in relevant_docs])

        # Add progression context to the LLM
        progression_context = f"\nCURRENT LEARNING PROGRESSION:\n- Topic: {current_topic}\n- Previous correct answers in this topic: {correct_answers_count}\n- Learning status: {'Near completion' if correct_answers_count >= 2 else 'Building understanding'}"

        enhanced_context = context + progression_context        # Call the chain with conversation context
        print(f"  Consulting CyberJustice Tutor with conversation context...")
        print(f"  Previous question: {previous_question}")

        faq_response = primary_faq_chain.invoke({
            "input_documents": relevant_docs,
            "context": enhanced_context,
            "question": user_question,
            "previous_question": previous_question
        })

        faq_answer = faq_response.get("output_text")

        if faq_answer:
            print(f"  CyberJustice Tutor responded: {faq_answer}")
            final_answer = clean_tutor_response(faq_answer)

            # Update conversation memory with progression tracking
            if "?" in final_answer:
                # Extract the question the tutor asked
                tutor_questions = [s.strip() + "?" for s in final_answer.split("?") if s.strip()]
                if tutor_questions:
                    last_tutor_question = tutor_questions[-1]  # Get the last question

                    # Check if this seems to be building on previous answer (indicating correct answer)
                    is_building_answer = any(phrase in final_answer.lower() for phrase in [
                        "excellent", "perfect", "outstanding", "good start", "well done", "correct"
                    ])

                    if is_building_answer and previous_question:
                        correct_answers_count += 1

                    conversation_memory[session_id] = {
                        'last_question': last_tutor_question,
                        'current_topic': current_topic,
                        'correct_answers': correct_answers_count,
                        'timestamp': time.time()
                    }
                    print(f"  Stored tutor question: {last_tutor_question}")
                    print(f"  Topic progression: {current_topic} - {correct_answers_count} correct answers")
            else:
                # Check if this is a completion response
                is_completion = any(phrase in final_answer.lower() for phrase in [
                    "outstanding work", "you've demonstrated", "you're ready", "solid understanding"
                ])

                if is_completion:
                    # Reset for new topic
                    conversation_memory[session_id] = {
                        'last_question': '',
                        'current_topic': '',
                        'correct_answers': 0,
                        'timestamp': time.time()
                    }
                    print(f"  Topic completed, memory reset")
                else:
                    # Keep current state but no new question
                    conversation_memory[session_id] = {
                        'last_question': '',
                        'current_topic': current_topic,
                        'correct_answers': correct_answers_count,
                        'timestamp': time.time()
                    }
        else:
            final_answer = "I'm having trouble accessing the curriculum materials right now. Let me try to help you think through this concept another way."

        print(f"Sending final answer: {final_answer}")
        return jsonify({"answer": final_answer})

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in /ask route: {e}\n{error_details}")
        return jsonify({"error": f"An error occurred while processing: {str(e)}"}), 500

# --- Health Check Endpoint ---
@app.route('/health', methods=['GET'])
def health_check():
    if primary_faq_chain and retriever and not is_loading:
        return jsonify({"status": "ready"}), 200
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
    print("Starting CyberJustice Pedagogical Tutor Flask app...")
    start_background_initialization()
    app.run(host='0.0.0.0', port=5000, debug=False)
