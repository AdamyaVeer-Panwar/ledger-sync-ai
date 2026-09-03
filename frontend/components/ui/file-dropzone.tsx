"use client";

import {
  ChangeEvent,
  DragEvent,
  KeyboardEvent,
  useRef,
  useState,
} from "react";

type FileDropzoneProps = {
  label: string;
  description: string;
  file: File | null;
  onFileChange: (file: File | null) => void;
  accept?: string;
};

export function FileDropzone({
  label,
  description,
  file,
  onFileChange,
  accept = ".csv,.json",
}: FileDropzoneProps) {
  const inputRef =
    useRef<HTMLInputElement>(null);

  const [dragging, setDragging] =
    useState(false);

  function openFilePicker() {
    inputRef.current?.click();
  }

  function handleInputChange(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    const selectedFile =
      event.target.files?.[0] ?? null;

    onFileChange(selectedFile);
  }

  function handleDrop(
    event: DragEvent<HTMLDivElement>,
  ) {
    event.preventDefault();
    setDragging(false);

    const droppedFile =
      event.dataTransfer.files?.[0] ?? null;

    onFileChange(droppedFile);
  }

  function handleKeyDown(
    event: KeyboardEvent<HTMLDivElement>,
  ) {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openFilePicker();
    }
  }

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <span className="font-mono text-[8px] font-semibold tracking-[0.16em] text-[var(--ink)]">
          {label}
        </span>

        <span className="font-mono text-[8px] tracking-[0.11em] text-[var(--ink-muted)]">
          CSV / JSON
        </span>
      </div>

      <div
        role="button"
        tabIndex={0}
        onClick={openFilePicker}
        onKeyDown={handleKeyDown}
        onDragEnter={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => {
          setDragging(false);
        }}
        onDrop={handleDrop}
        className={[
          "relative cursor-pointer border p-5 transition-all",
          dragging
            ? "border-[var(--copper)] bg-[var(--copper-soft)]"
            : file
              ? "border-[var(--lime)] bg-[var(--lime-soft)]"
              : "border-dashed border-[var(--border-strong)] bg-[var(--surface-soft)] hover:border-[var(--copper)] hover:bg-[var(--copper-soft)]",
        ].join(" ")}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleInputChange}
          className="hidden"
        />

        {file ? (
          <SelectedFile
            file={file}
            onRemove={() => onFileChange(null)}
          />
        ) : (
          <EmptyState
            description={description}
          />
        )}
      </div>
    </div>
  );
}

function EmptyState({
  description,
}: {
  description: string;
}) {
  return (
    <div className="flex items-center justify-between gap-5">
      <div>
        <div className="font-mono text-[9px] font-semibold tracking-[0.15em] text-[var(--ink)]">
          DROP FILE HERE
        </div>

        <div className="mt-2 text-xs text-[var(--ink-muted)]">
          {description}
        </div>
      </div>

      <div className="hidden border border-[var(--border)] bg-[var(--surface)] px-3 py-2 font-mono text-[8px] font-semibold tracking-[0.12em] text-[var(--ink-soft)] sm:block">
        BROWSE
      </div>
    </div>
  );
}

function SelectedFile({
  file,
  onRemove,
}: {
  file: File;
  onRemove: () => void;
}) {
  return (
    <div className="flex items-center justify-between gap-4">
      <div className="flex min-w-0 items-center gap-3">
        <div className="grid h-9 w-9 shrink-0 place-items-center border border-[var(--lime)] bg-[var(--surface)] font-mono text-[9px] font-semibold text-[var(--lime)]">
          ✓
        </div>

        <div className="min-w-0">
          <div className="truncate font-mono text-[10px] font-semibold text-[var(--ink)]">
            {file.name}
          </div>

          <div className="mt-1 font-mono text-[8px] tracking-[0.08em] text-[var(--ink-muted)]">
            {formatBytes(file.size)} · READY
          </div>
        </div>
      </div>

      <button
        type="button"
        onClick={(event) => {
          event.stopPropagation();
          onRemove();
        }}
        className="shrink-0 border border-[var(--border)] bg-[var(--surface)] px-2.5 py-2 font-mono text-[8px] font-semibold tracking-[0.1em] text-[var(--ink-muted)] hover:border-[var(--red)] hover:text-[var(--red)]"
      >
        REMOVE
      </button>
    </div>
  );
}

function formatBytes(bytes: number): string {
  if (bytes === 0) {
    return "0 B";
  }

  const units = [
    "B",
    "KB",
    "MB",
    "GB",
  ];

  const index = Math.min(
    Math.floor(Math.log(bytes) / Math.log(1024)),
    units.length - 1,
  );

  const value =
    bytes / 1024 ** index;

  return `${value.toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}