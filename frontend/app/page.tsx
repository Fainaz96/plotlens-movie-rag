"use client";

import {
  ArrowUpRight,
  Check,
  ChevronRight,
  CircleAlert,
  Clipboard,
  Database,
  Film,
  Layers3,
  LoaderCircle,
  Search,
  Sparkles,
} from "lucide-react";
import Image from "next/image";
import { FormEvent, useEffect, useMemo, useState } from "react";

type ServiceStatus = "initializing" | "ready" | "failed" | "offline";

type Health = {
  status: Exclude<ServiceStatus, "offline">;
  indexed_movies: number;
  indexed_chunks: number;
  chat_model: string;
  embedding_model: string;
  message: string | null;
};

type Context = {
  title: string;
  snippet: string;
  score: number;
  chunk_id: string;
};

type QueryResult = {
  answer: string;
  contexts: Context[];
  reasoning: string;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "/backend";

const EXAMPLES = [
  "Which movie features the HAL 9000 computer?",
  "What happens when Marty McFly travels to 1955?",
  "Which film follows a police chief hunting a great white shark?",
];

const PIPELINE = ["Question", "Retrieve", "Ground", "Answer"];

function errorMessage(payload: unknown, fallback: string): string {
  if (!payload || typeof payload !== "object" || !("detail" in payload)) return fallback;
  const detail = (payload as { detail: unknown }).detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail[0] && typeof detail[0].msg === "string") {
    return detail[0].msg.replace(/^Value error, /, "");
  }
  return fallback;
}

function RagScene({ active }: { active: boolean }) {
  return (
    <div className={`rag-scene ${active ? "scene-active" : ""}`} aria-hidden="true">
      <div className="scene-glow" />
      <div className="orbit orbit-one"><span /></div>
      <div className="orbit orbit-two"><span /></div>
      <div className="orbit orbit-three"><span /></div>
      <div className="core-cube">
        <div className="cube-face cube-front"><Search size={26} /><span>RAG</span></div>
        <div className="cube-face cube-back"><Database size={24} /><span>612</span></div>
        <div className="cube-face cube-right"><Layers3 size={24} /><span>TOP 5</span></div>
        <div className="cube-face cube-left"><Film size={24} /><span>300</span></div>
        <div className="cube-face cube-top" />
        <div className="cube-face cube-bottom" />
      </div>
      <div className="float-card float-query"><span>01</span> Question embedded</div>
      <div className="float-card float-context"><span>02</span> Evidence retrieved</div>
      <div className="float-card float-answer"><Check size={13} /> Grounded answer</div>
      <div className="scene-floor" />
    </div>
  );
}

export default function Home() {
  const [query, setQuery] = useState(EXAMPLES[0]);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [serviceStatus, setServiceStatus] = useState<ServiceStatus>("initializing");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"evidence" | "json">("evidence");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let alive = true;
    const checkHealth = async () => {
      try {
        const response = await fetch(`${API_URL}/health`, { cache: "no-store" });
        if (!response.ok) throw new Error("Health request failed");
        const payload = (await response.json()) as Health;
        if (alive) {
          setHealth(payload);
          setServiceStatus(payload.status);
        }
      } catch {
        if (alive) setServiceStatus("offline");
      }
    };
    void checkHealth();
    const timer = window.setInterval(checkHealth, 4000);
    return () => {
      alive = false;
      window.clearInterval(timer);
    };
  }, []);

  const rawJson = useMemo(() => (result ? JSON.stringify(result, null, 2) : ""), [result]);

  async function submit(event?: FormEvent) {
    event?.preventDefault();
    const trimmed = query.trim();
    if (trimmed.length < 3) {
      setError("Enter a question with at least three characters.");
      return;
    }

    setLoading(true);
    setError(null);
    setCopied(false);
    try {
      const response = await fetch(`${API_URL}/api/v1/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: trimmed, top_k: 5 }),
      });
      const payload: unknown = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(errorMessage(payload, "PlotLens could not answer that question."));
      }
      setResult(payload as QueryResult);
      setActiveTab("evidence");
    } catch (caught) {
      setError(
        caught instanceof TypeError
          ? "The API is unreachable. Start the backend and try again."
          : caught instanceof Error
            ? caught.message
            : "Something went wrong. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function copyJson() {
    await navigator.clipboard.writeText(rawJson);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  }

  const statusLabel =
    serviceStatus === "ready"
      ? `${health?.indexed_movies ?? 0} films indexed`
      : serviceStatus === "initializing"
        ? "Building movie index"
        : serviceStatus === "failed"
          ? "Index unavailable"
          : "API offline";

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="PlotLens home">
          <span className="plotlens-mark"><Film size={17} strokeWidth={2.3} /></span>
          <span className="brand-name">PlotLens</span>
        </a>
        <div className="built-for">
          <span>Built for</span>
          <a href="https://www.typeb.digital/" target="_blank" rel="noreferrer" aria-label="Type B Digital website">
            <Image src="/type-b-mark.png" alt="Type B Digital" width={28} height={28} priority />
            <strong>TYPE B DIGITAL</strong>
          </a>
        </div>
        <div className={`status-pill status-${serviceStatus}`}>
          <span className="status-dot" aria-hidden="true" />
          {statusLabel}
        </div>
      </header>

      <section className="hero" id="top">
        <div className="hero-content">
          <div className="eyebrow"><Sparkles size={14} /> Applied AI · Take-home prototype</div>
          <h1>Find the story.<br /><em>Verify the answer.</em></h1>
          <p className="hero-copy">
            A transparent movie intelligence experience that turns semantic retrieval into clear,
            evidence-backed answers.
          </p>
          <div className="hero-meta">
            <span><strong>300</strong> films</span>
            <span><strong>612</strong> passages</span>
            <span><strong>Top 5</strong> evidence</span>
          </div>
        </div>
        <RagScene active={loading || Boolean(result)} />
      </section>

      <section className="pipeline" aria-label="RAG pipeline">
        <div className="pipeline-title">How it works</div>
        <div className="pipeline-flow">
          {PIPELINE.map((step, index) => (
            <div className="pipeline-group" key={step}>
              <div className={`pipeline-step ${result || (loading && index < 2) ? "pipeline-active" : ""}`}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                {step}
              </div>
              {index < PIPELINE.length - 1 && <ChevronRight size={15} aria-hidden="true" />}
            </div>
          ))}
        </div>
        <span className="pipeline-note">Structured JSON out</span>
      </section>

      <section className="workspace" aria-label="Movie plot search">
        <div className="query-column">
          <div className="section-label"><Search size={15} /> Ask the archive</div>
          <h2>What do you want to know?</h2>
          <p className="section-intro">Ask about a character, event, setting, or plot detail.</p>
          <form onSubmit={submit} className="query-form">
            <textarea
              aria-label="Ask a movie plot question"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              onKeyDown={(event) => {
                if ((event.ctrlKey || event.metaKey) && event.key === "Enter") void submit();
              }}
              maxLength={500}
              placeholder="Ask a movie plot question..."
              rows={5}
            />
            <div className="form-footer">
              <span>{query.length}/500 · Ctrl + Enter</span>
              <button className="ask-button" type="submit" disabled={loading || serviceStatus !== "ready"}>
                {loading ? <LoaderCircle className="spin" size={18} /> : <ArrowUpRight size={18} />}
                {loading ? "Retrieving" : "Ask PlotLens"}
              </button>
            </div>
          </form>

          {error && (
            <div className="error-message" role="alert">
              <CircleAlert size={18} />
              <div><strong>Couldn&apos;t complete the search</strong><span>{error}</span></div>
            </div>
          )}

          <div className="example-block">
            <p>Try an example</p>
            <div className="example-list">
              {EXAMPLES.map((example) => (
                <button key={example} onClick={() => setQuery(example)} type="button">
                  <span>{example}</span><ArrowUpRight size={15} />
                </button>
              ))}
            </div>
          </div>

          <div className="index-note">
            <Database size={18} />
            <div>
              <strong>{health?.indexed_chunks ?? "—"} searchable plot passages</strong>
              <span>OpenAI embeddings · Chroma cosine search · Top 5 retrieval</span>
            </div>
          </div>
        </div>

        <div className="result-column" aria-live="polite">
          {loading ? (
            <div className="loading-state">
              <div className="search-orbit"><Search size={22} /></div>
              <strong>Searching the story archive</strong>
              <span>Embedding your question and ranking the closest plot passages...</span>
            </div>
          ) : result ? (
            <>
              <div className="answer-card">
                <div className="section-label"><Sparkles size={15} /> Grounded answer</div>
                <p>{result.answer}</p>
              </div>

              <div className="result-tabs" role="tablist" aria-label="Result details">
                <button type="button" role="tab" aria-selected={activeTab === "evidence"} className={activeTab === "evidence" ? "active" : ""} onClick={() => setActiveTab("evidence")}>
                  Retrieved evidence <span>{result.contexts.length}</span>
                </button>
                <button type="button" role="tab" aria-selected={activeTab === "json"} className={activeTab === "json" ? "active" : ""} onClick={() => setActiveTab("json")}>
                  Raw JSON
                </button>
              </div>

              {activeTab === "evidence" ? (
                <div className="evidence-stack">
                  {result.contexts.map((context, index) => (
                    <article className="evidence-card" key={context.chunk_id}>
                      <div className="evidence-heading">
                        <span className="rank">{String(index + 1).padStart(2, "0")}</span>
                        <div><h2>{context.title}</h2><span>Wikipedia plot · {context.chunk_id.slice(0, 8)}</span></div>
                        <div className="score"><strong>{Math.round(context.score * 100)}%</strong><span>match</span></div>
                      </div>
                      <p>{context.snippet}</p>
                    </article>
                  ))}
                  <div className="reasoning-card">
                    <span>Evidence rationale</span>
                    <p>{result.reasoning}</p>
                  </div>
                </div>
              ) : (
                <div className="json-card">
                  <button type="button" onClick={copyJson} className="copy-button">
                    {copied ? <Check size={15} /> : <Clipboard size={15} />}
                    {copied ? "Copied" : "Copy JSON"}
                  </button>
                  <pre>{rawJson}</pre>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">
              <div className="empty-illustration">
                <div className="film-frame frame-one" />
                <div className="film-frame frame-two" />
                <Search size={26} />
              </div>
              <div>
                <span className="empty-kicker">Ready to retrieve</span>
                <h2>Every answer starts with evidence.</h2>
                <p>Ask a question to see the generated answer, retrieved passages, similarity scores, and exact structured response.</p>
              </div>
              <div className="proof-points">
                <span><Check size={14} /> Grounded claims</span>
                <span><Check size={14} /> Visible sources</span>
                <span><Check size={14} /> Structured output</span>
              </div>
            </div>
          )}
        </div>
      </section>

      <footer>
        <div className="footer-brand">
          <Image src="/type-b-mark.png" alt="Type B Digital" width={30} height={30} />
          <div><strong>PlotLens</strong><span>Created for Type B Digital</span></div>
        </div>
        <span>FastAPI · Next.js · OpenAI · Chroma</span>
        <a href="https://www.typeb.digital/" target="_blank" rel="noreferrer">typeb.digital <ArrowUpRight size={13} /></a>
      </footer>
    </main>
  );
}
