import React from 'react';
import { CheckSquare, ArrowUpRight, ShieldAlert, Award, FileText } from 'lucide-react';

interface VerificationQueueViewProps {
  onSelectRecord: (recordId: number) => void;
}

export const VerificationQueueView: React.FC<VerificationQueueViewProps> = ({ onSelectRecord }) => {
  const queueItems = [
    {
      id: 2,
      docId: 2,
      docTitle: 'SaleDeed_Khasra_245_Deed.png',
      type: 'Sale Deed',
      khasra: '245/1',
      owner: 'Suresh Kumar Verma',
      village: 'Rampur',
      confidence: 0.72,
      status: 'Flagged',
      priority: 'High',
      reason: 'Ownership Conflict with Jamabandi ROR Master Record'
    },
    {
      id: 4,
      docId: 4,
      docTitle: 'Legacy_Handwritten_Girdawari_1998.png',
      type: 'Khasra Girdawari (Legacy)',
      khasra: '312/B',
      owner: 'Ramesh K. Sharma',
      village: 'Rampur',
      confidence: 0.61,
      status: 'LowConfidence',
      priority: 'High',
      reason: 'OCR score 52% due to character fading in 1998 document'
    },
    {
      id: 1,
      docId: 1,
      docTitle: 'Jamabandi_2024_Khasra_245.pdf',
      type: 'Jamabandi / ROR',
      khasra: '245/1',
      owner: 'Ramesh Kumar Sharma',
      village: 'Rampur',
      confidence: 0.94,
      status: 'Verified',
      priority: 'Normal',
      reason: 'High confidence match across mandatory fields'
    },
    {
      id: 3,
      docId: 3,
      docTitle: 'Mutation_Record_Khasra_118.pdf',
      type: 'Mutation Record',
      khasra: '118',
      owner: 'Priya Devi',
      village: 'Chandpur',
      confidence: 0.91,
      status: 'Verified',
      priority: 'Normal',
      reason: 'Location hierarchy and area non-zero validated'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center glass-panel p-6 rounded-2xl">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-blue-400" />
            Human-in-the-Loop Verification Queue
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Task queue prioritized by AI confidence scores. Low confidence and cross-document conflict items require Senior Verifier review.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-medium">Filter Priority:</span>
          <select className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-3 py-1.5 focus:outline-none">
            <option>All Tasks (4)</option>
            <option>High Priority (2)</option>
            <option>Low Confidence (1)</option>
            <option>Conflicts Flagged (1)</option>
          </select>
        </div>
      </div>

      <div className="glass-panel rounded-2xl overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/80 text-slate-400 uppercase font-semibold text-[11px] tracking-wider border-b border-slate-800">
            <tr>
              <th className="p-4">Document Title</th>
              <th className="p-4">Khasra Plot</th>
              <th className="p-4">Extracted Owner</th>
              <th className="p-4">Village</th>
              <th className="p-4">AI Confidence</th>
              <th className="p-4">Status</th>
              <th className="p-4 text-right">Workstation Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {queueItems.map((item) => (
              <tr key={item.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="p-4">
                  <div className="flex items-center gap-3">
                    <FileText className="w-4 h-4 text-blue-400" />
                    <div>
                      <div className="font-semibold text-slate-200">{item.docTitle}</div>
                      <div className="text-[11px] text-slate-400">{item.type}</div>
                    </div>
                  </div>
                </td>
                <td className="p-4 font-mono font-semibold text-blue-300">{item.khasra}</td>
                <td className="p-4 font-medium text-slate-200">{item.owner}</td>
                <td className="p-4 text-slate-300">{item.village}</td>
                <td className="p-4">
                  <div className="flex items-center gap-2">
                    <span className={`font-bold ${item.confidence < 0.7 ? 'text-red-400' : (item.confidence < 0.85 ? 'text-amber-400' : 'text-emerald-400')}`}>
                      {(item.confidence * 100).toFixed(0)}%
                    </span>
                    <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${item.confidence < 0.7 ? 'bg-red-500' : (item.confidence < 0.85 ? 'bg-amber-500' : 'bg-emerald-500')}`}
                        style={{ width: `${item.confidence * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </td>
                <td className="p-4">
                  <span className={`px-2.5 py-1 rounded-md text-[11px] font-semibold border ${
                    item.status === 'Verified'
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      : (item.status === 'Flagged'
                        ? 'bg-red-500/10 text-red-400 border-red-500/30'
                        : 'bg-amber-500/10 text-amber-400 border-amber-500/30')
                  }`}>
                    {item.status}
                  </span>
                </td>
                <td className="p-4 text-right">
                  <button
                    onClick={() => onSelectRecord(item.id)}
                    className="bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 border border-blue-500/30 px-3 py-1.5 rounded-lg font-medium inline-flex items-center gap-1 transition-all"
                  >
                    Open Workstation <ArrowUpRight className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
