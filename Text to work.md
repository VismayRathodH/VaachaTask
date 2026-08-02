# VaachaTask — Gujarati Business Instruction Assistant

**Gemma 4 Hackathon Sprint — Local Language Track**

Turn informal Gujarati / Gujarati-English business instructions (typed or spoken) into structured, editable tasks and ready-to-send Gujarati WhatsApp confirmation messages — powered by Gemma 4.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Roadmap](#project-roadmap)
  - [Phase 0: Setup](#phase-0-setup-000030)
  - [Phase 1: Gemma Extraction](#phase-1-prove-gemma-extraction-works-030130)
  - [Phase 2: Message Generation](#phase-2-message-generation-130215)
  - [Phase 3: Editable UI](#phase-3-ui--editable-card-215400)
  - [Phase 4: Robustness Pass](#phase-4-robustness-pass-400500)
  - [Phase 5: Polish & Deploy](#phase-5-polish--deploy-500600)
  - [Phase 6: Writeup & Submission](#phase-6-writeup--submission-600700)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [Example Input/Output](#example-inputoutput)
- [Scope](#scope)
- [Kaggle Submission Guide](#kaggle-submission-guide)
- [Evaluation Rubric](#evaluation-rubric)
- [Risks & Fallbacks](#risks--fallbacks)
- [Team](#team)

---

## Problem Statement

Shopkeepers, distributors, small manufacturers, contractors, and local offices in Gujarat manage most of their day-to-day operations — orders, deliveries, payment reminders, follow-ups — through informal spoken or typed instructions in Gujarati or mixed Gujarati-English. This information rarely gets structured, tracked, or turned into a clear message for the customer or team member involved.

**Challenge:** Build a Gemma-powered assistant that converts one informal Gujarati/Gujarati-English instruction into a structured task/order card and a Gujarati WhatsApp-ready confirmation message.

**Example:**

> Input: `"કાલે મનોજભાઈને 25 box મોકલવાના છે, ₹12,500 payment pending છે."`

> Output: Editable card with customer, action, quantity, due date, pending amount, payment status, next action → plus a natural Gujarati confirmation message.

---

## Solution Overview

1. User types (or speaks, optional stretch goal) one informal instruction.
2. Gemma 4 extracts structured fields as JSON.
3. Fields are shown in an **editable card** — user can correct anything before confirming.
4. On confirmation, Gemma 4 generates a natural, polite **Gujarati WhatsApp-style message** matching the action type (delivery, payment reminder, order, follow-up).
5. User copies the message and sends it manually (no live WhatsApp API integration — out of scope).

---

## Architecture

```
┌─────────────┐     ┌───────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│  Text Input  │ --> │  Gemma 4: Extract  │ --> │  Editable Card    │ --> │  Gemma 4: Generate  │
│ (Gujarati /  │     │  → structured JSON │     │  (user reviews &  │     │  → Gujarati WhatsApp│
│  mixed lang) │     │                    │     │   edits fields)   │     │     message         │
└─────────────┘     └───────────────────┘     └──────────────────┘     └────────────────────┘
```

- **Extraction call**: single Gemma 4 prompt, forced JSON-only output (acts as our structured/function-calling layer).
- **Editable card**: human-in-the-loop correction step — required by the challenge's "editable" requirement.
- **Generation call**: second Gemma 4 prompt, takes confirmed fields → natural Gujarati message.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Model | Gemma 4 (via API) |
| UI | Streamlit |
| Language | Python 3.11+ |
| Deployment | Streamlit Community Cloud / Kaggle Notebook |
| Version control | GitHub (public repo) |

---

## Project Roadmap

Total time budget: ~7 hours. Adjust proportionally if your actual window differs — **confirm the real deadline on the Kaggle event page before planning hours.**

### Phase 0: Setup (0:00–0:30)

- [ ] Create GitHub repo, commit README skeleton (this file)
- [ ] Confirm Gemma 4 API access with a trivial "hello world" call — biggest risk, kill it first
- [ ] Decide stack (Streamlit recommended for fastest editable-form UI)
- [ ] Set up folder structure:
  ```
  /app.py
  /gemma_client.py
  /prompts.py
  /examples.json
  README.md
  requirements.txt
  ```

### Phase 1: Prove Gemma Extraction Works (0:30–1:30)

- [ ] Write `gemma_client.py` with `extract_fields(text: str) -> dict`
- [ ] Use a JSON-only extraction prompt with these fields: `customer`, `action`, `quantity`, `due_date`, `amount`, `payment_status`, `next_action`
- [ ] Test against the brief's example sentence + 3–4 custom examples (include: messy input, missing amount, two people mentioned)
- [ ] Add basic error handling: strip markdown fences, retry once on malformed JSON

**Checkpoint:** reliable, clean JSON output across varied inputs before moving on. This is the highest-weight rubric item (Gemma Integration, 30%).

### Phase 2: Message Generation (1:30–2:15)

- [ ] Write `generate_confirmation(fields: dict) -> str`
- [ ] Prompt Gemma to write a 1–3 sentence natural Gujarati WhatsApp message, tone/content adapted to action type (delivery / payment reminder / order / follow-up)
- [ ] Chain-test using Phase 1's output as input

### Phase 3: UI — Editable Card (2:15–4:00)

- [ ] Text input box for the instruction
- [ ] "Extract" button → calls `extract_fields()` → pre-fills an editable form
- [ ] "Confirm & Generate Message" button → calls `generate_confirmation()` with (possibly edited) fields
- [ ] Display generated message in a copy-friendly box
- [ ] Add 2–3 clickable example presets (fast + safe fallback for live demo)

**Checkpoint:** full end-to-end flow works reliably — this is your demo backbone.

### Phase 4: Robustness Pass (4:00–5:00)

- [ ] Handle missing/null fields gracefully ("Not specified" instead of crashing)
- [ ] Input validation (empty, very long input)
- [ ] Test 5–6 more varied examples: pure Gujarati, pure English, mixed, multi-item, no date mentioned
- [ ] Refine extraction prompt based on failures (add few-shot examples if needed)
- [ ] Optional: fallback date parser for relative terms like "કાલે" (tomorrow) if prompt-only parsing is inconsistent

### Phase 5: Polish & Deploy (5:00–6:00)

- [ ] Clean up layout/styling (columns, header, spacing)
- [ ] Deploy to Streamlit Community Cloud (or package as a Kaggle Notebook)
- [ ] Finalize GitHub README: problem, architecture, how to run, how Gemma 4 is used
- [ ] Verify demo is publicly accessible with **no login/paywall**

### Phase 6: Writeup & Submission (6:00–7:00)

- [ ] Draft Kaggle Writeup (see [Kaggle Submission Guide](#kaggle-submission-guide) below)
- [ ] Attach public GitHub repo link
- [ ] Attach live demo / clonable notebook link
- [ ] Select **Local Language Track**
- [ ] Submit with buffer time before deadline — **draft/un-submitted writeups are not judged**

---

## Setup & Installation

```bash
git clone <your-repo-url>
cd vaachatask
pip install -r requirements.txt
```

Set your Gemma 4 API credentials as an environment variable (do not commit keys):

```bash
export GEMMA_API_KEY="your-key-here"
```

Run the app:

```bash
streamlit run app.py
```

---

## Usage

1. Open the app.
2. Type an informal Gujarati/Gujarati-English business instruction, or click an example preset.
3. Click **Extract** — review the auto-filled card.
4. Edit any field if needed.
5. Click **Confirm & Generate Message** — copy the generated Gujarati message.

---

## Example Input/Output

**Input:**
```
કાલે મનોજભાઈને 25 box મોકલવાના છે, ₹12,500 payment pending છે.
```

**Extracted fields:**
```json
{
  "customer": "મનોજભાઈ",
  "action": "delivery",
  "quantity": "25 box",
  "due_date": "tomorrow",
  "amount": "₹12,500",
  "payment_status": "pending",
  "next_action": "Deliver 25 boxes and follow up on pending payment"
}
```

**Generated message:**
```
મનોજભાઈ, કાલે તમારા 25 box ડિલિવર થશે. કૃપા કરી ₹12,500 ની બાકી ચુકવણી અંગે પણ ધ્યાન આપશો. આભાર!
```

---

## Scope

**In scope:**
- Single informal instruction → structured task/order card
- Field extraction: person, task, quantity, amount, date, status, next action
- Editable card before confirmation
- Gujarati WhatsApp-ready message generation

**Out of scope:**
- Full accounting or GST invoicing
- Real WhatsApp Business API integration
- Full inventory or CRM functionality
- Payment processing
- Multi-company administration

---

## Kaggle Submission Guide

A valid submission requires **all three** of the following, attached to a single Kaggle Writeup:

1. **Kaggle Writeup**
2. **Public Code Repository** (link, under Attachments → Project Links)
3. **Live Demo or Clonable Notebook** (link, under Attachments)

### Steps

1. Click **"New Writeup"** on the hackathon page.
2. Give it a **title and subtitle** (make it concrete — describe what the tool does, not just its name).
3. Select the **Local Language Track**.
4. Write the Writeup body (target: **under 1,500 words**; submissions over the limit may be penalized):
   - **Problem** — the real pain point (2–3 sentences)
   - **Solution architecture** — input → Gemma extraction (JSON) → editable card → Gemma message generation → output
   - **How Gemma 4 is specifically used** — the two prompts, why structured/JSON output, any prompt-engineering challenges solved
   - **Challenges faced in the 1-day sprint** — be specific and honest (e.g., relative date parsing in Gujarati)
   - **Impact** — tie back to intended users (shopkeepers, distributors, contractors, small offices)
5. Under **Attachments → Project Links**, add:
   - Public GitHub repo link (well-documented, no login/paywall)
   - Live demo link or clonable notebook (no login/paywall)
6. Save the Writeup, then click **Submit** in the top-right corner.
7. You can un-submit, edit, and re-submit as many times as needed before the deadline — **only one Writeup per team** is allowed.
8. **Note:** if you attach a private Kaggle Resource, it will automatically become public after the deadline.
9. Double-check the actual deadline on the official hackathon page before your final push — confirm hours remaining rather than assuming.

### Submission Checklist

- [ ] Writeup has title, subtitle, and full analysis
- [ ] Track selected: **Local Language Track**
- [ ] Word count under 1,500
- [ ] Public code repo linked and accessible without login
- [ ] Live demo or clonable notebook linked and accessible without login
- [ ] Writeup status shows **Submitted** (not draft) before deadline

---

## Evaluation Rubric

| Criteria | Weight | What Judges Look For |
|---|---|---|
| Gemma Integration | 30% | Is Gemma 4 core to the solution, not decorative? |
| Innovation & Impact | 30% | Does it solve a meaningful, relevant problem creatively? |
| Functionality | 20% | Does the prototype actually work? Is the demo convincing? |
| Presentation & Writeup | 20% | Is the problem and solution clearly explained? |

---

## Risks & Fallbacks

| Risk | Mitigation |
|---|---|
| Gemma 4 API access/rate limits fail during demo | Test access in Phase 0; have example presets pre-cached as fallback |
| Live demo breaks during judging | Record a short screen capture and embed/link it in the Writeup as backup |
| JSON parsing fails on messy input | Strip markdown fences, retry once, fall back to raw text display |
| Running out of time for voice input | Text input is core scope; voice is a stretch goal only — cut it first if behind schedule |
| Deadline confusion | Confirm actual hours remaining on the official Kaggle event page before planning |

---

## Team

*(Add team member names and roles here)*

---

## License

*(Add license if applicable)*
