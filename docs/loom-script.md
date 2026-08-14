# Two-minute Loom walkthrough

Keep the browser at the PlotLens homepage and the repository open beside it. Start a timer.

## 0:00–0:20 — Goal

> “PlotLens is a compact RAG system over 300 Wikipedia movie plots. The design goal is not just to answer a question, but to make the retrieval evidence and exact structured response visible to the reviewer.”

Find the story. Verify the answer.

## 0:20–0:55 — Pipeline

Open the architecture diagram in the README.

> “A fixed-seed preparation script cleans the source dataset. Plots are split into 300-word chunks with 50-word overlap and stable IDs. OpenAI embeddings are cached against the dataset and model fingerprint, then loaded into ephemeral Chroma. A query retrieves the five closest passages. The Responses API produces a validated answer and evidence rationale, while contexts are attached by the server from the actual retrieval results.”

Briefly show `backend/app/service.py` and `backend/app/provider.py`—do not scroll through every file.

## 0:55–1:45 — Live query

Ask: **Which movie features the HAL 9000 computer?**

> “The direct answer appears first. Below it are the retrieved movie, exact plot snippet, similarity score, and stable chunk ID. The evidence rationale states the supporting fact without asking the model for private chain-of-thought.”

Click **Raw JSON**, then **Copy JSON**.

> “This is the assignment’s required contract: answer, contexts, and reasoning. Importantly, the model cannot manufacture the contexts because the backend constructs them after retrieval.”

## 1:45–2:00 — Verification and trade-offs

Show the README quality section.

> “The project has deterministic offline tests, a ten-question Recall@5 evaluation, strict backend and frontend checks, and Docker setup. I intentionally kept Chroma in memory and excluded auth, agents, reranking, and chat history so the submission stays focused on a clear, testable RAG path.”

End on the evidence view.

