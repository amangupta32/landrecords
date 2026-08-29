import React from 'react';
import { ShieldCheck, UserCheck, Bell, Sparkles, AlertTriangle } from 'lucide-react';

interface NavbarProps {
  currentRole: string;
  onRoleChange: (role: string) => void;
  activeView: string;
}

export const Navbar: React.FC<NavbarProps> = ({ currentRole, onRoleChange, activeView }) => {
  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800 px-6 py-3">
      {/* Top Demo Data Disclaimer Bar */}
      <div className="bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs px-4 py-1 rounded-md mb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          <span className="font-semibold tracking-wide">DEMO DATA — NOT AN OFFICIAL LAND RECORD</span>
        </div>
        <span className="text-[11px] text-amber-400/80">LRMS / DILRMP Integration Adapter Active</span>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600/20 p-2 rounded-xl border border-blue-500/30 text-blue-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-lg font-bold bg-gradient-to-r from-blue-400 via-indigo-200 to-white bg-clip-text text-transparent">
              AI Intelligent Land Record Digitization
            </h1>
            <p className="text-xs text-slate-400">Government Record Validation & Cadastral Mapping System</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* AI Engine Status Indicator */}
          <div className="hidden md:flex items-center gap-2 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700 text-xs text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            <span>AI Neural OCR & Conflict Engine Online</span>
          </div>

          {/* Role Switcher */}
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-700/80 rounded-lg p-1 text-xs">
            <UserCheck className="w-4 h-4 text-slate-400 ml-1" />
            <select
              value={currentRole}
              onChange={(e) => onRoleChange(e.target.value)}
              className="bg-transparent text-slate-200 focus:outline-none font-medium pr-2 cursor-pointer"
            >
              <option value="Verifier" className="bg-slate-900 text-slate-200">Senior Verifier</option>
              <option value="Admin" className="bg-slate-900 text-slate-200">System Admin</option>
              <option value="Operator" className="bg-slate-900 text-slate-200">Data Entry Operator</option>
              <option value="Supervisor" className="bg-slate-900 text-slate-200">Tehsildar Supervisor</option>
              <option value="Viewer" className="bg-slate-900 text-slate-200">Public Viewer</option>
            </select>
          </div>

          <button className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors relative">
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-blue-500 rounded-full"></span>
          </button>
        </div>
      </div>
    </header>
  );
};
