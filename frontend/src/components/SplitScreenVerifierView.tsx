import React, { useState } from 'react';
import {
  Split, CheckCircle, Edit3, XCircle, Flag, Info, AlertTriangle,
  ZoomIn, ZoomOut, RotateCw, Eye, Sparkles, HelpCircle, Save
} from 'lucide-react';

interface SplitScreenVerifierViewProps {
  recordId: number;
  onActionComplete: () => void;
}

export const SplitScreenVerifierView: React.FC<SplitScreenVerifierViewProps> = ({ recordId, onActionComplete }) => {
  const [selectedFieldKey, setSelectedFieldKey] = useState<string>('owner_name');
  const [showExplainModal, setShowExplainModal] = useState<boolean>(false);
  const [explainField, setExplainField] = useState<any>(null);
  const [editingFields, setEditingFields] = useState<Record<string, string>>({});
  const [zoomLevel, setZoomLevel] = useState<number>(1.0);
  const [actionSuccessMsg, setActionSuccessMsg] = useState<string>('');

  // Sample data simulating backend query for Record #1 (Jamabandi / ROR)
  const docData = {
    title: 'Jamabandi_2024_Khasra_245.pdf',
    type: 'Jamabandi / Record of Rights',
    qualityScore: 0.92,
    blurMetric: 310.5,
    skewAngle: -0.8,
    status: 'Pending Verification',
    overallConfidence: 0.94,
    fields: [
      {
        key: 'owner_name',
        name: 'Owner Name',
        extractedValue: 'Ramesh Kumar Sharma',
        snippet: 'खाता धारक का नाम: रमेश कुमार शर्मा पुत्र हरीश चंद्र',
        bbox: { x: 120, y: 240, w: 280, h: 45 },
        ocrConf: 0.96,
        extConf: 0.95,
        valConf: 1.00,
        ctxConf: 0.90,
        finalConf: 0.96,
        explanation: 'High confidence: Clear Devnagari printed text match with owner entity pattern.'
      },
      {
        key: 'khasra_number',
        name: 'Khasra Number',
        extractedValue: '245/1',
        snippet: 'खसरा संख्या: २४५/१',
        bbox: { x: 420, y: 180, w: 110, h: 35 },
        ocrConf: 0.98,
        extConf: 0.96,
        valConf: 1.00,
        ctxConf: 0.95,
        finalConf: 0.97,
        explanation: 'High confidence: Precise numeric Devnagari digit normalization (२४५/१ -> 245/1).'
      },
      {
        key: 'land_area',
        name: 'Land Area & Unit',
        extractedValue: '4.25 Acres',
        snippet: 'कुल क्षेत्रफल: ४.२५ एकड़ (१७,१९९.१ वर्ग मीटर)',
        bbox: { x: 550, y: 310, w: 160, h: 40 },
        ocrConf: 0.92,
        extConf: 0.90,
        valConf: 0.95,
        ctxConf: 0.90,
        finalConf: 0.92,
        explanation: 'High confidence: Area non-zero with standard unit normalization (4.25 Acres = 17,199.1 sq.m).'
      },
      {
        key: 'village',
        name: 'Village Location',
        extractedValue: 'Rampur',
        snippet: 'ग्राम: रामपुर, तहसील: रामपुर',
        bbox: { x: 100, y: 140, w: 150, h: 30 },
        ocrConf: 0.95,
        extConf: 0.95,
        valConf: 1.00,
        ctxConf: 0.95,
        finalConf: 0.96,
        explanation: 'Location hierarchy verified: Rampur indexed under Rampur Tehsil in UP master database.'
      }
    ],
    conflictAlert: {
      active: true,
      message: 'Cross-Document Alert: Conflict detected with Sale Deed #9921 for Khasra 245/1 (Purchaser listed as Suresh Kumar Verma).'
    }
  };

  const handleFieldClick = (field: any) => {
    setSelectedFieldKey(field.key);
  };

  const openExplainability = (e: React.MouseEvent, field: any) => {
    e.stopPropagation();
    setExplainField(field);
    setShowExplainModal(true);
  };

  const handleEditChange = (key: string, val: string) => {
    setEditingFields(prev => ({ ...prev, [key]: val }));
  };

  const submitAction = (actionType: string) => {
    setActionSuccessMsg(`Verification action '${actionType}' submitted and recorded to Audit Trail.`);
    setTimeout(() => {
      onActionComplete();
    }, 1500);
  };

  const selectedField = docData.fields.find(f => f.key === selectedFieldKey) || docData.fields[0];

  return (
    <div className="space-y-4">
      {/* Action Notification Header */}
      {actionSuccessMsg && (
        <div className="bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 p-3 rounded-xl text-xs font-semibold flex items-center justify-between animate-fade-in">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span>{actionSuccessMsg}</span>
          </div>
        </div>
      )}

      {/* Cross Document Conflict Warning Banner */}
      {docData.conflictAlert.active && (
        <div className="bg-red-500/10 border border-red-500/30 p-3 rounded-xl text-xs text-red-300 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-400" />
            <span>{docData.conflictAlert.message}</span>
          </div>
          <button className="text-red-400 underline font-semibold hover:text-red-200">
            View Conflict Graph
          </button>
        </div>
      )}

      {/* Split-Screen Main Container */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-180px)]">
        {/* LEFT PANEL: Document Canvas Overlay */}
        <div className="lg:col-span-7 glass-panel rounded-2xl p-4 flex flex-col justify-between relative overflow-hidden">
          <div className="flex justify-between items-center pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2 text-xs">
              <span className="font-semibold text-white">{docData.title}</span>
              <span className="text-slate-400">• Page 1 of 1</span>
              <span className="bg-blue-500/20 text-blue-300 border border-blue-500/30 px-2 py-0.5 rounded text-[10px]">
                Quality: {(docData.qualityScore * 100).toFixed(0)}%
              </span>
            </div>
            <div className="flex items-center gap-1 bg-slate-900 border border-slate-700 rounded-lg p-1">
              <button onClick={() => setZoomLevel(z => Math.max(0.7, z - 0.1))} className="p-1 hover:bg-slate-800 rounded text-slate-300">
                <ZoomOut className="w-3.5 h-3.5" />
              </button>
              <span className="text-[11px] text-slate-400 px-2 font-mono">{(zoomLevel * 100).toFixed(0)}%</span>
              <button onClick={() => setZoomLevel(z => Math.min(1.5, z + 0.1))} className="p-1 hover:bg-slate-800 rounded text-slate-300">
                <ZoomIn className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Simulated Image Document with Overlay Canvas */}
          <div className="flex-1 overflow-auto p-4 flex justify-center items-center relative">
            <div
              className="relative transition-transform duration-200 bg-slate-900 rounded-lg shadow-2xl border border-slate-800 overflow-hidden"
              style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'top center', width: '600px', height: '480px' }}
            >
              {/* Document Image Representation */}
              <div className="p-8 text-slate-300 text-xs space-y-6 font-mono select-none bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px]">
                <div className="text-center font-bold text-base text-blue-300 border-b border-slate-700 pb-2 uppercase tracking-wide">
                  अधिकार अभिलेख (जमाबंदी) 2024
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>ग्राम: रामपुर (Rampur)</div>
                  <div>तहसील: रामपुर तहसील</div>
                  <div>खसरा संख्या: २४५/१</div>
                  <div>खाता संख्या: ८९</div>
                </div>

                <div className="p-3 bg-slate-800/40 rounded border border-slate-700/60 space-y-2">
                  <div>खाता धारक का नाम: रमेश कुमार शर्मा</div>
                  <div>पिता का नाम: हरीश चंद्र शर्मा</div>
                  <div>कुल क्षेत्रफल: ४.२५ एकड़ (१७,१९९.१ वर्ग मीटर)</div>
                </div>

                <div className="text-[10px] text-slate-500 pt-8">
                  उत्परिवर्तन क्रमांक: MUT-2023-882 • पंजीयन: REG-UP-9921
                </div>
              </div>

              {/* Bounding Box Highlights Synced to Selection */}
              {docData.fields.map((f) => {
                const isSelected = f.key === selectedFieldKey;
                return (
                  <div
                    key={f.key}
                    onClick={() => setSelectedFieldKey(f.key)}
                    className={`absolute cursor-pointer rounded transition-all ${
                      isSelected
                        ? 'border-2 border-blue-400 bg-blue-500/25 active-bbox z-20'
                        : 'border border-amber-400/50 bg-amber-400/10 hover:border-amber-400 z-10'
                    }`}
                    style={{
                      left: `${f.bbox.x}px`,
                      top: `${f.bbox.y}px`,
                      width: `${f.bbox.w}px`,
                      height: `${f.bbox.h}px`
                    }}
                  >
                    <span className={`absolute -top-5 left-0 text-[10px] font-bold px-1.5 py-0.5 rounded shadow ${
                      isSelected ? 'bg-blue-600 text-white' : 'bg-slate-800 text-amber-300'
                    }`}>
                      {f.name} ({(f.finalConf * 100).toFixed(0)}%)
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* RIGHT PANEL: Extracted Fields & Verification Action Controls */}
        <div className="lg:col-span-5 glass-panel rounded-2xl p-4 flex flex-col justify-between overflow-y-auto space-y-4">
          <div className="space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Split className="w-4 h-4 text-blue-400" />
                  Extracted Land Fields
                </h3>
                <p className="text-xs text-slate-400">Click field card to highlight source bounding box</p>
              </div>
              <div className="text-right">
                <div className="text-[10px] text-slate-400 uppercase">Overall Score</div>
                <div className="text-sm font-bold text-emerald-400">{(docData.overallConfidence * 100).toFixed(0)}%</div>
              </div>
            </div>

            {/* Field Cards Stack */}
            <div className="space-y-3">
              {docData.fields.map((f) => {
                const isSelected = f.key === selectedFieldKey;
                const isEdited = editingFields[f.key] !== undefined;
                const currentVal = editingFields[f.key] !== undefined ? editingFields[f.key] : f.extractedValue;

                return (
                  <div
                    key={f.key}
                    onClick={() => handleFieldClick(f)}
                    className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-blue-600/15 border-blue-500/50 shadow-lg shadow-blue-500/10'
                        : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-1.5">
                      <span className="text-xs font-semibold text-slate-300">{f.name}</span>
                      <button
                        onClick={(e) => openExplainability(e, f)}
                        className="flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full border bg-emerald-500/10 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/20"
                      >
                        <Sparkles className="w-3 h-3" />
                        {(f.finalConf * 100).toFixed(0)}% Explain
                      </button>
                    </div>

                    {/* Inline Field Editor */}
                    <div className="mt-1">
                      <input
                        type="text"
                        value={currentVal}
                        onChange={(e) => handleEditChange(f.key, e.target.value)}
                        className="w-full bg-slate-950/80 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-white font-medium focus:outline-none focus:border-blue-500"
                      />
                    </div>

                    <div className="text-[11px] text-slate-400 mt-2 font-mono line-clamp-1 bg-slate-950/40 px-2 py-1 rounded">
                      Snippet: "{f.snippet}"
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Action Buttons Bar */}
          <div className="pt-4 border-t border-slate-800 space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => submitAction('APPROVE')}
                className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold py-2.5 rounded-xl flex items-center justify-center gap-1.5 shadow-lg shadow-emerald-500/20 transition-all"
              >
                <CheckCircle className="w-4 h-4" />
                Approve & Verify
              </button>

              <button
                onClick={() => submitAction('EDIT_SAVE')}
                className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold py-2.5 rounded-xl flex items-center justify-center gap-1.5 shadow-lg shadow-blue-500/20 transition-all"
              >
                <Save className="w-4 h-4" />
                Save Edits
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => submitAction('FLAG')}
                className="bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-500/30 text-xs font-semibold py-2 rounded-xl flex items-center justify-center gap-1.5 transition-all"
              >
                <Flag className="w-3.5 h-3.5" />
                Flag for Supervisor
              </button>

              <button
                onClick={() => submitAction('REJECT')}
                className="bg-red-600/20 hover:bg-red-600/30 text-red-400 border border-red-500/30 text-xs font-semibold py-2 rounded-xl flex items-center justify-center gap-1.5 transition-all"
              >
                <XCircle className="w-3.5 h-3.5" />
                Reject Record
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* EXPLAINABILITY MODAL */}
      {showExplainModal && explainField && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel bg-slate-900 border border-slate-700 rounded-2xl max-w-md w-full p-6 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-emerald-400" />
                  Explainable AI Confidence Rationale
                </h3>
                <p className="text-xs text-slate-400">Field: {explainField.name}</p>
              </div>
              <button onClick={() => setShowExplainModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            {/* Score Weight Matrix */}
            <div className="space-y-3 text-xs">
              <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-2">
                <div className="flex justify-between">
                  <span className="text-slate-400">OCR Character Score (40%):</span>
                  <span className="font-bold text-white">{(explainField.ocrConf * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Extraction Pattern Score (30%):</span>
                  <span className="font-bold text-white">{(explainField.extConf * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Database Schema Validation (20%):</span>
                  <span className="font-bold text-white">{(explainField.valConf * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Contextual Rule Score (10%):</span>
                  <span className="font-bold text-white">{(explainField.ctxConf * 100).toFixed(0)}%</span>
                </div>
                <div className="border-t border-slate-800 pt-2 flex justify-between font-bold text-sm">
                  <span className="text-emerald-400">Final Weighted Score:</span>
                  <span className="text-emerald-400">{(explainField.finalConf * 100).toFixed(0)}%</span>
                </div>
              </div>

              {/* Text Explanation */}
              <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-xl text-blue-200">
                <p className="font-semibold mb-1">Human-Readable Rationale:</p>
                <p>{explainField.explanation}</p>
              </div>
            </div>

            <button
              onClick={() => setShowExplainModal(false)}
              className="w-full bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold py-2 rounded-xl transition-colors"
            >
              Close Rationale View
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
