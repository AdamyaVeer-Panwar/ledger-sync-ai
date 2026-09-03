import Link from "next/link";
import type { ReactNode } from "react";

type AppShellProps = {
  children: ReactNode;
};

const navigation = [
  ["01", "RUN", "/run"],
  ["02", "EXCEPTIONS", "/exceptions"],
  ["03", "EVALUATION", "/evaluation"],
  ["04", "ENGINEERING", "/engineering"],
] as const;

export function AppShell({
  children,
}: AppShellProps) {
  return (
    <div className="min-h-screen bg-[var(--canvas)] text-[var(--ink)]">
      <header className="border-b border-[var(--border-dark)] bg-[var(--navy)] text-white">
        <div className="mx-auto flex max-w-[1680px] items-center justify-between px-5 py-4 sm:px-7">
          <Link
            href="/"
            className="flex items-center gap-3"
          >
            <div className="grid h-9 w-9 place-items-center border border-[var(--copper)] bg-[var(--navy-2)] font-mono text-sm font-bold text-[var(--copper)]">
              L
            </div>

            <div>
              <div className="font-mono text-sm font-semibold tracking-[0.27em]">
                LEDGERSYNC
              </div>

              <div className="mt-1 font-mono text-[8px] tracking-[0.18em] text-[#9EABB9]">
                FINANCIAL RECONCILIATION CONTROL
              </div>
            </div>
          </Link>

          <div className="flex items-center gap-2.5 font-mono text-[9px] tracking-[0.15em] text-[#C7D0D8]">
            <span className="h-2.5 w-2.5 rounded-full bg-[var(--lime)]" />
            SYSTEM READY
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-[1680px] grid-cols-1 lg:grid-cols-[240px_1fr]">
        <aside className="bg-[var(--navy)] text-white lg:min-h-[calc(100vh-73px)] lg:border-r lg:border-[var(--border-dark)]">
          <div className="flex h-full flex-col">
            <nav className="p-4 sm:p-5">
              <div className="px-3 py-2 font-mono text-[8px] tracking-[0.22em] text-[#718196]">
                WORKSPACE
              </div>

              <div className="mt-2 space-y-1">
                {navigation.map(
                  ([index, label, href]) => (
                    <Link
                      key={href}
                      href={href}
                      className="group flex items-center gap-3 border border-transparent px-3 py-3.5 transition-colors hover:border-[var(--navy-3)] hover:bg-[var(--navy-2)]"
                    >
                      <span className="font-mono text-[9px] text-[#718196] group-hover:text-[var(--copper)]">
                        {index}
                      </span>

                      <span className="font-mono text-[10px] tracking-[0.15em] text-[#D1D8DF] group-hover:text-white">
                        {label}
                      </span>

                      <span className="ml-auto text-[#65778A] opacity-0 transition-opacity group-hover:opacity-100">
                        →
                      </span>
                    </Link>
                  ),
                )}
              </div>
            </nav>

            <div className="mt-auto border-t border-[var(--border-dark)] p-5">
              <div className="font-mono text-[8px] tracking-[0.22em] text-[#718196]">
                SYSTEM
              </div>

              <div className="mt-5 space-y-3 font-mono text-[9px]">
                <StatusRow
                  label="API"
                  value="ONLINE"
                  tone="text-[var(--lime)]"
                />

                <StatusRow
                  label="ENGINE"
                  value="READY"
                  tone="text-[var(--lime)]"
                />

                <StatusRow
                  label="AI"
                  value="AVAILABLE"
                  tone="text-[#72B8D0]"
                />

                <StatusRow
                  label="OBS"
                  value="ONLINE"
                  tone="text-[var(--lime)]"
                />
              </div>

              <div className="mt-7 border-t border-[var(--border-dark)] pt-5 font-mono text-[8px] leading-5 tracking-[0.08em] text-[#66778A]">
                SAFE AUTOMATION
                <br />
                REQUIRES VERIFIED EVIDENCE
              </div>
            </div>
          </div>
        </aside>

        <main className="min-w-0 bg-[var(--canvas)] p-5 sm:p-7 lg:p-10">
          {children}
        </main>
      </div>
    </div>
  );
}

function StatusRow({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: string;
}) {
  return (
    <div className="flex items-center">
      <span className="w-16 text-[#718196]">
        {label}
      </span>

      <span className="mr-2 text-[#556678]">
        ···
      </span>

      <span className={tone}>{value}</span>
    </div>
  );
}