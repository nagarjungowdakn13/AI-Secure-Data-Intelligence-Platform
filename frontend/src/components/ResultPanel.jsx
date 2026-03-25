function ResultPanel({ results }) {
  if (!results.length) {
    return (
      <div className="rounded-[28px] border border-slate-200 bg-slate-50 p-6">
        <div className="mb-3 inline-flex rounded-2xl bg-sky-100 p-3 text-sky-700">
          <DashboardGlyph />
        </div>
        <h3 className="text-lg font-semibold text-slate-950">Results dashboard</h3>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          Run an analysis to view risk score badges, severity breakdown, findings, and remediation recommendations.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {results.map((result) => (
        <article key={`${result.source_name}-${result.risk_score}`} className="rounded-[28px] border border-slate-200 bg-slate-50 p-5 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">{result.content_type}</p>
              <h3 className="mt-2 text-xl font-semibold text-slate-950">{result.source_name}</h3>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">{result.summary}</p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <RiskBadge level={result.risk_level} score={result.risk_score} />
            </div>
          </div>

          <div className="mt-5 grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
            <section className="rounded-[24px] border border-white bg-white p-4 shadow-sm">
              <div className="mb-3 flex items-center justify-between">
                <h4 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Findings List</h4>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                  Action: {result.action}
                </span>
              </div>
              <div className="space-y-3">
                {result.findings.slice(0, 10).map((finding, index) => (
                  <div key={`${finding.label}-${index}`} className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-100 px-4 py-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-slate-900">{finding.label}</span>
                        <SeverityPill severity={finding.severity} />
                      </div>
                      <p className="mt-1 text-xs text-slate-500">Line {finding.line_number || "-"} • {finding.explanation}</p>
                    </div>
                    <code className="rounded-xl bg-slate-100 px-3 py-2 text-xs text-slate-700">{finding.masked_text}</code>
                  </div>
                ))}
              </div>
            </section>

            <section className="space-y-4">
              <div className="rounded-[24px] border border-white bg-white p-4 shadow-sm">
                <h4 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Severity Breakdown</h4>
                <div className="mt-4 grid grid-cols-2 gap-3">
                  <BreakdownCard label="Critical" value={result.risk_breakdown?.critical || 0} tone="critical" />
                  <BreakdownCard label="High" value={result.risk_breakdown?.high || 0} tone="high" />
                  <BreakdownCard label="Medium" value={result.risk_breakdown?.medium || 0} tone="medium" />
                  <BreakdownCard label="Low" value={result.risk_breakdown?.low || 0} tone="low" />
                </div>
              </div>

              <div className="rounded-[24px] border border-white bg-white p-4 shadow-sm">
                <h4 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Recommendations</h4>
                <div className="mt-4 space-y-3">
                  {(result.recommendations || []).map((item, index) => (
                    <div key={`${index}-${item}`} className="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-600">
                      {item}
                    </div>
                  ))}
                </div>
              </div>
            </section>
          </div>
        </article>
      ))}
    </div>
  );
}

function RiskBadge({ level, score }) {
  const styles = {
    informational: "border-sky-100 bg-sky-50 text-sky-700",
    low: "border-sky-100 bg-sky-50 text-sky-700",
    medium: "border-amber-100 bg-amber-50 text-amber-700",
    high: "border-red-100 bg-red-50 text-red-700",
    critical: "border-red-900 bg-red-950 text-red-100"
  };

  return (
    <div className={`rounded-[24px] border px-4 py-3 shadow-sm ${styles[level] || styles.low}`}>
      <p className="text-[11px] font-semibold uppercase tracking-[0.18em]">Risk Score Badge</p>
      <div className="mt-2 flex items-end gap-3">
        <span className="text-2xl font-semibold">{score}</span>
        <span className="text-sm font-medium uppercase">{level}</span>
      </div>
    </div>
  );
}

function BreakdownCard({ label, value, tone }) {
  const styles = {
    low: "bg-sky-50 text-sky-700",
    medium: "bg-amber-50 text-amber-700",
    high: "bg-red-50 text-red-700",
    critical: "bg-red-950 text-red-100"
  };

  return (
    <div className={`rounded-2xl px-4 py-3 ${styles[tone] || styles.low}`}>
      <p className="text-xs font-semibold uppercase tracking-[0.16em]">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </div>
  );
}

function SeverityPill({ severity }) {
  const styles = {
    low: "bg-sky-100 text-sky-700",
    medium: "bg-amber-100 text-amber-700",
    high: "bg-red-100 text-red-700",
    critical: "bg-red-950 text-red-100"
  };

  return <span className={`rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] ${styles[severity] || styles.low}`}>{severity}</span>;
}

function DashboardGlyph() {
  return (
    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.8">
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 13h6V5H4v8zm10 6h6V5h-6v14zM4 19h6v-4H4v4zm10-8h6v-2h-6v2z" />
    </svg>
  );
}

export default ResultPanel;
