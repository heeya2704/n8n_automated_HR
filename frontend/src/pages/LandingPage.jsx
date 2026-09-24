import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Mail, Cpu, CheckCircle2, ArrowRight, ShieldCheck, FileCheck2, Award } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-16">
      {/* Hero Section */}
      <div className="text-center space-y-6 max-w-4xl mx-auto pt-6">
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider">
          <Sparkles className="w-4 h-4" />
          <span>n8n + Gemini AI Recruitment Automation</span>
        </div>
        
        <h1 className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight leading-tight">
          Next-Gen AI Hiring & <br />
          <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-cyan-300 bg-clip-text text-transparent">
            Automated Candidate Assessment
          </span>
        </h1>

        <p className="text-lg text-slate-400 max-w-2xl mx-auto">
          Streamline your hiring process end-to-end. Receive resumes via Gmail, screen candidates with Google Gemini AI, conduct secure online technical assessments, and automatically send offer letters.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Link
            to="/admin"
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold flex items-center justify-center space-x-2 shadow-lg shadow-blue-500/25 transition-all transform hover:-translate-y-0.5"
          >
            <span>Open HR Dashboard</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
          
          <a
            href="#workflow"
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold text-center transition-all"
          >
            Explore Workflow
          </a>
        </div>
      </div>

      {/* Workflow Visualization */}
      <div id="workflow" className="glass-panel rounded-2xl p-8 border border-slate-800 shadow-2xl">
        <h2 className="text-2xl font-bold text-white text-center mb-8">System Architecture & Workflow</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-slate-900/60 p-6 rounded-xl border border-slate-800/80 hover:border-blue-500/40 transition-all space-y-3">
            <div className="w-10 h-10 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold">1</div>
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Mail className="w-5 h-5 text-blue-400" />
              Resume Ingestion
            </h3>
            <p className="text-sm text-slate-400">Candidate sends email with resume attachment. n8n Gmail trigger automatically downloads and extracts resume text.</p>
          </div>

          <div className="bg-slate-900/60 p-6 rounded-xl border border-slate-800/80 hover:border-purple-500/40 transition-all space-y-3">
            <div className="w-10 h-10 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center font-bold">2</div>
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Cpu className="w-5 h-5 text-purple-400" />
              Gemini AI Screening
            </h3>
            <p className="text-sm text-slate-400">Google Gemini AI matches resume skills against the Job Description, returning a structured JSON score ($\ge 70\%$ threshold).</p>
          </div>

          <div className="bg-slate-900/60 p-6 rounded-xl border border-slate-800/80 hover:border-cyan-500/40 transition-all space-y-3">
            <div className="w-10 h-10 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold">3</div>
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-cyan-400" />
              Online Assessment
            </h3>
            <p className="text-sm text-slate-400">Eligible candidates receive a unique token test link (`/test/:token`). Candidate completes timed MCQ test.</p>
          </div>

          <div className="bg-slate-900/60 p-6 rounded-xl border border-slate-800/80 hover:border-emerald-500/40 transition-all space-y-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">4</div>
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Award className="w-5 h-5 text-emerald-400" />
              Offer Generation
            </h3>
            <p className="text-sm text-slate-400">Scoring $\ge 80\%$ triggers offer letter PDF creation & automated offer email via n8n webhook workflow.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
