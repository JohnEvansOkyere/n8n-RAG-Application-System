# 🚀 Quick Start Guide - VexaAI RAG Application

Get your VexaAI RAG chatbot running in **10 minutes**!

## ⚡ Prerequisites (5 minutes)

Before starting, create free accounts:

1. ✅ [Supabase](https://supabase.com) - Database
2. ✅ [n8n Cloud](https://n8n.cloud) - Workflow automation  
3. ✅ [Weaviate Cloud](https://console.weaviate.cloud) - Vector database
4. ✅ [Google AI Studio](https://makersuite.google.com/app/apikey) - Get Gemini API key
5. ✅ [Google Cloud Console](https://console.cloud.google.com) - Enable Drive API

## 📦 Step 1: Clone & Install (2 minutes)

```bash
# Clone the repository
git clone <your-repo-url>
cd vexaai-rag-app

# Run automated setup
chmod +x scripts/setup.sh
./scripts/setup.sh

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## 🗄️ Step 2: Setup Supabase (2 minutes)

```bash
# 1. Create new project at supabase.com
# 2. Go to SQL Editor → New Query
# 3. Copy and paste contents of supabase_schema.sql
# 4. Click "Run"
# 5. Go to Settings → API and copy:
#    - Project URL
#    - anon/public key
#    - service_role key
```

## 🔧 Step 3: Configure n8n (3 minutes)

```bash
# 1. Login to n8n.cloud
# 2. Import workflow:
#    - Workflows → Add Workflow → Import from File
#    - Select n8n/workflow_improved.json

# 3. Add credentials (click on each node):

# Google Drive OAuth2:
- Create OAuth credentials in Google Cloud Console
- Add redirect URI: https://your-n8n.app.n8n.cloud/rest/oauth2-credential/callback
- Paste Client ID and Secret in n8n

# Supabase:
- Host: Your Supabase URL
- Service Role Key: service_role key from Supabase

# Weaviate:
- URL: Your Weaviate cluster URL  
- API Key: From Weaviate dashboard

# Google Gemini:
- API Key: From Google AI Studio

# 4. Fix nodes (important!):
#    - Update "Google Drive Trigger" folder ID
#    - Remove hardcoded file ID from "Download File" node
#    - Replace with: ={{ $json.id }}

# 5. Click "Active" toggle to enable workflow

# 6. Copy webhook URL from "Webhook" node
```

## 🔐 Step 4: Configure Environment (1 minute)

```bash
# Edit .env file
nano .env

# Add your credentials:
N8N_WEBHOOK_URL=https://your-n8n-instance.app.n8n.cloud/webhook/41644729...
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Save and exit (Ctrl+X, then Y, then Enter)
```

## ✅ Step 5: Test & Run (2 minutes)

```bash
# Test the webhook
python scripts/test_webhook.py

# If tests pass, run the app
streamlit run app.py

# App opens at http://localhost:8501
```

## 🎉 You're Done!

Your chatbot is now running! Try asking:
- "What is VexaAI?"
- "How do I get started?"
- "What features does VexaAI offer?"

## 📤 Upload Your First Document

1. Create a FAQ document in Google Docs
2. Move it to the Google Drive folder you specified
3. Watch n8n process it (check Executions)
4. Verify in Supabase: Documents table shows "completed"
5. Ask questions about the document in your chatbot!

## 🐛 Troubleshooting

### ❌ "Webhook connection failed"
- Check n8n workflow is **Active**
- Verify webhook URL in .env matches n8n
- Test webhook directly with curl

### ❌ "Supabase connection error"
- Verify credentials in .env
- Check you're using anon key (not service_role)
- Test connection in Supabase dashboard

### ❌ "No AI response"
- Upload at least one document to Google Drive
- Check Weaviate has vectors (n8n execution logs)
- Verify Gemini API key is valid

### ❌ "Document processing failed"
- Check Google Drive permissions
- Verify OAuth scope includes drive.readonly
- Check file format is supported (PDF, DOCX, TXT)

## 📚 Next Steps

- ✅ Read [README.md](README.md) for detailed documentation
- ✅ Check [DEPLOYMENT.md](docs/DEPLOYMENT.md) to deploy to production  
- ✅ Customize the chatbot system prompt in n8n AI Agent node
- ✅ Add more documents to improve knowledge base
- ✅ Configure rate limiting and security

## 🆘 Need Help?

- 📖 Full documentation in README.md
- 🐛 Report issues on GitHub
- 💬 Check n8n community forum
- 📧 Email: support@vexaai.com

---

**Built with ❤️ by VexaAI Team**

Happy chatting! 🤖