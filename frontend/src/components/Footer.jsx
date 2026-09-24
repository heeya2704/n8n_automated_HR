import React from 'react';

export default function Footer() {
  return (
    <footer className="border-t border-slate-800/80 bg-slate-950 py-6 mt-auto">
      <div className="max-w-7xl mx-auto px-4 text-center text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div>
          © {new Date().getFullYear()} TechCorp Recruitment Automation • Powered by n8n, FastAPI & Google Gemini AI
        </div>
        <div className="flex space-x-4">
          <span className="hover:text-slate-400 cursor-pointer">Privacy Policy</span>
          <span>•</span>
          <span className="hover:text-slate-400 cursor-pointer">Terms of Assessment</span>
        </div>
      </div>
    </footer>
  );
}
