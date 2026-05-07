import { LogOut, Upload } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface SidebarFooterProps {
  onOpenUpload: () => void;
}

export default function SidebarFooter({ onOpenUpload }: SidebarFooterProps) {
  const { user, logout } = useAuth();

  const initials = user?.name
    ? user.name.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase()
    : '??';

  return (
    <div className="p-4 border-t border-slate-800/60 bg-[#0f172a] shrink-0">
      <div className="flex items-center gap-3 mb-4 px-2">
        {user?.avatar_url ? (
          <img
            src={user.avatar_url}
            alt={user.name}
            className="w-9 h-9 rounded-full object-cover shadow-lg"
          />
        ) : (
          <div className="w-9 h-9 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold text-xs shadow-lg shadow-blue-500/20">
            {initials}
          </div>
        )}
        <div className="flex-1 min-w-0">
          <div className="text-sm font-semibold text-white truncate">{user?.name ?? 'Loading…'}</div>
          <div className="text-[11px] text-slate-500 font-medium truncate">{user?.email ?? ''}</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <button
          onClick={onOpenUpload}
          className="flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors text-xs font-semibold"
        >
          <Upload className="w-3.5 h-3.5" />
          Upload
        </button>
        <button
          onClick={logout}
          className="flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-slate-800 text-slate-300 hover:bg-red-500/10 hover:text-red-400 transition-colors text-xs font-semibold"
        >
          <LogOut className="w-3.5 h-3.5" />
          Log out
        </button>
      </div>
    </div>
  );
}
