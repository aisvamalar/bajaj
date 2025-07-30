# Azure Deployment Guide for Document Intelligence API

This guide will help you deploy your FIN_RAG project to Azure using your student trial account.

## Prerequisites

1. **Azure Student Account**: Make sure you have an active Azure student trial account
2. **NVIDIA API Key**: Get your NVIDIA API key from [NVIDIA AI Playground](https://ai.nvidia.com/)
3. **Git**: Install Git on your local machine
4. **Azure CLI**: Install Azure CLI (optional but recommended)

## Step 1: Prepare Your Code for Azure

### 1.1 Update Code for CPU-Only Deployment

Since Azure App Service doesn't support GPU, we need to modify the code to use CPU-only versions:

```python
# In document_processor.py and question_answerer.py, change:
# FROM:
embedding_model = embedding_model.to('cuda')

# TO:
# embedding_model = embedding_model.to('cuda')  # Comment out or remove this line
```

### 1.2 Create a .env file (locally for testing)
```
NVIDIA_API_KEY=your_nvidia_api_key_here
```

## Step 2: Azure Portal Setup

### 2.1 Create Resource Group
1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Resource Group" and select it
4. Click "Create"
5. Fill in:
   - **Resource group name**: `fin-rag-rg`
   - **Region**: Choose a region close to you (e.g., East US)
6. Click "Review + create" then "Create"

### 2.2 Create App Service Plan
1. In your resource group, click "Create"
2. Search for "App Service Plan" and select it
3. Click "Create"
4. Fill in:
   - **Name**: `fin-rag-plan`
   - **Operating System**: Linux
   - **Region**: Same as resource group
   - **Pricing plan**: 
     - For trial: Choose "F1" (Free tier)
     - For better performance: Choose "B1" (Basic tier)
5. Click "Review + create" then "Create"

### 2.3 Create Web App
1. In your resource group, click "Create"
2. Search for "Web App" and select it
3. Click "Create"
4. Fill in:
   - **Resource Group**: Select your resource group
   - **Name**: `fin-rag-api` (must be unique globally)
   - **Publish**: Code
   - **Runtime stack**: Python 3.11
   - **Operating System**: Linux
   - **Region**: Same as resource group
   - **App Service Plan**: Select your plan
5. Click "Review + create" then "Create"

## Step 3: Configure Environment Variables

1. Go to your Web App in Azure Portal
2. In the left menu, click "Settings" → "Configuration"
3. Click "New application setting" and add:
   - **Name**: `NVIDIA_API_KEY`
   - **Value**: Your NVIDIA API key
4. Click "Save"

## Step 4: Deploy Your Code

### Option A: Deploy via Azure Portal (Easiest)

1. In your Web App, go to "Deployment Center"
2. Choose "Local Git/FTPS credentials"
3. Set up deployment credentials
4. Use Git to push your code:

```bash
# Initialize Git repository
git init
git add .
git commit -m "Initial commit"

# Add Azure remote
git remote add azure https://your-app-name.scm.azurewebsites.net:443/your-app-name.git

# Push to Azure
git push azure main
```

### Option B: Deploy via GitHub Actions (Recommended)

1. Push your code to GitHub
2. In Azure Portal, go to "Deployment Center"
3. Choose "GitHub" as source
4. Connect your GitHub account
5. Select your repository
6. Azure will automatically deploy when you push to main branch

### Option C: Deploy via Azure CLI

```bash
# Install Azure CLI
# Windows: Download from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows
# Mac: brew install azure-cli
# Linux: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Set subscription (if you have multiple)
az account set --subscription "Your Subscription Name"

# Deploy
az webapp up --name fin-rag-api --resource-group fin-rag-rg --runtime "PYTHON:3.11"
```

## Step 5: Test Your Deployment

### 5.1 Get Your Webhook URL
Your webhook URL will be: `https://fin-rag-api.azurewebsites.net/hackrx/run`

### 5.2 Test the API
Use curl or Postman to test:

```bash
curl -X POST "https://fin-rag-api.azurewebsites.net/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 9f40f077e610d431226b59eec99652153ccad94769da6779cc01725731999634" \
  -d '{
    "questions": ["What is the main topic of this document?"],
    "documents": "https://example.com/sample.pdf"
  }'
```

## Step 6: Monitor and Troubleshoot

### 6.1 View Logs
1. In Azure Portal, go to your Web App
2. Click "Log stream" to see real-time logs
3. Click "Logs" for detailed logs

### 6.2 Common Issues and Solutions

**Issue**: App fails to start
- **Solution**: Check logs in "Log stream"
- **Common cause**: Missing dependencies or environment variables

**Issue**: CUDA/GPU errors
- **Solution**: Make sure you're using CPU-only versions in azure-requirements.txt

**Issue**: Memory issues
- **Solution**: Upgrade to a higher tier App Service Plan

**Issue**: Timeout errors
- **Solution**: Increase timeout settings in Azure App Service configuration

## Step 7: Cost Optimization for Student Trial

### 7.1 Free Tier Limits
- **F1 (Free)**: 1 GB RAM, 60 minutes/day CPU time
- **B1 (Basic)**: 1.75 GB RAM, always on

### 7.2 Cost-Saving Tips
1. Use F1 tier for development/testing
2. Scale down when not in use
3. Monitor usage in Azure Portal
4. Set up spending alerts

## Step 8: Security Considerations

### 8.1 API Security
- Change the default token in `api.py`
- Use Azure Key Vault for sensitive data
- Enable HTTPS only

### 8.2 Network Security
- Configure IP restrictions if needed
- Use Azure Application Gateway for additional security

## Step 9: Scaling (When Needed)

### 9.1 Vertical Scaling
- Upgrade App Service Plan tier
- Add more memory/CPU

### 9.2 Horizontal Scaling
- Enable auto-scaling
- Add more instances

## Troubleshooting Checklist

- [ ] NVIDIA API key is set correctly
- [ ] All dependencies are installed (CPU versions)
- [ ] Environment variables are configured
- [ ] App Service Plan has enough resources
- [ ] Code is pushed to the correct branch
- [ ] Logs show no errors
- [ ] Network connectivity is working

## Support Resources

- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [Azure Student Benefits](https://azure.microsoft.com/en-us/free/students/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)

## Next Steps

1. Test your webhook URL
2. Monitor performance and costs
3. Set up CI/CD pipeline
4. Add monitoring and alerting
5. Consider using Azure Container Instances for GPU support (if needed) 