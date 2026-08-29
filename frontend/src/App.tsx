import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { DashboardView } from './components/DashboardView';
import { UploadView } from './components/UploadView';
import { VerificationQueueView } from './components/VerificationQueueView';
import { SplitScreenVerifierView } from './components/SplitScreenVerifierView';
import { ConflictGraphView } from './components/ConflictGraphView';
import { DuplicatesView } from './components/DuplicatesView';
import { GISMapView } from './components/GISMapView';
import { SearchExportView } from './components/SearchExportView';
import { AuditLogView } from './components/AuditLogView';
import { ExperimentsView } from './components/ExperimentsView';

export function App() {
  const [activeView, setActiveView] = useState<string>('dashboard');
  const [currentRole, setCurrentRole] = useState<string>('Verifier');
  const [selectedRecordId, setSelectedRecordId] = useState<number>(1);

  const handleNavigateToRecord = (recordId: number) => {
    setSelectedRecordId(recordId);
    setActiveView('verifier');
  };

  const handleUploadSuccess = (docId: number) => {
    setSelectedRecordId(docId);
    setActiveView('verifier');
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col font-['Inter',sans-serif]">
      {/* Top Navbar */}
      <Navbar
        currentRole={currentRole}
        onRoleChange={setCurrentRole}
        activeView={activeView}
      />

      {/* Main Workspace Body */}
      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          activeView={activeView}
          onViewChange={setActiveView}
        />

        <main className="flex-1 p-6 overflow-y-auto">
          {activeView === 'dashboard' && <DashboardView onNavigate={setActiveView} />}
          {activeView === 'upload' && <UploadView onUploadSuccess={handleUploadSuccess} />}
          {activeView === 'queue' && <VerificationQueueView onSelectRecord={handleNavigateToRecord} />}
          {activeView === 'verifier' && (
            <SplitScreenVerifierView
              recordId={selectedRecordId}
              onActionComplete={() => setActiveView('queue')}
            />
          )}
          {activeView === 'conflicts' && <ConflictGraphView />}
          {activeView === 'duplicates' && <DuplicatesView />}
          {activeView === 'gis' && <GISMapView />}
          {activeView === 'search' && <SearchExportView />}
          {activeView === 'audit' && <AuditLogView />}
          {activeView === 'experiments' && <ExperimentsView />}
        </main>
      </div>
    </div>
  );
}

export default App;
