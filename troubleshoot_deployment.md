# Troubleshooting Failed Azure Deployment

Based on your GitHub Actions failure, here's how to fix the deployment issues.

## 🔍 **Step 1: Check the Error Logs**

1. **Click on the failed workflow run** (the red X in GitHub)
2. **Look at the error message** in the logs
3. **Common error patterns**:
   - `ModuleNotFoundError`: Missing dependencies
   - `Environment variable not found`: Missing NVIDIA_API_KEY
   - `Build failed`: Python version or dependency issues

## 🔧 **Step 2: Fix Common Issues**

### **Issue A: Missing Environment Variables**

**Problem**: `NVIDIA_API_KEY` not configured in Azure

**Solution**:
1. Go to Azure Portal → Your App Service
2. Settings → Configuration
3. Add new application setting:
   - **Name**: `NVIDIA_API_KEY`
   - **Value**: Your NVIDIA API key
4. Click "Save"

### **Issue B: Dependencies Not Installing**

**Problem**: Requirements file has incompatible packages

**Solution**: Use the simplified requirements file I created:
```bash
# Use this file instead of the original requirements.txt
pip install -r requirements-azure.txt
```

### **Issue C: Python Version Mismatch**

**Problem**: Azure expects Python 3.11 but gets different version

**Solution**: Update your workflow to specify Python 3.11:
```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'
```

## 🚀 **Step 3: Manual Deployment (Alternative)**

If GitHub Actions keeps failing, deploy manually:

### **Option 1: Azure CLI Deployment**
```bash
# Install Azure CLI
# Windows: Download from Microsoft
# Mac: brew install azure-cli

# Login to Azure
az login

# Deploy
az webapp up \
  --name your-app-name \
  --resource-group fin-rag-rg \
  --runtime "PYTHON:3.11" \
  --sku F1
```

### **Option 2: Azure Portal Deployment**
1. Go to Azure Portal → Your App Service
2. Click "Deployment Center"
3. Choose "Local Git/FTPS credentials"
4. Use Git to push your code:
```bash
git remote add azure https://your-app.scm.azurewebsites.net:443/your-app.git
git push azure main
```

## 📋 **Step 4: Update Your Repository**

### **1. Update Requirements File**
Replace your current `requirements.txt` with `requirements-azure.txt`:
```bash
cp requirements-azure.txt requirements.txt
```

### **2. Update GitHub Secrets**
In your GitHub repository:
1. Go to Settings → Secrets and variables → Actions
2. Add these secrets:
   - `AZURE_WEBAPP_PUBLISH_PROFILE`: Your Azure publish profile
   - `NVIDIA_API_KEY`: Your NVIDIA API key

### **3. Update App Name**
In `.github/workflows/azure-deploy.yml`, change:
```yaml
AZURE_WEBAPP_NAME: your-actual-app-name
```

## 🧪 **Step 5: Test Your Fix**

### **Test Locally First**
```bash
# Test with simplified requirements
pip install -r requirements-azure.txt
python test_nvidia_key.py
```

### **Test Azure Deployment**
```bash
# Push changes to trigger new deployment
git add .
git commit -m "Fix deployment issues"
git push origin main
```

## 🔍 **Step 6: Monitor Deployment**

### **Check GitHub Actions**
1. Go to your repository → Actions tab
2. Watch the new workflow run
3. Click on it to see real-time logs

### **Check Azure Portal**
1. Go to Azure Portal → Your App Service
2. Click "Log stream" to see real-time logs
3. Look for any error messages

## 🚨 **Common Error Messages and Solutions**

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'torch'` | Use CPU-only torch: `torch==2.1.0+cpu` |
| `Environment variable NVIDIA_API_KEY not found` | Add to Azure App Service settings |
| `Build failed: Python version` | Specify Python 3.11 in workflow |
| `Deployment timeout` | Reduce requirements, use simplified file |
| `Memory limit exceeded` | Upgrade to B1 tier or optimize code |

## 📊 **Step 7: Verify Success**

### **Check Your Webhook URL**
Your webhook should be available at:
```
https://your-app-name.azurewebsites.net/hackrx/run
```

### **Test the Endpoint**
```bash
# Test with curl
curl -X POST "https://your-app-name.azurewebsites.net/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 9f40f077e610d431226b59eec99652153ccad94769da6779cc01725731999634" \
  -d '{"questions": ["Hello"], "documents": "https://example.com/test.pdf"}'
```

## 🎯 **Quick Fix Checklist**

- [ ] Check GitHub Actions logs for specific error
- [ ] Update requirements.txt to use simplified version
- [ ] Add NVIDIA_API_KEY to Azure App Service settings
- [ ] Update GitHub secrets with correct values
- [ ] Change app name in workflow file
- [ ] Test locally before pushing
- [ ] Monitor new deployment
- [ ] Verify webhook is working

## 📞 **If Still Failing**

1. **Share the specific error message** from GitHub Actions logs
2. **Check Azure App Service logs** in the portal
3. **Try manual deployment** using Azure CLI
4. **Consider using Azure Container Instances** for GPU support

The key is to identify the specific error in the logs and address it systematically! 