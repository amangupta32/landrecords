import React, { useEffect, useState } from 'react';
import { MapPin, Layers, Info, CheckCircle2, AlertOctagon, Clock } from 'lucide-react';

export const GISMapView: React.FC = () => {
  const [selectedPlot, setSelectedPlot] = useState<any>(null);

  const plotFeatures = [
    {
      id: 1,
      khasra: '245/1',
      village: 'Rampur',
      owner: 'Ramesh Kumar Sharma',
      area: '4.25 Acres',
      status: 'Verified',
      statusColor: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
      coords: [28.8125, 79.0250]
    },
    {
      id: 2,
      khasra: '245/2',
      village: 'Rampur',
      owner: 'Suresh Kumar Verma (Conflict)',
      area: '4.10 Acres',
      status: 'Conflict',
      statusColor: 'text-red-400 border-red-500/30 bg-red-500/10',
      coords: [28.8135, 79.0250]
    },
    {
      id: 3,
      khasra: '118',
      village: 'Chandpur',
      owner: 'Priya Devi',
      area: '6.17 Acres',
      status: 'Verified',
      statusColor: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
      coords: [28.8150, 79.0280]
    },
    {
      id: 4,
      khasra: '312/B',
      village: 'Rampur',
      owner: 'Ramesh K. Sharma',
      area: '4.25 Acres',
      status: 'LowConfidence',
      statusColor: 'text-amber-400 border-amber-500/30 bg-amber-500/10',
      coords: [28.8110, 79.0220]
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center glass-panel p-6 rounded-2xl">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <MapPin className="w-5 h-5 text-emerald-400" />
            GIS Cadastral Map View (Rampur Tehsil)
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Geospatial PostGIS GeoJSON mapping linking digitized land records directly to cadastral plot boundaries.
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-emerald-500"></span> Verified</div>
          <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-amber-500"></span> Low Confidence</div>
          <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></span> Conflict</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[500px]">
        {/* Map Container */}
        <div className="lg:col-span-8 glass-panel rounded-2xl p-4 relative overflow-hidden flex flex-col justify-between">
          {/* Simulated High-Tech Map Canvas */}
          <div className="w-full h-full rounded-xl bg-slate-950 border border-slate-800 relative overflow-hidden p-6 flex flex-col justify-between bg-[radial-gradient(#334155_1px,transparent_1px)] [background-size:24px_24px]">
            {/* Overlay Map Header */}
            <div className="flex justify-between items-center z-10">
              <span className="bg-slate-900/90 backdrop-blur border border-slate-700 text-xs px-3 py-1.5 rounded-lg text-slate-200 font-mono">
                Lat: 28.8124° N, Lng: 79.0250° E • Zoom: 15x
              </span>
              <span className="bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs px-3 py-1 rounded-full font-semibold">
                PostGIS Geometry Sync
              </span>
            </div>

            {/* Interactive Plots SVG Render */}
            <div className="absolute inset-0 flex items-center justify-center">
              <svg className="w-full h-full p-12">
                {/* Cadastral Polygon 1: Khasra 245/1 */}
                <polygon
                  points="180,140 320,140 320,240 180,240"
                  className="fill-emerald-500/20 stroke-emerald-500 stroke-2 hover:fill-emerald-500/40 cursor-pointer transition-all"
                  onClick={() => setSelectedPlot(plotFeatures[0])}
                />
                <text x="250" y="195" fill="#10b981" fontSize="12" fontWeight="bold" textAnchor="middle">Plot 245/1</text>

                {/* Cadastral Polygon 2: Khasra 245/2 (Conflict) */}
                <polygon
                  points="330,140 470,140 470,240 330,240"
                  className="fill-red-500/25 stroke-red-500 stroke-2 hover:fill-red-500/40 cursor-pointer transition-all animate-pulse"
                  onClick={() => setSelectedPlot(plotFeatures[1])}
                />
                <text x="400" y="195" fill="#ef4444" fontSize="12" fontWeight="bold" textAnchor="middle">Plot 245/2 (Conflict)</text>

                {/* Cadastral Polygon 3: Khasra 118 */}
                <polygon
                  points="220,260 420,260 420,360 220,360"
                  className="fill-emerald-500/20 stroke-emerald-500 stroke-2 hover:fill-emerald-500/40 cursor-pointer transition-all"
                  onClick={() => setSelectedPlot(plotFeatures[2])}
                />
                <text x="320" y="315" fill="#10b981" fontSize="12" fontWeight="bold" textAnchor="middle">Plot 118 (Chandpur)</text>
              </svg>
            </div>

            <div className="z-10 text-[11px] text-slate-400 bg-slate-900/80 p-2 rounded-lg border border-slate-800 w-max">
              Click any land plot polygon to inspect record attributes
            </div>
          </div>
        </div>

        {/* Selected Plot Detail Sidebar */}
        <div className="lg:col-span-4 glass-panel rounded-2xl p-6 flex flex-col justify-between space-y-4">
          <div>
            <h3 className="text-base font-bold text-white mb-1">Cadastral Plot Details</h3>
            <p className="text-xs text-slate-400">Selected plot metadata & ownership status</p>

            {selectedPlot ? (
              <div className="mt-6 space-y-4 text-xs">
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-sm text-white">Khasra #{selectedPlot.khasra}</span>
                    <span className={`px-2.5 py-0.5 rounded font-semibold border ${selectedPlot.statusColor}`}>
                      {selectedPlot.status}
                    </span>
                  </div>
                  <div className="space-y-2 pt-2 border-t border-slate-800">
                    <div className="flex justify-between"><span className="text-slate-400">Village:</span><span className="text-slate-200 font-semibold">{selectedPlot.village}</span></div>
                    <div className="flex justify-between"><span className="text-slate-400">Owner Name:</span><span className="text-slate-200 font-semibold">{selectedPlot.owner}</span></div>
                    <div className="flex justify-between"><span className="text-slate-400">Land Area:</span><span className="text-slate-200 font-semibold">{selectedPlot.area}</span></div>
                    <div className="flex justify-between"><span className="text-slate-400">Tehsil:</span><span className="text-slate-300">Rampur Tehsil</span></div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="mt-12 text-center text-slate-500 text-xs space-y-2">
                <Info className="w-8 h-8 mx-auto opacity-50" />
                <p>Click on plot polygon on map to view spatial details</p>
              </div>
            )}
          </div>

          <div className="text-[11px] text-slate-500 pt-4 border-t border-slate-800">
            Cadastral Coordinates linked via PostGIS GeoJSON API
          </div>
        </div>
      </div>
    </div>
  );
};
