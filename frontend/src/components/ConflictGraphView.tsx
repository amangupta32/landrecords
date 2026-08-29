import React from 'react';
import { Network, AlertOctagon, FileText, ArrowRight, ShieldAlert, CheckCircle } from 'lucide-react';

export const ConflictGraphView: React.FC = () => {
  const conflictNodes = [
    { id: 'plot_245', label: 'Plot Khasra 245/1', type: 'plot', color: 'border-red-500 bg-red-500/20 text-red-300', x: '50%', y: '25%' },
    { id: 'doc_1', label: 'Jamabandi_2024.pdf (ROR)', type: 'document', color: 'border-blue-500 bg-blue-500/20 text-blue-300', x: '25%', y: '65%' },
    { id: 'doc_2', label: 'SaleDeed_2023.png (Deed)', type: 'document', color: 'border-blue-500 bg-blue-500/20 text-blue-300', x: '75%', y: '65%' },
    { id: 'owner_1', label: 'Ramesh Kumar Sharma (Master Owner)', type: 'owner', color: 'border-emerald-500 bg-emerald-500/20 text-emerald-300', x: '25%', y: '90%' },
    { id: 'owner_2', label: 'Suresh Kumar Verma (Purchaser)', type: 'owner', color: 'border-amber-500 bg-amber-500/20 text-amber-300', x: '75%', y: '90%' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center glass-panel p-6 rounded-2xl">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Network className="w-5 h-5 text-red-400" />
            Cross-Document Conflict Graph Engine
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Cross-references Jamabandi ROR master records against recent Sale Deeds and Mutation applications to catch illegal transfers and land area discrepancies.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="bg-red-500/20 text-red-400 border border-red-500/30 text-xs px-3 py-1 rounded-full font-semibold">
            2 Active Conflicts Detected
          </span>
        </div>
      </div>

      {/* Visual Relationship Graph */}
      <div className="glass-panel rounded-2xl p-6 h-80 relative overflow-hidden flex flex-col justify-between">
        <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Interactive Node Relationship Map — Plot Khasra 245/1 (Rampur)
        </div>

        {/* Visual Node Representation */}
        <div className="relative w-full h-full my-4 border border-slate-800/60 rounded-xl bg-slate-950/60 p-4">
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            {/* SVG Connecting Lines */}
            <svg className="w-full h-full">
              <line x1="50%" y1="25%" x2="25%" y2="65%" stroke="#3b82f6" strokeWidth="2" strokeDasharray="4 4" />
              <line x1="50%" y1="25%" x2="75%" y2="65%" stroke="#ef4444" strokeWidth="2" />
              <line x1="25%" y1="65%" x2="25%" y2="90%" stroke="#10b981" strokeWidth="2" />
              <line x1="75%" y1="65%" x2="75%" y2="90%" stroke="#f59e0b" strokeWidth="2" />
              <line x1="25%" y1="90%" x2="75%" y2="90%" stroke="#ef4444" strokeWidth="2" strokeDasharray="6 6" />
            </svg>
          </div>

          {conflictNodes.map((n) => (
            <div
              key={n.id}
              className={`absolute -translate-x-1/2 -translate-y-1/2 px-4 py-2 rounded-xl border text-xs font-semibold shadow-lg backdrop-blur-md transition-all hover:scale-105 ${n.color}`}
              style={{ left: n.x, top: n.y }}
            >
              {n.label}
            </div>
          ))}
        </div>

        <div className="flex justify-between items-center text-xs text-slate-400">
          <span>Solid Red Line: Active Ownership Conflict</span>
          <span>Dashed Blue: Verified Master ROR Link</span>
        </div>
      </div>

      {/* Side-by-Side Discrepancy Table */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <AlertOctagon className="w-4 h-4 text-red-400" />
          Side-by-Side Field Discrepancy Breakdown
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Document A */}
          <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl space-y-3">
            <div className="flex justify-between items-center border-b border-slate-800 pb-2">
              <span className="text-xs font-bold text-blue-400">Document A: Master Jamabandi 2024</span>
              <span className="bg-emerald-500/20 text-emerald-400 text-[10px] px-2 py-0.5 rounded font-mono">Master ROR</span>
            </div>
            <div className="text-xs space-y-2">
              <div className="flex justify-between"><span className="text-slate-400">Owner Name:</span><span className="font-semibold text-emerald-400">Ramesh Kumar Sharma</span></div>
              <div className="flex justify-between"><span className="text-slate-400">Land Area:</span><span className="font-semibold text-white">4.25 Acres (17,199 sq.m)</span></div>
              <div className="flex justify-between"><span className="text-slate-400">Registration Ref:</span><span className="font-mono text-slate-300">REG-UP-9921</span></div>
              <div className="flex justify-between"><span className="text-slate-400">Record Date:</span><span className="text-slate-300">15/01/2024</span></div>
            </div>
          </div>

          {/* Document B */}
          <div className="bg-slate-900/80 border border-red-500/30 p-4 rounded-xl space-y-3">
            <div className="flex justify-between items-center border-b border-slate-800 pb-2">
              <span className="text-xs font-bold text-red-400">Document B: Recent Sale Deed 2023</span>
              <span className="bg-red-500/20 text-red-400 text-[10px] px-2 py-0.5 rounded font-mono">Conflicting Deed</span>
            </div>
            <div className="text-xs space-y-2">
              <div className="flex justify-between"><span className="text-slate-400">Purchaser Name:</span><span className="font-semibold text-red-400">Suresh Kumar Verma</span></div>
              <div className="flex justify-between"><span className="text-slate-400">Land Area:</span><span className="font-semibold text-amber-400">4.10 Acres (16,592 sq.m)</span></div>
              <div className="flex justify-between"><span className="text-slate-400">Mutation Status:</span><span className="font-mono text-red-400">MUT-PENDING (Unverified)</span></div>
              <div className="flex justify-between"><span className="text-slate-400">Deed Date:</span><span className="text-slate-300">20/11/2023</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
