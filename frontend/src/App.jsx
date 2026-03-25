import { useMemo, useState } from "react";
import UploadBox from "./components/UploadBox";
import ResultPanel from "./components/ResultPanel";
import InsightsPanel from "./components/InsightsPanel";
import LogViewer from "./components/LogViewer";

const apiBase = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const defaultOptions = {
  mask: true,
  block_high_risk: true,
  log_analysis: true
};

const quickSample = `2026-03-10 INFO login
email=admin@company.com
password=admin123
api_key=sk-test-xyzABC12345
2026-03-10 WARN invalid login attempt username=admin
ERROR stack trace: null pointer`;

function App() {
  const [inputType, setInputType] = useState("text");
  const [content, setContent] = useState("");
  const [options, setOptions] = useState(defaultOptions);
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const topResult = results[0] || null;
  const findingCount = useMemo(
    () => results.reduce((total, item) => total + item.findings.length, 0),
    [results]
  );

  const updateOption = (key) => {
    setOptions((previous) => ({
      ...previous,
      [key]: !previous[key]
    }));
  };

  const handleAnalyzeText = async () => {
    if (!content.trim()) {
      setError("Provide content to analyze.");
      return;
    }

    setError("");
    setIsLoading(true);
    try {
      const response = await fetch(`${apiBase}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          input_type: inputType,
          content,
          options
        })
      });

      if (!response.ok) {
        throw new Error("Analysis request failed.");
      }

      const payload = await response.json();
      setResults([payload]);
    } catch (requestError) {
      setError(requestError.message || "Unable to analyze the content.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyzeFiles = async (files) => {
    if (!files.length) {
      return;
    }

    setError("");
    setIsLoading(true);
    try {
      const formData = new FormData();
      files.forEach((file) => formData.append("files", file));
      formData.append("mask", options.mask);
      formData.append("block_high_risk", options.block_high_risk);
      formData.append("log_analysis", options.log_analysis);

      const response = await fetch(`${apiBase}/analyze/files`, {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        throw new Error("File analysis failed.");
      }

      const payload = await response.json();
      setResults(payload);
    } catch (requestError) {
      setError(requestError.message || "Unable to analyze uploaded files.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen px-4 py-6 sm:px-6 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <header className="mb-6 rounded-[32px] border border-white/50 bg-white/75 p-6 shadow-2xl shadow-slate-950/10 backdrop-blur md:p-8">
          <div className="flex flex-col gap-8 xl:flex-row xl:items-center xl:justify-between">
            <div className="max-w-3xl">
              <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-sky-200 bg-sky-50 px-4 py-2 text-xs font-semibold uppercase tracking-[0.28em] text-sky-700">
                <SparkIcon className="h-3.5 w-3.5" />
                AI Secure Data Intelligence Platform
              </div>
              <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
                Modern AI security review for logs, files, secrets, and risky content.
              </h1>
              <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-600 sm:text-base">
                Analyze documents, logs, SQL, and free text with an AI-assisted detection pipeline that identifies
                sensitive data, suspicious activity, and operational risk in a clean analyst-ready workspace.
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                <HeroPill label="AI Gateway" />
                <HeroPill label="Data Scanner" />
                <HeroPill label="Log Analyzer" />
                <HeroPill label="Risk Engine" />
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 xl:w-[360px]">
              <MetricCard label="Sources Analyzed" value={String(results.length)} tone="blue" icon={<LayersIcon />} />
              <MetricCard label="Findings" value={String(findingCount)} tone="medium" icon={<PulseIcon />} />
              <MetricCard
                label="Top Risk"
                value={(topResult?.risk_level || "none").toUpperCase()}
                tone={topResult?.risk_level || "blue"}
                icon={<ShieldIcon />}
              />
              <MetricCard label="API Status" value="LIVE" tone="blue" icon={<BoltIcon />} />
            </div>
          </div>
        </header>

        <main className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <section className="space-y-6">
            <Panel>
              <div className="mb-6 flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-700">Home Page</p>
                  <h2 className="mt-2 text-2xl font-semibold text-slate-950">Security Analysis Workspace</h2>
                  <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
                    Submit chat text, SQL snippets, logs, or operational notes for immediate analysis. The results
                    dashboard will score risk, surface findings, and explain anomalies.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setContent(quickSample)}
                  className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
                >
                  Load Sample
                </button>
              </div>

              <div className="mb-5 flex flex-wrap items-center gap-3">
                {["text", "chat", "log", "sql"].map((type) => (
                  <button
                    key={type}
                    type="button"
                    className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                      inputType === type
                        ? "bg-sky-600 text-white shadow-lg shadow-sky-600/20"
                        : "border border-slate-200 bg-white text-slate-600 hover:border-sky-200 hover:text-sky-700"
                    }`}
                    onClick={() => setInputType(type)}
                  >
                    {type.toUpperCase()}
                  </button>
                ))}
              </div>

              <label className="mb-3 flex items-center gap-2 text-sm font-medium text-slate-700">
                <DocumentIcon className="h-4 w-4 text-sky-600" />
                Text Input Area
              </label>
              <textarea
                value={content}
                onChange={(event) => setContent(event.target.value)}
                className="min-h-72 w-full rounded-[24px] border border-slate-200 bg-slate-50/70 p-5 text-sm leading-6 text-slate-800 outline-none transition focus:border-sky-400 focus:bg-white focus:shadow-lg focus:shadow-sky-100 placeholder:text-slate-400"
                placeholder="Paste text, logs, SQL, or chat content here for AI-assisted security analysis."
              />

              <div className="mt-5 flex flex-wrap gap-3">
                <ToggleChip label="Mask detected values" enabled={options.mask} onClick={() => updateOption("mask")} />
                <ToggleChip label="Block high risk" enabled={options.block_high_risk} onClick={() => updateOption("block_high_risk")} />
                <ToggleChip label="Log analysis enabled" enabled={options.log_analysis} onClick={() => updateOption("log_analysis")} />
              </div>

              <div className="mt-6 flex flex-wrap items-center gap-4">
                <button
                  type="button"
                  onClick={handleAnalyzeText}
                  disabled={isLoading}
                  className="inline-flex items-center gap-2 rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-slate-950/15 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  <ScanIcon className="h-4 w-4" />
                  {isLoading ? "Analyzing..." : "Analyze Content"}
                </button>
                <p className="text-sm text-slate-500">
                  Connected to <span className="font-medium text-slate-700">{apiBase}</span>
                </p>
              </div>

              {error ? (
                <div className="mt-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {error}
                </div>
              ) : null}
            </Panel>

            <Panel>
              <div className="mb-4 flex items-center gap-2">
                <UploadIcon className="h-5 w-5 text-sky-600" />
                <div>
                  <h2 className="text-xl font-semibold text-slate-950">Upload Section</h2>
                  <p className="text-sm text-slate-600">Drag, drop, and batch-analyze documents and log files.</p>
                </div>
              </div>
              <UploadBox onFilesSelected={handleAnalyzeFiles} disabled={isLoading} />
            </Panel>
          </section>

          <section className="space-y-6">
            <Panel>
              <div className="mb-4 flex items-center gap-2">
                <DashboardIcon className="h-5 w-5 text-sky-600" />
                <div>
                  <h2 className="text-xl font-semibold text-slate-950">Results Dashboard</h2>
                  <p className="text-sm text-slate-600">Risk score, findings, masked content, and AI insights.</p>
                </div>
              </div>
              <ResultPanel results={results} />
            </Panel>

            <Panel>
              <InsightsPanel insights={topResult?.insights || []} summary={topResult?.summary || ""} />
            </Panel>
          </section>
        </main>

        <div className="mt-6">
          <Panel>
            <LogViewer results={results} />
          </Panel>
        </div>
      </div>
    </div>
  );
}

function Panel({ children }) {
  return <section className="rounded-[32px] border border-white/60 bg-white/80 p-6 shadow-2xl shadow-slate-950/10 backdrop-blur">{children}</section>;
}

function HeroPill({ label }) {
  return (
    <span className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm">
      {label}
    </span>
  );
}

function MetricCard({ label, value, tone, icon }) {
  const tones = {
    blue: "border-sky-100 bg-sky-50 text-sky-700",
    low: "border-sky-100 bg-sky-50 text-sky-700",
    medium: "border-amber-100 bg-amber-50 text-amber-700",
    high: "border-red-100 bg-red-50 text-red-700",
    critical: "border-red-900 bg-red-950 text-red-100"
  };

  return (
    <div className={`rounded-[24px] border p-4 shadow-sm ${tones[tone] || tones.blue}`}>
      <div className="mb-3 flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-[0.2em]">{label}</span>
        <span className="rounded-xl bg-white/60 p-2">{icon}</span>
      </div>
      <p className="text-2xl font-semibold tracking-tight">{value}</p>
    </div>
  );
}

function ToggleChip({ label, enabled, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-full px-4 py-2 text-sm font-medium transition ${
        enabled
          ? "bg-sky-100 text-sky-700 ring-1 ring-sky-200"
          : "border border-slate-200 bg-white text-slate-600 hover:border-slate-300"
      }`}
    >
      {label}
    </button>
  );
}

function iconProps(className) {
  return {
    className,
    fill: "none",
    stroke: "currentColor",
    viewBox: "0 0 24 24",
    strokeWidth: "1.8"
  };
}

function SparkIcon({ className }) {
  return (
    <svg {...iconProps(className)}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 3l1.6 4.4L18 9l-4.4 1.6L12 15l-1.6-4.4L6 9l4.4-1.6L12 3zM5 16l.8 2.2L8 19l-2.2.8L5 22l-.8-2.2L2 19l2.2-.8L5 16zm14-1l1 2.6L23 19l-3 1-1 3-1-3-3-1 3-1 1-3z" />
    </svg>
  );
}

function LayersIcon() {
  return (
    <svg {...iconProps("h-4 w-4")}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4l8 4-8 4-8-4 8-4zm8 8-8 4-8-4m16 4-8 4-8-4" />
    </svg>
  );
}

function PulseIcon() {
  return (
    <svg {...iconProps("h-4 w-4")}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 12h4l2-5 4 10 2-5h6" />
    </svg>
  );
}

function ShieldIcon() {
  return (
    <svg {...iconProps("h-4 w-4")}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 3l7 3v5c0 5-3.5 8.5-7 10-3.5-1.5-7-5-7-10V6l7-3z" />
    </svg>
  );
}

function BoltIcon() {
  return (
    <svg {...iconProps("h-4 w-4")}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M13 2L4 14h6l-1 8 9-12h-6l1-8z" />
    </svg>
  );
}

function DocumentIcon({ className }) {
  return (
    <svg {...iconProps(className)}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M8 3h6l5 5v11a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M14 3v5h5" />
    </svg>
  );
}

function ScanIcon({ className }) {
  return (
    <svg {...iconProps(className)}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 7V5a1 1 0 0 1 1-1h2m8 0h2a1 1 0 0 1 1 1v2M4 17v2a1 1 0 0 0 1 1h2m8 0h2a1 1 0 0 0 1-1v-2M7 12h10" />
    </svg>
  );
}

function UploadIcon({ className }) {
  return (
    <svg {...iconProps(className)}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 16V4m0 0-4 4m4-4 4 4M5 16v2a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-2" />
    </svg>
  );
}

function DashboardIcon({ className }) {
  return (
    <svg {...iconProps(className)}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 13h6V5H4v8zm10 6h6V5h-6v14zM4 19h6v-4H4v4zm10-8h6v-2h-6v2z" />
    </svg>
  );
}

export default App;
