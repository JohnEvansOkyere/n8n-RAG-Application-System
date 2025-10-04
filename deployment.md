# VexaAI RAG Application - Deployment Guide

This guide covers deploying the VexaAI RAG application to production.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
3. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
4. [n8n Deployment](#n8n-deployment)
5. [Supabase Setup](#supabase-setup)
6. [Weaviate Setup](#weaviate-setup)
7. [Post-Deployment](#post-deployment)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying, ensure you have:

- ✅ GitHub account (for Streamlit Cloud)
- ✅ n8n Cloud account or self-hosted instance
- ✅ Supabase account
- ✅ Weaviate Cloud account or self-hosted instance
- ✅ Google Cloud Project (for Drive & Gemini APIs)
- ✅ All API keys and credentials ready

## Deployment Options

### Option 1: Fully Managed (Recommended for beginners)
- **Frontend**: Streamlit Cloud
- **Backend**: n8n Cloud
- **Database**: Supabase (managed)
- **Vector Store**: Weaviate Cloud

### Option 2: Self-Hosted
- **Frontend**: Docker + Nginx
- **Backend**: Self-hosted n8n
- **Database**: Self-hosted PostgreSQL
- **Vector Store**: Self-hosted Weaviate

### Option 3: Hybrid
- **Frontend**: Streamlit Cloud
- **Backend**: Self-hosted n8n
- **Database**: Supabase (managed)
- **Vector Store**: Weaviate Cloud

## Streamlit Cloud Deployment

### Step 1: Prepare Repository

```bash
# Create a new GitHub repository
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/vexaai-rag.git
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select your repository
4. Set:
   - **Main file path**: `app.py`
   - **Python version**: 3.11
5. Click **"Advanced settings"**
6. Add secrets (from your `.env`):

```toml
# .streamlit/secrets.toml format
N8N_WEBHOOK_URL = "https://your-n8n.com/webhook/chat"
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-anon-key"
```

7. Click **"Deploy"**

### Step 3: Update app.py for Secrets

Modify `app.py` to read from Streamlit secrets:

```python
import streamlit as st
import os

# Load from secrets in production, .env in development
try:
    WEBHOOK_URL = st.secrets["N8N_WEBHOOK_URL"]
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except:
    from dotenv import load_dotenv
    load_dotenv()
    WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
```

## n8n Deployment

### Option A: n8n Cloud (Recommended)

1. **Sign up** at [n8n.cloud](https://n8n.cloud)
2. **Create workspace**
3. **Import workflow**:
   - Click **Workflows** → **Add Workflow**
   - Click **⋯** → **Import from File**
   - Select `n8n/workflow_improved.json`
4. **Configure credentials** (see below)
5. **Activate workflow**

### Option B: Self-Hosted n8n (Docker)

#### Quick Start

```bash
# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  n8n:
    image: docker.n8n.io/n8nio/n8n
    container_name: n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=changeme
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - NODE_ENV=production
      - WEBHOOK_URL=https://your-domain.com/
      - GENERIC_TIMEZONE=UTC
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
EOF

# Start n8n
docker-compose up -d

# Check logs
docker-compose logs -f
```

#### Production Setup with Nginx

```nginx
# /etc/nginx/sites-available/n8n
server {
    listen 80;
    server_name n8n.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:5678;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        chunked_transfer_encoding off;
        proxy_buffering off;
        proxy_cache off;
    }
}
```

```bash
# Enable site and restart nginx
sudo ln -s /etc/nginx/sites-available/n8n /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d n8n.yourdomain.com
```

### Configuring n8n Credentials

#### 1. Google Drive OAuth2

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create/Select project
3. Enable **Google Drive API**
4. Create **OAuth 2.0 credentials**
5. Add authorized redirect URIs:
   - `https://your-n8n-instance.com/rest/oauth2-credential/callback`
6. In n8n:
   - Credentials → Add Credential → Google Drive OAuth2
   - Enter Client ID and Client Secret
   - Click **Connect** and authorize

#### 2. Supabase API

1. Get from Supabase Dashboard → Settings → API
2. In n8n:
   - Credentials → Add Credential → Supabase
   - **Host**: Your Supabase URL
   - **Service Role Secret**: Service role key (not anon key!)

#### 3. Weaviate API

1. Get from Weaviate Cloud Console
2. In n8n:
   - Credentials → Add Credential → Weaviate
   - **URL**: Your Weaviate cluster URL
   - **API Key**: Your API key

#### 4. Google Gemini (PaLM) API

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create API key
3. In n8n:
   - Credentials → Add Credential → Google PaLM API
   - **API Key**: Your Gemini API key

## Supabase Setup

### Step 1: Create Project

1. Go to [supabase.com](https://supabase.com)
2. Click **New Project**
3. Configure:
   - **Name**: vexaai-rag
   - **Database Password**: Strong password
   - **Region**: Choose closest to users
4. Click **Create new project**

### Step 2: Run Schema

1. Go to **SQL Editor**
2. Click **New Query**
3. Copy entire contents of `supabase_schema.sql`
4. Click **Run**
5. Verify tables created in **Table Editor**

### Step 3: Configure Security

#### Enable Row Level Security

Already configured in schema, but verify:

```sql
-- Check RLS status
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';
```

#### API Settings

1. Go to **Settings** → **API**
2. Copy:
   - **Project URL**
   - **anon/public key** (for Streamlit)
   - **service_role key** (for n8n)
3. Update your `.env` files

### Step 4: Set Up Database Functions

Already included in schema. Test them:

```sql
-- Test rate limiting function
SELECT check_rate_limit('test-user-id'::uuid, 10, 1);

-- Test chat history function
SELECT * FROM get_chat_history('test-session-id'::uuid, 10);

-- Test document stats
SELECT * FROM get_document_stats();
```

## Weaviate Setup

### Option A: Weaviate Cloud

1. Go to [console.weaviate.cloud](https://console.weaviate.cloud)
2. Click **Create Cluster**
3. Configure:
   - **Name**: vexaai-faq
   - **Region**: Choose closest to n8n
   - **Plan**: Free tier is sufficient for testing
4. Wait for cluster creation
5. Copy:
   - **Cluster URL**
   - **API Key**

### Option B: Self-Hosted Weaviate

```bash
# docker-compose.yml for Weaviate
cat > weaviate-compose.yml << 'EOF'
version: '3.4'

services:
  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8080:8080"
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'false'
      AUTHENTICATION_APIKEY_ENABLED: 'true'
      AUTHENTICATION_APIKEY_ALLOWED_KEYS: 'your-secret-key'
      AUTHENTICATION_APIKEY_USERS: 'admin'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      DEFAULT_VECTORIZER_MODULE: 'none'
      CLUSTER_HOSTNAME: 'node1'
    volumes:
      - weaviate_data:/var/lib/weaviate

volumes:
  weaviate_data:
EOF

docker-compose -f weaviate-compose.yml up -d
```

### Create Collection

The collection is created automatically by n8n when you first run the workflow. Verify in Weaviate:

```bash
# Using curl
curl http://localhost:8080/v1/schema

# Or Weaviate Cloud Console → Schema
```

## Post-Deployment

### 1. Test the Complete Flow

#### Test Document Processing

1. Upload a test document to Google Drive folder
2. Check n8n execution:
   - Should show successful execution
   - Verify all nodes completed
3. Check Supabase:
   ```sql
   SELECT * FROM documents ORDER BY created_at DESC LIMIT 5;
   ```
4. Check Weaviate:
   - Verify vectors are stored
   - Check object count

#### Test Chat Endpoint

```bash
# Use the test script
python scripts/test_webhook.py

# Or manual test
curl -X POST https://your-n8n.com/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is VexaAI?",
    "session_id": "test-123",
    "user_id": "user-123"
  }'
```

#### Test Streamlit App

1. Open your Streamlit app URL
2. Send a test message
3. Verify response appears
4. Check chat history loads
5. Verify document stats display

### 2. Set Up Monitoring

#### Supabase Monitoring

1. Go to **Database** → **Logs**
2. Monitor query performance
3. Set up alerts for errors

#### n8n Monitoring

1. Enable execution logging
2. Set up error notifications:
   - Workflow Settings → Error Workflow
   - Add email/Slack notification

#### Streamlit Monitoring

Add error tracking to `app.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Use in code
try:
    response = send_message(user_input)
except Exception as e:
    logger.error(f"Error sending message: {str(e)}", exc_info=True)
    st.error("An error occurred. Please try again.")
```

### 3. Performance Optimization

#### Database Indexes

Verify indexes exist (already in schema):

```sql
-- Check indexes
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

#### Supabase Connection Pooling

Update Supabase client in production:

```python
from supabase import create_client

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
    options={
        'schema': 'public',
        'auto_refresh_token': True,
        'persist_session': True,
        'detect_session_in_url': False
    }
)
```

#### Streamlit Caching

Add caching to expensive operations:

```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_document_stats():
    # Your function
    pass

@st.cache_resource
def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)
```

### 4. Security Hardening

#### Enable HTTPS Everywhere

- Streamlit Cloud: Automatic
- n8n Cloud: Automatic  
- Self-hosted: Use Let's Encrypt

#### Environment Variables

Never commit secrets:

```bash
# Verify .gitignore includes
echo ".env" >> .gitignore
echo ".streamlit/secrets.toml" >> .gitignore
```

#### Supabase RLS Policies

Review and tighten policies:

```sql
-- Example: Restrict chat messages to session owners
CREATE POLICY "Users can only see their own sessions"
ON chat_messages FOR SELECT
USING (user_id = auth.uid());
```

#### Rate Limiting

Implement in n8n webhook validation:

```javascript
// Add to Validate Request node
const userId = body.user_id;
const canProceed = await $executeWorkflow('Check Rate Limit', { userId });

if (!canProceed) {
  throw new Error('Rate limit exceeded. Please try again later.');
}
```

## Monitoring

### Set Up Uptime Monitoring

Use services like:
- [UptimeRobot](https://uptimerobot.com) (Free)
- [Pingdom](https://pingdom.com)
- [StatusCake](https://statuscake.com)

Monitor:
- ✅ Streamlit app URL
- ✅ n8n webhook endpoint
- ✅ Supabase API

### Log Aggregation

For self-hosted deployments:

```bash
# Install Loki + Grafana (optional)
docker-compose -f monitoring-compose.yml up -d
```

### Analytics

Add basic analytics to Streamlit:

```python
def log_interaction(event_type, metadata):
    """Log user interactions"""
    try:
        supabase.table('analytics').insert({
            'event_type': event_type,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }).execute()
    except Exception as e:
        logger.error(f"Analytics error: {e}")
```

## Troubleshooting

### Common Issues

#### 1. Webhook Returns 404

**Problem**: n8n workflow not activated or wrong URL

**Solution**:
```bash
# Verify workflow is active in n8n
# Check webhook URL matches .env
# Test with curl first
```

#### 2. Supabase Connection Fails

**Problem**: Wrong credentials or RLS blocking access

**Solution**:
```sql
-- Check RLS policies
SELECT * FROM pg_policies WHERE tablename = 'chat_messages';

-- Temporarily disable RLS for testing
ALTER TABLE chat_messages DISABLE ROW LEVEL SECURITY;
```

#### 3. No AI Response

**Problem**: Weaviate empty or Gemini API issue

**Solution**:
```bash
# Check Weaviate has data
curl http://your-weaviate-url/v1/objects

# Check Gemini API key
# Test in n8n node execution
```

#### 4. Document Processing Fails

**Problem**: Google Drive permissions or file format

**Solution**:
- Verify Drive API enabled
- Check OAuth scopes include drive.readonly
- Test with different file formats

### Debug Mode

Enable verbose logging:

```python
# In app.py
import logging
logging.basicConfig(level=logging.DEBUG)

# In n8n nodes
console.log('Debug:', JSON.stringify(data, null, 2));
```

### Health Checks

Add health check endpoint:

```python
# health.py - Simple health check
from supabase import create_client
import os

def check_health():
    checks = {
        'supabase': False,
        'webhook': False
    }
    
    # Check Supabase
    try:
        supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        supabase.table('documents').select('id').limit(1).execute()
        checks['supabase'] = True
    except:
        pass
    
    # Check webhook
    try:
        import requests
        response = requests.post(os.getenv('N8N_WEBHOOK_URL'), timeout=5)
        checks['webhook'] = True
    except:
        pass
    
    return checks

if __name__ == '__main__':
    print(check_health())
```

## Scaling Considerations

### When to Scale

Monitor these metrics:
- Response time > 3 seconds
- Error rate > 1%
- Database connections > 80% of pool
- Weaviate query time > 500ms

### Scaling Options

1. **Horizontal Scaling**: Add more Streamlit instances
2. **Database**: Upgrade Supabase plan
3. **Vector Store**: Upgrade Weaviate cluster
4. **Caching**: Add Redis for session management

---

## Next Steps

✅ Set up staging environment  
✅ Configure CI/CD pipeline  
✅ Add automated backups  
✅ Implement A/B testing  
✅ Add user authentication  
✅ Set up error tracking (Sentry)  

---

**Need Help?** Check the [main README](../README.md) or open an issue on GitHub.