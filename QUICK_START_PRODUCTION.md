# Quick Start: Deploy to Production (10 minutes)

## Requirements
- GitHub account with this repo
- Render account (free: render.com)
- Vercel account (free: vercel.com)
- Google Gemini API key (free tier: ai.google.dev)
- Gmail account with App Password (support.google.com/accounts/answer/185833)

---

## Step 1: Push to GitHub (2 min)

```bash
git add -A
git commit -m "Production deployment"
git push origin main
```

---

## Step 2: Deploy Backend to Render (3 min)

1. Go to **render.com** → Sign up / Log in
2. Click **New** → **Blueprint**
3. Paste: `https://github.com/YOUR_USERNAME/n8n.git`
4. Render reads `render.yaml` and auto-configures
5. Set **Environment Variables:**
   - `GEMINI_API_KEY` = from ai.google.dev
   - `GMAIL_USER` = hr@company.com
   - `GMAIL_APP_PASSWORD` = 16-char from Gmail settings
   - `COMPANY_NAME` = Your Company
   - `ENV` = production
6. Click **Deploy** → Wait 5 min

**Note the Render URL:** `https://recruitment-api-xxxx.onrender.com`

---

## Step 3: Deploy Frontend to Vercel (3 min)

1. Go to **vercel.com** → Sign up / Log in
2. Click **Add New** → **Project**
3. Select this GitHub repo
4. **Framework:** Vite
5. **Root Directory:** `frontend`
6. **Environment Variable:**
   - `VITE_BACKEND_URL` = https://recruitment-api-xxxx.onrender.com (from Step 2)
7. Click **Deploy** → Wait 2 min

**Note the Vercel URL:** `https://your-project.vercel.app`

---

## Step 4: Update Render Backend URL (1 min)

Back in Render dashboard:
1. Click **recruitment-api** service
2. Settings → Environment
3. Add: `FRONTEND_URL` = https://your-project.vercel.app
4. Click **Save** → Auto-redeploys

---

## Done! ✅

- **HR Panel:** https://your-project.vercel.app/admin
- **API Docs:** https://recruitment-api-xxxx.onrender.com/docs
- **Test Endpoint:** https://recruitment-api-xxxx.onrender.com/api/jobs

---

## Test It

```bash
# List available jobs
curl https://recruitment-api-xxxx.onrender.com/api/jobs

# View dashboard
curl https://recruitment-api-xxxx.onrender.com/api/dashboard/stats
```

Open HR panel in browser and you're live!

---

## Optional: n8n Email Delivery

For advanced email flows with n8n:

1. Deploy n8n separately (n8n.cloud or self-hosted)
2. Import workflows from `n8n/` folder
3. Set n8n env vars:
   - `GEMINI_API_KEY`
   - `BACKEND_URL=https://recruitment-api-xxxx.onrender.com`
   - `N8N_BLOCK_ENV_ACCESS_IN_NODE=false`
4. Update Render `N8N_TEST_RESULT_WEBHOOK_URL`

Without n8n: Backend uses Gmail SMTP directly (already configured via `GMAIL_USER` + `GMAIL_APP_PASSWORD`).

---

## Troubleshooting

| Problem | Fix |
|---|---|
| 502 Bad Gateway | Check Render logs: `recruitment-api` → Logs |
| Emails not sending | Verify `GMAIL_APP_PASSWORD` (must be 16-char from Gmail settings, not your Gmail password) |
| Frontend blank | Check browser console (F12). Verify `VITE_BACKEND_URL` in Vercel env vars. |
| Database error | Render auto-creates PostgreSQL. Check connection string in logs. |

---

## See Also

- Full guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- Local setup: [README.md](README.md) (Section 5)
