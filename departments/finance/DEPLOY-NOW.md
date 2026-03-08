# 🚀 DEPLOY GITHUB PAGES - IMMEDIATE ACTION

**Status:** ⏳ AWAITING GITHUB AUTH  
**Templates:** ✅ Approved & Ready  
**Time to Deploy:** 2 minutes after auth

---

## Step 1: Authenticate GitHub (REQUIRED - 30 seconds)

**Option A: Browser Flow (Easiest)**
```bash
# Run this command:
gh auth login

# Then:
# 1. Select "GitHub.com"
# 2. Select "HTTPS"
# 3. Copy the one-time code shown
# 4. Click the URL to open browser
# 5. Paste code and authorize
# 6. Come back - auth is automatic after browser
```

**Option B: Personal Access Token**
If you have a GitHub PAT:
```bash
# Create token at: https://github.com/settings/tokens
# Scopes: repo, workflow, read:org
# Then run:
echo "YOUR_PAT_TOKEN" | gh auth login --with-token
```

---

## Step 2: Deploy Templates (30 seconds)

After GitHub auth succeeds, run:

```bash
bash /home/ubuntu/.openclaw/workspace/departments/finance/tools/setup-gh-pages.sh
```

This will:
1. ✅ Create repo: `pandora-leadqual-templates`
2. ✅ Upload 5 files (index.html + 4 templates)
3. ✅ Enable GitHub Pages
4. ✅ Deploy to: `https://<your-username>.github.io/pandora-leadqual-templates/`

---

## Step 3: Verify Deployment (1 minute)

After script completes:

1. Visit: `https://<your-username>.github.io/pandora-leadqual-templates/`
2. Click each template link to verify
3. Test mobile responsiveness (shrink browser)
4. Test lead forms (they'll log to console)

---

## 📊 What You'll Get

**Live URLs:**
- Landing: `https://<username>.github.io/pandora-leadqual-templates/`
- Trades: `.../website-trades.html`
- Consultant: `.../website-consultant.html`
- Local Business: `.../website-local-business.html`

**Revenue Impact:**
- Week 1 Target: 5 website sales
- One-time: $1,485–$2,485
- MRR: $1,485–$2,485 (bundled with Lead Qual)

---

## 📧 Add to Cold Email (After Deployment)

Update Batch 2 cold emails with:

```
P.S. We're including a FREE professional website with Lead Qual 
subscriptions this month ($997 value). See our templates:

→ Trades: https://<username>.github.io/pandora-leadqual-templates/website-trades.html
→ Consultant: https://<username>.github.io/pandora-leadqual-templates/website-consultant.html
→ Local Business: https://<username>.github.io/pandora-leadqual-templates/website-local-business.html

Offer valid for first 10 customers this month.
```

---

## 🆘 Troubleshooting

**"Repository already exists"**
```bash
cd /tmp/pandora-leadqual-templates
git pull origin main
bash /home/ubuntu/.openclaw/workspace/departments/finance/tools/setup-gh-pages.sh
```

**"Pages not deploying"**
- Go to repo Settings > Pages
- Ensure Source is "Deploy from branch: main, /"
- Wait 2-5 minutes

**"404 Error"**
- Files must be in root directory
- Check file names are exact (case-sensitive)
- Wait for GitHub Pages build (Actions tab)

---

## ✅ Checklist

- [x] Templates created (5 files)
- [x] Templates approved by Jim
- [x] Deployment script ready
- [ ] GitHub authenticated ← **DO THIS NOW**
- [ ] Deploy script run
- [ ] Live URLs verified
- [ ] Cold email updated with links

---

**Ready when you are! Run `gh auth login` to start.**
