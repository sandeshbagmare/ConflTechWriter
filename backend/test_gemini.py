import requests
import json

print("🚀 Testing Gemini AI integration...")

# Create a job
response = requests.post('http://localhost:8000/v1/jobs', json={
    'topic': 'Advanced Machine Learning with Neural Networks'
})

if response.status_code == 200:
    job_data = response.json()
    print(f"✅ Job created successfully!")
    print(f"   Job ID: {job_data['job_id']}")
    
    # Get the result
    job_id = job_data['job_id']
    result_response = requests.get(f'http://localhost:8000/v1/jobs/{job_id}')
    
    if result_response.status_code == 200:
        job_result = result_response.json()
        article = job_result['result']['article']
        
        print(f"\n📊 Article Generation Results:")
        print(f"   🤖 AI Powered: {article.get('ai_powered', False)}")
        print(f"   🔧 Method: {article.get('generation_method', 'unknown')}")
        print(f"   📝 Word Count: {article.get('word_count', 0)}")
        print(f"   📖 Title: {article.get('title', 'No title')}")
        
        if article.get('ai_powered'):
            print("\n🎉 SUCCESS! Gemini AI is working with your API key!")
        else:
            print("\n⚠️  Using template fallback (Gemini may not be available)")
            
        # Show first 200 characters of content
        content = article.get('content', '')
        if content:
            print(f"\n📃 Content Preview:")
            print(f"   {content[:200]}...")
    else:
        print(f"❌ Failed to get job result: {result_response.status_code}")
else:
    print(f"❌ Failed to create job: {response.status_code}")

print("\n✅ Test completed!")
