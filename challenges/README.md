# R&D Community — Challenge Questions

Pick **one** question below, run it with the SDK, and submit your result as `/challenges/<your-github-handle>.md` following the format in [`TEMPLATE.md`](TEMPLATE.md).

The challenge has three purposes:
1. Proves you're a real human, not a bot
2. Proves you can use the SDK
3. Gives you a real first taste of what HumanJudge data feels like

**Range of difficulty.** Pick at your level. The deeper you go, the more signal we get about your interests — but the easy ones are perfectly fine. We're filtering for genuine curiosity, not technical olympics.

---

## Before you start

You need a **HumanJudge PAT** (Personal Access Token). If you haven't signed up:

1. Go to [humanjudge.com/auth?role=builder](https://humanjudge.com/auth?role=builder) — free, no credit card
2. Copy the PAT from your profile page
3. Set it in your environment:

```bash
export GRANDJURY_API_KEY=gj_sk_live_...
```

4. Install the package:

```bash
pip install grandjury
```

5. (Important) Visit [humanjudge.com/profile](https://humanjudge.com/profile) and click **Connect GitHub** — this links your GitHub handle to your HumanJudge profile so we can match your PR to your account.

Then run any of the challenges below.

---

## Discover available arenas first

Before picking a challenge, you might want to see what arenas (benchmarks) exist:

```python
from grandjury import GrandJury
gj = GrandJury()
benchmarks = gj.benchmarks.list()
for b in benchmarks:
    print(b)
```

This lists every public benchmark you can query. Pick one that interests you — there are arenas across marketing, healthcare, cultural fluency, code review, and more.

---

## The challenges

### Easy (~15–20 minutes)

**A. Count evaluations in any arena**

```python
from grandjury import GrandJury
gj = GrandJury()

df = gj.results(evaluation='<arena-slug-of-your-choice>')
print(f"Total evaluations in this arena: {len(df)}")
```

Just paste the count, the arena slug you used, and the timestamp into your submission.

**B. Top-5 most active reviewers in any arena**

```python
df = gj.results(evaluation='<arena-slug>', detail='votes')
top_reviewers = df.groupby('voter_name')['voter_id'].count().sort_values(ascending=False).head(5)
print(top_reviewers)
```

Paste the top 5 (names + counts).

**C. Highest pass-rate model in any arena**

```python
df = gj.results(evaluation='<arena-slug>')
best_model = df.groupby('model')['pass_rate'].mean().sort_values(ascending=False).head(1)
print(best_model)
```

---

### Medium (~30–60 minutes)

**D. Most controversial trace — highest reviewer disagreement**

```python
df = gj.results(evaluation='<arena-slug>', detail='votes')
disagreement = (
    df.groupby('trace_id')['verdict']
      .agg(lambda x: x.value_counts(normalize=True).max())
      .sort_values()
      .head(3)
)
# Lower max-share = more disagreement (closer to 50/50)
print(disagreement)
```

Find the 3 traces where reviewers most disagree. Paste their trace IDs and the disagreement scores.

**E. Pass-rate trend over the last 30 days for any model**

```python
df = gj.results(model='<model-slug>', detail='votes', from_date='2026-04-21')
df['date'] = pd.to_datetime(df['created_at']).dt.date
trend = df.groupby('date')['verdict'].apply(lambda x: (x == 'pass').mean())
print(trend)
```

Pick any model, plot or print the daily pass-rate. Drop a chart if you want.

**F. Which categorical flag is most common per model**

```python
df = gj.results(evaluation='<arena-slug>', detail='votes')
flag_dist = df.groupby(['model', 'flag_category']).size().unstack(fill_value=0)
print(flag_dist)
```

Find which flag type (compliance, tone, factual accuracy, etc.) each model gets flagged for most.

---

### Spicier (~1–2 hours, optional)

**G. Side-by-side comparison of two models on any arena**

Build a small notebook or script that takes two model slugs and compares them on:
- Pass rate
- Most common flag categories
- Reviewer disagreement variance

**H. Most "diagnostic" reviewer — whose votes correlate least with the crowd**

Identify reviewers whose verdicts deviate most from the majority. These are people seeing something different — often the most informative signal in a pluralistic system.

**I. Open-ended — your call**

Found something interesting in the data we didn't list? Show us. Anything that demonstrates SDK fluency + curiosity about pluralistic signal counts.

---

## Submission

Once you have your result:

1. Copy [`TEMPLATE.md`](TEMPLATE.md) to `challenges/<your-github-handle>.md`
2. Fill in the streams you're interested in (with 1–2 sentences per stream — see the [README](../README.md) for stream descriptions)
3. Paste your challenge result
4. Open the PR

See [`/CONTRIBUTING.md`](../CONTRIBUTING.md) for the full apply walkthrough.

---

## What we look at when reviewing

- **Code runs.** Your snippet executes against the real platform.
- **Numbers match.** What you paste matches what we see in the DB.
- **Stream interest reads genuine.** 1–2 sentences per stream that shows you actually thought about it.

That's it. We're not grading the analysis — just confirming you're human, you can code, you've used the SDK, and you have real interest. Reviewed within ~3 business days.
