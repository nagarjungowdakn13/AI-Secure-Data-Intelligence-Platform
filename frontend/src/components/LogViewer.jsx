function LogViewer({ results }) {
  const topResult = results[0];

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <HighlightGlyph />
          <div>
            <h2 className="text-xl font-semibold text-slate-950">Highlighted Sensitive Text</h2>
            <p className="text-sm text-slate-600">Masked output with line numbers, highlighted sensitive rows, and risk markers.</p>
          </div>
        </div>
        <Legend />
      </div>

      {!topResult ? (
        <div className="rounded-[28px] border border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
          Highlighted content will appear here after analysis.
        </div>
      ) : (
        <div className="rounded-[28px] border border-slate-200 bg-slate-950 p-4 shadow-inner">
          <pre className="max-h-[460px] overflow-auto whitespace-pre-wrap text-sm leading-7 text-slate-100">
            {topResult.masked_content.split("\n").map((line, index) => {
              const lineNumber = index + 1;
              const lineFindings = topResult.findings.filter((finding) => finding.line_number === lineNumber);
              const lineSeverity = getHighestSeverity(lineFindings);
              const hasRisk = lineFindings.length > 0;

              return (
                <div
                  key={`${index}-${line}`}
                  className={`mb-1 flex items-start gap-3 rounded-xl px-3 py-1.5 ${
                    hasRisk ? rowStyle(lineSeverity) : ""
                  }`}
                >
                  <span className="inline-block w-8 pt-1 text-right text-xs text-slate-500">{lineNumber}</span>
                  <div className="w-24 shrink-0 pt-0.5">
                    {hasRisk ? <RiskMarker severity={lineSeverity} count={lineFindings.length} /> : null}
                  </div>
                  <span className="min-w-0 flex-1 break-words">{line || " "}</span>
                </div>
              );
            })}
          </pre>
        </div>
      )}
    </div>
  );
}

function getHighestSeverity(findings) {
  const order = ["critical", "high", "medium", "low"];
  for (const severity of order) {
    if (findings.some((finding) => finding.severity === severity)) {
      return severity;
    }
  }
  return "low";
}

function rowStyle(severity) {
  const styles = {
    low: "bg-sky-950/40 ring-1 ring-sky-800/40",
    medium: "bg-amber-900/30 ring-1 ring-amber-700/40",
    high: "bg-red-900/35 ring-1 ring-red-700/40",
    critical: "bg-red-950/80 ring-1 ring-red-800/80"
  };
  return styles[severity] || styles.low;
}

function RiskMarker({ severity, count }) {
  const styles = {
    low: "bg-sky-100 text-sky-700",
    medium: "bg-amber-100 text-amber-700",
    high: "bg-red-100 text-red-700",
    critical: "bg-red-950 text-red-100"
  };

  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] ${styles[severity] || styles.low}`}>
      {severity}
      <span className="ml-1.5 rounded-full bg-black/10 px-1.5 py-0.5 text-[10px] leading-none">{count}</span>
    </span>
  );
}

function Legend() {
  return (
    <div className="flex flex-wrap items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.12em]">
      <LegendPill label="Low" tone="bg-sky-100 text-sky-700" />
      <LegendPill label="Medium" tone="bg-amber-100 text-amber-700" />
      <LegendPill label="High" tone="bg-red-100 text-red-700" />
      <LegendPill label="Critical" tone="bg-red-950 text-red-100" />
    </div>
  );
}

function LegendPill({ label, tone }) {
  return <span className={`rounded-full px-2.5 py-1 ${tone}`}>{label}</span>;
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
