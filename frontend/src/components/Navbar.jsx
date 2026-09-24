import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Cpu, LayoutDashboard, FileText, CheckCircle2 } from 'lucide-react';

export default function Navbar() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-600 rounded-xl text-white shadow-lg shadow-blue-500/30">
              <Cpu className="w-6 h-6" />
            </div>
            <Link to="/" className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-300 bg-clip-text text-transparent">
              RecruitAI Platform
            </Link>
          </div>

          <div className="flex items-center space-x-4">
            <Link
              to="/"
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive('/') ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30' : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              Overview
            </Link>
            <Link
              to="/admin"
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all shadow-md ${
                isActive('/admin') 
                  ? 'bg-blue-600 text-white shadow-blue-500/25' 
                  : 'bg-slate-800 text-slate-200 border border-slate-700 hover:bg-slate-700 hover:border-slate-600'
              }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              <span>HR Admin Dashboard</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
