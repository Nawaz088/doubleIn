# Business Plan — DoubleHQ Clone

## Executive Summary

A full-featured month-end close management platform for accounting firms. Ships **every module from day one** — no MVP, no staged releases. Competes directly with DoubleHQ at **50-70% lower cost** while running on a single €19/mo VPS with **97%+ margins**.

**Target Market**: Small-to-medium accounting firms (2-50 employees) managing 10-500 clients.

**Revenue Model**: Per-client per-month pricing, unlimited users, annual discount option.

**Goal**: Ship the complete product in 16 weeks. Reach 100 paid clients within 8 months of launch at ~$7,000 MRR with **98% net margins**.

---

## Feature Set (All Shipped Day One)

| Module | Build Time | Complexity |
|--------|-----------|------------|
| Auth + Multi-tenant | 1 week | Low |
| CRM / Client Management | 1 week | Low |
| Task Management + Close Page | 2 weeks | Medium |
| QBO/Xero Integration (2-way) | 3 weeks | High |
| Bank Feeds (manual + rules) | 1 week | Medium |
| Journal Entries | 1 week | Medium |
| File Review (rule-based) | 1 week | Medium |
| Reports + PDF Export | 1 week | Medium |
| Client Portal (white-label) | 1 week | Medium |
| Receipts (Tesseract OCR) | 1 week | Medium |
| Accruals | 1 week | Medium |
| 1099 Management | 1 week | Low |
| Tax Suite (organizers, signatures) | 1 week | High |
| Email Inbox | 1 week | Medium |
| **Total** | **16 weeks** | |

No AI. No dependencies on OpenAI/Anthropic. Zero variable cost per client.

---

## Market Research

### Competitor Pricing

| Competitor | Starting Price | Per-Client? | Unlimited Users? |
|------------|---------------|-------------|------------------|
| **DoubleHQ** | ~$89/mo | Per client | Yes |
| **Jetpack Workflow** | ~$99/mo flat | No | Limited by tier |
| **Karbon** | ~$79/mo/user | Per user | No |
| **Our Price** | **$39/mo** | **Per client** | **Yes** |

### Competitive Advantages

1. **Price**: 50-70% cheaper than DoubleHQ
2. **Transparency**: No sales calls, no demos required — self-serve signup
3. **No AI hype**: Delivers real value without expensive AI add-ons
4. **Unlimited users**: Firms can add their entire team without cost fear
5. **Complete from day one**: Every feature ships on launch, not a roadmap

### TAM / SAM / SOM

- **TAM**: 500,000 accounting firms globally
- **SAM** (US firms 2-50 employees): ~45,000 firms × 40 avg clients = 1.8M client connections
- **Year 1 Target**: 100 firms × 10 clients = 1,000 client connections
- **Year 3 Target**: 500 firms × 25 clients = 12,500 client connections

---

## Cost Structure

### Infrastructure (Single Hetzner VPS)

| Item | Cost |
|------|------|
| Hetzner CX42 (8 vCPU, 16GB, 320GB NVMe) | €18.99/mo |
| Object Storage (1TB, S3-compatible) | €5.99/mo |
| Domain + DNS | ~$1/mo |
| Email API (Resend, 5k/day) | ~$15/mo |
| Monitoring (self-hosted) | $0 |
| PostgreSQL backups (to Object Storage) | $0 |
| **Total monthly infra** | **~€25 + $16 = ~$43/mo** |

### Variable Costs

| Item | Cost/Client | Notes |
|------|-------------|-------|
| File storage (200MB avg/client) | ~$0.01 | S3-compatible object storage |
| Email (200 emails/client/mo) | ~$0.02 | Resend pricing |
| OCR (Tesseract — self-hosted, free) | $0.00 | Runs on our own server |
| AI APIs | $0.00 | Deliberately excluded |
| **Total variable** | **~$0.03/client/mo** | **Effectively zero** |

### Total Cost Examples

| Clients | Monthly Cost | Per-Client Cost |
|---------|-------------|----------------|
| 0 (pre-launch) | ~$43 | — |
| 10 | ~$43.30 | $4.33 |
| 50 | ~$44.50 | $0.89 |
| 100 | ~$46.00 | $0.46 |
| 500 | ~$58.00 | $0.12 |
| 1,000 | ~$73.00 | $0.07 |

**Key insight**: Moving from 0 to 1,000 clients increases monthly cost by only ~$30. Infrastructure is almost purely fixed.

---

## Pricing

### Core Tiers

| Tier | Monthly | Annually | What's Included |
|------|---------|----------|-----------------|
| **Starter** | **$39/mo** per client | **$390/yr** per client | Task management, CRM, Close Page, Client Portal (basic), Basic reports, Dashboard |
| **Professional** | **$79/mo** per client | **$790/yr** per client | Everything in Starter + QBO/Xero sync, Bank feeds, File review, Journal entries, Receipts (100/mo), 1099 management, Advanced reports (exec summary, KPIs), Custom portal domain |
| **Enterprise** | **$149/mo** per client | **$1,490/yr** per client | Everything in Professional + Accruals, Tax Suite, Email Inbox, Receipts (unlimited), White-label branding, Priority support, Onboarding call |

### Internal Finance Teams

| Plan | Monthly | Annually |
|------|---------|----------|
| **Standard** | $499/mo flat | $4,990/yr |
| **Enterprise** | $999/mo flat | $9,990/yr |

Unlimited clients, all features. Different pricing from accounting firm model.

### Add-ons

| Add-on | Price | Notes |
|--------|-------|-------|
| Extra Receipt Credits | $10/100 | Beyond plan limits |
| Additional Email Inboxes | $10/mo | Per connected team email |
| Custom Domain Portal | Included Pro+ | Setup assistance |
| Onboarding Workshop | $499 | 60-min setup with CSM |

---

## Revenue Projections

### Year 1

| Month | New Clients | Total Clients | Est. Mix (40% Starter, 40% Pro, 20% Enterprise) | MRR |
|-------|------------|---------------|-------------------------------------------------|-----|
| 1 (build) | 0 | 0 | — | $0 |
| 2 (build) | 0 | 0 | — | $0 |
| 3 (build) | 0 | 0 | — | $0 |
| 4 (build) | 0 | 0 | — | $0 |
| 5 (launch) | 5 | 5 | 2×$39 + 2×$79 + 1×$149 | **$384** |
| 6 | 5 | 10 | 4×$39 + 4×$79 + 2×$149 | **$768** |
| 7 | 8 | 18 | 7×$39 + 7×$79 + 4×$149 | **$1,382** |
| 8 | 10 | 28 | 11×$39 + 11×$79 + 6×$149 | **$2,188** |
| 9 | 12 | 40 | 16×$39 + 16×$79 + 8×$149 | **$3,088** |
| 10 | 15 | 55 | 22×$39 + 22×$79 + 11×$149 | **$4,247** |
| 11 | 20 | 75 | 30×$39 + 30×$79 + 15×$149 | **$5,790** |
| 12 | 25 | 100 | 40×$39 + 40×$79 + 20×$149 | **$7,720** |

**Year 1 Revenue**: ~**$28,000** (months 5-12 of actual sales)
**Year 1 Costs**: ~**$600** (infrastructure only)
**Year 1 Gross Profit**: ~**$27,400** (97.9% margin)

### Year 2

| Month | Clients | MRR |
|-------|---------|-----|
| 13 | 130 | $10,036 |
| 14 | 160 | $12,352 |
| 15 | 200 | $15,440 |
| 16 | 240 | $18,528 |
| 17 | 280 | $21,616 |
| 18 | 320 | $24,704 |
| 19 | 360 | $27,792 |
| 20 | 400 | $30,880 |
| 21 | 450 | $34,740 |
| 22 | 500 | $38,600 |
| 23 | 550 | $42,460 |
| 24 | 600 | $46,320 |

**Year 2 Revenue**: **$306,180**
**Year 2 Costs**: ~**$1,200**
**Year 2 Margin**: **99.6%**

### Year 3

At 1,500 clients: **$115,800 MRR / $1.39M ARR** at **99.7% margins**.

---

## Break-even Analysis

| Scenario | Clients Needed | Monthly Cost | Breakeven Revenue | Time to Achieve |
|----------|---------------|-------------|-------------------|-----------------|
| Solo, no salary (bootstrap) | 1 | ~$45 | $39 | Day 1 |
| Solo, $3k/mo draw | ~40 | ~$50 infra + $3k | ~$3,050 | Month 9 |
| Solo, $5k/mo draw | ~65 | ~$50 infra + $5k | ~$5,050 | Month 11 |
| Two founders, $5k/mo each | ~130 | ~$55 infra + $10k | ~$10,055 | Month 13 |
| Full team (3 devs, support), $20k/mo | ~260 | ~$60 infra + $20k | ~$20,060 | Month 17 |

**This business is profitable from its first dollar of revenue.**

---

## Customer Acquisition ($0 Marketing Budget)

Every channel listed here is free. No ad spend.

| Channel | Method | Expected Signups | % Free → Paid | Paid Clients |
|---------|--------|-----------------|---------------|-------------|
| **Product Hunt** | Launch day post | 200-500 | 5% | 10-25 |
| **Reddit** (r/bookkeeping, r/accounting) | "I built this" posts, advice threads | 50-100 | 10% | 5-10 |
| **QBO App Store** | List as free beta → reviews | 20-50/mo | 8% | 2-4/mo |
| **Facebook Groups** | Bookkeeping communities | 10-30/mo | 10% | 1-3/mo |
| **Direct Cold Email** | 50 firms/week manually | 2-3/week | 20% | 0.4-0.6/week |
| **Referral Program** | 1 month free per referral | Spreads virally | High | Growing |
| **Content Marketing** | Blog posts, comparison pages | SEO lag 6mo | 5% | Long-term |

**Year 1 Target**: 100 paid clients. Primary channels: Product Hunt (launch), Reddit (sustainable), cold email (direct).

### Launch Day — Product Hunt Checklist

- [ ] 7 days before: Post in relevant Reddit threads, build wishlist
- [ ] 3 days before: Email pre-launch list, ask for upvotes
- [ ] Launch day: Post at 12:01am PT, respond to every comment
- [ ] Offer: PH Launch discount — 40% off first 6 months (capped at first 100 signups)
- [ ] Ask every user for QBO App Store review
- [ ] Week after: Turn PH users into case studies

### Viral Loop

1. Firm signs up and connects QBO/Xero
2. Their clients log into the Client Portal (magic link)
3. Portal is white-labeled — looks like the firm's own product
4. Other firms see it and ask "what portal is this?"
5. Referral: "It's XYZ — here's my referral link"

Each firm that adopts us can be our best salesperson. Every client portal they send out is a billboard.

---

## Customer Retention

### Expected Churn Rates

| Month | Expected Churn | Notes |
|-------|---------------|-------|
| 1-3 (early) | 5-8% | Some trial signups will churn |
| 4-6 | 3-5% | Product/market fit improving |
| 7-12 | 2-3% | Stickiness from QBO lock-in |
| 12+ | 1-2% | Portal adoption makes switching painful |

**Lifetime Value (LTV) at $79 avg MRR, 3% monthly churn**:
- Average lifetime: 33 months
- LTV: $79 × 33 = **$2,607 per client**
- CAC: ~$0 (organic channels)
- **LTV/CAC: ∞**

---

## Key Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **QBO API changes break sync** | Feature outage | Abstract integration layer, monitor API changelogs, automated integration tests, handle gracefully |
| **DoubleHQ drops prices** | Price pressure | Our cost base is lower; we can win on price at any level since we have no AI costs |
| **Low trial conversion** | Revenue stalls | Improve onboarding, add in-app chat, offer free onboarding call |
| **Server down** | Trust lost | Hetzner 99.9% SLA; daily DB backups to S3; recovery in <1 hour |
| **Buggy file review reports** | Trust lost | Manual QC before each release, test with real QBO data |
| **No one knows we exist** | Zero revenue | Product Hunt, QBO App Store, Reddit — these all work for B2B SaaS |

---

## What Happens When We Add AI Later

Without AI, we ship a complete product in 16 weeks. Once we have paying customers and feedback:

### AI Phase 2 (Post-Launch, Month 5+)

| Feature | Dev Time | Impact | Priority |
|---------|----------|--------|----------|
| AI Bank Feeds (4-tier classification) | 3 weeks | Justify price increase to $79+ | High |
| AI Financial Summaries | 1 week | Report value bump | Medium |
| AI Reconciliations | 2 weeks | Time-saver for accountants | Medium |
| AI Transactions (chat agent) | 4 weeks | Major differentiator | High |
| Ask Double (Q&A) | 2 weeks | Support deflection | Low |

**AI pricing addition**: $20/mo per client AI add-on (or move to new Pricing v2).

---

## The Math That Makes This Work

```
Revenue per client (blended):   $79/mo
Infrastructure cost:             ~$43/mo flat (+$0.03/client)
Variable cost per client:        $0.03/mo
---
Gross profit per client:         $78.97/mo (99.96% margin)

To replace a $60k salary:        63 clients
To replace a $120k salary:      127 clients
To reach $10k MRR:              127 clients
To reach $50k MRR:              633 clients
To reach $100k MRR:            1,266 clients

Infrastructure cost at 1,000 clients: ~$73/mo
Revenue at 1,000 clients:             ~$79,000/mo
Ratio:                                ~1,082x return on infrastructure
```

**Bottom line**: This is an infrastructure-arbitrage business. A single €19/mo Hetzner VPS can support $79,000/mo in revenue. No AI API costs, no per-client compute, no variable scaling cost. Pure leverage.
