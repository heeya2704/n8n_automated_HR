import axios from 'axios';

// In production (single Render URL), use relative paths (same domain)
// In development, use localhost:8000 or the specified VITE_BACKEND_URL
const API_BASE_URL = (() => {
  const env = import.meta.env.VITE_BACKEND_URL;
  if (env) return env;

  // If running locally in dev, use localhost
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }

  // Production: use same domain (Render serves both frontend + backend)
  return window.location.origin;
})();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const testService = {
  verifyToken: async (token) => {
    const response = await api.get(`/api/test/${token}`);
    return response.data;
  },
  submitTest: async (token, answers) => {
    const response = await api.post(`/api/test/${token}/submit`, { answers });
    return response.data;
  }
};

export const dashboardService = {
  getStats: async () => {
    const response = await api.get('/api/dashboard/stats');
    return response.data;
  },
  getResume: async (candidateId) => {
    const response = await api.get(`/api/candidates/${candidateId}/resume`);
    return response.data;
  },
  offerLetterUrl: (candidateId) => `${API_BASE_URL}/api/candidates/${candidateId}/offer-letter`,
  getCandidates: async (status) => {
    const response = await api.get('/api/candidates', {
      params: status ? { status } : {}
    });
    return response.data;
  }
};

export const gmailService = {
  syncInbox: async (job_id = 'python-ml-developer-001') => {
    const response = await api.post(`/api/gmail/sync-inbox`, null, {
      params: { job_id }
    });
    return response.data;
  },
  configure: async (gmail_user, gmail_app_password) => {
    const response = await api.post('/api/gmail/configure', {
      gmail_user,
      gmail_app_password
    });
    return response.data;
  }
};

export const jobService = {
  getJobs: async () => {
    const response = await api.get('/api/jobs');
    return response.data;
  }
};

export default api;
