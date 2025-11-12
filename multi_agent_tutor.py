# multi_agent_tutor.py - CyberJustice Multi-Agent Tutor System

import os
import json
import time
import re
from typing import Dict, Any, Optional, List
from enum import Enum
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain


def analyze_input_intent(user_input: str, previous_question: str = "", llm=None) -> str:
    """
    Use LLM to intelligently analyze user input to determine if they're answering a previous question or asking something new.
    Returns 'answering' or 'new_question'
    """
    if not user_input:
        return "new_question"

    # If no previous question exists, it must be a new question
    if not previous_question:
        return "new_question"

    # If no LLM provided, fall back to simple heuristics
    if not llm:
        if len(user_input.split()) <= 5 and not user_input.strip().endswith('?'):
            return "answering"
        return "new_question"

    # Use LLM to analyze intent
    try:
        intent_prompt = f"""You are an expert at understanding conversation flow in educational contexts. Analyze the student's input to determine their intent.

PREVIOUS TUTOR QUESTION: "{previous_question}"

STUDENT INPUT: "{user_input}"

TASK: Determine if the student is:
1. ANSWERING the previous tutor question/guidance
2. ASKING a NEW QUESTION about a different topic

ANALYSIS GUIDELINES:
- If student is responding to/addressing the previous question → "answering"
- If student is asking about something completely different → "new_question"
- Consider context: short responses after questions are usually answers
- Consider content: responses that relate to the previous question are usually answers
- Consider format: questions ending with "?" are usually new questions

EXAMPLES:
Previous: "What are the main types of malware?"
Student: "viruses, trojans, and worms" → answering

Previous: "How does encryption work?"
Student: "What is a firewall?" → new_question

Previous: "Can you identify the security risks in this scenario?"
Student: "logs or metadata and electronic communications" → answering

Respond with exactly one word: "answering" or "new_question"
"""

        response = llm.invoke(intent_prompt)
        intent = response.content.strip().lower()

        # Validate response
        if "answering" in intent:
            return "answering"
        elif "new_question" in intent or "new question" in intent:
            return "new_question"
        else:
            # Fallback if LLM response is unclear
            return "answering" if len(user_input.split()) <= 10 else "new_question"

    except Exception as e:
        print(f"Error in LLM intent analysis: {e}")
        # Fallback to simple heuristics
        if len(user_input.split()) <= 5 and not user_input.strip().endswith('?'):
            return "answering"
        return "new_question"


class UserProfile(Enum):
    CJ_STUDENT = "cj_student"
    POLICE_OFFICER = "police_officer"
    GENERAL = "general"

class ScaffoldingLevel(Enum):
    HIGH_SUPPORT = "high_support"      # I Do - Level 3
    GUIDED_SUPPORT = "guided_support"  # We Do - Level 2
    LOW_SUPPORT = "low_support"        # You Do - Level 1

class ConversationContext:
    def __init__(self):
        self.session_id: str = ""
        self.user_profile: UserProfile = UserProfile.GENERAL
        self.current_topic: str = ""
        self.learning_objective: str = ""
        self.knowledge_level: int = 1  # 1-5 scale
        self.scaffolding_level: ScaffoldingLevel = ScaffoldingLevel.HIGH_SUPPORT
        self.last_agent_type: Optional[str] = None  # Now just a string since we use unified agent
        self.last_question: str = ""
        self.conversation_history: List[Dict[str, str]] = []
        self.timestamp: float = time.time()


        self.learning_plan: Optional[List[str]] = None

        self.current_plan_step: int = 0

        self.plan_created_at: float = 0.0
        self.step_completion_status: List[bool] = []
        self.plan_just_completed: bool = False

class UnifiedTutorAgent:
    """
    CJ-Mentor: A personalized AI learning tutor for Cyber Criminal Justice students

    Implements the scaffolding teaching method with dynamic assessment and ZPD-based support.
    Personality: Patient, guiding, logical, encouraging, and highly adaptive.
    Core Philosophy: try not giving direct answers, instead guides students to discover through questioning.
    """
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever

    def _get_profile_instructions(self, profile: UserProfile) -> str:
        """Detailed profile-specific guidance aligned with CJ-Mentor blueprint"""
        if profile == UserProfile.CJ_STUDENT:
            return """Focus on academic depth, theoretical understanding, and connecting concepts to broader criminal justice principles.
            Emphasize critical thinking, legal analysis, and research methodologies. Connect technical concepts to policy implications."""
        elif profile == UserProfile.POLICE_OFFICER:
            return """Emphasize practical applications, operational procedures, and real-world law enforcement scenarios.
            Focus on actionable intelligence, investigative techniques, and court-admissible evidence collection.
            Connect technical knowledge to field operations and case work."""
        else:
            return """Provide balanced approach suitable for general professional development in cybersecurity.
            Bridge theoretical understanding with practical applications across various career paths."""

    def _determine_scaffolding_approach(self, scaffolding_level: ScaffoldingLevel) -> str:
        """Define scaffolding approaches according to CJ-Mentor blueprint"""
        if scaffolding_level == ScaffoldingLevel.HIGH_SUPPORT:
            return """Level 3 (High-Density Support - I Do):
            - Provide clear definitions and detailed step-by-step instructions
            - Give fully worked-out examples with complete explanations
            - Break down complex concepts into digestible components
            - Use concrete examples from real cyber justice cases
            - Demonstrate the complete analytical process"""

        elif scaffolding_level == ScaffoldingLevel.GUIDED_SUPPORT:
            return """Level 2 (Guided Support - We Do):
            - Offer strategic hints and guiding questions
            - Provide templates and partial solutions
            - Ask probing questions to guide thinking
            - Collaborate on problem-solving processes
            - Give feedback on student's reasoning approach"""

        else:  # LOW_SUPPORT
            return """Level 1 (Low-Density Support - You Do):
            - Pose open-ended analytical questions
            - Present challenging scenarios and complex cases
            - Encourage independent critical thinking
            - Set tasks that require synthesis of multiple concepts
            - Challenge students to apply knowledge creatively"""

    def generate_response(self, user_input: str, context: ConversationContext) -> Dict[str, Any]:
        """
        CJ-Mentor's enhanced intelligence: Implements THINK, PLAN, ACT cycle
        for strategic learning guidance with proactive planning capabilities.
        """
        profile_instructions = self._get_profile_instructions(context.user_profile)
        scaffolding_approach = self._determine_scaffolding_approach(context.scaffolding_level)

        # Enhanced retrieval with topic context
        search_query = f"{user_input} {context.current_topic or ''} {context.learning_objective or ''}"
        relevant_docs = self.retriever.invoke(search_query)  # Updated to use invoke instead of deprecated method
        course_content = "\n\n".join([doc.page_content for doc in relevant_docs[:3]])

        # Strategic planning prompt with THINK-PLAN-ACT cycle
        unified_prompt = f"""
You are CJ-Mentor, an expert AI tutor with strategic planning abilities. Your goal is to guide the student through a logical learning path, not just answer questions reactively.

**STUDENT PROFILE:**
- User Type: {context.user_profile.value}
- Profile Guidance: {profile_instructions}
- Current Scaffolding Level: {context.scaffolding_level.value}

**CONVERSATION CONTEXT:**
- Current Topic: {context.current_topic or "Not set"}
- Learning Objective: {context.learning_objective or "To be determined"}
- Previous Tutor Question: "{context.last_question or "None"}"
- **Current Learning Plan:** {context.learning_plan or "None. A new plan needs to be created."}
- **Current Plan Step:** {context.current_plan_step + 1 if context.learning_plan else "No plan exists"}
- **Total Plan Steps:** {len(context.learning_plan) if context.learning_plan else 0}
- **Plan Just Completed:** {context.plan_just_completed}

**STUDENT'S LATEST INPUT:** "{user_input}"

**RELEVANT KNOWLEDGE BASE:**
---
{course_content}
---

**YOUR TASK: Follow the THINK, PLAN, ACT cycle.**

**1. THINK (Internal Assessment & Strategy):**
   - **Topic Analysis:** Is this a new topic, continuation of current topic, or student answering my question?
   - **Student Assessment:** How well did they understand? Are they ready for next step or need more support?
   - **Plan Status:** Should I create new plan, advance current plan, stay on current step, or adapt plan?
   - **Plan Completion Check:** If plan_just_completed is True, congratulate completion and ask what they'd like to learn next
   - **Learning Goal:** What specific learning outcome should this interaction achieve?

**2. PLAN (Strategic Learning Path):**
   - **If plan_just_completed is True:** Acknowledge the completion and ask student what new topic they'd like to explore
   - **If no plan exists OR topic completely changed:** Create a new 4-6 step learning plan that progresses logically from basic understanding to practical application
   - **If plan exists and student succeeded:** Advance to next step (increment plan_step)
   - **If plan exists but student needs help:** Stay on current step, provide more scaffolding
   - **If student asks great unexpected question:** Adapt plan or temporarily deviate then return

**3. ACT (Execute Current Plan Step):**
   - Craft response that directly implements the current plan step
   - Provide appropriate scaffolding level for current step
   - Always end with clear question/challenge aligned with current step
   - Be encouraging and build on student's progress

**SCAFFOLDING APPROACH FOR CURRENT LEVEL:**
{scaffolding_approach}


**OUTPUT FORMAT - RESPOND WITH JSON:**
{{
  "internal_thought": "Your step-by-step thinking process: topic analysis, student assessment, plan decision, and response strategy",
  "updated_plan": {{
    "plan": ["Step 1 description", "Step 2 description", "Step 3 description", "Step 4 description"],
    "plan_step": 0,
    "plan_adaptation": "Explanation of any plan changes or why staying on current step"
  }},
  "scaffolding_adjustment": {{
    "new_scaffolding_level": "HIGH_SUPPORT" | "GUIDED_SUPPORT" | "LOW_SUPPORT",
    "reasoning": "Why this scaffolding level is appropriate for current step"
  }},
  "response_to_student": "Your natural, encouraging response that executes the current plan step and ends with a guiding question"
}}

**EXAMPLE SUCCESSFUL CYCLE:**

Student: "I want to learn about phishing"
Internal Thought: "New topic detected. Student wants to learn phishing. I need to create a comprehensive 4-step plan starting with basic definition and building to practical prevention. This is step 1."
Updated Plan: {{"plan": ["Basic definition and recognition", "Analyze phishing email examples", "Understand attack consequences", "Learn prevention strategies"], "plan_step": 0}}
Response: "Phishing is a crucial cybersecurity topic! Let's build your expertise step by step. To start our learning journey, how would you describe what phishing is in your own words? Don't worry if you're not sure - we'll build from whatever understanding you have."

Now, analyze the current situation and generate your strategic CJ-Mentor response:
"""

        try:
            raw_response = self.llm.invoke(unified_prompt)
            import json

            # Enhanced JSON parsing
            content = raw_response.content.strip()

            # Find JSON boundaries more reliably
            start_idx = content.find('{')
            brace_count = 0
            end_idx = -1

            for i in range(start_idx, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break

            if start_idx != -1 and end_idx != -1:
                json_string = content[start_idx:end_idx]
                parsed_response = json.loads(json_string)

                # Validate and ensure required structure
                if not parsed_response.get("response_to_student"):
                    parsed_response["response_to_student"] = "I'm here to guide your learning journey. What would you like to explore?"

                if not parsed_response.get("updated_plan"):
                    parsed_response["updated_plan"] = {
                        "plan": ["Explore the topic together"],
                        "plan_step": 0,
                        "plan_adaptation": "Created basic exploration plan"
                    }

                if not parsed_response.get("internal_thought"):
                    parsed_response["internal_thought"] = "Engaging with student's learning interests"

                # Log the internal thinking for debugging
                print(f"CJ-Mentor Internal Thought: {parsed_response.get('internal_thought', '')[:100]}...")

                return parsed_response
            else:
                # Fallback with basic plan structure
                return {
                    "internal_thought": "JSON parsing failed, creating basic response",
                    "updated_plan": {
                        "plan": ["Continue learning conversation"],
                        "plan_step": 0,
                        "plan_adaptation": "Fallback plan created"
                    },
                    "scaffolding_adjustment": {
                        "new_scaffolding_level": context.scaffolding_level.value,
                        "reasoning": "Maintaining current level due to parsing error"
                    },
                    "response_to_student": content if content else "That's an interesting point. What specific aspect would you like to explore further?"
                }

        except Exception as e:
            print(f"Error in CJ-Mentor Strategic Planning: {e}")
            # Enhanced fallback with planning structure
            return {
                "internal_thought": f"Error occurred during planning: {str(e)[:50]}. Providing supportive fallback response.",
                "updated_plan": {
                    "plan": ["Understand student's learning goals", "Provide appropriate guidance"],
                    "plan_step": 0,
                    "plan_adaptation": "Emergency fallback plan due to error"
                },
                "scaffolding_adjustment": {
                    "new_scaffolding_level": "HIGH_SUPPORT",
                    "reasoning": "Providing high support due to technical difficulty"
                },
                "response_to_student": "I'm experiencing a momentary difficulty, but let's keep our learning momentum going. What specific aspect of cyber criminal justice interests you most right now?"
            }

class CyberJusticeMultiAgentTutor:
    """
    CJ-Mentor: Advanced Scaffolding-Based Learning System for Cyber Criminal Justice

    Implements the complete CJ-Mentor blueprint with four core modules:
    1. Diagnostic & Assessment Module - Pinpoints knowledge level and learning objectives
    2. Knowledge & Curriculum Module - Structured repository of CJ domain knowledge
    3. Scaffolding Logic Engine - Dynamic support adjustment (I Do -> We Do -> You Do)
    4. State & Progress Tracking Module - Comprehensive learning continuity and analytics

    Personality: Patient, guiding, logical, encouraging, and highly adaptive
    Teaching Philosophy: Guides discovery through questioning rather than direct answers
    """

    def __init__(self, groq_api_key: str, knowledge_file_path: str, vectorstore_path: str):
        self.groq_api_key = groq_api_key
        self.knowledge_file_path = knowledge_file_path
        self.vectorstore_path = vectorstore_path

        # Initialize LLM
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            groq_api_key=groq_api_key,
            temperature=0.4
        )

        # Initialize RAG components
        self.retriever = self._initialize_rag()

        # We only need one powerful agent now
        self.tutor_agent = UnifiedTutorAgent(self.llm, self.retriever)

        # Conversation management
        self.conversations: Dict[str, ConversationContext] = {}

        print("CJ-Mentor Advanced Scaffolding Learning System initialized successfully!")
        print(f"- Diagnostic & Assessment Module: ✓ Active")
        print(f"- Knowledge & Curriculum Module: ✓ Vectorstore loaded")
        print(f"- Scaffolding Logic Engine: ✓ 3-level support system ready")
        print(f"- State & Progress Tracking: ✓ Conversation analytics enabled")

    def _initialize_rag(self):
        """Initialize RAG system with adaptive fallback"""
        try:
            # Load and process documents
            if not os.path.exists(self.knowledge_file_path):
                raise FileNotFoundError(f"Knowledge file not found: {self.knowledge_file_path}")

            loader = TextLoader(self.knowledge_file_path, encoding='utf-8')
            documents = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            split_docs = text_splitter.split_documents(documents)

            # Use optimized embeddings with reduced memory usage
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},  # Force CPU to avoid GPU memory issues
                encode_kwargs={'normalize_embeddings': True, 'batch_size': 1}  # Small batch size
            )

            # Load or create vectorstore
            if os.path.exists(self.vectorstore_path):
                print(f"Loading vectorstore from {self.vectorstore_path}")
                vectorstore = FAISS.load_local(self.vectorstore_path, embeddings, allow_dangerous_deserialization=True)
            else:
                print(f"Creating new vectorstore at {self.vectorstore_path}")
                vectorstore = FAISS.from_documents(split_docs, embeddings)
                vectorstore.save_local(self.vectorstore_path)

            return vectorstore.as_retriever(search_kwargs={"k": 5})

        except Exception as e:
            print(f"Error initializing RAG: {e}")
            raise

    def _get_or_create_context(self, session_id: str, user_profile: str = "general") -> ConversationContext:
        """Get existing conversation context or create new one"""
        if session_id not in self.conversations:
            context = ConversationContext()
            context.session_id = session_id
            context.user_profile = UserProfile(user_profile.lower()) if user_profile.lower() in ['cj_student', 'police_officer'] else UserProfile.GENERAL
            self.conversations[session_id] = context

        return self.conversations[session_id]

    def _update_context(self, context: ConversationContext, user_input: str, agent_output: Dict[str, Any]):
        """
        Enhanced context updating with strategic learning plan management
        Implements comprehensive State & Progress Tracking with plan execution
        """
        # Reset plan completion flag at start of new interaction
        context.plan_just_completed = False

        response_text = agent_output.get("response_to_student", "I'm here to guide your learning journey.")
        updated_plan_data = agent_output.get("updated_plan", {})
        scaffolding_adjustment = agent_output.get("scaffolding_adjustment", {})
        internal_thought = agent_output.get("internal_thought", "")

        # Enhanced conversation history with strategic thinking
        context.conversation_history.append({
            'user_input': user_input,
            'internal_thought': internal_thought,  # Log CJ-Mentor's strategic thinking
            'response': response_text,
            'scaffolding_level': scaffolding_adjustment.get("new_scaffolding_level", context.scaffolding_level.value),
            'plan_step': updated_plan_data.get("plan_step", context.current_plan_step),
            'timestamp': time.time()
        })

        # Update learning plan based on strategic planning output
        if updated_plan_data.get("plan"):
            old_plan = context.learning_plan
            context.learning_plan = updated_plan_data["plan"]

            # Initialize step completion status if new plan
            if old_plan != context.learning_plan:
                context.step_completion_status = [False] * len(context.learning_plan)
                context.plan_created_at = time.time()
                print(f"CJ-Mentor New Learning Plan Created: {len(context.learning_plan)} steps")
                for i, step in enumerate(context.learning_plan):
                    print(f"  Step {i+1}: {step}")

        # Update plan progress
        if updated_plan_data.get("plan_step") is not None:
            old_step = context.current_plan_step
            context.current_plan_step = updated_plan_data["plan_step"]

            # Mark previous step as completed if we advanced
            if old_step < context.current_plan_step and old_step < len(context.step_completion_status):
                context.step_completion_status[old_step] = True
                print(f"CJ-Mentor Step {old_step + 1} Completed! Advancing to Step {context.current_plan_step + 1}")

                # Check if we've completed the final step of the plan
                if context.current_plan_step >= len(context.learning_plan):
                    # Mark plan as completed
                    context.learning_plan = None
                    context.current_plan_step = 0
                    context.step_completion_status = []
                    print(f"CJ-Mentor Learning Plan Completed! Ready for new learning topic.")

            # Also check if we just completed the last step (current_plan_step equals plan length - 1)
            elif context.learning_plan and context.current_plan_step == len(context.learning_plan) - 1:
                # Mark the final step as completed
                if context.current_plan_step < len(context.step_completion_status):
                    context.step_completion_status[context.current_plan_step] = True
                print(f"CJ-Mentor Final Step {context.current_plan_step + 1} Completed! Plan finished.")
                # Set flag that plan is completed (we'll clear it after next response)
                context.plan_just_completed = True

        # Log plan adaptation reasoning
        plan_adaptation = updated_plan_data.get("plan_adaptation", "")
        if plan_adaptation:
            print(f"CJ-Mentor Plan Adaptation: {plan_adaptation}")

        # Update scaffolding level based on strategic assessment
        new_scaffolding = scaffolding_adjustment.get("new_scaffolding_level")
        if new_scaffolding and new_scaffolding.lower() in ['high_support', 'guided_support', 'low_support']:
            old_level = context.scaffolding_level
            context.scaffolding_level = ScaffoldingLevel(new_scaffolding.lower())

            if old_level != context.scaffolding_level:
                reasoning = scaffolding_adjustment.get("reasoning", "Strategic adjustment")
                print(f"CJ-Mentor Scaffolding Adjustment: {old_level.value} → {context.scaffolding_level.value} ({reasoning})")

        # Enhanced question extraction and tracking
        if "?" in response_text:
            questions = [q.strip() + "?" for q in response_text.split("?") if q.strip()]
            if questions:
                context.last_question = questions[-1]
                print(f"CJ-Mentor Next Question: {context.last_question[:50]}...")

        context.timestamp = time.time()

    def _clean_response(self, response: str) -> str:
        """Clean response by removing thinking tags and formatting issues"""
        if not response:
            return response

        # Remove thinking tags
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL | re.IGNORECASE)
        response = re.sub(r'<[^>]*>', '', response)

        # Clean up whitespace
        response = re.sub(r'\n\s*\n', '\n\n', response)
        return response.strip()

    def chat(self, user_input: str, session_id: str = "default", user_profile: str = "general") -> Dict[str, Any]:
        """
        CJ-Mentor: Strategic learning interface with proactive planning capabilities

        Implements complete THINK-PLAN-ACT workflow:
        1. Session Management & Context Retrieval
        2. Strategic Assessment & Planning
        3. Plan Execution & Response Generation
        4. Progress Tracking & Plan Adaptation
        5. Comprehensive Analytics & Feedback
        """
        try:
            # Get conversation context (Session Management)
            context = self._get_or_create_context(session_id, user_profile)

            # Initialize new sessions with CJ-Mentor planning capability
            if len(context.conversation_history) == 0:
                print("CJ-Mentor: Initializing strategic learning session with planning capabilities")

            # Core CJ-Mentor Strategic Intelligence: THINK-PLAN-ACT cycle
            agent_output = self.tutor_agent.generate_response(user_input, context)

            # Extract response for student
            cleaned_response = self._clean_response(agent_output.get("response_to_student", ""))
            if not cleaned_response:
                cleaned_response = "I'm here to guide your strategic learning journey in cyber criminal justice. What would you like to explore today?"

            # Update context with strategic planning data
            self._update_context(context, user_input, agent_output)

            # Enhanced intent analysis for better continuity
            input_intent = analyze_input_intent(user_input, context.last_question, self.llm)

            # Calculate plan progress metrics
            plan_progress = 0
            if context.learning_plan and len(context.learning_plan) > 0:
                completed_steps = sum(context.step_completion_status)
                plan_progress = (completed_steps / len(context.learning_plan)) * 100

            # Comprehensive response data with strategic planning analytics
            response_data = {
                "response": cleaned_response,
                "agent_type": "cj_mentor_strategic",  # Enhanced strategic CJ-Mentor
                "scaffolding_level": context.scaffolding_level.value,
                "user_profile": context.user_profile.value,
                "knowledge_level": context.knowledge_level,
                "input_intent": input_intent,
                "learning_objective": context.learning_objective,
                "current_topic": context.current_topic,
                "session_id": session_id,

                # Strategic Planning Analytics
                "learning_plan": context.learning_plan,
                "current_plan_step": context.current_plan_step + 1 if context.learning_plan else 0,  # 1-indexed for UI
                "total_plan_steps": len(context.learning_plan) if context.learning_plan else 0,
                "plan_progress_percentage": round(plan_progress, 1),
                "step_completion_status": context.step_completion_status,
                "plan_created_at": context.plan_created_at,

                # Enhanced Analytics
                "internal_thought": agent_output.get("internal_thought", ""),
                "plan_adaptation": agent_output.get("updated_plan", {}).get("plan_adaptation", ""),
                "scaffolding_reasoning": agent_output.get("scaffolding_adjustment", {}).get("reasoning", ""),
                "conversation_length": len(context.conversation_history)
            }

            # Log comprehensive learning analytics
            plan_status = f"Step {context.current_plan_step + 1}/{len(context.learning_plan)}" if context.learning_plan else "No active plan"
            print(f"CJ-Mentor Strategic Analytics - "
                  f"Scaffolding: {context.scaffolding_level.value}, "
                  f"Plan: {plan_status}, "
                  f"Progress: {plan_progress:.1f}%, "
                  f"Topic: {context.current_topic or 'General'}")

            return response_data

        except Exception as e:
            print(f"Error in CJ-Mentor Strategic System: {e}")
            # Enhanced error response maintaining strategic planning personality
            return {
                "response": "I'm experiencing a brief technical challenge, but my commitment to your strategic learning remains strong! Your curiosity about cyber criminal justice shows great potential. While I recalibrate my planning systems, could you share what specific learning goal you'd like to achieve? This will help me create an even better strategic learning plan once we're back on track.",
                "error": str(e),
                "agent_type": "cj_mentor_strategic_error",
                "scaffolding_level": "high_support",
                "session_id": session_id,
                "user_profile": user_profile,

                # Basic plan structure for error state
                "learning_plan": ["Recover from technical issue", "Resume strategic learning"],
                "current_plan_step": 1,
                "total_plan_steps": 2,
                "plan_progress_percentage": 0.0
            }

def create_tutor_system():
    """Factory function to create the CJ-Mentor Advanced Scaffolding Learning System"""
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not set in environment variables")

    knowledge_file = './knowledge.txt'
    vectorstore_path = "faiss_index_cybersecurity_navigator"

    return CyberJusticeMultiAgentTutor(groq_api_key, knowledge_file, vectorstore_path)