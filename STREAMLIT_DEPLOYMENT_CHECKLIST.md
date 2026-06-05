# Streamlit Cloud Deployment Checklist

## ✅ Before Deploying

- [ ] All code is committed and pushed to GitHub
- [ ] `.gitignore` includes:
  - [ ] `.env` and `.env.*`
  - [ ] `.streamlit/secrets.toml`
  - [ ] `.venv/` or `venv/`
  - [ ] `__pycache__/`
  - [ ] `.DS_Store`, `Thumbs.db`
- [ ] `requirements.txt` is up-to-date:
  ```bash
  pip freeze > requirements.txt
  ```
- [ ] App runs locally without errors:
  ```bash
  streamlit run app.py
  ```

## ✅ During Deployment

1. **Go to** [share.streamlit.io](https://share.streamlit.io)
2. **Click** "New app"
3. **Select:**
   - Repository: `yourusername/biologics_dashboards`
   - Branch: `main`
   - Main file path: `app.py`
4. **Click** "Deploy" (wait 2-3 minutes)

## ✅ After Deployment - Add Secrets (CRITICAL)

1. **Click** the **Settings gear icon** (top-right of your app)
2. **Click** "Advanced settings"
3. **Scroll to** "Secrets" section
4. **Paste this TOML** (update values for your setup):

```toml
MONGODB_URL = "mongodb+srv://quantxai25_db_user:2Xj4kePUqLqoIZcm@cluster0.qyzjacn.mongodb.net/?appName=Cluster0"
DATABASE_NAME = "biologics_platform"
RESEND_API_KEY = "your-api-key-here"
DASHBOARD_TITLE = "Biologics Discovery Platform Analytics"
DEFAULT_THEME = "dark"
LOG_LEVEL = "INFO"
```

5. **Click** "Save"
6. **Wait 1-2 minutes** for secrets to propagate
7. **Refresh** your app URL

## ✅ Troubleshooting

| Issue | Solution |
|-------|----------|
| **"Database connection failed"** | 1. Check MONGODB_URL in secrets<br>2. Add Streamlit IPs to MongoDB whitelist (0.0.0.0/0)<br>3. Verify username/password has no special chars |
| **Secrets not working** | 1. Verify TOML syntax (no quotes around URLs)<br>2. Wait 2 minutes after saving<br>3. Click **Reboot** in app settings |
| **App won't load** | Check app logs: Settings > Manage app > View logs |
| **Module import error** | Add missing packages to `requirements.txt` and redeploy |

## 📋 Required Secrets

```toml
# MUST HAVE - MongoDB connection
MONGODB_URL = "mongodb+srv://username:password@cluster.mongodb.net/?appName=Cluster0"
DATABASE_NAME = "biologics_platform"
```

## 📋 Optional Secrets

```toml
# Only if using email features
RESEND_API_KEY = "re_xxxxxxxxx"

# Only if you want custom values (defaults work fine)
DASHBOARD_TITLE = "My Dashboard"
DEFAULT_THEME = "dark"
LOG_LEVEL = "INFO"
CACHE_TTL = "3600"
```

## 🔗 Useful Links

- **Streamlit Secrets Docs**: https://docs.streamlit.io/deploy/streamlit-cloud/deploy-your-app#secrets-management
- **MongoDB Connection String**: https://docs.mongodb.com/manual/reference/connection-string/
- **App URL**: `https://share.streamlit.io/yourusername/biologics_dashboards`

---

**💡 Tip**: Test locally first by adding secrets to `.streamlit/secrets.toml` and running `streamlit run app.py`
