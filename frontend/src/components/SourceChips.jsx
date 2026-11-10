export default function SourceChips({ sources = [] }) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-2.5 flex flex-wrap items-center gap-1.5 text-xs">
      <span className="text-gray-500 font-medium mr-1">Sources:</span>
      {sources.map((s, idx) => {
        let domain = "";
        try {
          domain = new URL(s.url).hostname.replace(/^www\./, "");
        } catch {
          domain = s.title || s.url;
        }

        return (
          <a
            key={idx}
            href={s.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-neutral-800 hover:bg-neutral-700 text-blue-400 hover:text-blue-300 border border-neutral-700 transition-colors"
          >
            <span className="font-semibold text-gray-400">[{idx + 1}]</span>
            <span className="truncate max-w-[140px]">{domain}</span>
          </a>
        );
      })}
    </div>
  );
}
