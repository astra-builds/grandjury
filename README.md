<div align="center">

# grandjury

<!--
  GROWTH TEAM: tagline below is editable — A/B test framings as needed.
  Numbers (25K reviews, 200+ reviewers, 58 models, 44 benchmarks) reflect
  production DB at last edit time; refresh on rewrite. Keep the model
  names current as the leaderboard evolves.
-->
> Real human evaluations of AI models. **25,000+ blind reviews** by **200+ verified reviewers** across **58 models** (GPT-5, Claude Opus 4.7, Gemini 3.1, Grok 4.3, DeepSeek V4, Mistral, Kimi K2.6 and more) and **44 benchmarks**. Free. Python SDK + MCP server + ChatGPT GPT + REST.

[![PyPI](https://img.shields.io/pypi/v/grandjury?style=flat-square&color=blue)](https://pypi.org/project/grandjury/)
[![Python](https://img.shields.io/pypi/pyversions/grandjury?style=flat-square&color=blue)](https://pypi.org/project/grandjury/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-humanjudge.com-blue?style=flat-square)](https://humanjudge.com/docs)
[![Discord](https://img.shields.io/badge/Discord-Join-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.gg/vw43ufYmDH)
[![Berkeley RDI](https://img.shields.io/badge/Berkeley_RDI-Aug_1--2_2026-003262?style=flat-square)](https://rdi.berkeley.edu/)

**[Install the SDK ↓](#installation) · [Join the R&D community ↓](#research-community)**

</div>

---

Get human feedback on your AI in 3 lines of Python:

```python
from grandjury import GrandJury

gj = GrandJury()  # reads GRANDJURY_API_KEY from env
gj.trace(name="chat", input=prompt, output=response, model="gpt-4o")
```

Then open your Jupyter notebook:

```python
df = gj.results()  # traces with human votes — as a DataFrame
print(f"Pass rate: {df['pass_rate'].mean():.1%}")
```

**Patent Pending.**

## Why HumanJudge

Most AI evaluation pipelines use LLMs to judge LLMs. That inherits the same biases, conventions, and blind spots as the models being evaluated — and tends to produce eval pipelines with ~0% disagreement, which is the diagnostic for "not measuring quality, just confirming assumptions" ([essay](https://humanjudge.com/ai-reviews/your-eval-pipeline-has-zero-disagreement)).

HumanJudge uses **real human reviewers** who blind-evaluate AI outputs across structured benchmarks (marketing, healthcare, end-of-life conversations, cultural fluency, code review, and more) and write their reasoning. Reviewers earn XP, get credentialing letters, and stay anonymous to the reader by default.

The data is queryable via this SDK, the [MCP server](https://humanjudge.com/docs/pulse/claude-desktop), a [ChatGPT GPT action](https://humanjudge.com/docs/pulse/chatgpt), and a REST API.

## Integrations

| Surface | Install | Docs |
|---|---|---|
| **Python SDK** | `pip install grandjury` | [docs/pulse/python-sdk](https://humanjudge.com/docs/pulse/python-sdk) |
| **Claude Desktop MCP** | Add `https://api.humanjudge.com/mcp` as a custom connector | [docs/pulse/claude-desktop](https://humanjudge.com/docs/pulse/claude-desktop) |
| **Claude Code MCP** | Add to `.mcp.json` (remote, no install) | [docs/pulse/claude-code](https://humanjudge.com/docs/pulse/claude-code) |
| **ChatGPT GPT** | Search "HumanJudge" in the GPT Store | [docs/pulse/chatgpt](https://humanjudge.com/docs/pulse/chatgpt) |
| **REST API** | n/a | [humanjudge.com/docs](https://humanjudge.com/docs) |

## Use cases

- **ML engineers** — benchmark your model against 58+ commercial models on real tasks; see exactly what humans flag with category + reasoning
- **Data scientists** — pull reviewer reasoning, flag patterns, and disagreement data as pandas DataFrames for analysis
- **AI agent developers** — log traces from any agent loop (decorator, context manager, or direct call); get reviewer feedback you can quote to stakeholders
- **Independent researchers** — query the public benchmark data without an API key (read-only)
- **Builders** — register your own AI, create a custom benchmark on the topics you care about, get real human reviews on YOUR specific use case ([humanjudge.com/for-developers](https://humanjudge.com/for-developers))

## What is GrandJury?

[HumanJudge](https://humanjudge.com) connects your AI to a community of human reviewers who evaluate your model's outputs. GrandJury is the Python SDK — it sends traces and retrieves human evaluation results.

**Write path:** Log AI calls from your app → traces appear in your developer dashboard.
**Read path:** Fetch evaluation results (votes, pass rates, reviewer feedback) into DataFrames for analysis.

## Installation

```bash
pip install grandjury
```

Optional performance dependencies:
```bash
pip install grandjury[performance]  # msgspec, pyarrow, polars
```

## Quick Start

### 1. Register your model

Go to [humanjudge.com/projects/new](https://humanjudge.com/projects/new), register your AI, and copy the secret key.

```bash
export GRANDJURY_API_KEY=gj_sk_live_...
```

### 2. Log traces from your app

```python
from grandjury import GrandJury

gj = GrandJury()  # zero-config — reads from env

# Option A: Direct call
gj.trace(name="chat", input="What is ML?", output="Machine learning is...", model="gpt-4o")

# Option B: Decorator — auto-captures input/output/latency
@gj.observe(name="chat", model="gpt-4o")
def call_llm(prompt: str) -> str:
    return openai.chat(prompt)

# Option C: Context manager
with gj.span("chat", input=prompt) as s:
    response = call_llm(prompt)
    s.set_output(response)
```

### 3. Get human evaluation results

Once reviewers vote on your traces:

```python
# Trace-level summary
df = gj.results()
# trace_id | input | output | model | pass_count | flag_count | total_votes | pass_rate

# Individual votes with reviewer identity
df_votes = gj.results(detail='votes')
# trace_id | voter_id | voter_name | verdict | flag_category | feedback | created_at

# Filter by benchmark
df_benchmark = gj.results(evaluation='marketing-benchmark')

# Export
df.to_parquet('evaluation_results.parquet')
```

### 4. Run analytics

Works on both live platform data and offline datasets:

```python
# Auto-fetch from platform
gj.analytics.vote_histogram()
gj.analytics.population_confidence(voter_list=[...])

# Or pass your own data
import pandas as pd
df = pd.read_csv("my_votes.csv")
gj.analytics.vote_histogram(df)
gj.analytics.votes_distribution(df)
```

## Enroll in Benchmarks

List and enroll your model in open benchmarks programmatically:

```python
# Browse available benchmarks
benchmarks = gj.benchmarks.list()

# Enroll with endpoint config
gj.benchmarks.enroll(
    benchmark_id="...",
    model_id="...",
    endpoint_config={
        "endpoint": "https://api.myapp.com/v1/chat/completions",
        "apiKey": "sk-...",
        "request_template": '{"model":"gpt-4o","messages":[{"role":"user","content":"{{prompt}}"}]}',
        "response_path": "choices[0].message.content"
    }
)
```

## Analytics Methods

All analytics methods work on both platform data (`gj.results(detail='votes')`) and offline data (pandas/polars/CSV/parquet):

| Method | Description |
|---|---|
| `gj.analytics.evaluate_model()` | Decay-adjusted scoring |
| `gj.analytics.vote_histogram()` | Vote time distribution |
| `gj.analytics.vote_completeness()` | Completeness per voter |
| `gj.analytics.population_confidence()` | Confidence metrics |
| `gj.analytics.majority_good_votes()` | Threshold analysis |
| `gj.analytics.votes_distribution()` | Votes per inference |

## Privacy

- `gj.results()` only returns traces with at least 1 human vote (privacy gate)
- Zero-vote traces are invisible to the SDK — only visible on the web dashboard
- Reviewer identity is public (consistent with platform's public profile/leaderboard model)

## API Reference

```python
gj = GrandJury(
    api_key=None,     # reads GRANDJURY_API_KEY from env if not provided
    base_url="https://grandjury-server.onrender.com",
    timeout=5.0,
)

# Write
gj.trace(name, input, output, model, latency_ms, metadata, gj_inference_id)
await gj.atrace(...)  # async version (requires httpx)
gj.observe(name, model, metadata)  # decorator
gj.span(name, input, model, metadata)  # context manager

# Read
gj.results(detail=None, evaluation=None)  # returns DataFrame or list[dict]

# Browse
gj.models.list()
gj.models.get(model_id)
gj.benchmarks.list()
gj.benchmarks.enroll(benchmark_id, model_id, endpoint_config)

# Analytics
gj.analytics.evaluate_model(...)
gj.analytics.vote_histogram(data=None, ...)
gj.analytics.vote_completeness(data=None, voter_list=None, ...)
gj.analytics.population_confidence(data=None, voter_list=None, ...)
gj.analytics.majority_good_votes(data=None, ...)
gj.analytics.votes_distribution(data=None, ...)
```

## Research community

Our center of gravity is **post-deployment evaluation**. We treat live evaluation as a **datastream, not a fixed dataset** — capturing pluralistic, multi-user, multi-context feedback continuously, and keeping the signal rich rather than collapsing it to a single score. Anchored at the [Berkeley RDI Agentic AI Summit, Aug 1–2 2026](https://rdi.berkeley.edu/) (confirmed poster presenter spot).

Six research streams below. Pick by interest, not assignment.

### The streams

<details>
<summary><b>Stream 0 — Applied training bridge</b> · for alignment researchers, preference-optimization specialists, multi-objective RL folks</summary>

The optimizers are solved (KTO, DPO, GRPO, MOPO via [Hugging Face TRL](https://github.com/huggingface/trl)). The **aggregation rule** across multi-dimensional pluralistic signal isn't.

Standard multi-objective RLHF defaults to weighted sum — which lets a model trade dimensions off. We're empirically comparing min / Tchebycheff / constrained / CVaR aggregations on production multi-reviewer data — the kind no other dataset has at scale.

Working name for the deliverable: `grandjury-train`. Thin layer over TRL: data adapters + aggregation experiments + comparison notebooks.

</details>

<details>
<summary><b>Stream 1 — AI Safety + Evaluation Resource Curation</b> · for community curators, content-marketing-adjacent contributors, knowledge-base builders</summary>

A public, opinionated index of AI safety + production-evaluation tools, frameworks, and papers. Built in public on X/Twitter. We curate, adjacent communities amplify back.

Community/outreach work — the curated index is the artifact.

</details>

<details>
<summary><b>Stream 2 — Selector mechanism / "Pick The Right Brain"</b> · for ML systems engineers, RAG / dynamic-workflow practitioners, routing specialists</summary>

Given a stream of pluralistic feedback signals, how do we help agent devs pick the right model for their use case? **Empathy** is the first use case — highly subjective, recurring in healthcare / coaching / customer support.

Existing quality routers (NotDiamond, Martian, OpenRouter's auto router) train on synthetic eval datasets they construct themselves. We have the pluralistic, multi-reviewer production data they don't. Working name: `grandjury-router`.

</details>

<details>
<summary><b>Stream 3 — Public guardrailing from real-time feedback</b> · for safety researchers, content-policy engineers, guardrail tool builders</summary>

How do live production signals drive *immediate* guardrail updates, user apologies, human handoff for dangerous content — without waiting for the next retrain? Includes the "censorship-first vs censorship-via-slicing" design question.

Working name: `grandjury-guardrail`. Runtime rules engine consuming the live stream.

</details>

<details>
<summary><b>Stream 4 — Pluralistic signal: vocabulary + public artifacts (twin threads)</b> · for schema designers, data architects, HCI / data-viz designers, accountability researchers, policy folks</summary>

Two threads:

**4-A — Input vocabulary.** What richer K/V signal can reviewers submit beyond pass/flag? Fixed K-axis ratings (HelpSteer2-style) vs open-vocabulary K/V tags. The schema we land on directly feeds Stream 0's training experiments. Working name: `grandjury-schema`.

**4-B — Public accountability artifacts.** What does an AI *user* actually see about an AI? Model cards are static and vendor-published. LMSys Arena gives you one-dimensional Elo. What's the live, multi-dimensional, third-party-attested, consumer-readable representation of how an AI is *actually* behaving — built on pluralistic production feedback? Working name: `grandjury-pulse-card`.

</details>

<details>
<summary><b>Stream 5 — UI integration: HumanJudge signal anywhere</b> · for integration engineers, DX folks, observability insiders, no-code / workflow builders, plugin & bot developers</summary>

The widest stream by surface area. Anywhere a developer or workflow touches AI output is in scope:

- **Observability:** Langfuse, Galileo, Arize Phoenix, LangSmith, Helicone
- **Workflow / automation:** n8n, Zapier, Make, Pipedream, Activepieces
- **Agent / IDE platforms:** OpenClaw, Cursor, Continue, Cline, Windmill
- **Dashboards / BI:** Datadog, Grafana, Metabase, Superset
- **Dev workflow:** GitHub Actions, Linear, Jira (eval-triggered tasks)
- **Comms / alerts:** Slack, Discord
- **Notebooks:** Jupyter, Colab, Observable

Each integration ships into its own discovery channel. Lowest "0 → 1" cost of any stream — Langfuse / Phoenix / LangSmith adapters already exist in the platform code.

</details>

### Apply by opening a PR

No CV, no "tell us about yourself." The application is a small PR with a challenge result + which streams interest you. Five steps:

1. **Sign up** at [humanjudge.com/auth?role=builder](https://humanjudge.com/auth?role=builder) (free) — gets you a PAT and the `builder` role
2. **Connect GitHub** on [humanjudge.com/profile](https://humanjudge.com/profile) so we can link your PR to your account
3. **Pick a challenge** from [`/challenges/README.md`](challenges/README.md), run it locally
4. **Add `/challenges/<your-github-handle>.md`** following [`TEMPLATE.md`](challenges/TEMPLATE.md), open the PR
5. **Reviewed personally** within ~3 business days → after merge, Discord invite arrives via email

Full walkthrough in [`CONTRIBUTING.md`](CONTRIBUTING.md#apply-to-the-rd-community). Privacy: email never appears in the public PR — your GitHub handle is the only public identifier.

[Join Discord →](https://discord.gg/vw43ufYmDH)

Stream-level conversations, research context, and active threads all live in Discord (private after onboarding).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and PR guidelines.

## License

See [LICENSE](LICENSE).
