# TakeMeter

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, the
> notebook, the baseline, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> head -5 data/practice_labels.csv     # the shape your labels.csv needs
> ```
>
> Then open `takemeter.ipynb` **in this folder** — in VS Code, or with
> `jupyter notebook` if you prefer. Pick the kernel: the `.venv` inside this
> project. Run section 1, which reports the hardware you'll be training on.
> Everything else waits until you have data.
>
> Nothing to upload, nothing to connect, no accounts and no keys. The notebook
> runs on your machine and writes next to your code.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     Unit 5 asks for the first five sections. Unit 6 adds the five below them.

     Everything is pasted as TEXT. No screenshots, no images.

     ⚠️ The confusion matrix especially. The notebook prints one as a markdown
     table, ready to copy. A screenshot of a matrix earns nothing. Paste the
     table.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 5 — THE BUILD ═══════════════════════ -->

## What This Does

I chose reddit as the platform and r/degoogle as the subreddit. I picked a recent and
popular post that I think is somewhat controversial. Each post is an individual 
comment and replies will not be included. The classifier will sorts each post into 
different categories based on some aspect of the comment.


---

## Label Taxonomy

### `label_one`

**Definition:** If a comment defends google's actions in some shape or form classify it as 'Support'.

**Example 1:**
> A court ordered subpoena would require all these email sites to share information to the government. If Proton was hit with a subpoena and didn’t respond, they would be liable.

**Example 2:**
> Uh, Google responded to a legal order. Tuta and Proton will do the exact same if they have no other choice.

### `label_two`

**Definition:** If a comment provides advice on what a user or anyone should do classify it as 'Advice'.

**Example 1:**
> Poooh, nas/server, mailcow, and a domain name is my to go solution. Not for the faint of heart to set up, but worth wile

**Example 2:**
> Switching providers doesn't make you subpoena-proof, it just changes what can be handed over. Google can be compelled by a US warrant directly. Proton is Swiss, so the US has to go through a mutual legal assistance treaty and a Swiss court order, and Proton publishes how many of those it gets in its transparency report. And they do comply when the order is legally binding. In 2021 they logged a French activist's IP under a Swiss order, and in 2024 they handed over a recovery email to Swiss authorities in a Spanish case. The difference is your inbox. Proton's zero-access encryption means they literally can't read or hand over your email contents, only metadata like IPs, recovery info, and who you emailed. If you're switching for privacy, the real move is end-to-end encryption plus not attaching a personal recovery email or phone number, because no provider can refuse a valid court order.

### `label_three`

**Definition:** If a comment is questioning the legitmacy of the post in some way classify it as 'Suspicious'.

**Example 1:**
> This e-mail is clearly a scam. So many red flags. Main red flag is the signature. Google is not an LLC it's a corporation. Most likely a C-Corp. LLC's are usually smaller companies. I really hope you didn't click any links. Use G-Mail or don't. A lot of professional companies do because of the security features of their paid service. The company I work for uses gmail.

**Example 2:**
> Google does not notify you if the FBI has a subpeona or warrant to get any material data from them about you. If you actually got this letter, it is a hoax.

### `label_four`

**Definition:** If a comment provides no worthwhile contribution label it as 'Worthless'.

**Example 1:**
> Oh yeah, it never happened to me, but as soon as i saw this happening to someone else a year ago, i immediately stopped using gmail important and started minding about privacy

**Example 2:**
> Let's just start with the obvious. If you're up to anything remotely questionable from a legal perspective. Using freemail services is a dumb idea.

### The hardest boundary

**Which two labels:** 'Advice' & 'Support'

**The decision rule I used every time:**
If a post supports google's action but still provide an alternative method to communication
label it as 'Advice'.

---

## The Dataset

**Where the posts came from:** Reddit: https://www.reddit.com/r/degoogle/comments/1x8d0u2/i_think_this_is_a_wakeup_call_for_anyone_still_on/?sort=controversial

**How I labelled them:** I labelled the first 44 comments cold by hand without assistance (marked `cold` in the note column). The remaining 156 comments were pre-labelled with AI using my taxonomy definitions and hardest boundary decision rule, and then reviewed and checked (marked `pre-labelled, checked`).

**Counts per label:**

| Label | Count | Share |
|---|---|---|
| worthless | 98 | 49.0% |
| support | 46 | 23.0% |
| advice | 34 | 17.0% |
| suspicious | 22 | 11.0% |
| **Total** | 200 | 100% |

**Three hard cases**

<!-- Any post that made you pause: what it was, which two labels it could have
     been, and what you chose. These are worth more than the easy 190. -->

**1.**
> *The post:*
> I wouldn't trust anything located in Germany anymore not with the current government. Mailbox.org which is also located there has been revealed to read your emails when they deem it necessary
> *Could have been:*
> The tag could have been 'Support'.
> *I chose, because:*
> I chose advice because the post isn't defending google's action and while it isn't giving advice on what the user shold do they are telling why their choice may not work. 

**2.**
> *The post:*
> What the fuck is wrong with people? "Wah I did a crime and Google weported me wah"
> *Could have been:*
> The tag could have been 'Worthless'.
> *I chose, because:*
> I chose 'Support' because even though the tone is harsh internet mockery, it substantively rejects blame against Google and defends their action as a justified response to a crime rather than corporate misconduct.

**3.**
> *The post:*
> This is any email service. Don't use email for anything sensitive.
> *Could have been:*
> The tag could have been 'Support'.
> *I chose, because:*
> I chose 'Advice' because although the first sentence defends Google/email providers by stating this applies to everyone, the post still provides an alternative rule/guideline for communication, matching my hardest boundary decision rule.

---

## The Training Run

**Base model:** `distilbert-base-uncased`

**Settings:**
- Hardware Device: `mps` (Apple Silicon GPU)
- PyTorch Version: `2.14.1`
- Epochs: 3
- Learning Rate: 2e-5
- Batch Size: 16
- Max Length: 128
- Seed: 42

**Anything I changed from the defaults, and why:**
None. I kept all default hyperparameters (3 epochs, lr 2e-5, batch size 16, max length 128, seed 42) to establish a clean, standard baseline fine-tuning run on `distilbert-base-uncased` before experimenting with any tuning in Unit 6.

**Split sizes:**
- Stratified 70/15/15 split: Train: 139, Val: 31, Test: 30 (Total: 200)
- Per-label counts in test split:
  - `worthless`: 15
  - `support`: 7
  - `advice`: 5
  - `suspicious`: 3
- *Note on thin classes:* `support` (7), `advice` (5), and `suspicious` (3) each have fewer than 8 examples in the test split, which means per-label test metrics (especially for `suspicious`) will be sensitive to individual misclassifications and can fluctuate across seeds.



---

## How I Used AI

**Moment 1**

- *What I asked for:* Assistance pre-labeling a batch of 156 unlabeled Reddit comments from the thread according to my taxonomy definitions (`support`, `advice`, `suspicious`, `worthless`) and my hardest boundary decision rule.
- *What came back:* Candidate label suggestions across all four categories, along with an initial distribution breakdown and a flagged list of ambiguous edge cases where comments combined multiple traits (such as advice embedded within scam warnings or aggressive snark that substantively defended Google).
- *What I changed:* I reviewed and verified the suggested labels against the taxonomy definitions, manually adjusted borderline classifications (e.g. enforcing the explicit hardest boundary rule that classifies comments defending email services as `advice` if they provide alternative communication guidance), updated their notes to `pre-labelled, checked`, and preserved my original 44 cold-labeled examples untouched.

**Moment 2**

- *What I asked for:* A Python script to collect 200 public comments from a controversial Reddit thread on r/degoogle using Reddit's endpoints/parsers.
- *What came back:* An initial script designed to fetch only top-level comments, handle rate limits with pacing delays and backoff on HTTP 429/5xx errors, strip [deleted], [removed], and AutoModerator bot comments, and output RFC 4180-compliant CSV with untruncated text. However, the thread only yielded 162 unique readable top-level comments, leaving the dataset short of the 200 required rows.
- *What I changed:* I modified the collection architecture to introduce a Top-Level Priority & Single-Reply Cap mechanism: the script prioritizes all 162 unique top-level comments (parent_id / depth 0), and then backfills the remaining 38 comments using direct replies under the strict constraint of at most 1 reply per comment. This maintained post independence while safely reaching the required 200-row dataset floor.

**Pre-labelling disclosure:**
I labeled the first 44 comments cold by hand without any AI assistance (marked `cold` in the `note` column). For the remaining 156 comments, I used AI to generate initial pre-labels based strictly on my label definitions and hardest boundary decision rule, and then manually reviewed, checked, and adjusted every single row (marked `pre-labelled, checked`).

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

<!-- Both models on the same posts. `python baseline.py --trained results.json`
     prints this table for you. -->

| Measure | Baseline | Trained | Difference |
|---|---|---|---|
| Overall accuracy |  |  |  |
| Macro F1 |  |  |  |
| F1 — `label_one` |  |  |  |
| F1 — `label_two` |  |  |  |

**What I predicted before I looked:**
<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A
     prediction made afterwards isn't one. -->

**What the gap actually means:**
<!-- If the baseline matched your trained model, your fine-tuning added
     nothing — and that is a real finding, not a failure. Say it plainly. -->



---

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

### Confusion matrix

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.
     An image of a matrix earns nothing. -->

| true \ predicted |  |  |  |
|---|---|---|---|
| **** |  |  |  |
| **** |  |  |  |
| **** |  |  |  |

**My biggest off-diagonal number, and what it means:**
<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which
     direction. "7 real analysis posts were called hot_take and only 3 went the
     other way" is a direction, not just an error rate. -->



---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**

<!-- For each miss: the cause, and how you know. The four common causes are:
     too few examples for a label, a boundary you applied inconsistently, a
     genuinely hard label pair, and a task the model can't reach from this
     much data.

     ⚠️ Use your agreement report as evidence. It is the only instrument you
     have that can tell a LABELLING problem from a MODEL problem, and this
     section is graded on whether you used it that way. -->



---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** ___ / 30 = ___%

<!-- Nobody grades this number. A 60% who argues every disagreement from the
     stated rules beats a 95% who wrote "staff was right" nine times. Several
     of the 30 were chosen because they're genuinely ambiguous — you should be
     winning some of these. -->

**Disagreements**

<!-- Three lines each: the post, both labels, and who you think is right and
     why — grounded in the staff definitions you were both applying.

     Then sort each into one of three piles:
       (a) the rule covered it and I applied it loosely → a consistency problem
       (b) the rule genuinely doesn't say               → a gap in the definitions
       (c) the rule is ambiguous here and my reading is defensible → argue it.
           This is a legitimate win.

     Pile (a) is the one that matters most for your diagnosis: if you applied a
     written rule two different ways on 30 posts, that is direct evidence about
     what you did across your own 200. -->

**1.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**2.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**What the pattern in my disagreements tells me:**



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely
     interesting result and earns full credit. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->



**The gap between what I meant my labels to capture and what the model
learned:**
<!-- Two sentences. Your confusion matrix is the evidence. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 5

       [ ] criteria.md has five numbered criteria, each naming a NUMBER
       [ ] Each has a reason underneath tied to your data or taxonomy
       [ ] labels.csv: at least 150 rows, text/label/note, ONE file not split
       [ ] No label above 70%
       [ ] All five unit 5 sections have real content
       [ ] Label Taxonomy includes the decision rule for your hardest boundary
       [ ] The Dataset includes three hard cases
       [ ] results.json and test_split.csv committed (the notebook does this)
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 6

       [ ] Baseline vs. Trained table, with your prediction written beforehand
       [ ] Run Log — Before, five criteria across three seeds
       [ ] Confusion matrix TYPED AS A MARKDOWN TABLE
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, using the agreement report as evidence
       [ ] Agreement Report with every disagreement adjudicated
       [ ] One improvement, with Run Log — After
       [ ] What's Still Broken
       [ ] results_three_seeds_before.json, results_three_seeds_after.json,
           baseline_results.json and
           agreement_results.json committed
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
