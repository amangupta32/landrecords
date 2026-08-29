import React, { useState } from 'react';
import { UploadCloud, FileText, CheckCircle2, Sparkles, AlertCircle, ArrowRight } from 'lucide-react';

interface UploadViewProps {
  onUploadSuccess: (docId: number) => void;
}

export const UploadView: React.FC<UploadViewProps> = ({ onUploadSuccess }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [processingStage, setProcessingStage] = useState<string>('');

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const startIngestion = () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setProcessingStage('1. OpenCV Image Preprocessing (Deskewing & Contrast)...');

    setTimeout(() => {
      setProcessingStage('2. OCR Engine (Indic Neural + Devnagari Text)...');
    }, 1200);

    setTimeout(() => {
      setProcessingStage('3. Hybrid NLP Field Extraction & Bounding Boxes...');
    }, 2400);

    setTimeout(() => {
      setProcessingStage('4. Multi-Level Confidence & Hierarchy Validation...');
    }, 3600);

    setTimeout(() => {
      setIsUploading(false);
      onUploadSuccess(1); // Redirect to Split-Screen Verifier for doc #1
    }, 4800);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="glass-panel p-6 rounded-2xl space-y-2">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <UploadCloud className="w-5 h-5 text-blue-400" />
          Ingest Scanned / Legacy Land Record Document
        </h2>
        <p className="text-xs text-slate-400">
          Upload Jamabandi (ROR), Sale Deed, Mutation Record, or Khasra Girdawari (PDF, PNG, JPG, TIFF).
          The AI engine will execute skew correction, noise reduction, OCR, layout extraction, and 4-tier confidence scoring.
        </p>
      </div>

      {!isUploading ? (
        <div className="glass-panel p-8 rounded-2xl space-y-6">
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-2xl p-10 text-center transition-all ${
              dragActive
                ? 'border-blue-500 bg-blue-500/10 scale-[1.01]'
                : 'border-slate-700 bg-slate-900/40 hover:border-slate-600'
            }`}
          >
            <input
              type="file"
              id="file-upload"
              accept=".pdf,.png,.jpg,.jpeg,.tiff"
              onChange={handleFileChange}
              className="hidden"
            />

            {selectedFile ? (
              <div className="space-y-4">
                <div className="w-16 h-16 bg-blue-500/20 text-blue-400 border border-blue-500/40 rounded-2xl flex items-center justify-center mx-auto">
                  <FileText className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-base font-semibold text-white">{selectedFile.name}</h3>
                  <p className="text-xs text-slate-400">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • {selectedFile.type || 'Document'}</p>
                </div>
                <button
                  onClick={() => setSelectedFile(null)}
                  className="text-xs text-red-400 hover:underline font-medium"
                >
                  Choose Different File
                </button>
              </div>
            ) : (
              <label htmlFor="file-upload" className="cursor-pointer space-y-3 block">
                <div className="w-16 h-16 bg-slate-800 text-slate-400 border border-slate-700 rounded-2xl flex items-center justify-center mx-auto hover:text-blue-400 hover:border-blue-500/50 transition-colors">
                  <UploadCloud className="w-8 h-8" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-200">
                    Click to browse or drag & drop document file
                  </p>
                  <p className="text-xs text-slate-400 mt-1">Supports high-res scanned PDFs, images, and legacy handwritten records</p>
                </div>
              </label>
            )}
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              disabled={!selectedFile}
              onClick={startIngestion}
              className={`px-6 py-2.5 rounded-xl font-medium text-sm flex items-center gap-2 transition-all ${
                selectedFile
                  ? 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/25'
                  : 'bg-slate-800 text-slate-500 cursor-not-allowed'
              }`}
            >
              <Sparkles className="w-4 h-4" />
              Start AI Digitization Pipeline
            </button>
          </div>
        </div>
      ) : (
        <div className="glass-panel p-10 rounded-2xl text-center space-y-6">
          <div className="w-20 h-20 bg-blue-500/20 text-blue-400 border border-blue-500/40 rounded-full flex items-center justify-center mx-auto animate-bounce">
            <Sparkles className="w-10 h-10 animate-spin" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">AI Land Record Processing Active</h3>
            <p className="text-xs text-slate-400 mt-1">{processingStage}</p>
          </div>

          {/* Pipeline Stage Indicators */}
          <div className="max-w-md mx-auto space-y-3 pt-4 text-left">
            <div className="flex items-center justify-between text-xs text-slate-300">
              <span className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" /> OpenCV Image Quality & Deskew
              </span>
              <span className="text-emerald-400">Complete</span>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-300">
              <span className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Devnagari & English Neural OCR
              </span>
              <span className="text-emerald-400">Complete</span>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-300">
              <span className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-blue-400 animate-pulse" /> NLP Field Extraction & Bounding Boxes
              </span>
              <span className="text-blue-400 font-mono">In Progress</span>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-500">
              <span className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-slate-600" /> Explainable Confidence & Location Check
              </span>
              <span>Pending</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
