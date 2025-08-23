import requests
import json

print("Testing the Content Creation API...")

# Test 1: Create a job
print("\n1. Creating a job...")
response = requests.post('http://localhost:8000/v1/jobs', json={
    'topic': 'Python FastAPI Development',
    'desired_depth': 'intermediate'
})

if response.status_code == 200:
    job_data = response.json()
    print(f"✅ Job created successfully: {job_data['job_id']}")
    
    # Test 2: Get the job result
    print("\n2. Getting job result...")
    result_response = requests.get(f'http://localhost:8000/v1/jobs/{job_data["job_id"]}')
    
    if result_response.status_code == 200:
        job_result = result_response.json()
        article = job_result['result']['article']
        
        print(f"✅ Article generated successfully!")
        print(f"   Title: {article['title']}")
        print(f"   Word count: {article['word_count']}")
        print(f"   Content preview: {article['content'][:200]}...")
        
        # Test 3: List all jobs
        print("\n3. Listing all jobs...")
        list_response = requests.get('http://localhost:8000/v1/jobs')
        if list_response.status_code == 200:
            jobs_list = list_response.json()
            print(f"✅ Found {jobs_list['total']} jobs")
        else:
            print(f"❌ Failed to list jobs: {list_response.status_code}")
    else:
        print(f"❌ Failed to get job result: {result_response.status_code}")
else:
    print(f"❌ Failed to create job: {response.status_code}")

print("\nAPI testing complete!")
