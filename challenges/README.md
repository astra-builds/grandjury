# The challenge

One short task. Anyone with basic Python can finish in ~15 minutes.

## What you'll do

Count how many evaluations exist in any arena on the platform, using the Python SDK. Submit your result by adding a file at `/challenges/<your-github-handle>.md` and opening a PR.

## Step 1 — Get a HumanJudge account

Sign up at [humanjudge.com/auth?role=builder](https://humanjudge.com/auth?role=builder). Free, no credit card. You'll land on your profile page with a token you can use with the SDK — copy it now.

## Step 2 — Install the SDK locally

```bash
pip install grandjury
export GRANDJURY_API_KEY=<paste-token-from-step-1>
```

## Step 3 — See what arenas exist

```python
from grandjury import GrandJury
gj = GrandJury()

for b in gj.benchmarks.list():
    print(b)
```

This lists the public benchmarks. Pick one that looks interesting — there are arenas across marketing, healthcare, cultural fluency, code review, and others.

## Step 4 — Run the challenge

```python
from grandjury import GrandJury
gj = GrandJury()

df = gj.results(evaluation='<arena-slug-you-picked>')
print(f"Total evaluations in this arena: {len(df)}")
```

Note the number, the arena slug, and the timestamp when you ran it.

## Step 5 — Connect your GitHub

While you're still logged in, visit [humanjudge.com/profile](https://humanjudge.com/profile) and click **Connect GitHub**. This links your GitHub handle to your HumanJudge account so we can match your PR to your profile after it's merged.

## Step 6 — Submit your result

Copy [`TEMPLATE.md`](TEMPLATE.md) to `challenges/<your-github-handle>.md`, fill in:

- The streams you're interested in (one or two sentences each — see the streams in the [main README](../README.md))
- The arena slug, the count, the timestamp from step 4

Open a PR. That's the application.

## Reviewed

Reviewed personally within ~3 business days. Once merged, instructions for joining the Discord arrive in your inbox.

---

## Going further (optional)

If you want to show more than the bare minimum, the streams in the [main README](../README.md) sketch what we're working on — pick whatever pulls you and explore that part of the data yourself. The SDK has a small surface area; everything in `gj.results()`, `gj.benchmarks`, `gj.models`, and `gj.analytics` is fair game. Anything you discover that's worth sharing, drop in the same submission file.

Not required for acceptance — the count above is enough.
