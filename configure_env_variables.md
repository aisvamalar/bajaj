# Configure NVIDIA_API_KEY Environment Variable

This guide shows you exactly where and how to set up your NVIDIA API key.

## Method 1: Local Development (.env file)

### Step 1: Create .env file in your project root

**Location**: Create this file in the same folder as your `main.py` file

**File name**: `.env` (exactly this name, with the dot)

**Content**:
```
NVIDIA_API_KEY=your_actual_api_key_here
```

### Step 2: Example .env file
```
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 3: Verify the file exists
```bash
# Check if .env file exists
ls -la .env

# On Windows:
dir .env
```

## Method 2: Azure Portal Configuration

### Step 1: Go to Azure Portal
1. Visit [Azure Portal](https://portal.azure.com)
2. Sign in with your student account

### Step 2: Find Your App Service
1. Click "App Services" in the left menu
2. Find and click on your web app name (e.g., `fin-rag-api`)

### Step 3: Configure Environment Variables
1. In your web app, click **"Settings"** in the left menu
2. Click **"Configuration"**
3. Click **"New application setting"**
4. Fill in:
   - **Name**: `NVIDIA_API_KEY`
   - **Value**: Your NVIDIA API key
5. Click **"OK"**
6. Click **"Save"** at the top

### Step 4: Visual Steps
```
Azure Portal → App Services → Your App → Settings → Configuration → New application setting
```

## Method 3: Azure CLI (Command Line)

### Step 1: Install Azure CLI
```bash
# Windows (download from Microsoft)
# https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows

# Mac
brew install azure-cli

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### Step 2: Login to Azure
```bash
az login
```

### Step 3: Set Environment Variable
```bash
az webapp config appsettings set \
  --name your-app-name \
  --resource-group your-resource-group \
  --settings NVIDIA_API_KEY=your_api_key_here
```

## Method 4: Windows Environment Variables

### Step 1: Open System Properties
1. Press `Windows + R`
2. Type `sysdm.cpl`
3. Press Enter

### Step 2: Set Environment Variable
1. Click "Environment Variables"
2. Under "User variables", click "New"
3. Variable name: `NVIDIA_API_KEY`
4. Variable value: Your API key
5. Click "OK"

## Method 5: Linux/Mac Environment Variables

### Step 1: Add to .bashrc or .zshrc
```bash
# Open your shell profile
nano ~/.bashrc
# or
nano ~/.zshrc

# Add this line:
export NVIDIA_API_KEY=your_api_key_here

# Save and reload
source ~/.bashrc
```

### Step 2: Or set temporarily
```bash
export NVIDIA_API_KEY=your_api_key_here
```

## Verification Steps

### Step 1: Test Locally
```bash
# Run the test script
python test_nvidia_key.py
```

### Step 2: Test in Azure
```bash
# Check if the variable is set in Azure
az webapp config appsettings list \
  --name your-app-name \
  --resource-group your-resource-group
```

### Step 3: Check in Code
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("NVIDIA_API_KEY")
print(f"API Key found: {'Yes' if api_key else 'No'}")
```

## Troubleshooting

### Issue: "API key not found"
**Solution**: 
1. Check if `.env` file exists in project root
2. Make sure the file name is exactly `.env` (with dot)
3. Verify the format: `NVIDIA_API_KEY=your_key_here`

### Issue: "Invalid API key"
**Solution**:
1. Copy the key exactly as shown in NVIDIA dashboard
2. Remove any extra spaces
3. Make sure the key starts with `nvapi-`

### Issue: Azure not picking up the key
**Solution**:
1. Restart your Azure App Service
2. Check Azure Portal → Configuration
3. Verify the key is saved and not in "Slot setting"

## File Structure Example

Your project should look like this:
```
FIN_RAG-Rohan_dev/
├── .env                    ← Create this file here
├── main.py
├── api.py
├── document_processor.py
├── question_answerer.py
├── requirements.txt
└── test_nvidia_key.py
```

## Quick Setup Commands

### For Local Development:
```bash
# Create .env file
echo "NVIDIA_API_KEY=your_key_here" > .env

# Test it
python test_nvidia_key.py
```

### For Azure:
```bash
# Set in Azure
az webapp config appsettings set \
  --name your-app-name \
  --resource-group your-resource-group \
  --settings NVIDIA_API_KEY=your_key_here

# Verify
az webapp config appsettings list \
  --name your-app-name \
  --resource-group your-resource-group
```

## Security Notes

1. **Never commit .env file** - It's already in `.gitignore`
2. **Use Azure Key Vault** for production (advanced)
3. **Rotate keys regularly**
4. **Monitor usage** in NVIDIA dashboard

## Next Steps

1. ✅ Get your NVIDIA API key from [NVIDIA AI Playground](https://ai.nvidia.com/)
2. ✅ Create `.env` file locally
3. ✅ Test with `python test_nvidia_key.py`
4. ✅ Deploy to Azure
5. ✅ Set environment variable in Azure Portal
6. ✅ Test your webhook endpoint

Your API key is now configured and ready to use! 