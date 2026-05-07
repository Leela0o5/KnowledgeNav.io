import { useRef, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, Upload, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import { getCorpora, ingestFiles, Corpus } from '../../lib/api';
import { useEffect } from 'react';

interface UploadModalProps {
  open: boolean;
  onClose: () => void;
  onUploaded?: () => void;
}

export default function UploadModal({ open, onClose, onUploaded }: UploadModalProps) {
  const [corpora, setCorpora] = useState<Corpus[]>([]);
  const [corpusId, setCorpusId] = useState('');
  const [newCorpusName, setNewCorpusName] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [overwrite, setOverwrite] = useState(false);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'done' | 'error'>('idle');
  const [result, setResult] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      getCorpora().then((c) => {
        setCorpora(c);
        if (c.length > 0 && !corpusId) setCorpusId(c[0].id);
      }).catch(() => {});
    }
  }, [open]);

  const handleFiles = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) setFiles(Array.from(e.target.files));
  };

  const handleSubmit = async () => {
    const targetCorpus = corpusId || newCorpusName.trim();
    if (!targetCorpus || files.length === 0) return;
    setStatus('uploading');
    try {
      const res = await ingestFiles(targetCorpus, files, overwrite);
      setResult(`Indexed ${res.chunks_indexed} chunks into "${res.corpus_id}"`);
      setStatus('done');
      setFiles([]);
      setNewCorpusName('');
      onUploaded?.();
    } catch {
      setResult('Upload failed. Check the backend and try again.');
      setStatus('error');
    }
  };

  const reset = () => {
    setStatus('idle');
    setResult('');
    setFiles([]);
    setNewCorpusName('');
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="bg-[#0f172a] border border-slate-700 rounded-2xl p-6 w-full max-w-md mx-4 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-white font-bold text-lg">Upload Documents</h2>
              <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>

            {status === 'done' || status === 'error' ? (
              <div className="flex flex-col items-center py-8 gap-4 text-center">
                {status === 'done' ? (
                  <CheckCircle2 className="w-12 h-12 text-emerald-400" />
                ) : (
                  <AlertCircle className="w-12 h-12 text-red-400" />
                )}
                <p className={`text-sm font-medium ${status === 'done' ? 'text-emerald-300' : 'text-red-300'}`}>
                  {result}
                </p>
                <button
                  onClick={reset}
                  className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-500 transition-colors"
                >
                  Upload More
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Corpus selection */}
                <div>
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-widest block mb-2">
                    Corpus
                  </label>
                  {corpora.length > 0 && (
                    <select
                      value={corpusId}
                      onChange={(e) => setCorpusId(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 mb-2"
                    >
                      {corpora.map((c) => (
                        <option key={c.id} value={c.id}>{c.name}</option>
                      ))}
                      <option value="">+ New corpus…</option>
                    </select>
                  )}
                  {(corpusId === '' || corpora.length === 0) && (
                    <input
                      type="text"
                      placeholder="New corpus name (e.g. legal-docs)"
                      value={newCorpusName}
                      onChange={(e) => setNewCorpusName(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500"
                    />
                  )}
                </div>

                {/* File picker */}
                <div>
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-widest block mb-2">
                    Files
                  </label>
                  <button
                    onClick={() => fileRef.current?.click()}
                    className="w-full border-2 border-dashed border-slate-700 hover:border-blue-500 rounded-xl p-6 flex flex-col items-center gap-2 transition-colors group"
                  >
                    <Upload className="w-8 h-8 text-slate-500 group-hover:text-blue-400 transition-colors" />
                    <span className="text-xs text-slate-500 group-hover:text-slate-300 transition-colors">
                      Click to select files (PDF, DOCX, TXT…)
                    </span>
                  </button>
                  <input
                    ref={fileRef}
                    type="file"
                    multiple
                    className="hidden"
                    onChange={handleFiles}
                    accept=".pdf,.docx,.doc,.txt,.md"
                  />
                  {files.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {files.map((f) => (
                        <div key={f.name} className="flex items-center gap-2 text-xs text-slate-300 bg-slate-800/50 px-3 py-1.5 rounded-lg">
                          <FileText className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                          <span className="truncate">{f.name}</span>
                          <span className="text-slate-500 shrink-0">({(f.size / 1024).toFixed(0)} KB)</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Overwrite */}
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={overwrite}
                    onChange={(e) => setOverwrite(e.target.checked)}
                    className="w-4 h-4 rounded accent-blue-500"
                  />
                  <span className="text-xs text-slate-400">Overwrite existing chunks for this corpus</span>
                </label>

                {/* Submit */}
                <button
                  onClick={handleSubmit}
                  disabled={status === 'uploading' || files.length === 0 || (!corpusId && !newCorpusName.trim())}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-colors text-sm flex items-center justify-center gap-2"
                >
                  {status === 'uploading' ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Uploading…
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4" />
                      Upload {files.length > 0 ? `${files.length} file${files.length > 1 ? 's' : ''}` : 'Files'}
                    </>
                  )}
                </button>
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
