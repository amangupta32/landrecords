import React, { useState } from 'react';
import { Copy, ArrowRight, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';

export const DuplicatesView: React.FC = () => {
  const [duplicateList, setDuplicateList] = useState([
    {
      id: 1,
      record1: { id: 1, owner: 'Ramesh Kumar Sharma', khasra: '245/1', area: '4.25 Acres', doc: 'Jamabandi_2024.pdf' },
      record2: { id: 4, owner: 'Ramesh K. Sharma', khasra: '245/1', area: '4.25 Acres', doc: 'Legacy_Girdawari_1998.png' },
      village: 'Rampur',
      similarity: 0.91,
      reason: '91% fuzzy Levenshtein match for owner name & identical Khasra plot in Village Rampur.',
      status: 'Pending'
    }
  ]);

  const [message, setMessage] = useState<string>('');

  const resolveDuplicate = (dupId: number, action: 'MERGE' | 'DISMISS') => {
    setDuplicateList(prev => prev.map(d => d.id === dupId ? { ...d, status: action === 'MERGE' ? 'Merged' : 'Dismissed' } : d));
    setMessage(`Duplicate pair successfully ${action === 'MERGE' ? 'merged into Master ROR' : 'marked as distinct records'}.`);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center glass-panel p-6 rounded-2xl">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Copy className="w-5 h-5 text-purple-400" />
            Duplicate Candidate Detection & Resolution
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Fuzzy text similarity & token overlap engine identifies duplicate land ownership entries across legacy digitized registers.
          </p>
        </div>
      </div>

      {message && (
        <div className="bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 p-3 rounded-xl text-xs font-semibold">
          {message}
        </div>
      )}

      <div className="space-y-4">
        {duplicateList.map((dup) => (
          <div key={dup.id} className="glass-panel p-6 rounded-2xl space-y-4 border-l-4 border-l-purple-500">
            <div className="flex justify-between items-center pb-3 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <span className="bg-purple-500/20 text-purple-300 border border-purple-500/30 text-xs px-3 py-1 rounded-full font-bold">
                  {(dup.similarity * 100).toFixed(0)}% Similarity Match
                </span>
                <span className="text-xs text-slate-400">Village: {dup.village} • Khasra: {dup.record1.khasra}</span>
              </div>
              <span className={`text-xs font-semibold px-2.5 py-1 rounded ${
                dup.status === 'Merged' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'
              }`}>
                {dup.status}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Record 1 */}
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-2 text-xs">
                <div className="text-slate-400 font-semibold text-[11px] uppercase">Primary Record (#1)</div>
                <div className="text-sm font-bold text-white">{dup.record1.owner}</div>
                <div>Khasra: <span className="font-mono text-blue-300">{dup.record1.khasra}</span></div>
                <div>Land Area: <span className="text-slate-300">{dup.record1.area}</span></div>
                <div className="text-slate-500 text-[11px]">Source: {dup.record1.doc}</div>
              </div>

              {/* Record 2 */}
              <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-2 text-xs">
                <div className="text-slate-400 font-semibold text-[11px] uppercase">Duplicate Candidate (#2)</div>
                <div className="text-sm font-bold text-purple-300">{dup.record2.owner}</div>
                <div>Khasra: <span className="font-mono text-blue-300">{dup.record2.khasra}</span></div>
                <div>Land Area: <span className="text-slate-300">{dup.record2.area}</span></div>
                <div className="text-slate-500 text-[11px]">Source: {dup.record2.doc}</div>
              </div>
            </div>

            <div className="bg-slate-950 p-3 rounded-xl text-xs text-slate-300 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-purple-400 shrink-0" />
              <span>{dup.reason}</span>
            </div>

            {dup.status === 'Pending' && (
              <div className="flex justify-end gap-3 pt-2">
                <button
                  onClick={() => resolveDuplicate(dup.id, 'DISMISS')}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition-colors"
                >
                  Keep Separate
                </button>
                <button
                  onClick={() => resolveDuplicate(dup.id, 'MERGE')}
                  className="px-5 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-purple-500/20 transition-all"
                >
                  Merge into Master Record
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
