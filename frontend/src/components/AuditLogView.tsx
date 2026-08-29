import React from 'react';
import { History, ShieldCheck, UserCheck, FileText, Lock } from 'lucide-react';

export const AuditLogView: React.FC = () => {
  const auditLogs = [
    { id: 4, user: 'Ananya Verma', role: 'Verifier', action: 'VERIFY_APPROVE', target: 'RECORD #1 (Jamabandi)', details: 'Approved all fields against registry master.', time: '10 mins ago' },
    { id: 3, user: 'System AI Pipeline', role: 'AI Core', action: 'CONFLICT_DETECTED', target: 'CONFLICT #245/1', details: 'Ownership mismatch flagged between Jamabandi & Deed.', time: '25 mins ago' },
    { id: 2, user: 'System AI Pipeline', role: 'AI Core', action: 'OCR_EXTRACT', target: 'DOCUMENT #1', details: 'Extracted 8 fields with 94% average confidence.', time: '30 mins ago' },
    { id: 1, user: 'Sanjay Patel', role: 'Data Entry Operator', action: 'UPLOAD', target: 'DOCUMENT #1', details: 'Uploaded jamabandi_rampur_2024.pdf (2.4 MB).', time: '35 mins ago' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center glass-panel p-6 rounded-2xl">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <History className="w-5 h-5 text-blue-400" />
            Immutable Audit Trail Logs
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Complete cryptographic audit trail recording document ingestion, AI extraction, verifier overrides, and approvals.
          </p>
        </div>
        <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 text-xs px-3 py-1.5 rounded-lg text-emerald-400">
          <Lock className="w-3.5 h-3.5" /> Immutable Log Chain Active
        </div>
      </div>

      <div className="glass-panel rounded-2xl overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/80 text-slate-400 uppercase font-semibold text-[11px] border-b border-slate-800">
            <tr>
              <th className="p-4">Timestamp</th>
              <th className="p-4">User</th>
              <th className="p-4">Role</th>
              <th className="p-4">Action</th>
              <th className="p-4">Target Entity</th>
              <th className="p-4">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {auditLogs.map((log) => (
              <tr key={log.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="p-4 font-mono text-slate-400">{log.time}</td>
                <td className="p-4 font-semibold text-slate-200">{log.user}</td>
                <td className="p-4">
                  <span className="bg-blue-500/10 text-blue-300 border border-blue-500/30 text-[10px] px-2 py-0.5 rounded font-medium">
                    {log.role}
                  </span>
                </td>
                <td className="p-4 font-mono font-semibold text-emerald-400">{log.action}</td>
                <td className="p-4 font-mono text-blue-300">{log.target}</td>
                <td className="p-4 text-slate-300">{log.details}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
