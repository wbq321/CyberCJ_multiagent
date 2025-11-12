# 紧急备用响应系统
# 当主 AI 系统过载时提供基本功能

EMERGENCY_RESPONSES = {
    "hello": "Hello! I'm CJ-Mentor, your cybersecurity learning assistant. How can I help you today?",
    "help": "I can help you learn about cybersecurity topics including computer security, internet security, and privacy. What would you like to explore?",
    "what is cybersecurity": "Cybersecurity is the practice of protecting digital systems, networks, and data from cyber threats and attacks.",
    "computer security": "Computer security focuses on protecting individual computers and their data from threats like malware, unauthorized access, and data breaches.",
    "internet security": "Internet security involves protecting data and communications while using internet services, including safe browsing, email security, and network protection.",
    "privacy": "Privacy in cybersecurity refers to protecting personal information and maintaining control over how your data is collected, used, and shared.",
    "default": "I'm currently experiencing high load. Please try a more specific question about cybersecurity topics, or try again in a moment."
}

def get_emergency_response(user_input):
    """Provide basic responses when main system is overloaded"""
    user_input_lower = user_input.lower().strip()
    
    # Check for exact matches
    for key, response in EMERGENCY_RESPONSES.items():
        if key in user_input_lower:
            return response
    
    # Return default response
    return EMERGENCY_RESPONSES["default"]