export default function StatusLine({ status, error }) {
  if (error) {
    return (
      <div className="flex items-center gap-2 text-sm text-red-400 bg-red-950/30 border border-red-800/50 px-3 py-2 rounded-lg my-2">
        <span>⚠️</span>
        <span>{error}</span>
      </div>
    );
  }

  if (status === "searching") {
    return (
      <div className="flex items-center gap-2 text-sm text-blue-400 py-2 animate-pulse">
        <span>🔍</span>
        <span>Searching the web…</span>
      </div>
    );
  }

  return null;
}
