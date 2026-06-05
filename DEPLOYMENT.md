# Deployment Guide: Biologics Discovery Platform

## Streamlit Cloud Deployment

### Prerequisites
- Streamlit Community Cloud account ([streamlit.io](https://streamlit.io))
- GitHub repository with your code
- MongoDB Atlas account with a connection string
- (Optional) Resend API key for email functionality

---

## Step 1: Prepare Your Repository

### 1.1 Ensure `.gitignore` is properly configured
Your `.gitignore` should exclude:
- `.env` and `.env.*` - local environment files
- `.streamlit/secrets.toml` - local secrets (already excluded)
- `.venv/` and `venv/` - virtual environments
- `__pycache__/` - Python cache
- `.DS_Store`, `Thumbs.db` - OS files

### 1.2 Commit and push to GitHub
```bash
git add -A
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

---

## Step 2: Deploy on Streamlit Cloud

### 2.1 Connect your GitHub repo
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select your GitHub repo, branch, and main file (`app.py`)
4. Click **"Deploy"**

### 2.2 Add Secrets in Advanced Settings
Once your app is deployed, go to your app's settings and add secrets:

1. Click **Settings** (gear icon in top-right)
2. Click **Advanced settings**
3. Scroll to **"Secrets"** section
4. Paste the following in TOML format:

```toml
# Required: MongoDB Connection
MONGODB_URL = "mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?appName=Cluster0"
DATABASE_NAME = "biologics_platform"

# Optional: API Keys
RESEND_API_KEY = "your-resend-api-key-here"

# Optional: Dashboard Config (use defaults if not specified)
DASHBOARD_TITLE = "Biologics Discovery Platform Analytics"
DEFAULT_THEME = "dark"
LOG_LEVEL = "INFO"
CACHE_TTL = "3600"
```

5. Click **Save**

---

## Step 3: Required Secrets/Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `MONGODB_URL` | ✅ Yes | MongoDB connection string (use `mongodb+srv://` for Atlas) | `mongodb+srv://user:pass@cluster.mongodb.net/?appName=Cluster0` |
| `DATABASE_NAME` | ✅ Yes | Database name in MongoDB | `biologics_platform` |
| `RESEND_API_KEY` | ❌ No | Email API key (only needed if using email features) | `re_xxxxx` |
| `DASHBOARD_TITLE` | ❌ No | Custom app title | `"My Analytics"` |
| `DEFAULT_THEME` | ❌ No | Theme (`dark` or `light`) | `dark` |
| `LOG_LEVEL` | ❌ No | Logging level (`INFO`, `DEBUG`, `ERROR`) | `INFO` |
| `CACHE_TTL` | ❌ No | Cache TTL in seconds | `3600` |

---

## Step 4: Troubleshooting Connection Issues

### Problem: "Database connection failed"

**Solution 1: Verify MONGODB_URL format**
- Must start with `mongodb+srv://` (for Atlas) or `mongodb://` (for self-hosted)
- Include username and password
- Check for special characters - escape if needed

**Solution 2: Check MongoDB IP Whitelist**
- Go to MongoDB Atlas > Network Access
- Add Streamlit Cloud IPs to whitelist:
  - `0.0.0.0/0` (allow all - less secure but works)
  - Or specific Streamlit Cloud IPs (check Streamlit docs)

**Solution 3: Verify Secrets were saved**
- Go back to Advanced settings
- Confirm all secrets appear correctly (passwords may be masked)
- Secrets take ~1 minute to propagate

**Solution 4: Check application logs**
- Click **Manage app** > **View logs**
- Look for MongoDB connection errors
- Check for `st.secrets` access errors

---

## Step 5: Local Development Setup

### 5.1 Create `.streamlit/secrets.toml`
This file is automatically gitignored. Add your local secrets:

```toml
MONGODB_URL = "mongodb+srv://your-username:your-password@cluster.mongodb.net/?appName=Cluster0"
DATABASE_NAME = "biologics_platform"
RESEND_API_KEY = "your-api-key"
```

### 5.2 Run locally
```bash
# Activate virtual environment
.venv\Scripts\Activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Run the app
streamlit run app.py
```

---

## Step 6: Useful Streamlit Cloud Links

- **App Dashboard**: https://share.streamlit.io/your-username/your-repo
- **Settings**: Click gear icon on your app
- **View Logs**: Settings > Manage app > View logs
- **Secrets Docs**: https://docs.streamlit.io/deploy/streamlit-cloud/deploy-your-app#secrets-management

---

## Notes

- **Secrets are encrypted** at rest and in transit on Streamlit Cloud
- **Never commit** `.env` or `.streamlit/secrets.toml` files
- **Updates to secrets** require the app to restart
- **Environment variables** from your OS are NOT accessible on Streamlit Cloud (must use Secrets)
- The app reads from Streamlit Secrets first, then falls back to environment variables for local development

