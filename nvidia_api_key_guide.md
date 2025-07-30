# NVIDIA API Key Setup Guide

This guide will walk you through getting your NVIDIA API key for the Document Intelligence API.

## Step 1: Create NVIDIA Account

### 1.1 Go to NVIDIA AI Playground
1. Visit [NVIDIA AI Playground](https://ai.nvidia.com/)
2. Click "Get Started" or "Sign Up"

### 1.2 Sign Up Process
1. **Email**: Use your student email address
2. **Password**: Create a strong password
3. **Account Type**: Select "Student" if available
4. **Verification**: Check your email and verify your account

## Step 2: Access the API Key

### 2.1 Navigate to API Section
1. After logging in, go to your dashboard
2. Look for "API Keys" or "Developer" section
3. Click on "API Keys" or "Get API Key"

### 2.2 Generate API Key
1. Click "Generate New API Key"
2. Give it a name like "Document Intelligence API"
3. Copy the generated key immediately (it won't be shown again)

## Step 3: Alternative Method (If Above Doesn't Work)

### 3.1 NVIDIA NGC
1. Go to [NVIDIA NGC](https://ngc.nvidia.com/)
2. Sign up for a free account
3. Navigate to "API Keys" section
4. Generate your API key

### 3.2 NVIDIA Developer Program
1. Visit [NVIDIA Developer](https://developer.nvidia.com/)
2. Join the developer program
3. Access API keys through the developer portal

## Step 4: Set Up API Key Locally

### 4.1 Create .env File
Create a file named `.env` in your project root:

```bash
# On Windows
echo NVIDIA_API_KEY=your_api_key_here > .env

# On Mac/Linux
echo "NVIDIA_API_KEY=your_api_key_here" > .env
```

### 4.2 Or Create .env File Manually
Create a file named `.env` and add:
```
NVIDIA_API_KEY=your_actual_api_key_here
```

## Step 5: Test Your API Key

### 5.1 Test Locally
```bash
# Test if the key works
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('API Key loaded:', 'NVIDIA_API_KEY' in os.environ)
"
```

### 5.2 Test with Simple Request
```python
# Create test_api_key.py
import os
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA

load_dotenv()

def test_nvidia_api():
    try:
        llm = ChatNVIDIA(model="meta/llama-3.1-70b-instruct")
        response = llm.invoke("Hello, how are you?")
        print("✅ API Key works!")
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"❌ API Key error: {e}")

if __name__ == "__main__":
    test_nvidia_api()
```

## Step 6: Set Up for Azure Deployment

### 6.1 Azure Portal Configuration
1. Go to your Azure App Service
2. Click "Settings" → "Configuration"
3. Click "New application setting"
4. Add:
   - **Name**: `NVIDIA_API_KEY`
   - **Value**: Your NVIDIA API key
5. Click "Save"

### 6.2 Using Azure CLI
```bash
az webapp config appsettings set \
  --name your-app-name \
  --resource-group your-resource-group \
  --settings NVIDIA_API_KEY=your_api_key_here
```

## Step 7: Troubleshooting

### 7.1 Common Issues

**Issue**: "API key not found"
- **Solution**: Make sure the key is in your `.env` file or Azure environment variables

**Issue**: "Invalid API key"
- **Solution**: Double-check the key, make sure there are no extra spaces

**Issue**: "Rate limit exceeded"
- **Solution**: NVIDIA has rate limits for free accounts. Wait and try again.

**Issue**: "Model not available"
- **Solution**: Check if the model "meta/llama-3.1-70b-instruct" is available in your region

### 7.2 API Key Format
Your API key should look like:
```
nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Step 8: Security Best Practices

### 8.1 Never Commit API Keys
- The `.env` file is already in `.gitignore`
- Never share your API key publicly
- Use environment variables in production

### 8.2 Rotate Keys Regularly
- Generate new keys periodically
- Delete old keys when not needed
- Monitor usage in NVIDIA dashboard

## Step 9: Cost and Limits

### 9.1 Free Tier Limits
- **Requests per day**: Varies by model
- **Concurrent requests**: Limited
- **Model access**: Some models may be restricted

### 9.2 Monitoring Usage
1. Check your NVIDIA dashboard regularly
2. Monitor Azure App Service logs
3. Set up alerts for high usage

## Step 10: Alternative Models

If the default model doesn't work, try these alternatives:

```python
# Alternative models you can use
models = [
    "meta/llama-3.1-70b-instruct",
    "meta/llama-3.1-8b-instruct",
    "microsoft/DialoGPT-medium",
    "gpt2"
]
```

## Quick Test Script

Create a file called `test_nvidia_key.py`:

```python
#!/usr/bin/env python3
"""
Quick test script for NVIDIA API key
"""

import os
from dotenv import load_dotenv

def test_api_key():
    load_dotenv()
    
    api_key = os.getenv("NVIDIA_API_KEY")
    
    if not api_key:
        print("❌ NVIDIA_API_KEY not found in environment")
        print("Please add it to your .env file or Azure environment variables")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        from langchain_nvidia_ai_endpoints import ChatNVIDIA
        llm = ChatNVIDIA(model="meta/llama-3.1-70b-instruct")
        response = llm.invoke("Say hello!")
        print("✅ API Key is working!")
        print(f"Response: {response.content}")
        return True
    except Exception as e:
        print(f"❌ API Key test failed: {e}")
        return False

if __name__ == "__main__":
    test_api_key()
```

Run it:
```bash
python test_nvidia_key.py
```

## Summary

1. **Get API Key**: Sign up at [NVIDIA AI Playground](https://ai.nvidia.com/)
2. **Test Locally**: Use the test script above
3. **Deploy to Azure**: Add the key to Azure App Service settings
4. **Monitor Usage**: Check your NVIDIA dashboard regularly

Your API key is essential for the LLM functionality in your Document Intelligence API! 