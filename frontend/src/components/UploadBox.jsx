function UploadBox({ onFilesSelected, disabled }) {
  const handleFiles = (fileList) => {
    const files = Array.from(fileList || []);
    if (files.length) {
      onFilesSelected(files);
    }
  };

  return (
    <div
      onDragEnter={(event) => event.preventDefault()}
      onDragLeave={(event) => event.preventDefault()}
      onDragOver={(event) => event.preventDefault()}
      onDrop={(event) => {
        event.preventDefault();
        handleFiles(event.dataTransfer.files);
      }}
      className="rounded-[28px] border border-dashed border-sky-200 bg-gradient-to-br from-sky-50 to-white p-6 shadow-sm"
    >
      <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
        <div className="max-w-xl">
          <div className="mb-3 inline-flex rounded-2xl bg-sky-100 p-3 text-sky-700">
            <UploadGlyph />
          </div>
          <h3 className="text-lg font-semibold text-slate-950">Drag and drop upload box</h3>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Upload PDF, DOCX, TXT, LOG, or SQL files for batch scanning. The platform extracts content,
            evaluates risk, and surfaces findings in the dashboard.
          </p>
        </div>

        <label className="inline-flex cursor-pointer items-center justify-center rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-slate-950/15 transition hover:bg-slate-800">
          Choose Files
          <input
            type="file"
            multiple
            accept=".pdf,.docx,.txt,.log,.sql"
            className="hidden"
            disabled={disabled}
            onChange={(event) => handleFiles(event.target.files)}
          />
        </label>
      </div>
    </div>
  );
}

function UploadGlyph() {
  return (
    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.8">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 16V5m0 0-4 4m4-4 4 4M5 16v2a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-2" />
    </svg>
  );
}

export default UploadBox;
