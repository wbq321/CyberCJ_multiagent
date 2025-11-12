import os
import sys
import psutil
import time
from datetime import datetime

def diagnose_render_environment():
    """Diagnose potential issues in Render environment"""
    
    print("=" * 60)
    print("CyberCJ Render Environment Diagnostic")
    print("=" * 60)
    
    # System info
    print(f"🕒 Current time: {datetime.now()}")
    print(f"🐍 Python version: {sys.version}")
    print(f"💾 Available memory: {psutil.virtual_memory().available / 1024 / 1024:.1f} MB")
    print(f"💾 Used memory: {psutil.virtual_memory().percent:.1f}%")
    print(f"🔧 CPU count: {psutil.cpu_count()}")
    print(f"📁 Current directory: {os.getcwd()}")
    
    # Environment variables
    print(f"\n📋 Environment Variables:")
    print(f"   PORT: {os.environ.get('PORT', 'Not set')}")
    print(f"   GROQ_API_KEY: {'Set' if os.environ.get('GROQ_API_KEY') else 'Not set'}")
    print(f"   TOKENIZERS_PARALLELISM: {os.environ.get('TOKENIZERS_PARALLELISM', 'Not set')}")
    print(f"   TRANSFORMERS_CACHE: {os.environ.get('TRANSFORMERS_CACHE', 'Not set')}")
    
    # File system
    print(f"\n📂 File System:")
    print(f"   knowledge.txt exists: {os.path.exists('knowledge.txt')}")
    print(f"   multi_agent_tutor.py exists: {os.path.exists('multi_agent_tutor.py')}")
    print(f"   FAISS index exists: {os.path.exists('faiss_index_cybersecurity_navigator')}")
    
    # Network connectivity test
    print(f"\n🌐 Network Test:")
    try:
        import requests
        response = requests.get("https://api.groq.com/", timeout=10)
        print(f"   Groq API reachable: ✅ (Status: {response.status_code})")
    except Exception as e:
        print(f"   Groq API reachable: ❌ (Error: {e})")
    
    # Memory pressure test
    print(f"\n🧠 Memory Pressure Test:")
    try:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        print(f"   Tokenizer loading: ✅")
        print(f"   Memory after tokenizer: {psutil.virtual_memory().percent:.1f}%")
    except Exception as e:
        print(f"   Tokenizer loading: ❌ (Error: {e})")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    diagnose_render_environment()