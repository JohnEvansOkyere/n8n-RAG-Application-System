# n8n-RAG-Application-System

# VexaAI RAG Chat Application

A complete Retrieval-Augmented Generation (RAG) chat application with Streamlit UI, n8n backend, Weaviate vector store, and Supabase database.

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Streamlit  │─────→│  n8n Webhook │─────→│   Weaviate  │
│     UI      │      │   Backend    │      │Vector Store │
└─────────────┘      └──────────────┘      └─────────────┘
       │                     │
       │                     │
       ▼                     ▼
┌─────────────────────────────────┐
│         Supabase DB             │
│  - Chat Messages                │
│  - Documents                    │
│  - Rate Limits                  │
└─────────────────────────────────┘
```

## 📁 Project Structure

```
vexaai-rag-app/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (create this)
├── .env.example                   # Environment variables template
├── README.md                      # This file
├── supabase_schema.sql            # Database schema
├── n8n/
│   ├── workflow_improved.json     # Enhanced n8n workflow
│   └── workflow_original.json     # Original workflow backup
├── scripts/
│   ├── setup.sh                   # Automated setup script
│   └── test_webhook.py            # Webhook testing script
├── docs/
│   ├── DEPLOYMENT.md              # Deployment guide
│   └── API.md                     # API documentation
└── .gitignore                     # Git ignore file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- n8n instance (cloud or self-hosted)
- Supabase account
- Weaviate Cloud account or self-hosted instance
- Google Drive API access
- Google Gemini API key

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd vexaai-rag-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Supabase

```bash
# 1. Create a new Supabase project at https://supabase.com
# 2. Run the schema SQL
# - Go to SQL Editor in Supabase Dashboard
# - Copy contents of supabase_schema.sql
# - Execute the SQL

# 3. Get your credentials
# - Go to Project Settings > API
# - Copy the Project URL and anon/public key
```

### 3. Setup Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use any text editor
```

Required environment variables:
```env
N8N_WEBHOOK_URL=https://your-n8n.com/webhook/chat
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key
```

### 4. Configure n8n Workflow

#### Import the Workflow

1. Log into your n8n instance
2. Click **Workflows** > **Add Workflow**
3. Click **⋯** menu > **Import from File**
4. Select `n8n/workflow_improved.json`

#### Configure Credentials

You need to set up these credentials in n8n:

1. **Google Drive OAuth2** (`okyerevansjohn@gmail.com`)
   - Settings > Credentials > Add Credential
   - Search for "Google Drive OAuth2 API"
   - Follow OAuth setup

2. **Supabase API**
   - Add Credential > Supabase
   - URL: Your Supabase project URL
   - Service Role Key: From Supabase Dashboard

3. **Weaviate API**
   - Add Credential > Weaviate
   - URL: Your Weaviate cluster URL
   - API Key: From Weaviate dashboard

4. **Google Gemini (PaLM) API**
   - Add Credential > Google PaLM API
   - API Key: From Google AI Studio

#### Update Workflow Nodes

**Important fixes to apply:**

1. **Google Drive Trigger** - Already configured
2. **Download file node** - Change from hardcoded ID:
   ```json
   "fileId": {
     "__rl": true,
     "value": "={{ $json.id }}",
     "mode": "id"
   }
   ```

3. **Add Chunk Counter** (between Code and Weaviate Vector Store):
   ```javascript
   // Count chunks before storing
   const chunks = $input.all();
   const chunkCount = chunks.length;
   
   console.log(`Processing ${chunkCount} chunks`);
   
   // Pass through all chunks with metadata
   return chunks.map((chunk, index) => ({
     json: {
       ...chunk.json,
       chunk_index: index,
       total_chunks: chunkCount,
       document_id: $('Download file').item.json.id
     }
   }));
   ```

4. **Fix Update Success Node** - Update the expression:
   ```javascript
   "fieldValue": "={{ $('Code1').first().json.total_chunks }}"
   ```

5. **Fix Validation Node** - Remove UUID generation:
   ```javascript
   // Simplified validation without UUID conversion
   const body = $input.first().json.body;
   
   if (!body || !body.message || !body.session_id || !body.user_id) {
     throw new Error('Missing required fields: message, session_id, user_id');
   }
   
   return {
     json: {
       message: body.message.trim(),
       session_id: body.session_id,
       user_id: body.user_id,
       timestamp: new Date().toISOString()
     }
   };
   ```

#### Activate the Workflow

1. Click **Save** in n8n
2. Toggle **Active** to enable the workflow
3. Copy the webhook URL from the Webhook node
4. Update your `.env` file with this URL

### 5. Run the Application

```bash
# Start Streamlit
streamlit run app.py

# The app will open at http://localhost:8501
```

## 🧪 Testing

### Test the Webhook

```bash
# Use the provided test script
python scripts/test_webhook.py

# Or use curl
curl -X POST https://your-n8n.com/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is VexaAI?",
    "session_id": "test-session-123",
    "user_id": "test-user-123"
  }'
```

### Test Document Processing

1. Upload a document to your Google Drive folder
2. Check n8n execution logs
3. Verify in Supabase that document status updates
4. Confirm chunks are stored in Weaviate

## 📊 Features

### Current Features

✅ Real-time chat interface  
✅ RAG-based responses using Weaviate vector store  
✅ Session persistence with Supabase  
✅ Document processing pipeline  
✅ Google Drive integration  
✅ Chat history loading  
✅ Document statistics dashboard  
✅ Error handling and logging  

### Recommended Enhancements

🔄 Rate limiting per user  
🔄 User authentication  
🔄 File upload via UI  
🔄 Conversation export  
🔄 Multi-language support  
🔄 Advanced analytics  
🔄 Mobile responsive design  

## 🔧 Configuration

### Streamlit Configuration

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1976d2"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
enableCORS = false
enableXsrfProtection = true
```

### Rate Limiting (Supabase Function)

Already included in schema. To use:

```sql
-- Check if user can make request
SELECT check_rate_limit('user-uuid', 10, 1);
-- Returns true if allowed, false if limit exceeded
```

## 🐛 Troubleshooting

### Common Issues

**1. Webhook Connection Failed**
```
Error: Network error: Connection refused
```
**Solution:** 
- Verify n8n workflow is active
- Check webhook URL in .env
- Ensure n8n instance is accessible

**2. Supabase Connection Error**
```
Error: Invalid API key
```
**Solution:**
- Verify SUPABASE_URL and SUPABASE_KEY in .env
- Ensure you're using the anon/public key, not service role key
- Check Supabase project is not paused

**3. No AI Response**
```
AI returns empty response
```
**Solution:**
- Check Weaviate has indexed documents
- Verify Google Gemini API key is valid
- Check n8n execution logs for errors
- Ensure vector store is properly connected in AI Agent

**4. Document Processing Fails**
```
Processing status stays as "processing"
```
**Solution:**
- Check Google Drive credentials in n8n
- Verify file permissions
- Check n8n execution logs
- Ensure Download file node uses correct file ID

**5. Chat History Not Loading**
```
Error loading chat history
```
**Solution:**
- Verify Supabase credentials
- Check chat_messages table exists
- Ensure RLS policies allow read access

## 📈 Performance Optimization

### Supabase Indexes

Already included in schema. Verify they exist:

```sql
-- Check indexes
SELECT * FROM pg_indexes 
WHERE tablename IN ('chat_messages', 'documents', 'rate_limits');
```

### Caching Strategy

Add caching to frequently accessed data:

```python
import streamlit as st

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_document_stats():
    # Your existing function
    pass
```

### Connection Pooling

For production, use connection pooling:

```python
from supabase import create_client
from postgrest import SyncPostgrestClient

# Create client with custom config
supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
    options={
        'postgrest_client_timeout': 10,
        'storage_client_timeout': 10
    }
)
```

## 🚀 Deployment

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add secrets in dashboard (same as .env)
5. Deploy

### Deploy n8n

**Option 1: n8n Cloud**
- Sign up at [n8n.cloud](https://n8n.cloud)
- Import workflow
- Configure credentials

**Option 2: Self-hosted (Docker)**

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n
```

### Environment Variables for Production

```env
# Production settings
N8N_WEBHOOK_URL=https://your-production-n8n.com/webhook/chat
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-production-key

# Optional production settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
LOG_LEVEL=INFO
```

## 🔐 Security Best Practices

1. **Never commit .env file**
   ```bash
   # Already in .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use environment-specific keys**
   - Development: Use test keys
   - Production: Use production keys with restricted permissions

3. **Enable RLS in Supabase**
   - Already configured in schema
   - Review policies regularly

4. **Rate limiting**
   - Implement in n8n webhook
   - Use Supabase function provided

5. **Input validation**
   - Already in validation node
   - Add additional checks as needed

## 📚 API Documentation

### Chat Endpoint

**POST** `/webhook/chat`

Request:
```json
{
  "message": "Your question here",
  "session_id": "unique-session-id",
  "user_id": "unique-user-id"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "message": "AI response here",
    "session_id": "unique-session-id",
    "user_id": "unique-user-id",
    "timestamp": "2025-10-03T12:00:00Z",
    "metadata": {
      "role": "assistant",
      "created_at": "2025-10-03T12:00:00Z"
    }
  }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - feel free to use for personal or commercial projects

## 🆘 Support

- **Issues:** Open an issue on GitHub
- **Email:** support@vexaai.com
- **Documentation:** Check /docs folder

## 🎯 Roadmap

- [ ] Multi-user authentication
- [ ] File upload interface
- [ ] Advanced analytics dashboard
- [ ] Export conversations
- [ ] API key management
- [ ] Webhook security
- [ ] Docker compose setup
- [ ] Kubernetes deployment configs
- [ ] Automated testing suite
- [ ] CI/CD pipeline

---

**Built with ❤️ by VexaAI Team**