#!/usr/bin/env python3
"""
Script to update frontend API URLs after backend deployment to Render
Run this after deploying your backend to Render
"""

import os
import re
import sys

def update_api_urls(render_url, directory=".", use_relative=False):
    """
    Update API URLs in frontend files to point to Render backend
    
    Args:
        render_url: Your Render service URL (e.g., https://cybercj-backend.onrender.com)
        directory: Directory to search for files (default: current directory)
        use_relative: If True, use relative URLs instead of absolute URLs
    """
    
    # Remove trailing slash
    render_url = render_url.rstrip('/')
    
    # Patterns to find localhost URLs
    patterns = [
        r'http://localhost:5000',
        r'https://localhost:5000',
        r'http://127\.0\.0\.1:5000',
        r'https://127\.0\.0\.1:5000',
        r'localhost:5000',
        r'127\.0\.0\.1:5000'
    ]
    
    # File extensions to check
    extensions = ['.html', '.js', '.css']
    
    updated_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        if any(skip_dir in root for skip_dir in ['.git', '__pycache__', '.conda', 'node_modules', 'faiss_index']):
            continue
            
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Special handling for specific patterns
                    if use_relative:
                        # For frontend deployed separately, use relative URLs
                        replacement = ''
                        # Replace full URLs with relative paths
                        for pattern in patterns:
                            content = re.sub(pattern + r'(/[^\'"\s]*)?', r'\1', content)
                    else:
                        # Replace all localhost patterns with Render URL
                        for pattern in patterns:
                            content = re.sub(pattern, render_url, content)
                    
                    # If content changed, write it back
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        updated_files.append(file_path)
                        
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    return updated_files

def main():
    if len(sys.argv) < 2:
        print("Usage: python update_api_urls.py <render_url> [--relative]")
        print("Example: python update_api_urls.py https://cybercj-backend.onrender.com")
        print("         python update_api_urls.py https://cybercj-backend.onrender.com --relative")
        return
    
    render_url = sys.argv[1]
    use_relative = '--relative' in sys.argv
    
    if use_relative:
        print("Updating API URLs to use relative paths...")
    else:
        print(f"Updating API URLs to point to: {render_url}")
    
    updated_files = update_api_urls(render_url, use_relative=use_relative)
    
    if updated_files:
        print("\nUpdated files:")
        for file_path in updated_files:
            print(f"  - {file_path}")
        print(f"\nTotal files updated: {len(updated_files)}")
    else:
        print("\nNo files needed updating.")
    
    print("\nNext steps:")
    if use_relative:
        print("1. Test your frontend with relative API calls")
        print("2. Ensure your backend handles CORS properly")
    else:
        print("1. Test your frontend with the new backend URL")
        print("2. Commit and push changes to your frontend repository")
        print("3. Redeploy your frontend on Netlify if needed")

if __name__ == "__main__":
    main()