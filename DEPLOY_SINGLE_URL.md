# Deploy Everything on Render (Single URL)

One simple command. One Render service. Frontend + Backend + Database on the same URL.

---

## Architecture

```
Single Render URL: https://recruitment-app-xxxx.onrender.com
    ├── Frontend (React app served as static files)
    ├── Backend API (/api/*)
    └── PostgreSQL Database
```

**Everything is on ONE domain.** No CORS issues, no separate deployments.

---

## Prerequisites

- GitHub account with this repo
- Render account (free tier: render.com)
- Google Gemini API key (free: ai.google.dev)
- Gmail account with App Password

---

## Deploy in 5 Minutes

### Step 1: Push to GitHub

```bash
git add -A
git commit -m "Deploy to single Render URL"
git push origin main
```

### Step 2: Deploy to Render

1. Go to **render.com** → Sign up / Log in
2. Click **New** → **Blueprint**
3. Paste your GitHub repo URL:
   ```
   https://github.com/YOUR_USERNAME/n8n.git
   ```
4. Render auto-reads `render.yaml` and configures:
   - Single service for frontend + backend
   - PostgreSQL database
   - Automatic builds

5. **Set Environment Variables:**
   - `GEMINI_API_KEY` = your Google Gemini key
   - `GMAIL_USER` = hr@your-company.com
   - `GMAIL_APP_PASSWORD` = 16-char app password
   - `COMPANY_NAME` = Your Company Name

6. Click **Deploy** → Wait 5-10 minutes

### Step 3: Done!

Your app is live at: `https://recruitment-app-xxxx.onrender.com`

- **HR Panel:** `https://recruitment-app-xxxx.onrender.com/admin`
- **API Docs:** `https://recruitment-app-xxxx.onrender.com/docs`
- **Jobs API:** `https://recruitment-app-xxxx.onrender.com/api/jobs`

---

## What Happens During Deployment

Render automatically:

1. **Builds frontend**: `npm install && npm run build` → creates `frontend/dist/`
2. **Installs backend**: `pip install -r requirements.txt`
3. **Creates PostgreSQL**: Auto-provisioned database
4. **Starts backend**: Gunicorn serves both API + frontend static files
5. **Health checks**: Monitors if service stays online

```
Render Build Process:
  cd frontend && npm install && npm run build
  cd backend && pip install -r requirements.txt
  gunicorn app.main:app  (serves / for React + /api/* for backend)
```

---

## Architecture (How It Works)

```
Browser Request → Render Server (Single URL)
    │
    ├─ GET / → FastAPI serves frontend/dist/index.html (React SPA)
    ├─ GET /admin → FastAPI serves frontend/dist/index.html
    ├─ GET /test/:token → FastAPI serves frontend/dist/index.html
    │
    ├─ GET /api/jobs → Backend API returns JSON
    ├─ POST /api/candidates/screen → Backend processes resume
    └─ GET /api/dashboard/stats → Backend returns stats
    
    All requests go to the same Render domain.
    PostgreSQL handles all data persistence.
```

### No CORS Issues

Because frontend and backend are on the **same domain** (`recruitment-app-xxxx.onrender.com`), there are no CORS restrictions. Requests from React to API work automatically.

---

## Local Development (Unchanged)

Development workflow stays the same:

```bash
# Terminal 1 - Backend
cd backend
./venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend (dev server)
cd frontend
npm run dev  # Runs on http://localhost:5173, proxies API to localhost:8000
```

The frontend dev server still proxies API calls to `localhost:8000` for development.

---

## Environment Variables

### Required (Set in Render)

| Variable | Value |
|---|---|
| `GEMINI_API_KEY` | Your Google Gemini key |
| `GMAIL_USER` | hr@company.com |
| `GMAIL_APP_PASSWORD` | 16-char app password from Gmail |
| `COMPANY_NAME` | Your Company Name |

### Auto-Set by Render

| Variable | Value |
|---|---|
| `DATABASE_URL` | PostgreSQL connection (auto-set) |
| `ENV` | `production` |
| `FRONTEND_URL` | Auto-set to Render domain |
| `BACKEND_URL` | Auto-set to Render domain |

### Optional

| Variable | Default |
|---|---|
| `N8N_TEST_RESULT_WEBHOOK_URL` | Not set (uses Gmail SMTP) |
| `GEMINI_MODEL` | `gemini-3.6-flash` |

---

## Testing After Deployment

```bash
# Test API is running
curl https://recruitment-app-xxxx.onrender.com/api/jobs

# Test frontend loads
curl https://recruitment-app-xxxx.onrender.com/admin

# Test database stats
curl https://recruitment-app-xxxx.onrender.com/api/dashboard/stats
```

All three should work on the **same URL**.

---

## Cost

| Service | Cost |
|---|---|
| Render (Web Service) | $7/month (free tier available but limited) |
| PostgreSQL | $15/month (free tier available) |
| Google Gemini | Free tier + pay-as-you-go (~$1-5/month) |
| **Total** | ~$22-25/month |

**Free tier available**: Both web service and database have limited free tiers on Render.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| 502 Bad Gateway | Check Render logs. Frontend build might have failed. |
| Blank page / 404 | Check that `frontend/dist/` was built. Look at build logs. |
| API 404 | Ensure backend is running. Test `/api/jobs` endpoint. |
| Database connection error | Render auto-creates PostgreSQL. Check if service status is "Live". |
| Emails not sending | Verify `GMAIL_USER` and `GMAIL_APP_PASSWORD` in Render env vars. |

---

## Logs

Check logs in Render dashboard:

1. Go to **recruitment-app** service
2. Click **Logs** tab
3. See real-time output from gunicorn and build process

---

## Update & Redeploy

To update the app:

```bash
git add -A
git commit -m "Update"
git push origin main
```

Render auto-detects the push and redeploys automatically.

---

## Custom Domain (Optional)

To use your own domain:

1. Go to Render service → **Settings** → **Custom Domains**
2. Add `recruiter.yourcompany.com`
3. Point DNS CNAME to Render's domain
4. SSL auto-configures (free)

---

## FAQ

**Q: Why is everything on one URL?**  
A: Simpler deployment, no CORS issues, and everything stays in sync. The backend serves both API and static files.

**Q: Can I separate frontend and backend later?**  
A: Yes. Remove the static file serving from `backend/app/main.py` and deploy frontend to Vercel separately.

**Q: What if the service goes down?**  
A: Render has uptime monitoring. Set up email alerts in Settings.

**Q: How do I scale?**  
A: Render handles auto-scaling on paid plans. Start with free/basic tier.

**Q: Can I use a different database?**  
A: Yes. Change `DATABASE_URL` to any PostgreSQL-compatible database.

---

## Next Steps

1. Push to GitHub
2. Go to Render and create blueprint
3. Set env vars
4. Deploy
5. Done! 🎉

Your recruitment system is live on a single Render URL.
