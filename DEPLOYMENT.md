# Production Deployment Guide

Deploy to **Render** (backend + PostgreSQL) and **Vercel** (frontend).

## Prerequisites

- GitHub account with this repo pushed
- Render account (free tier available)
- Vercel account (free tier available)
- Google Gemini API key
- Gmail account with App Password enabled
- n8n instance (self-hosted or cloud)

---

## Step 1: Prepare the Backend for Production

### 1a. Update `backend/requirements.txt`

Add production dependencies:

```bash
cd backend
pip freeze > requirements-temp.txt
```

Ensure these are in `requirements.txt`:
- `gunicorn>=21.0.0` (WSGI server)
- `psycopg2-binary>=2.9.0` (PostgreSQL driver)
- All existing packages from earlier freeze

```bash
echo "gunicorn>=21.0.0" >> requirements.txt
echo "psycopg2-binary>=2.9.0" >> requirements.txt
```

### 1b. Update `backend/app/database.py` for PostgreSQL

The code already uses `DATABASE_URL` env var, so it will work with PostgreSQL's connection string:

```python
# Already correct - no changes needed if DATABASE_URL is set
# Render will inject: postgresql://user:pass@host:5432/recruitment_db
```

---

## Step 2: Push to GitHub

```bash
cd /d/Personal/n8n
git add -A
git commit -m "Production deployment ready for Render + Vercel"
git push origin main
```

---

## Step 3: Deploy Backend to Render

1. Go to [render.com](https://render.com) → Sign up / Log in
2. Click **New** → **Blueprint**
3. Paste this repo's GitHub URL: `https://github.com/YOUR_USERNAME/n8n.git`
4. Render will detect `render.yaml` and auto-configure:
   - **recruitment-api** (Python/Gunicorn)
   - **recruitment-db** (PostgreSQL)
5. Set environment variables:
   - `GEMINI_API_KEY` = your Google Gemini key
   - `GMAIL_USER` = hr@your-company.com
   - `GMAIL_APP_PASSWORD` = 16-char app password from Google
   - `N8N_TEST_RESULT_WEBHOOK_URL` = https://your-n8n.com/webhook/test-result
   - `COMPANY_NAME` = Your Company
6. Click **Deploy**
7. Wait ~5 min. Note the URL: `https://recruitment-api-xxxx.onrender.com`

**First deploy:** Render runs migrations automatically. Check logs if the database doesn't initialize.

---

## Step 4: Deploy Frontend to Vercel

### 4a. Update `frontend/.env.production`

Create this file:

```env
VITE_BACKEND_URL=https://recruitment-api-xxxx.onrender.com
```

Replace `xxxx` with your Render service ID.

### 4b. Deploy to Vercel

1. Go to [vercel.com](https://vercel.com) → Sign up / Log in
2. Click **Add New** → **Project**
3. Select this GitHub repo
4. **Framework:** Vite
5. **Root Directory:** `frontend`
6. **Build Command:** `npm run build`
7. **Output Directory:** `dist`
8. Environment variables:
   - `VITE_BACKEND_URL` = https://recruitment-api-xxxx.onrender.com (from Step 3)
9. Click **Deploy**
10. Wait ~2 min. Note the URL: `https://your-project.vercel.app`

---

## Step 5: Update Backend URLs

Back in Render, update environment variables:

- `FRONTEND_URL` = https://your-project.vercel.app
- `BACKEND_URL` = https://recruitment-api-xxxx.onrender.com

Render auto-redeploys.

---

## Step 6: Test the Live System

1. Open **HR Panel:** https://your-project.vercel.app/admin
2. Test resume screening:
   ```bash
   $resume = Get-Content sample_data\sample_resume_eligible.txt -Raw
   $uri = "https://recruitment-api-xxxx.onrender.com/api/candidates/screen-resume?name=Jane&email=jane@example.com&job_id=python-ml-developer-001"
   Invoke-RestMethod -Method Post -Uri $uri -ContentType "application/json" -Body ($resume | ConvertTo-Json)
   ```
3. Verify the test link in the response opens and works.
4. Check logs in Render if any errors occur.

---

## Step 7: Configure n8n (Optional)

If using n8n for email delivery:

1. Deploy n8n (self-hosted or cloud)
2. Import workflows from `n8n/` folder
3. Set n8n environment variables:
   - `GEMINI_API_KEY`
   - `GEMINI_MODEL=gemini-3.6-flash`
   - `BACKEND_URL=https://recruitment-api-xxxx.onrender.com`
   - `N8N_BLOCK_ENV_ACCESS_IN_NODE=false`
4. Update backend `N8N_TEST_RESULT_WEBHOOK_URL` to your n8n deployment
5. Activate both workflows in n8n

**Without n8n:** The backend uses Gmail SMTP directly to send emails. Set `GMAIL_USER` and `GMAIL_APP_PASSWORD` and it works.

---

## Step 8: Set Up a Custom Domain (Optional)

### Vercel Custom Domain
1. Go to Vercel project → Settings → Domains
2. Add your domain (e.g., `portal.company.com`)
3. Point DNS CNAME to `cname.vercel.com`

### Render Custom Domain
1. Go to Render service → Settings → Custom Domains
2. Add your domain (e.g., `api.company.com`)
3. Point DNS to Render's nameserver

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Database connection error | Check `DATABASE_URL` in Render env vars. Vercel provides the connection string automatically. |
| 502 Bad Gateway | Check backend logs in Render. Run `curl https://recruitment-api-xxxx.onrender.com/api/jobs` to verify it's responding. |
| Emails not sending | Verify `GMAIL_USER` and `GMAIL_APP_PASSWORD` are correct. Test with `POST /api/gmail/sync-inbox` endpoint. |
| Gemini API 404 | Ensure `GEMINI_MODEL=gemini-3.6-flash` (not the deprecated `gemini-1.5-flash`). |
| CORS errors in browser | Backend CORS already allows `*` in production. If still failing, check frontend's actual `VITE_BACKEND_URL`. |

---

## Monitoring & Logs

### Render
- Click service → Logs tab
- View real-time logs and past deployments

### Vercel
- Click project → Deployments tab
- Click "View Logs" on any deployment

### Database
- Render dashboard → Postgres instance → Logs tab
- Check for connection issues or query timeouts

---

## Scaling (When You Get More Traffic)

- **Render:** Upgrade plan to paid instances (standard plan is ~$7/mo)
- **Vercel:** Automatic scaling (stays on free tier for normal traffic)
- **Database:** Upgrade PostgreSQL plan to standard (~$15/mo)
- **n8n:** Consider self-hosted or n8n Cloud with paid plan

---

## Security Checklist

✅ Never commit `.env` files (`.gitignore` includes them)
✅ Use strong `GMAIL_APP_PASSWORD` (16 chars, not actual Gmail password)
✅ Rotate `GEMINI_API_KEY` if leaked
✅ Backend CORS allows only your frontend domain in production (update if needed)
✅ Database backups: Render PostgreSQL auto-backups daily
✅ Use HTTPS everywhere (both platforms provide free SSL)
✅ Monitor logs for suspicious activity

---

## Cost Estimate (Monthly)

| Service | Free Tier | Starter |
|---|---|---|
| Render API | $0 (limited) | $7 |
| Render PostgreSQL | $0 (limited) | $15 |
| Vercel Frontend | $0 | N/A |
| Google Gemini API | $0 (free tier) | Pay-as-you-go |
| **Total** | ~$0-2 | ~$22-30 |

---

## Next Steps

1. Enable **database backups** (Render → Postgres → Settings)
2. Set up **error monitoring** (Sentry, LogRocket, etc.)
3. Add **rate limiting** to prevent abuse
4. Implement **analytics** (Vercel Web Analytics, PostHog)
5. Set up **automated tests** in GitHub Actions
