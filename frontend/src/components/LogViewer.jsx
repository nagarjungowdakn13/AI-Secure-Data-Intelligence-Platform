function LogViewer({ results }) {
  const topResult = results[0];

  return (
    <div>
      <div className="mb-4 flex items-center gap-2">
        <HighlightGlyph />
        <div>
          <h2 className="text-xl font-semibold text-slate-950">Highlighted Sensitive Text</h2>
          <p className="text-sm text-slate-600">Masked output with sensitive lines visually emphasized for review.</p>
        </div>
      </div>

      {!topResult ? (
        <div className="rounded-[28px] border border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
          Highlighted content will appear here after analysis.
        </div>
      ) : (
        <div className="rounded-[28px] border border-slate-200 bg-slate-950 p-4 shadow-inner">
          <pre className="max-h-[420px] overflow-auto whitespace-pre-wrap text-sm leading-7 text-slate-100">
            {topResult.masked_content.split("\n").map((line, index) => {
              const isSensitive = topResult.findings.some((finding) => finding.line_number === index + 1);
              return (
                <div
                  key={`${index}-${line}`}
                  className={`rounded-xl px-3 ${isSensitive ? "bg-red-950/70 text-red-100 ring-1 ring-red-800/70" : ""}`}
                >
                  <span className="mr-3 inline-block w-8 text-right text-xs text-slate-500">{index + 1}</span>
                  {line || " "}
                </div>
              );
            })}
          </pre>
        </div>
      )}
    </div>
  );
}

function HighlightGlyph() {
  return (
    <span className="inline-flex rounded-2xl bg-red-50 p-3 text-red-700">
      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.8">
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 5l4 4M4 20l4.5-1 9-9a2.12 2.12 0 0 0-3-3l-9 9L4 20z" />
      </svg>
    </span>
  );
}

export default LogViewer;
