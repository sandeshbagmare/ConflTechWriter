import os
from dotenv import load_dotenv

print("🔍 Debugging Gemini configuration...")

# Load .env file
env_path = "../.env"
print(f"Loading .env from: {env_path}")
load_dotenv(dotenv_path=env_path)

# Check API key
api_key = os.getenv('GEMINI_API_KEY')
model = os.getenv('GEMINI_MODEL')

print(f"API Key found: {bool(api_key)}")
print(f"API Key (first 10 chars): {api_key[:10] if api_key else 'None'}...")
print(f"Model: {model}")

# Test Gemini initialization
try:
    import google.generativeai as genai
    print("✅ google.generativeai imported successfully")
    
    if api_key:
        genai.configure(api_key=api_key)
        print("✅ Gemini configured with API key")
        
        model_name = model or 'gemini-pro'
        gemini_model = genai.GenerativeModel(model_name)
        print(f"✅ Gemini model '{model_name}' initialized")
        
        # Test a simple generation
        print("🧪 Testing simple generation...")
        response = gemini_model.generate_content("Write a one-sentence summary of machine learning.")
        print(f"✅ Test response: {response.text[:100]}...")
        
    else:
        print("❌ No API key found")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Gemini error: {e}")

print("🔍 Debug complete!")
