import React, { useState, useEffect } from 'react';
import { dashboardService, gmailService } from '../services/api';
import { 
  Users, CheckCircle, XCircle, Mail, Send, Award, FileText, 
  Search, Filter, RefreshCw, ExternalLink, Copy, Cpu, Eye, Check, Settings, Loader2
} from 'lucide-react';

export default function AdminDashboardPage() {
  const [stats, setStats] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [copiedToken, setCopiedToken] = useState(null);

  // Gmail Modal State
  const [showGmailModal, setShowGmailModal] = useState(false);
  const [gmailUser, setGmailUser] = useState('');
  const [gmailPassword, setGmailPassword] = useState('');
  const [syncingGmail, setSyncingGmail] = useState(false);
  const [syncMsg, setSyncMsg] = useState(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await dashboardService.getStats();
      setStats(data);
      setCandidates(data.recent_candidates || []);
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleCopyTestLink = (token) => {
    const link = `${window.location.origin}/test/${token}`;
    navigator.clipboard.writeText(link);
    setCopiedToken(token);
    setTimeout(() => setCopiedToken(null), 2000);
  };

  const handleSyncGmail = async () => {
    try {
      setSyncingGmail(true);
      setSyncMsg(null);
      const res = await gmailService.syncInbox();
      if (res.status === 'SUCCESS') {
        setSyncMsg(`Successfully synced inbox! Processed ${res.processed_count} candidate email(s).`);
        fetchDashboardData();
      } else {
        setSyncMsg(res.message || 'Gmail credentials not configured.');
      }
    } catch (err) {
      setSyncMsg(err.response?.data?.detail || 'Failed to sync Gmail inbox.');
    } finally {
      setSyncingGmail(false);
    }
  };

  const handleSaveGmailConfig = async (e) => {
    e.preventDefault();
    try {
      setSyncingGmail(true);
      await gmailService.configure(gmailUser, gmailPassword);
      setSyncMsg('Gmail credentials saved successfully!');
      setShowGmailModal(false);
      handleSyncGmail();
    } catch (err) {
      setSyncMsg('Failed to save Gmail credentials.');
    } finally {
      setSyncingGmail(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'OFFER_SENT':
      case 'SELECTED':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">SELECTED / OFFER SENT</span>;
      case 'TEST_SENT':
      case 'RESUME_SHORTLISTED':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">TEST SENT</span>;
      case 'TEST_STARTED':
      case 'TEST_COMPLETED':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-purple-500/20 text-purple-400 border border-purple-500/30">TEST IN PROGRESS</span>;
      case 'RESUME_REJECTED':
      case 'TEST_FAILED':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-red-500/20 text-red-400 border border-red-500/30">REJECTED</span>;
      default:
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-slate-800 text-slate-300 border border-slate-700">{status}</span>;
    }
  };

  const filteredCandidates = candidates.filter((c) => {
    const matchesStatus = !statusFilter || c.application_status === statusFilter;
    const matchesSearch = !searchQuery || 
      c.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
      c.email.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Users className="w-7 h-7 text-blue-400" />
            HR Recruitment & Candidate Pipeline Dashboard
          </h1>
          <p className="text-sm text-slate-400 mt-1">Real-time status tracking across Gmail, n8n, Gemini AI, and Candidate Assessments.</p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleSyncGmail}
            disabled={syncingGmail}
            className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold flex items-center space-x-2 shadow-lg shadow-blue-500/20 transition-all disabled:opacity-50"
          >
            {syncingGmail ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Mail className="w-4 h-4" />
            )}
            <span>Sync Gmail Inbox</span>
          </button>

          <button
            onClick={() => setShowGmailModal(true)}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-all"
            title="Configure Gmail Credentials"
          >
            <Settings className="w-4 h-4" />
          </button>

          <button
            onClick={fetchDashboardData}
            className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold flex items-center space-x-2 border border-slate-700 transition-all"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Sync Notification Banner */}
      {syncMsg && (
        <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-300 text-xs flex items-center justify-between">
          <span>{syncMsg}</span>
          <button onClick={() => setSyncMsg(null)} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Metric Cards Grid */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
          <div className="glass-card p-4 rounded-2xl border border-slate-800 space-y-1">
            <div className="text-xs font-medium text-slate-400">Total Applications</div>
            <div className="text-2xl font-black text-white">{stats.total_applications}</div>
          </div>

          <div className="glass-card p-4 rounded-2xl border border-slate-800 space-y-1">
            <div className="text-xs font-medium text-blue-400">Shortlisted</div>
            <div className="text-2xl font-black text-blue-400">{stats.shortlisted}</div>
          </div>

          <div className="glass-card p-4 rounded-2xl border border-slate-800 space-y-1">
            <div className="text-xs font-medium text-red-400">Rejected</div>
            <div className="text-2xl font-black text-red-400">{stats.rejected}</div>
          </div>

          <div className="glass-card p-4 rounded-2xl border border-slate-800 space-y-1">
            <div className="text-xs font-medium text-purple-400">Tests Sent</div>
            <div className="text-2xl font-black text-purple-400">{stats.tests_sent}</div>
          </div>

          <div className="glass-card p-4 rounded-2xl border border-slate-800 space-y-1">
            <div className="text-xs font-medium text-cyan-400">Tests Completed</div>
            <div className="text-2xl font-black text-cyan-400">{stats.tests_completed}</div>
          </div>

          <div className="glass-card p-4 rounded-2xl border border-slate-800 space-y-1">
            <div className="text-xs font-medium text-emerald-400">Selected</div>
            <div className="text-2xl font-black text-emerald-400">{stats.selected}</div>
          </div>

          <div className="glass-card p-4 rounded-2xl border border-slate-800 space-y-1">
            <div className="text-xs font-medium text-indigo-400">Offers Sent</div>
            <div className="text-2xl font-black text-indigo-400">{stats.offers_sent}</div>
          </div>
        </div>
      )}

      {/* Candidate Filters & Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
        <div className="p-6 border-b border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-bold text-white">Candidates Overview</h2>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-400">
              {filteredCandidates.length} Candidates
            </span>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-3">
            {/* Search Input */}
            <div className="relative w-full sm:w-64">
              <Search className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
              <input
                type="text"
                placeholder="Search candidate name/email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-900/90 text-sm text-white pl-9 pr-4 py-2 rounded-xl border border-slate-700 focus:outline-none focus:border-blue-500"
              />
            </div>

            {/* Status Filter Dropdown */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full sm:w-auto bg-slate-900/90 text-sm text-slate-200 px-4 py-2 rounded-xl border border-slate-700 focus:outline-none focus:border-blue-500"
            >
              <option value="">All Statuses</option>
              <option value="RESUME_SHORTLISTED">Shortlisted</option>
              <option value="TEST_SENT">Test Sent</option>
              <option value="TEST_COMPLETED">Test Completed</option>
              <option value="SELECTED">Selected</option>
              <option value="OFFER_SENT">Offer Sent</option>
              <option value="RESUME_REJECTED">Resume Rejected</option>
              <option value="TEST_FAILED">Test Failed</option>
            </select>
          </div>
        </div>

        {/* Candidate Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-900/80 text-xs text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">Candidate</th>
                <th className="px-6 py-4">Job Position</th>
                <th className="px-6 py-4">Gemini Score</th>
                <th className="px-6 py-4">Test Score</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Test Link</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredCandidates.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center text-slate-500">
                    No candidate applications match your current filters.
                  </td>
                </tr>
              ) : (
                filteredCandidates.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-semibold text-white">{c.name}</div>
                      <div className="text-xs text-slate-400">{c.email}</div>
                    </td>

                    <td className="px-6 py-4 text-slate-300 font-medium">
                      {c.job_id}
                    </td>

                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <span className={`font-bold ${c.resume_score >= 70 ? 'text-emerald-400' : 'text-slate-400'}`}>
                          {c.resume_score}%
                        </span>
                        {c.resume_analysis && (
                          <button
                            onClick={() => setSelectedCandidate(c)}
                            className="p-1 rounded hover:bg-slate-700 text-slate-400 hover:text-white"
                            title="View AI Analysis Breakdown"
                          >
                            <Cpu className="w-4 h-4 text-purple-400" />
                          </button>
                        )}
                      </div>
                    </td>

                    <td className="px-6 py-4 font-bold text-white">
                      {c.test_score ? `${c.test_score}%` : '—'}
                    </td>

                    <td className="px-6 py-4">
                      {getStatusBadge(c.application_status)}
                    </td>

                    <td className="px-6 py-4">
                      {c.test_token ? (
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleCopyTestLink(c.test_token)}
                            className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs flex items-center space-x-1 border border-slate-700"
                            title="Copy unique test link"
                          >
                            {copiedToken === c.test_token ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                            <span>{copiedToken === c.test_token ? 'Copied!' : 'Copy Link'}</span>
                          </button>
                          <a
                            href={`/test/${c.test_token}`}
                            target="_blank"
                            rel="noreferrer"
                            className="p-1.5 rounded bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 text-xs border border-blue-500/30"
                            title="Open Test Page"
                          >
                            <ExternalLink className="w-3.5 h-3.5" />
                          </a>
                        </div>
                      ) : (
                        <span className="text-xs text-slate-500">None</span>
                      )}
                    </td>

                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => setSelectedCandidate(c)}
                        className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700"
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Gmail Config Modal */}
      {showGmailModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel max-w-md w-full rounded-2xl border border-slate-700 p-6 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Mail className="w-5 h-5 text-blue-400" />
                Configure Gmail Credentials
              </h3>
              <button onClick={() => setShowGmailModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <form onSubmit={handleSaveGmailConfig} className="space-y-4">
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-300">HR Gmail Address</label>
                <input
                  type="email"
                  required
                  placeholder="hr@company.com"
                  value={gmailUser}
                  onChange={(e) => setGmailUser(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-300">Gmail App Password (16 characters)</label>
                <input
                  type="password"
                  required
                  placeholder="xxxx xxxx xxxx xxxx"
                  value={gmailPassword}
                  onChange={(e) => setGmailPassword(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
                />
                <p className="text-[11px] text-slate-400 pt-1">
                  Generate an App Password from your Google Account: Security $\rightarrow$ 2-Step Verification $\rightarrow$ App Passwords.
                </p>
              </div>

              <div className="pt-2 flex items-center justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowGmailModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={syncingGmail}
                  className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-500/20"
                >
                  Save & Sync Inbox
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Candidate AI Details Modal */}
      {selectedCandidate && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="glass-panel max-w-xl w-full rounded-2xl border border-slate-700 p-6 space-y-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-xl font-bold text-white">{selectedCandidate.name}</h3>
                <p className="text-xs text-slate-400">{selectedCandidate.email} • Job: {selectedCandidate.job_id}</p>
              </div>
              <button
                onClick={() => setSelectedCandidate(null)}
                className="text-slate-400 hover:text-white p-1"
              >
                ✕
              </button>
            </div>

            {/* AI Breakdown */}
            {selectedCandidate.resume_analysis ? (
              <div className="space-y-4">
                <div className="flex items-center space-x-2 text-sm font-semibold text-purple-400">
                  <Cpu className="w-4 h-4" />
                  <span>Google Gemini AI Match Analysis</span>
                </div>

                <div className="grid grid-cols-2 gap-3 bg-slate-900/80 p-4 rounded-xl border border-slate-800 text-xs">
                  <div>
                    <span className="text-slate-400">Overall Score: </span>
                    <span className="font-bold text-white">{selectedCandidate.resume_analysis.match_score}%</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Skills Match: </span>
                    <span className="font-bold text-white">{selectedCandidate.resume_analysis.skills_match || selectedCandidate.resume_analysis.match_score}%</span>
                  </div>
                </div>

                {selectedCandidate.resume_analysis.matched_skills && (
                  <div className="space-y-1 text-xs">
                    <span className="text-slate-400 font-semibold">Matched Skills:</span>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {selectedCandidate.resume_analysis.matched_skills.map((s, idx) => (
                        <span key={idx} className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {selectedCandidate.resume_analysis.missing_skills && (
                  <div className="space-y-1 text-xs">
                    <span className="text-slate-400 font-semibold">Missing Skills:</span>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {selectedCandidate.resume_analysis.missing_skills.map((s, idx) => (
                        <span key={idx} className="px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/20">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {selectedCandidate.resume_analysis.reason && (
                  <div className="text-xs bg-slate-900/80 p-3 rounded-xl border border-slate-800 text-slate-300">
                    <span className="text-slate-400 font-semibold">AI Evaluation Summary: </span>
                    {selectedCandidate.resume_analysis.reason}
                  </div>
                )}
              </div>
            ) : (
              <div className="text-xs text-slate-400">No AI evaluation metadata available for this candidate.</div>
            )}

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedCandidate(null)}
                className="px-5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
