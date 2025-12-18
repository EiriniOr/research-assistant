# 🚀 Quick Deploy to Streamlit Cloud

## Step 1: Merge to Main Branch

```bash
cd /Users/rena/research-assistant

# Create main branch if it doesn't exist
git checkout -b main
git push -u origin main

# Or merge your current branch into main
git checkout main
git pull origin main
git merge eirini/initial-setup
git push origin main
```

## Step 2: Go to Streamlit Cloud

1. Visit: **https://share.streamlit.io/**
2. Sign in with GitHub

## Step 3: Deploy Your App

Click **"New app"** button and fill in:

```
Repository: [your-username]/research-assistant
Branch: main
Main file path: src/main.py
```

Click **"Deploy!"**

## Step 4: Add Your API Key

While the app is deploying (or after it fails the first time):

1. Click **"Advanced settings"** or **"⋮" menu → "Settings"**
2. Go to **"Secrets"** tab
3. Paste this (with your actual key):

```toml
ANTHROPIC_API_KEY = "sk-ant-your-actual-key-here"
```

4. Click **"Save"**
5. App will automatically restart

## Step 5: Done! 🎉

Your app will be live at:

```
https://research-assistant-[something].streamlit.app
```

Or similar URL (check the dashboard for exact URL)

## Common Issues

### "Config file not found"
- **Solution**: App is trying to find config.yaml, but on Streamlit Cloud it uses secrets
- This should work automatically with our updated config_loader.py
- If it doesn't, check that secrets are saved correctly

### "ANTHROPIC_API_KEY not set"
- **Solution**: Add the key in Streamlit Cloud Secrets (Step 4 above)
- Make sure there are no extra spaces or quotes

### "Import errors"
- **Solution**: requirements.txt should have all dependencies
- Check deployment logs for specific missing packages

### App is slow/crashes
- **Solution**: Free tier has limited resources
- First run is always slower
- Try reducing "Sources per query" in the UI

## Updating Your Deployed App

After deployment, any push to GitHub will auto-deploy:

```bash
# Make changes locally
git add .
git commit -m "Update something"
git push origin main

# Streamlit Cloud auto-deploys in ~1 minute
```

## Share Your App

Once deployed, you can share the URL with anyone!

Example: `https://research-assistant.streamlit.app`

## Monitoring

- **View logs**: Streamlit Cloud dashboard → Your app → "Manage app" → "Logs"
- **Restart**: Dashboard → "⋮" → "Reboot app"
- **View metrics**: Dashboard shows usage stats

## Next Steps

- [ ] Test the deployed app with a sample question
- [ ] Share the URL in your portfolio
- [ ] Consider making the GitHub repo public (optional)
- [ ] Add the app link to your README

## Support

If you get stuck:
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting
- Streamlit Docs: https://docs.streamlit.io/streamlit-community-cloud
- Community: https://discuss.streamlit.io/

---

**Ready to deploy? Follow Steps 1-4 above! 🚀**
