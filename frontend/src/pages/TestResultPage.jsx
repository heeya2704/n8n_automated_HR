import React from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { CheckCircle2, XCircle, Award, ArrowLeft, Mail, FileCheck } from 'lucide-react';

export default function TestResultPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const result = location.state?.result;

  if (!result) {
    return (
      <div className="max-w-md mx-auto my-16 p-8 glass-panel rounded-2xl text-center space-y-4">
        <h2 className="text-2xl font-bold text-white">No Submission Found</h2>
        <p className="text-slate-400 text-sm">You have not completed an active assessment session.</p>
        <Link to="/" className="inline-block px-6 py-2.5 rounded-xl bg-blue-600 text-white font-semibold text-sm">
          Return to Home
        </Link>
      </div>
    );
  }

  const isPassed = result.eligible_for_offer;

  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <div className="glass-panel p-8 rounded-3xl border border-slate-800 shadow-2xl space-y-8 text-center">
        {isPassed ? (
          <div className="w-20 h-20 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center mx-auto ring-8 ring-emerald-500/10 animate-bounce">
            <Award className="w-10 h-10" />
          </div>
        ) : (
          <div className="w-20 h-20 bg-slate-800 text-slate-400 rounded-full flex items-center justify-center mx-auto">
            <FileCheck className="w-10 h-10" />
          </div>
        )}

        <div className="space-y-2">
          <h1 className="text-3xl font-extrabold text-white">
            {isPassed ? "Congratulations! Assessment Passed" : "Assessment Submitted Successfully"}
          </h1>
          <p className="text-slate-400 text-sm max-w-md mx-auto">
            {isPassed 
              ? "You have successfully met our technical requirements. Your offer letter has been generated and sent to your email."
              : "Thank you for completing the technical assessment. Your response has been recorded."
            }
          </p>
        </div>

        {/* Score Details Box */}
        <div className="grid grid-cols-3 gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800">
          <div className="space-y-1">
            <div className="text-xs font-medium text-slate-400">Score</div>
            <div className={`text-2xl font-black ${isPassed ? 'text-emerald-400' : 'text-blue-400'}`}>
              {result.score}%
            </div>
          </div>

          <div className="space-y-1 border-x border-slate-800">
            <div className="text-xs font-medium text-slate-400">Correct</div>
            <div className="text-2xl font-bold text-white">
              {result.correct_answers} / {result.total_questions}
            </div>
          </div>

          <div className="space-y-1">
            <div className="text-xs font-medium text-slate-400">Status</div>
            <div className="text-xs font-bold uppercase tracking-wider mt-2">
              <span className={`px-2.5 py-1 rounded-full ${
                isPassed ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-slate-800 text-slate-300'
              }`}>
                {result.status}
              </span>
            </div>
          </div>
        </div>

        <div className="p-4 bg-blue-500/10 rounded-xl border border-blue-500/20 text-blue-300 text-xs text-left flex items-start space-x-3">
          <Mail className="w-5 h-5 flex-shrink-0 text-blue-400 mt-0.5" />
          <div>
            <span className="font-semibold text-white">Email Notification Triggered: </span>
            A notification with your detailed assessment outcome has been dispatched to <b>{result.candidate_email}</b> via n8n automation.
          </div>
        </div>

        <div>
          <button
            onClick={() => navigate('/')}
            className="px-8 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold transition-all inline-flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Return to Main Portal</span>
          </button>
        </div>
      </div>
    </div>
  );
}
