import React, { useState } from 'react';
import { Search, Download, Filter, FileSpreadsheet, FileCode, CheckCircle2 } from 'lucide-react';

export const SearchExportView: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const records = [
    { id: 1, khasra: '245/1', khata: '89', owner: 'Ramesh Kumar Sharma', village: 'Rampur', area: '4.25 Acres', status: 'Verified', confidence: 0.94, verifiedBy: 'Ananya Verma' },
    { id: 2, khasra: '245/1', khata: '89', owner: 'Suresh Kumar Verma', village: 'Rampur', area: '4.10 Acres', status: 'Flagged', confidence: 0.72, verifiedBy: 'AI Pipeline' },
    { id: 3, khasra: '118', khata: '42', owner: 'Priya Devi', village: 'Chandpur', area: '2.50 Hectares', status: 'Verified', confidence: 0.91, verifiedBy: 'Ananya Verma' },
    { id: 4, khasra: '312/B', khata: '104', owner: 'Ramesh K. Sharma', village: 'Rampur', area: '4.25 Acres', status: 'LowConfidence', confidence: 0.61, verifiedBy: 'AI Pipeline' },
  ];

  const filteredRecords = records.filter(r => {
    const matchesSearch = r.owner.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          r.khasra.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          r.village.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || r.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const exportData = (format: string) => {
    const jsonStr = JSON.stringify(filteredRecords, null, 2);
    const blob = new Blob([jsonStr], { type: format === 'json' ? 'application/json' : 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `land_records_export_${Date.now()}.${format}`;
    a.click();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center glass-panel p-6 rounded-2xl">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Search className="w-5 h-5 text-blue-400" />
            Land Record Search & Multi-Format Export
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Perform fuzzy & exact queries across Owner Names, Khasra Numbers, Villages, and Document IDs.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => exportData('csv')}
            className="bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 text-xs px-3.5 py-2 rounded-xl font-semibold flex items-center gap-1.5 transition-all"
          >
            <FileSpreadsheet className="w-4 h-4" /> Export CSV
          </button>
          <button
            onClick={() => exportData('json')}
            className="bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 text-xs px-3.5 py-2 rounded-xl font-semibold flex items-center gap-1.5 transition-all"
          >
            <FileCode className="w-4 h-4" /> Export JSON
          </button>
        </div>
      </div>

      {/* Query Bar */}
      <div className="glass-panel p-4 rounded-2xl flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            placeholder="Search by Owner Name (e.g. Ramesh K), Khasra No (245/1), or Village..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-xl px-4 py-2 focus:outline-none"
        >
          <option value="ALL">All Statuses</option>
          <option value="Verified">Verified Only</option>
          <option value="Flagged">Flagged Conflicts</option>
          <option value="LowConfidence">Low Confidence</option>
        </select>
      </div>

      {/* Table */}
      <div className="glass-panel rounded-2xl overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/80 text-slate-400 uppercase font-semibold text-[11px] border-b border-slate-800">
            <tr>
              <th className="p-4">Khasra Plot</th>
              <th className="p-4">Khata No</th>
              <th className="p-4">Owner Name</th>
              <th className="p-4">Village</th>
              <th className="p-4">Land Area</th>
              <th className="p-4">Verification Status</th>
              <th className="p-4">Verified By</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {filteredRecords.map((r) => (
              <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="p-4 font-mono font-semibold text-blue-300">{r.khasra}</td>
                <td className="p-4 text-slate-300">{r.khata}</td>
                <td className="p-4 font-medium text-slate-200">{r.owner}</td>
                <td className="p-4 text-slate-300">{r.village}</td>
                <td className="p-4 text-slate-300">{r.area}</td>
                <td className="p-4">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
                    r.status === 'Verified' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-red-500/10 text-red-400 border-red-500/30'
                  }`}>
                    {r.status}
                  </span>
                </td>
                <td className="p-4 text-slate-400">{r.verifiedBy}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
