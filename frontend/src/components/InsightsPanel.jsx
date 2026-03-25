function InsightsPanel({ insights, summary }) {
  return (
    <div>
      <div className="mb-4 flex items-center gap-2">
        <InsightGlyph />
        <div>
          <h2 className="text-xl font-semibold text-slate-950">Insights Panel Card</h2>
          <p className="text-sm text-slate-600">AI-generated summary, anomaly explanation, and risk context.</p>
        </div>
      </div>

      <div className="rounded-[28px] border border-sky-100 bg-gradient-to-br from-sky-50 to-white p-5 shadow-sm">
        <p className="text-sm leading-6 text-slate-700">{summary || "Insights will appear after running an analysis."}</p>
      </div>

      <div className="mt-4 space-y-4">
        {insights.map((insight, index) => (
          <article key={`${insight.title}-${index}`} className="rounded-[24px] border border-slate-200 bg-slate-50 p-5 shadow-sm">
            <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-700">{insight.title}</h3>
            <p className="mt-3 text-sm leading-6 text-slate-600">{insight.detail}</p>
          </article>
        ))}
      </div>
    </div>
  );
}

function InsightGlyph() {
  return (
    <span className="inline-flex rounded-2xl bg-sky-100 p-3 text-sky-700">
      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.8">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 3a7 7 0 0 0-4 12.8V19a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-3.2A7 7 0 0 0 12 3z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 21h6" />
      </svg>
    </span>
  );
}

export default InsightsPanel;
