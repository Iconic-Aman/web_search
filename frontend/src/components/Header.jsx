export default function Header({ onNewChat }) {
  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-border bg-surface select-none">
      <div className="flex items-center gap-2">
        <span className="text-xl">🔍</span>
        <h1 className="text-lg font-semibold text-gray-100">Search Chat Agent</h1>
      </div>
      <button
        onClick={onNewChat}
        className="px-3 py-1.5 text-sm font-medium text-gray-300 hover:text-white bg-card hover:bg-neutral-800 border border-border rounded-lg transition-colors"
      >
        New chat
      </button>
    </header>
  );
}
