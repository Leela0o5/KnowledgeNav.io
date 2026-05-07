import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar/Sidebar";
import ChatWindow from "../components/Chat/ChatWindow";
import UploadModal from "../components/Upload/UploadModal";
import { getCorpora, Corpus } from "../lib/api";

export default function ChatApp() {
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
  const [selectedCorpusId, setSelectedCorpusId] = useState<string | null>(null);
  const [corpora, setCorpora] = useState<Corpus[]>([]);
  const [uploadOpen, setUploadOpen] = useState(false);

  useEffect(() => {
    getCorpora().then(setCorpora).catch(() => {});
  }, []);

  const currentCorpus = corpora.find((c) => c.id === selectedCorpusId) ?? null;

  const handleCorpusSelect = (id: string) => {
    setSelectedCorpusId(id);
  };

  const handleCorporaRefresh = () => {
    getCorpora().then(setCorpora).catch(() => {});
  };

  return (
    <div className="h-screen w-screen flex overflow-hidden bg-[#0f172a]">
      <Sidebar
        selectedSessionId={selectedSessionId}
        onSelectSession={setSelectedSessionId}
        selectedCorpusId={selectedCorpusId}
        onSelectCorpus={handleCorpusSelect}
        corpora={corpora}
        onOpenUpload={() => setUploadOpen(true)}
        onCorporaChange={handleCorporaRefresh}
      />

      <main className="flex-1 flex flex-col min-h-0 overflow-hidden bg-slate-50">
        <ChatWindow
          sessionId={selectedSessionId}
          corpus={currentCorpus}
          corpusId={selectedCorpusId}
          onSessionCreated={setSelectedSessionId}
        />
      </main>

      <UploadModal
        open={uploadOpen}
        onClose={() => setUploadOpen(false)}
        onUploaded={handleCorporaRefresh}
      />
    </div>
  );
}
