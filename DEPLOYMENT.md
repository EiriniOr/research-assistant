# Deployment Guide - Streamlit Cloud

## Prerequisites

- GitHub repository with code (✓ already done)
- Streamlit Cloud account
- Anthropic API key

## Deployment Steps

### 1. Push Latest Changes to GitHub

Make sure all files are committed:

```bash
cd /Users/rena/research-assistant
git add .
git commit -m "Add Streamlit Cloud deployment config"
git push origin eirini/initial-setup
```

### 2. Merge to Main (Recommended)

Streamlit Cloud typically deploys from `main` branch:

```bash
# Create PR and merge via GitHub UI, or:
git checkout main
git merge eirini/initial-setup
git push origin main
```

### 3. Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Sign in with GitHub

2. **Create New App**
   - Click "New app" button
   - Select repository: `eirinior/research-assistant`
   - Branch: `main` (or `eirini/initial-setup`)
   - Main file path: `src/main.py`
   - Click "Deploy"

3. **Configure Secrets**
   - Before app runs, click "Advanced settings" or "Secrets"
   - Add your secrets in TOML format:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-your-actual-key-here"
   ```
   - Click "Save"

4. **Wait for Deployment**
   - First deployment takes 2-5 minutes
   - Watch the logs for any errors
   - App will auto-restart after secrets are added

### 4. Your App Will Be Live At:

```
https://eirinior-research-assistant.streamlit.app
```

Or similar URL (Streamlit will show the exact URL)

## Configuration Files Added

- `.streamlit/config.toml` - Streamlit UI config
- `.streamlit/secrets.toml.example` - Secret template (example only)
- `packages.txt` - System packages (if needed)
- `requirements.txt` - Python dependencies (already exists)

## Streamlit Cloud Features

- **Auto-deploys**: Pushes to GitHub auto-deploy
- **Free tier**: Public apps are free
- **Secrets management**: Secure API key storage
- **SSL/HTTPS**: Automatic
- **Custom domain**: Available on paid plans

## Troubleshooting

### If deployment fails:

1. **Check logs** in Streamlit Cloud dashboard
2. **Common issues:**
   - Missing `requirements.txt` (✓ we have it)
   - Wrong main file path (should be `src/main.py`)
   - Missing secrets (add ANTHROPIC_API_KEY)
   - Import errors (check all dependencies in requirements.txt)

### If app crashes on load:

1. Check secrets are set correctly (ANTHROPIC_API_KEY in Streamlit secrets)
2. Config automatically uses defaults on Streamlit Cloud (no config.yaml needed)
3. Check logs for specific error messages

### If search fails ("No sources found"):

**Known Issue**: DuckDuckGo may rate-limit or block Streamlit Cloud IPs

**Workarounds**:
1. Try more specific queries
2. Wait a few minutes between searches
3. Consider alternative: use a search API with auth (requires code changes)
4. Deploy on your own server with different IP

## Monitoring

- **View logs**: Streamlit Cloud dashboard → Manage app → Logs
- **View metrics**: Dashboard shows usage stats
- **Errors**: Will appear in logs and app UI

## Updates

To update your deployed app:

```bash
# Make changes locally
git add .
git commit -m "Update: description"
git push origin main

# Streamlit Cloud auto-deploys within ~1 minute
```

## Making Repository Public (Optional)

Currently your repo is private. To share the app publicly:

1. Go to GitHub repo settings
2. Scroll to "Danger Zone"
3. Click "Change visibility" → "Make public"
4. Confirm

Note: Keep secrets in Streamlit Cloud dashboard, not in repo!

## Custom Domain (Paid Feature)

To use your own domain:
1. Upgrade to Streamlit Cloud Pro
2. Add custom domain in settings
3. Configure DNS records

## Costs

- **Free tier**: Unlimited public apps, 1GB resources per app
- **Paid tier**: Private apps, more resources, custom domains

## Security Notes

- ✅ API key stored securely in Streamlit secrets
- ✅ secrets.toml excluded from git
- ✅ HTTPS automatic
- ✅ Environment variables not exposed to users

## Support

- Streamlit Docs: https://docs.streamlit.io/streamlit-community-cloud
- Community: https://discuss.streamlit.io/
