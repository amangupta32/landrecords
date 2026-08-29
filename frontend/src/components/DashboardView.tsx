import React from 'react';
import {
  FileText, CheckCircle, Clock, AlertOctagon, Copy, Network,
  TrendingUp, Award, ArrowUpRight
} from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';

interface DashboardViewProps {
  onNavigate: (view: string) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ onNavigate }) => {
  // Demo analytics data matching backend API schemas
  const metrics = [
    { title: 'Total Uploaded', value: '4 Documents', sub: 'PDF / Image Ingested', icon: FileText, color: 'from-blue-500/20 to-indigo-500/10 border-blue-500/30 text-blue-400' },
    { title: 'Verified Records', value: '2 Records', sub: 'Human + AI Approved', icon: CheckCircle, color: 'from-emerald-500/20 to-teal-500/10 border-emerald-500/30 text-emerald-400' },
    { title: 'Pending Queue', value: '2 Records', sub: 'Low Confidence / Flagged', icon: Clock, color: 'from-amber-500/20 to-yellow-500/10 border-amber-500/30 text-amber-400' },
    { title: 'Active Conflicts', value: '2 Conflicts', sub: 'Cross-Doc Discrepancies', icon: AlertOctagon, color: 'from-red-500/20 to-rose-500/10 border-red-500/30 text-red-400' },
    { title: 'Duplicate Pairs', value: '1 Candidate', sub: 'Fuzzy Match (91%)', icon: Copy, color: 'from-purple-500/20 to-pink-500/10 border-purple-500/30 text-purple-400' },
    { title: 'Avg Confidence', value: '88.5%', sub: '4-Tier Weighted Score', icon: Award, color: 'from-cyan-500/20 to-blue-500/10 border-cyan-500/30 text-cyan-400' },
  ];

  const confidenceDist = [
    { range: '< 60%', count: 1, fill: '#ef4444' },
    { range: '60% - 75%', count: 1, fill: '#f59e0b' },
    { range: '75% - 90%', count: 1, fill: '#3b82f6' },
    { range: '> 90%', count: 2, fill: '#10b981' },
  ];

  const statusPie = [
    { name: 'Verified', value: 2, color: '#10b981' },
    { name: 'Pending Verification', value: 1, color: '#f59e0b' },
    { name: 'Flagged (Conflict)', value: 1, color: '#ef4444' },
  ];

  const districtProgress = [
    { district: 'Rampur District', digitized: 1420, pending: 180 },
    { district: 'Lucknow District', digitized: 3100, pending: 240 },
    { district: 'Indore District', digitized: 2250, pending: 310 },
    { district: 'Nagpur District', digitized: 1890, pending: 420 },
  ];

  const processingVelocity = [
    { time: '09:00', processed: 12 },
    { time: '11:00', processed: 28 },
    { time: '13:00', processed: 45 },
    { time: '15:00', processed: 62 },
    { time: '17:00', processed: 88 },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex justify-between items-center bg-gradient-to-r from-slate-900 via-blue-950/40 to-slate-900 p-6 rounded-2xl border border-blue-500/20">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-3">
            Digitization Analytics & Verification Hub
            <span className="text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-full font-medium">
              Live Monitoring
            </span>
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Real-time tracking for OCR quality metrics, multi-level confidence scores, and cross-document land plot conflicts.
          </p>
        </div>
        <button
          onClick={() => onNavigate('upload')}
          className="bg-blue-600 hover:bg-blue-500 text-white font-medium px-5 py-2.5 rounded-xl shadow-lg shadow-blue-500/20 flex items-center gap-2 transition-all"
        >
          <FileText className="w-4 h-4" />
          Ingest New Record
        </button>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {metrics.map((m, idx) => {
          const Icon = m.icon;
          return (
            <div key={idx} className={`p-4 rounded-2xl bg-gradient-to-br border ${m.color} glass-card`}>
              <div className="flex justify-between items-start mb-2">
                <span className="text-xs text-slate-400 font-medium">{m.title}</span>
                <Icon className="w-4 h-4 opacity-80" />
              </div>
              <div className="text-xl font-bold text-white">{m.value}</div>
              <div className="text-[11px] text-slate-400 mt-1">{m.sub}</div>
            </div>
          );
        })}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Confidence Score Distribution */}
        <div className="glass-panel p-5 rounded-2xl space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-base font-semibold text-white">4-Tier Explainable Confidence Distribution</h3>
              <p className="text-xs text-slate-400">OCR (40%) + Extraction (30%) + Validation (20%) + Context (10%)</p>
            </div>
            <TrendingUp className="w-5 h-5 text-blue-400" />
          </div>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={confidenceDist}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="range" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {confidenceDist.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Verification Status Breakdown */}
        <div className="glass-panel p-5 rounded-2xl space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-base font-semibold text-white">Record Verification Status</h3>
              <p className="text-xs text-slate-400">Human-in-the-Loop approval breakdown</p>
            </div>
            <button onClick={() => onNavigate('queue')} className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1">
              View Queue <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="h-56 flex items-center justify-between">
            <div className="w-1/2 h-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={statusPie} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={4}>
                    {statusPie.map((entry, index) => (
                      <Cell key={`pie-cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="w-1/2 space-y-3 pl-4">
              {statusPie.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></span>
                    <span className="text-slate-300">{item.name}</span>
                  </div>
                  <span className="font-semibold text-white">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* District Digitization Velocity & Recent Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel p-5 rounded-2xl space-y-4">
          <h3 className="text-base font-semibold text-white">District Digitization Velocity</h3>
          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={districtProgress}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="district" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                <Bar dataKey="digitized" fill="#3b82f6" name="Digitized Records" radius={[4, 4, 0, 0]} />
                <Bar dataKey="pending" fill="#f59e0b" name="Pending Queue" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Quick Quick Actions Card */}
        <div className="glass-panel p-5 rounded-2xl space-y-3">
          <h3 className="text-base font-semibold text-white">High Priority Actions</h3>
          
          <div
            onClick={() => onNavigate('conflicts')}
            className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 hover:bg-red-500/20 cursor-pointer transition-all flex items-center justify-between"
          >
            <div className="flex items-center gap-3">
              <AlertOctagon className="w-5 h-5 text-red-400" />
              <div>
                <div className="text-xs font-semibold text-red-300">Resolve Conflict #245/1</div>
                <div className="text-[11px] text-slate-400">Ownership mismatch on Khasra plot</div>
              </div>
            </div>
            <ArrowUpRight className="w-4 h-4 text-red-400" />
          </div>

          <div
            onClick={() => onNavigate('duplicates')}
            className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/30 hover:bg-purple-500/20 cursor-pointer transition-all flex items-center justify-between"
          >
            <div className="flex items-center gap-3">
              <Copy className="w-5 h-5 text-purple-400" />
              <div>
                <div className="text-xs font-semibold text-purple-300">Review Duplicate Pair</div>
                <div className="text-[11px] text-slate-400">Ramesh Kumar vs Ramesh K. (91%)</div>
              </div>
            </div>
            <ArrowUpRight className="w-4 h-4 text-purple-400" />
          </div>

          <div
            onClick={() => onNavigate('gis')}
            className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 hover:bg-emerald-500/20 cursor-pointer transition-all flex items-center justify-between"
          >
            <div className="flex items-center gap-3">
              <Network className="w-5 h-5 text-emerald-400" />
              <div>
                <div className="text-xs font-semibold text-emerald-300">Inspect Rampur Cadastral Map</div>
                <div className="text-[11px] text-slate-400">4 plots mapped with PostGIS GeoJSON</div>
              </div>
            </div>
            <ArrowUpRight className="w-4 h-4 text-emerald-400" />
          </div>
        </div>
      </div>
    </div>
  );
};
