import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { testService } from '../services/api';
import { Clock, ShieldCheck, CheckCircle2, AlertCircle, Loader2, Send } from 'lucide-react';

export default function CandidateTestPage() {
  const { token } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [testData, setTestData] = useState(null);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [timeLeft, setTimeLeft] = useState(1800); // 30 minutes in seconds

  useEffect(() => {
    async function loadTest() {
      try {
        setLoading(true);
        const data = await testService.verifyToken(token);
        setTestData(data);
        setTimeLeft(data.time_limit_minutes * 60);
      } catch (err) {
        setError(err.response?.data?.detail || 'Test link is invalid, expired, or already used.');
      } finally {
        setLoading(false);
      }
    }
    if (token) {
      loadTest();
    }
  }, [token]);

  // Timer Countdown Effect
  useEffect(() => {
    if (!testData || submitting) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          handleAutoSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [testData, submitting]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSelectOption = (questionId, optionText) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: optionText,
    }));
  };

  const handleAutoSubmit = () => {
    handleSubmitTest();
  };

  const handleSubmitTest = async (e) => {
    if (e) e.preventDefault();
    if (submitting) return;

    try {
      setSubmitting(true);
      const formattedAnswers = Object.entries(answers).map(([qId, opt]) => ({
        question_id: parseInt(qId),
        selected_option: opt,
      }));

      const response = await testService.submitTest(token, formattedAnswers);
      navigate('/result', { state: { result: response } });
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to submit test. Please try again.');
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center space-y-4">
        <Loader2 className="w-10 h-10 text-blue-500 animate-spin" />
        <p className="text-slate-400 font-medium">Validating your secure assessment link...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-md mx-auto my-16 p-8 glass-panel rounded-2xl border border-red-500/30 text-center space-y-4">
        <div className="w-14 h-14 bg-red-500/20 text-red-400 rounded-full flex items-center justify-center mx-auto">
          <AlertCircle className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-white">Assessment Link Unavailable</h2>
        <p className="text-slate-400 text-sm">{error}</p>
        <div className="pt-2">
          <button
            onClick={() => navigate('/')}
            className="px-6 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold transition-all"
          >
            Return to Home
          </button>
        </div>
      </div>
    );
  }

  const answeredCount = Object.keys(answers).length;
  const totalQuestions = testData.questions.length;
  const progressPercent = Math.round((answeredCount / totalQuestions) * 100);

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      {/* Sticky Assessment Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 sticky top-20 z-40 shadow-xl flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-semibold uppercase text-blue-400 tracking-wider">
            <ShieldCheck className="w-4 h-4" />
            <span>TechCorp Solutions • Official Candidate Evaluation</span>
          </div>
          <h1 className="text-xl font-bold text-white mt-1">{testData.job_title}</h1>
          <p className="text-xs text-slate-400">Candidate: <span className="text-slate-200 font-medium">{testData.candidate_name}</span> ({testData.candidate_email})</p>
        </div>

        <div className="flex items-center space-x-6">
          <div className="text-right">
            <div className="text-xs text-slate-400 font-medium">Questions Answered</div>
            <div className="text-lg font-bold text-white">{answeredCount} / {totalQuestions}</div>
          </div>

          <div className="flex items-center space-x-2 bg-slate-900/90 px-4 py-2.5 rounded-xl border border-slate-700/80">
            <Clock className={`w-5 h-5 ${timeLeft < 300 ? 'text-red-400 animate-pulse' : 'text-blue-400'}`} />
            <div className="font-mono text-xl font-bold text-white">
              {formatTime(timeLeft)}
            </div>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-800/80 h-2 rounded-full overflow-hidden">
        <div 
          className="bg-gradient-to-r from-blue-500 to-indigo-500 h-full transition-all duration-300"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Questions List */}
      <form onSubmit={handleSubmitTest} className="space-y-6">
        {testData.questions.map((q, index) => (
          <div key={q.id} className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4 hover:border-slate-700 transition-all">
            <div className="flex items-start justify-between">
              <span className="text-xs font-semibold px-3 py-1 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20">
                Question {index + 1} of {totalQuestions} • {q.category}
              </span>
              {answers[q.id] && (
                <span className="flex items-center space-x-1 text-xs text-emerald-400 font-medium">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Answered</span>
                </span>
              )}
            </div>

            <h3 className="text-base font-semibold text-white leading-relaxed">{q.question}</h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
              {q.options.map((opt, optIdx) => {
                const isSelected = answers[q.id] === opt;
                return (
                  <button
                    key={optIdx}
                    type="button"
                    onClick={() => handleSelectOption(q.id, opt)}
                    className={`p-4 rounded-xl text-left font-medium text-sm transition-all border flex items-center justify-between ${
                      isSelected
                        ? 'bg-blue-600/20 border-blue-500 text-white shadow-md shadow-blue-500/10'
                        : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:bg-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <span>{opt}</span>
                    <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${
                      isSelected ? 'border-blue-400 bg-blue-500' : 'border-slate-600'
                    }`}>
                      {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        ))}

        {/* Submit Button */}
        <div className="pt-4 flex justify-end">
          <button
            type="submit"
            disabled={submitting}
            className="px-8 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold flex items-center space-x-2 shadow-lg shadow-blue-500/30 transition-all disabled:opacity-50"
          >
            {submitting ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Submitting Test...</span>
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                <span>Submit Assessment</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
