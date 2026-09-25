# Production Deployment Checklist

## Pre-Deployment (Before pushing to GitHub)

- [ ] **Secrets**: All API keys moved to `.env.production` (never committed)
- [ ] **Database**: PostgreSQL connection string verified
- [ ] **CORS**: Set `FRONTEND_URL` and `BACKEND_URL` env vars
- [ ] **Email**: `GMAIL_USER` and `GMAIL_APP_PASSWORD` configured
- [ ] **Gemini**: API key set and `GEMINI_MODEL=gemini-3.6-flash`
- [ ] **Logging**: Check `backend/app/services/notifications.py` for proper error logging
- [ ] **Tests**: `pytest tests -q` passes locally
- [ ] **Dependencies**: `requirements.txt` includes gunicorn and psycopg2-binary
- [ ] **Environment**: `.env` in `.gitignore` (never commit)

## GitHub Setup

- [ ] Repository pushed with `render.yaml` and `vercel.json`
- [ ] GitHub Actions workflow (`test.yml`) configured
- [ ] README updated with production deployment steps

## Render Deployment (Backend + PostgreSQL)

- [ ] **Create render.yaml blueprint**
  - [ ] Backend service uses gunicorn
  - [ ] PostgreSQL database auto-created
  - [ ] Environment variables set
- [ ] **Deploy**
  - [ ] Click "Blueprint" on Render
  - [ ] Paste GitHub repo URL
  - [ ] Render auto-detects `render.yaml`
  - [ ] Set secret env vars (GEMINI_API_KEY, GMAIL_USER, GMAIL_APP_PASSWORD)
  - [ ] Click Deploy → Wait 5 minutes
  - [ ] Check logs for errors
  - [ ] Test health check: `curl https://api-xxxx.onrender.com/`
- [ ] **Note Render URL** for next steps

## Vercel Deployment (Frontend)

- [ ] **Create vercel.json** with Vite config
- [ ] **Connect GitHub repo**
  - [ ] Go to vercel.com → Add Project
  - [ ] Select this GitHub repo
  - [ ] Framework: Vite, Root: frontend
- [ ] **Environment Variables**
  - [ ] `VITE_BACKEND_URL=https://api-xxxx.onrender.com` (from Render step)
- [ ] **Deploy** → Wait 2 minutes
- [ ] **Note Vercel URL** for Render update

## Post-Deployment

### Render: Update Backend with Frontend URL

- [ ] Go to Render dashboard → recruitment-api service
- [ ] Settings → Environment Variables
- [ ] Add `FRONTEND_URL=https://your-project.vercel.app`
- [ ] Save → Auto-redeploys

### Test Everything

- [ ] API Docs: `https://api-xxxx.onrender.com/docs` loads
- [ ] HR Panel: `https://your-project.vercel.app/admin` loads
- [ ] Dashboard stats: `curl https://api-xxxx.onrender.com/api/dashboard/stats`
- [ ] List jobs: `curl https://api-xxxx.onrender.com/api/jobs`
- [ ] Test resume screening endpoint
- [ ] Check database logs on Render

### Optional: n8n Setup (For Advanced Email Flows)

- [ ] Deploy n8n instance
- [ ] Import `n8n/resume-screening-workflow.json`
- [ ] Import `n8n/test-result-workflow.json`
- [ ] Set n8n environment variables
  - [ ] `GEMINI_API_KEY`
  - [ ] `BACKEND_URL=https://api-xxxx.onrender.com`
  - [ ] `N8N_BLOCK_ENV_ACCESS_IN_NODE=false`
- [ ] Update Render `N8N_TEST_RESULT_WEBHOOK_URL` with n8n webhook URL
- [ ] Activate both workflows in n8n

## Monitoring & Maintenance

- [ ] **Logging**
  - [ ] Render: Check service logs daily for errors
  - [ ] Vercel: Check deployment logs if issues occur
- [ ] **Database Backups**
  - [ ] Render PostgreSQL: Auto-backs up daily (free tier)
  - [ ] Monitor database size
- [ ] **Email Delivery**
  - [ ] Test sending emails via Gmail SMTP
  - [ ] Monitor bounce rate in Gmail
- [ ] **API Performance**
  - [ ] Monitor Gemini API latency
  - [ ] Check rate limits on Google API
- [ ] **Error Tracking**
  - [ ] Set up Sentry or similar (optional)
  - [ ] Monitor Render logs for exceptions
- [ ] **Security**
  - [ ] Rotate GEMINI_API_KEY quarterly
  - [ ] Rotate JWT_SECRET if compromised
  - [ ] Monitor for unauthorized access attempts

## Scaling (When Needed)

### If hitting Render limits:
- [ ] Upgrade to Standard plan ($7/mo for backend, $15/mo for database)
- [ ] Add more Gunicorn workers (set via env var)
- [ ] Enable caching on Vercel Pro ($20/mo)

### Cost tracking:
- Render API: $7/mo (standard)
- Render PostgreSQL: $15/mo (standard)
- Vercel Frontend: $0/mo (free tier)
- Google Gemini API: ~$1-5/mo (free tier + pay-as-you-go)
- **Total: ~$22-27/mo**

## Rollback Procedure

If deployment breaks:

1. **Vercel**: Click a previous deployment → Click Deploy button
2. **Render**: Click a previous deployment in the Deployments tab

Both auto-rollback to previous stable version.

## SSL/HTTPS Certificate

- ✅ Render: Auto-provides free SSL
- ✅ Vercel: Auto-provides free SSL
- Optional: Add custom domain with DNS CNAME

## Emergency Contacts

- Render Support: https://render.com/support
- Vercel Support: https://vercel.com/support
- Google Cloud: https://console.cloud.google.com

## Post-Launch Tasks

- [ ] Set up domain name (optional)
- [ ] Configure email notifications for Render alerts
- [ ] Set up analytics (Vercel Web Analytics, PostHog)
- [ ] Add error tracking (Sentry, LogRocket)
- [ ] Schedule regular database backups export
- [ ] Document runbook for your team
- [ ] Set up status page (status.io, Statuspage.io)
