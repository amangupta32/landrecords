import React from 'react';
import {
  LayoutDashboard, Upload, CheckSquare, Split, Network, Copy,
  MapPin, Search, History, TestTube, ChevronRight
} from 'lucide-react';

interface SidebarProps {
  activeView: string;
  onViewChange: (view: string) => void;
  pendingCount?: number;
  conflictCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeView,
  onViewChange,
  pendingCount = 4,
  conflictCount = 2
}) => {
  const menuItems = [
    { id: 'dashboard', label: 'Analytics Dashboard', icon: LayoutDashboard },
    { id: 'upload', label: 'Upload Land Document', icon: Upload },
    { id: 'queue', label: 'Verification Queue', icon: CheckSquare, badge: pendingCount },
    { id: 'verifier', label: 'Split-Screen Verifier', icon: Split },
    { id: 'conflicts', label: 'Cross-Doc Conflict Graph', icon: Network, badge: conflictCount, badgeColor: 'bg-red-500/20 text-red-400 border-red-500/30' },
    { id: 'duplicates', label: 'Duplicate Resolution', icon: Copy },
    { id: 'gis', label: 'GIS Cadastral Map', icon: MapPin },
    { id: 'search', label: 'Search & Data Export', icon: Search },
    { id: 'audit', label: 'Audit Trail Logs', icon: History },
    { id: 'experiments', label: 'AI Benchmark Bench', icon: TestTube },
  ];

  return (
    <aside className="w-64 glass-panel border-r border-slate-800 flex flex-col justify-between py-4 px-3 min-h-[calc(100vh-80px)]">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[11px] font-semibold text-slate-400 tracking-wider uppercase">
          Navigation Workspace
        </div>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                isActive
                  ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-lg shadow-blue-500/10'
                  : 'text-slate-300 hover:bg-slate-800/60 hover:text-slate-100'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge ? (
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${item.badgeColor || 'bg-blue-500/20 text-blue-300 border-blue-500/30'}`}>
                  {item.badge}
                </span>
              ) : (
                isActive && <ChevronRight className="w-4 h-4 text-blue-400" />
              )}
            </button>
          );
        })}
      </div>

      {/* Footer System Specs */}
      <div className="px-3 pt-4 border-t border-slate-800/80 text-xs text-slate-500 space-y-1">
        <div className="flex justify-between">
          <span>Engine Version:</span>
          <span className="text-slate-300">v1.0.0 (FastAPI)</span>
        </div>
        <div className="flex justify-between">
          <span>OCR Fallback:</span>
          <span className="text-emerald-400 font-mono">Indic Neural</span>
        </div>
      </div>
    </aside>
  );
};
