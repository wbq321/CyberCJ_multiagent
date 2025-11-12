#!/usr/bin/env python3
"""
Feedback Viewer - Human-in-the-Loop Data Analysis Tool

This script helps you analyze collected user feedback for improving the RAG system.
"""

import json
import os
from datetime import datetime
from collections import Counter

def load_feedback_data(filename='feedback_data.jsonl'):
    """Load feedback data from JSONL file"""
    feedback_data = []
    if not os.path.exists(filename):
        print(f"No feedback file found: {filename}")
        return feedback_data

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                feedback_data.append(json.loads(line.strip()))
            except json.JSONDecodeError as e:
                print(f"Error parsing line: {e}")

    return feedback_data

def analyze_feedback(feedback_data):
    """Analyze feedback patterns and generate insights"""
    if not feedback_data:
        print("No feedback data to analyze.")
        return

    print("=" * 60)
    print("🔍 FEEDBACK ANALYSIS REPORT")
    print("=" * 60)

    # Basic statistics
    total_feedback = len(feedback_data)
    helpful_count = sum(1 for f in feedback_data if f['feedback_type'] == 'helpful')
    flagged_count = sum(1 for f in feedback_data if f['feedback_type'] == 'flag')

    print(f"\n📊 OVERVIEW:")
    print(f"   Total feedback received: {total_feedback}")
    print(f"   👍 Helpful responses: {helpful_count} ({helpful_count/total_feedback*100:.1f}%)")
    print(f"   🚩 Flagged responses: {flagged_count} ({flagged_count/total_feedback*100:.1f}%)")

    # User profiles analysis
    profiles = Counter(f.get('user_profile', 'unknown') for f in feedback_data)
    print(f"\n👥 USER PROFILES:")
    for profile, count in profiles.items():
        print(f"   {profile}: {count} feedback items")

    # Session analysis
    sessions = Counter(f['session_id'] for f in feedback_data)
    print(f"\n💬 SESSION ACTIVITY:")
    print(f"   Total unique sessions: {len(sessions)}")
    print(f"   Average feedback per session: {total_feedback/len(sessions):.1f}")

    # Show flagged responses that need human review
    flagged_responses = [f for f in feedback_data if f['feedback_type'] == 'flag']
    if flagged_responses:
        print(f"\n🚩 FLAGGED RESPONSES NEEDING REVIEW:")
        print("=" * 60)
        for i, response in enumerate(flagged_responses[-5:], 1):  # Show last 5
            print(f"\n#{i} | {response['timestamp']} | {response['user_profile']}")
            print(f"Query: {response['user_query'][:100]}...")
            print(f"AI Response: {response['ai_response'][:150]}...")
            print("-" * 40)

    return {
        'total': total_feedback,
        'helpful': helpful_count,
        'flagged': flagged_count,
        'flagged_responses': flagged_responses
    }

def export_flagged_for_review(feedback_data, output_file='flagged_responses.json'):
    """Export flagged responses for human expert review"""
    flagged_responses = [f for f in feedback_data if f['feedback_type'] == 'flag']

    if not flagged_responses:
        print("No flagged responses to export.")
        return

    # Create structured data for expert review
    review_data = {
        'export_timestamp': datetime.now().isoformat(),
        'total_flagged': len(flagged_responses),
        'responses_for_review': []
    }

    for response in flagged_responses:
        review_item = {
            'id': response['message_id'],
            'timestamp': response['timestamp'],
            'user_profile': response['user_profile'],
            'user_query': response['user_query'],
            'ai_response': response['ai_response'],
            'expert_review': {
                'status': 'pending',
                'improved_response': '',
                'notes': '',
                'reviewer': '',
                'review_date': ''
            }
        }
        review_data['responses_for_review'].append(review_item)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(review_data, f, indent=2, ensure_ascii=False)

    print(f"\n📤 Exported {len(flagged_responses)} flagged responses to: {output_file}")
    print("Send this file to human experts for review and improvement.")

def main():
    """Main function"""
    print("🤖 CJ-Mentor Feedback Analysis Tool")
    print("Loading feedback data...")

    feedback_data = load_feedback_data()
    analysis = analyze_feedback(feedback_data)

    if analysis and analysis['flagged'] > 0:
        print(f"\n🔄 NEXT STEPS:")
        print("1. Export flagged responses for expert review")
        print("2. Have experts provide improved responses")
        print("3. Integrate improved responses into knowledge base")

        export_choice = input("\nExport flagged responses for expert review? (y/n): ").lower()
        if export_choice == 'y':
            export_flagged_for_review(feedback_data)

if __name__ == "__main__":
    main()