"""
Simple Article Generation Test Script
This script tests the backend API and saves articles as markdown files.
"""

import requests
import json
import os
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
OUTPUT_FOLDER = "output"

def create_output_folder():
    """Create output folder if it doesn't exist."""
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"✅ Created output folder: {OUTPUT_FOLDER}")

def test_backend_health():
    """Test if backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("✅ Backend is healthy and running")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print(f"   Make sure the server is running on {BACKEND_URL}")
        return False

def generate_article(topic, depth="intermediate"):
    """Generate an article and save it as markdown."""
    print(f"\n🚀 Generating article for topic: '{topic}'")
    print(f"   Target audience: {depth}")
    
    try:
        # Create job
        job_data = {
            "topic": topic,
            "desired_depth": depth,
            "max_length": 5000,
            "include_visuals": True
        }
        
        print("   📝 Creating job...")
        response = requests.post(f"{BACKEND_URL}/v1/jobs", json=job_data)
        
        if response.status_code != 200:
            print(f"   ❌ Failed to create job: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        job_result = response.json()
        job_id = job_result["job_id"]
        print(f"   ✅ Job created: {job_id}")
        
        # Get job result
        print("   📊 Fetching results...")
        result_response = requests.get(f"{BACKEND_URL}/v1/jobs/{job_id}")
        
        if result_response.status_code != 200:
            print(f"   ❌ Failed to get job result: {result_response.status_code}")
            return False
        
        job_data = result_response.json()
        
        if "result" not in job_data or "article" not in job_data["result"]:
            print("   ❌ No article found in job result")
            print(f"   Job data: {json.dumps(job_data, indent=2)}")
            return False
        
        article = job_data["result"]["article"]
        
        # Display article info
        print(f"   📖 Article Title: {article.get('title', 'No title')}")
        print(f"   📝 Word Count: {article.get('word_count', 0)}")
        print(f"   🤖 AI Powered: {article.get('ai_powered', False)}")
        print(f"   🔧 Generation Method: {article.get('generation_method', 'unknown')}")
        
        # Save to markdown file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_topic = safe_topic.replace(' ', '_')
        filename = f"{timestamp}_{safe_topic}.md"
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        
        # Create markdown content
        markdown_content = f"""# Article Generation Test Results

**Generated on:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Topic:** {topic}  
**Target Audience:** {depth}  
**Job ID:** {job_id}  
**AI Powered:** {article.get('ai_powered', False)}  
**Generation Method:** {article.get('generation_method', 'unknown')}  
**Word Count:** {article.get('word_count', 0)}  

---

{article.get('content', 'No content available')}

---

**Metadata:**
```json
{json.dumps(job_data.get('result', {}).get('metadata', {}), indent=2)}
```
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"   ✅ Article saved to: {filepath}")
        print(f"   📄 File size: {os.path.getsize(filepath)} bytes")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error generating article: {e}")
        return False

def main():
    """Main function to run the test."""
    print("🧪 Article Generation Test Script")
    print("=" * 50)
    
    # Create output folder
    create_output_folder()
    
    # Test backend health
    if not test_backend_health():
        return
    
    # Test topics to try
    test_topics = [
        ("Machine Learning Fundamentals", "beginner"),
        ("Advanced React Development", "intermediate"), 
        ("Microservices Architecture", "expert"),
        ("Python FastAPI Best Practices", "intermediate")
    ]
    
    print(f"\n📋 Testing {len(test_topics)} different topics...")
    
    successful = 0
    failed = 0
    
    for topic, depth in test_topics:
        if generate_article(topic, depth):
            successful += 1
        else:
            failed += 1
        time.sleep(1)  # Small delay between requests
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📁 Output folder: {os.path.abspath(OUTPUT_FOLDER)}")
    
    if successful > 0:
        print(f"\n🎉 Success! Check the '{OUTPUT_FOLDER}' folder for generated articles.")
    else:
        print("\n⚠️  No articles were generated successfully. Check the backend server.")

if __name__ == "__main__":
    main()
