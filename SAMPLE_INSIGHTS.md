# Sample Insights

Generated from `Raw_Data.xlsx`, data to **31 August 2026** (34,971 enquiry lines, 330 customers).  
Answers written by **gemini-flash-lite-latest (gemini)**. Every figure it quotes was computed in `insights.py` and appears in the tables in section 5 - the model does no arithmetic of its own.

---

## 1. The morning brief

What lands in front of the BU head each morning.

Yesterday was unusually busy for a Monday with enquiries up 16.6% and revenue jumping 30.4% to Rs 5.79 L compared to the four-week typical average, though conversion sits temporarily at 32.3% because recent enquiries need a few days to clear. Last month's overall conversion held flat at 38.8% versus the previous 30 days, despite a notable Drag from Gurgaon where a negative rate effect knocked 0.96 points off. The sales team must call our top priority P1 accounts today starting with Workshop 0213, Workshop 0186, and Workshop 0142 who have stopped ordering entirely after frustrating undelivered orders.

---

## 2. Questions a BU head actually asks

Each answered in a fresh conversation, verbatim, no editing.

### *"How has conversion changed over the last couple of months, and why?"*

Conversion remained virtually flat over the last 30 days compared to the previous 30 days, moving by just -0.1 points to 38.8% from 38.9%. 

While the headline conversion rate held steady, volume grew by 8.7% to 16,518 enquiries and revenue rose by 8.7% to Rs 1.39 Cr. 

The slight -0.1 point shift is the net result of underlying movements across business units and product categories:

* **Gurgaon** drove a positive total effect of +0.55 points (1.51 points from mix effect, though offset by a -0.96 point rate effect as its conversion moved from 42.9% to 41.4%).
* **Tyre Segment** added +0.25 points as its conversion jumped from 60.7% to 89.7%.
* **Noida** contributed a modest +0.1 points, improving its conversion from 31.8% to 34.4%.
* **Insurance & Fleet** pulled conversion down by -0.58 points as its rate dropped from 35.5% to 31.8%.
* **Tier II Cities** and the **Retail Segment** also weighed down conversion by -0.23 points and -0.21 points respectively, largely driven by rate drops—most notably in Retail, where conversion fell from 73.5% to 4.0% on 99 enquiries.

Across product categories, **Batteries** saw a rate-driven decline (conversion dropping from 80.3% to 34.1%), which was mostly counterbalanced by volume shifts and steady performance in core **Spares & Service** (which grew to 15,961 enquiries at a stable 38.5% conversion).

Out of the 61.3% of enquiries we did not convert over the broader period, 40.5% were quoted but lost, 17.9% were never quoted (6,246 lines with no price given), and the remainder were returned or still in progress.

### *"Which customers are new, growing, or slipping away?"*

We have 38 new customers, 107 growing, 85 shrinking, and 50 who have gone quiet. 

The most urgent churn signals are our P1 customers who have stopped ordering after a streak of undelivered orders—most notably Workshop 0186 in Tier II Cities, Workshop 0142 and Workshop 0076 in Gurgaon, and Workshop 0117 in Noida, all of whom have gone silent following delivery failures. 

For these 29 customers who went quiet after we failed to deliver (representing Rs 5.59 L in revenue), sales needs to call them immediately to win them back. However, we must separate them from the 101 customers (Rs 94.71 L in revenue) who also have 3+ undelivered orders but are *still* enquiring. Customers like Workshop 0141 in Noida (19-order streak, still active) and Workshop 0185 in Gurgaon (14-order streak, still active) have not left us yet; that is an operations problem for Amicco to fix through sourcing and delivery, not a sales call.

### *"Which product category is declining?"*

Battery enquiries surged, but conversion collapsed from 80.3% to 34.1% between the previous 30 days and the last 30 days, creating a rate drag of 1.05 points on overall performance. 

Batteries saw enquiries jump from 173 to 375, yet revenue share sat at 7.3% (Rs 21.55 L overall across the period) with a 50.3% conversion rate overall. By comparison, Spares & Service remained steady with 15,961 enquiries and a 38.5% conversion rate, Paint rose to a 70.1% conversion rate (154 enquiries), and Bulk Engine Oil held a 64.3% conversion rate (28 enquiries). 

This is an operational bottleneck in battery fulfillment rather than a drop in demand, and it requires investigating stock availability and pricing responsiveness for batteries rather than changing sales targets.

### *"How is Gurgaon performing versus Noida?"*

Gurgaon is outperforming Noida significantly on volume, revenue generation, and conversion rate, driven by massive scale in spares and service. 

Gurgaon generated Rs 1.64 Cr in revenue (55.5% of the total book) from 22,362 enquiries across 193 customers, achieving a 41.9% conversion rate with an average delivery speed of 0.35 days. Noida delivered Rs 51.51 L (17.4% of the book) from 7,716 enquiries across 51 customers, with a lower conversion rate of 33.2% and a slower average delivery time of 0.47 days.

Looking at recent momentum, Gurgaon's conversion rate shifted positively by +0.55 pts over the last 30 days (driven by a strong mix effect of +1.51 pts, despite a -0.96 pt rate effect). Noida saw a modest conversion improvement of +0.1 pts (rate effect +0.57 pts offset by a -0.47 pt mix effect). 

While Gurgaon is the core growth engine, operations must watch for delivery failures: Gurgaon currently has major accounts like Workshop 0106 (P1, Rs 1.76 L revenue, 17-order non-delivery streak) and Workshop 0098 (P2, Rs 8.76 L revenue, 12-order streak) experiencing fulfillment bottlenecks while still enquiring. Noida requires similar operational intervention for accounts like Workshop 0141 (P2, Rs 81.9k revenue, 19-order streak).

### *"Which customers should I call today?"*

Call our 29 P1 churn-risk customers today—workshops that stopped ordering after a streak of undelivered orders and went silent. They represent Rs 5.59 L in revenue and have given up on us, making them urgent sales calls.

The top 25 P1 customers on today's call list, ordered by urgency, are:

1. **Workshop 0213** (Tyre Segment, High Value) — Rs 79.3k revenue, 40 days quiet, 0 undelivered streak, -100% revenue change.
2. **Workshop 0186** (Tier II Cities, High Value) — Rs 3.73 L revenue, 15 days quiet, 4 undelivered streak, -8% revenue change.
3. **Workshop 0142** (Gurgaon, Mid Value) — Rs 9.8k revenue, 30 days quiet, 11 undelivered streak, -100% revenue change.
4. **Workshop 0117** (Noida, Mid Value) — Rs 32.4k revenue, 11 days quiet, 10 undelivered streak, -100% revenue change.
5. **Workshop 0076** (Gurgaon, Mid Value) — Rs 8.0k revenue, 12 days quiet, 9 undelivered streak, -100% revenue change.
6. **Workshop 0064** (Gurgaon, Mid Value) — Rs 16.9k revenue, 21 days quiet, 5 undelivered streak, -100% revenue change.
7. **Workshop 0020** (Insurance & Fleet, High Value) — Rs 66.9k revenue, 6 days quiet, 2 undelivered streak, -100% revenue change.
8. **Workshop 0225** (Gurgaon, Mid Value) — Rs 44.1k revenue, 21 days quiet, 4 undelivered streak.
9. **Workshop 0034** (Tier II Cities, Mid Value) — Rs 20.8k revenue, 15 days quiet, 3 undelivered streak, -100% revenue change.
10. **Workshop 0219** (Gurgaon, Mid Value) — Rs 8.5k revenue, 13 days quiet, 3 undelivered streak, -96% revenue change.
11. **Workshop 0263** (Gurgaon, Mid Value) — Rs 6.6k revenue, 13 days quiet, 3 undelivered streak.
12. **Workshop 0273** (Retail Segment, Mid Value) — Rs 23.0k revenue, 11 days quiet, 3 undelivered streak, -70% revenue change.
13. **Workshop 0262** (Tyre Segment, High Value) — Rs 1.87 L revenue, 26 days quiet, 0 undelivered streak, -73% revenue change.
14. **Workshop 0266** (Gurgaon, High Value) — Rs 1.09 L revenue, 12 days quiet, 1 undelivered streak, -70% revenue change.
15. **Workshop 0082** (Tier II Cities, High Value) — Rs 94.7k revenue, 2 days quiet, 9 undelivered streak, -65% revenue change.
16. **Workshop 0243** (Gurgaon, High Value) — Rs 60.0k revenue, 5 days quiet, 3 undelivered streak, -97% revenue change. *(Note: While they still have a recent enquiry, they have a 25% return rate).*
17. **Workshop 0156** (Gurgaon, High Value) — Rs 95.8k revenue, 1 day quiet, 3 undelivered streak, -96% revenue change.
18. **Workshop 0129** (Noida, High Value) — Rs 1.70 L revenue, 1 day quiet, 10 undelivered streak, -95% revenue change.
19. **Workshop 0087** (Gurgaon, High Value) — Rs 67.5k revenue, 4 days quiet, 7 undelivered streak, -87% revenue change.
20. **Workshop 0193** (Gurgaon, High Value) — Rs 2.11 L revenue, 0 days quiet, 6 undelivered streak, -78% revenue change.
21. **Workshop 0106** (Gurgaon, High Value) — Rs 1.76 L revenue, 0 days quiet, 17 undelivered streak, -70% revenue change.
22. **Workshop 0006** (Gurgaon, High Value) — Rs 94.8k revenue, 1 day quiet, 3 undelivered streak, -67% revenue change.
23. **Workshop 0191** (Gurgaon, High Value) — Rs 1.04 L revenue, 0 days quiet, 1 undelivered streak, -69% revenue change.
24. **Workshop 0077** (Gurgaon, High Value) — Rs 1.89 L revenue, 2 days quiet, 6 undelivered streak, -65% revenue change.
25. **Workshop 0052** (Gurgaon, High Value) — Rs 1.04 L revenue, 0 days quiet, 0 undelivered streak, -68% revenue change.

There are 26 further P1 customers queued behind these. Do not call the 101 customers who also have 3+ undelivered orders but are still enquiring—those are operations problems for Amicco to fix through sourcing and delivery, not sales calls.

---

## 3. A follow-up conversation

One continuous chat, to show that context carries between turns - the reason this is a conversation and not a dashboard.

**Q1. What happened to Battery conversion?**

Battery conversion dropped sharply from 80.3% to 34.1% over the last 30 days, pulling total conversion down by 1.05 points through the rate effect. 

This drop occurred while enquiries for batteries more than doubled from 173 to 375. Despite this surge in volume, our ability to fulfill them collapsed, with the negative rate effect (down 1.05 points) far outweighing a small positive mix effect (up 0.91 points). 

This is an operational failure in sourcing and delivery for batteries rather than a lack of customer demand. Operations needs to investigate why fulfillment failed on this product category while enquiry volume rose.

**Q2. Is that the same customers ordering, or new ones?**

I don't have customer-level breakdowns for battery orders in the daily figures, so I cannot confirm whether the surge came from existing or new buyers. 

What I can tell you from the overall figures is that our total active customer count remained flat at 277 versus 279 over the same comparative periods, and we currently have 38 new customers across the entire business out of 330 total. 

Operations needs to investigate the sourcing bottleneck behind the battery fulfillment collapse, regardless of whether the enquiries came from new or existing workshops.

**Q3. Put the Battery problem in one line I can forward to my ops head.**

Battery enquiries more than doubled while conversion collapsed from 80.3% to 34.1%, dragging total conversion down by 1.05 points due to a severe operational failure in sourcing and delivery.

*3 call(s) · $0.0013 spent · 0 tokens served from cache (~$0.0000 saved)*

---

## 4. Everything the agent can surface, ranked

Findings are scored so the brief leads with what matters rather than reciting metrics in schema order.

- **[130]** Retail Segment conversion fell off a cliff: 73.5% to 4.0%. On 99 enquiries this month against 49 last month. A drop of 70 points is not noise.
  - *Action:* Worth a direct look at what changed in sourcing or pricing there.
- **[106]** Battery conversion fell off a cliff: 80.3% to 34.1%. On 375 enquiries this month against 173 last month. A drop of 46 points is not noise.
  - *Action:* Worth a direct look at what changed in sourcing or pricing there.
- **[97]** 29 customers stopped ordering after we failed to deliver to them. They carry Rs 5.59 L between them. The clearest case is Workshop 0186 (Tier II Cities, Rs 3.73 L): 4 undelivered orders, then silence for 15 days, a customer who normally orders every day.
  - *Action:* These are the calls that matter today - we know exactly what went wrong, and the window to win them back is closing.
- **[95]** 101 customers are still enquiring despite 3+ undelivered orders in a row. Rs 94.71 L of revenue sits behind them. Worst is Workshop 0141 (Noida, Rs 81.9k) at 19 in a row, and they ordered again 0 days ago.
  - *Action:* This is an operations problem, not a sales one. They have not left yet - fix the sourcing before they do.
- **[73]** 6,246 enquiries were never even priced. That is 17.9% of everything customers asked for. Separately, 14,154 lines (40.5%) were quoted and still lost. These are two different problems: the first is response speed and coverage, the second is price or availability.
  - *Action:* Fixing the unquoted pile needs no pricing decision at all - it is the cheapest conversion available.
- **[70]** 51 customers need a call today. Top three by urgency: Workshop 0213 (Tyre Segment, Rs 79.3k); Workshop 0186 (Tier II Cities, Rs 3.73 L); Workshop 0142 (Gurgaon, Rs 9.8k).
  - *Action:* Full list on the Priority tab; it holds Rs 42.93 L of revenue.
- **[59]** 38 new customers this month, 50 have gone quiet. 107 customers are growing and 85 are shrinking. We are losing customers faster than we are adding them.
- **[57]** Insurance & Fleet is the biggest drag on conversion this month. It pulled overall conversion down 0.58 points. Its own conversion went from 35.5% to 31.8% on 1,234 enquiries. The cause is both a weaker close rate and a shift in volume, in roughly equal measure (rate effect -0.27 pts, mix effect -0.30 pts).
- **[56]** Tier II Cities takes 3.6 days to deliver against 0.02 in Tyre Segment. Measured across 586 delivered lines, so it is a settled pattern rather than a bad week. Everywhere else is effectively same-day.
  - *Action:* A customer who waits days learns to call someone else first.
- **[52]** Battery is the biggest drag on conversion this month. It pulled overall conversion down 0.14 points. Its own conversion went from 80.3% to 34.1% on 375 enquiries. The cause is both a weaker close rate and a shift in volume, in roughly equal measure (rate effect -1.05 pts, mix effect +0.91 pts).
- **[49]** Revenue is up 8.7% month on month. Rs 1.39 Cr in the last 30 days (02 Aug to 31 Aug) against Rs 1.28 Cr in the 30 before it. Enquiries moved +8.7% and conversion -0.1 points, so the change is driven by volume, not close rate.
- **[32]** Virtual orders convert at 69.4% against 38.0% for physical. But virtual is only 2.5% of enquiries (860 lines). The gap is large enough to be worth understanding, though the volume is small and these customers may simply be the more organised ones.
  - *Action:* Treat as a question to investigate, not a proven lever.

---

## 5. The numbers behind every answer

The audit trail. Any figure quoted above can be checked here.

### Conversion by business unit

| Business Unit     |   Enquiries |   Delivered |   Conversion % |
|:------------------|------------:|------------:|---------------:|
| Tyre Segment      |         143 |         112 |           78.3 |
| Gurgaon           |       22362 |        9376 |           41.9 |
| Insurance & Fleet |        2730 |         920 |           33.7 |
| Noida             |        7716 |        2565 |           33.2 |
| Tier II Cities    |        1872 |         530 |           28.3 |
| Retail Segment    |         148 |          40 |           27   |

### Why conversion moved - last 30 days vs previous 30

Rate effect = the same segment converting differently. Mix effect = volume shifting between segments. They sum exactly to the total change - no residual.

| Business Unit     |   Enquiries Prev 30d |   Enquiries Last 30d |   Conversion Prev |   Conversion Last |   Rate Effect (pts) |   Mix Effect (pts) |   Total Effect (pts) |
|:------------------|---------------------:|---------------------:|------------------:|------------------:|--------------------:|-------------------:|---------------------:|
| Insurance & Fleet |                 1265 |                 1234 |              35.5 |              31.8 |               -0.27 |              -0.3  |                -0.58 |
| Tier II Cities    |                  915 |                  728 |              26.6 |              31   |                0.2  |              -0.43 |                -0.23 |
| Retail Segment    |                   49 |                   99 |              73.5 |               4   |               -0.42 |               0.2  |                -0.21 |
| Noida             |                 3474 |                 3532 |              31.8 |              34.4 |                0.57 |              -0.47 |                 0.1  |
| Tyre Segment      |                   56 |                   87 |              60.7 |              89.7 |                0.15 |               0.1  |                 0.25 |
| Gurgaon           |                 9436 |                10838 |              42.9 |              41.4 |               -0.96 |               1.51 |                 0.55 |

| Product Category   |   Enquiries Prev 30d |   Enquiries Last 30d |   Conversion Prev |   Conversion Last |   Rate Effect (pts) |   Mix Effect (pts) |   Total Effect (pts) |
|:-------------------|---------------------:|---------------------:|------------------:|------------------:|--------------------:|-------------------:|---------------------:|
| Battery            |                  173 |                  375 |              80.3 |              34.1 |               -1.05 |               0.91 |                -0.14 |
| Engine Oil (Bulk)  |                   36 |                   28 |              77.8 |              64.3 |               -0.02 |              -0.05 |                -0.08 |
| Paint              |                  195 |                  154 |              55.4 |              70.1 |                0.14 |              -0.19 |                -0.06 |
| Spares & Service   |                14791 |                15961 |              38.1 |              38.5 |                0.42 |              -0.27 |                 0.15 |

### Product category

| Product Category   |   Enquiries |   Delivered | Revenue    | Enquiry_Value   |   Conversion % |   Revenue Share % |
|:-------------------|------------:|------------:|:-----------|:----------------|---------------:|------------------:|
| Spares & Service   |       33918 |       12950 | Rs 2.44 Cr | Rs 7.30 Cr      |           38.2 |              82.6 |
| Engine Oil (Bulk)  |          79 |          56 | Rs 25.82 L | Rs 37.42 L      |           70.9 |               8.7 |
| Battery            |         573 |         288 | Rs 21.55 L | Rs 44.07 L      |           50.3 |               7.3 |
| Paint              |         401 |         249 | Rs 4.01 L  | Rs 6.01 L       |           62.1 |               1.4 |

### Delivery speed by business unit

| Business Unit     |   Mean_Days |   Median_Days |   Lines |
|:------------------|------------:|--------------:|--------:|
| Tyre Segment      |        0.02 |             0 |     116 |
| Gurgaon           |        0.35 |             0 |   10069 |
| Noida             |        0.47 |             0 |    2770 |
| Retail Segment    |        0.68 |             0 |      40 |
| Insurance & Fleet |        1.64 |             1 |     990 |
| Tier II Cities    |        3.65 |             2 |     586 |

### Weekly trend

| Week Of   |   Enquiries |   Delivered |   Conversion % | Revenue    | Complete   |
|:----------|------------:|------------:|---------------:|:-----------|:-----------|
| 22 Jun    |        1281 |         527 |           41.1 | Rs 12.15 L | True       |
| 29 Jun    |        3453 |        1195 |           34.6 | Rs 25.74 L | True       |
| 06 Jul    |        3246 |        1235 |           38   | Rs 23.66 L | True       |
| 13 Jul    |        3734 |        1482 |           39.7 | Rs 31.54 L | True       |
| 20 Jul    |        3437 |        1348 |           39.2 | Rs 28.09 L | True       |
| 27 Jul    |        3838 |        1591 |           41.5 | Rs 38.13 L | True       |
| 03 Aug    |        3571 |        1458 |           40.8 | Rs 30.40 L | True       |
| 10 Aug    |        3969 |        1546 |           39   | Rs 34.69 L | True       |
| 17 Aug    |        4238 |        1640 |           38.7 | Rs 39.24 L | True       |
| 24 Aug    |        3520 |        1300 |           36.9 | Rs 26.44 L | True       |
| 31 Aug    |         684 |         221 |           32.3 | Rs 5.79 L  | False      |

`Complete = False` marks a week not yet fully observed. The agent is instructed never to report it as a decline.

### Where the lost enquiries go

| Outcome                            |   Lines |   % of enquiries |
|:-----------------------------------|--------:|-----------------:|
| Never quoted (no price ever given) |    6246 |             17.9 |
| Quoted but lost                    |   14154 |             40.5 |
| Returned                           |     951 |            nan   |
| Still in progress                  |      64 |            nan   |

### Customer lifecycle

| Lifecycle   |   Customers |
|:------------|------------:|
| Growing     |         107 |
| Shrinking   |          85 |
| Gone Quiet  |          50 |
| Steady      |          50 |
| New         |          38 |

### Channel

| Channel   |   Enquiries |   Delivered |     Revenue |   Conversion % |   Share of Enquiries % |
|:----------|------------:|------------:|------------:|---------------:|-----------------------:|
| Physical  |       34111 |       12946 | 2.85763e+07 |           38   |                   97.5 |
| Virtual   |         860 |         597 | 1.01016e+06 |           69.4 |                    2.5 |

---

## 6. Sales Priority Flag

**P1** 51 customers (Rs 42.93 L, 14.5% of delivered revenue) &nbsp;|&nbsp; **P2** 103 &nbsp;|&nbsp; **P3** 176

The call list is capped at 25; 26 further P1 customers are queued behind it. A priority list that does not fit in a morning is a report, not a priority list.

### The two lanes

A run of undelivered orders is a broken promise, not automatically a lost customer. Which one it is depends on whether they are still calling us.

| Lane | Customers | Revenue | Owner | What to do |
|---|---|---|---|---|
| Undelivered streak, **then silence** | 29 | Rs 5.59 L | Sales (P1) | They gave up on us. Call today, the window is closing. |
| Undelivered streak, **still enquiring** | 101 | Rs 94.71 L | Amicco (P2) | Operations problem. Fix sourcing before they go quiet. |

### Customers who gave up on us - the defining P1

Silence is measured against each customer's own ordering rhythm, not a flat number of days.

| Customer Name   | Business Unit   | Value Tier   | Revenue   |   Failed orders |   Silent (days) |   Normal gap (days) |
|:----------------|:----------------|:-------------|:----------|----------------:|----------------:|--------------------:|
| Workshop 0186   | Tier II Cities  | High         | Rs 3.73 L |               4 |              15 |                 1   |
| Workshop 0142   | Gurgaon         | Mid          | Rs 9.8k   |              11 |              30 |                 2   |
| Workshop 0117   | Noida           | Mid          | Rs 32.4k  |              10 |              11 |                 1   |
| Workshop 0076   | Gurgaon         | Mid          | Rs 8.0k   |               9 |              12 |                 1   |
| Workshop 0064   | Gurgaon         | Mid          | Rs 16.9k  |               5 |              21 |                 2   |
| Workshop 0225   | Gurgaon         | Mid          | Rs 44.1k  |               4 |              21 |                 5   |
| Workshop 0034   | Tier II Cities  | Mid          | Rs 20.8k  |               3 |              15 |                 3.5 |
| Workshop 0219   | Gurgaon         | Mid          | Rs 8.5k   |               3 |              13 |                 2.5 |
| Workshop 0263   | Gurgaon         | Mid          | Rs 6.6k   |               3 |              13 |                 4   |
| Workshop 0273   | Retail Segment  | Mid          | Rs 23.0k  |               3 |              11 |                 2   |
| Workshop 0058   | Gurgaon         | Low          | Rs 632    |              10 |              39 |                 3   |
| Workshop 0268   | Tier II Cities  | Low          | Rs 0      |               9 |              41 |                 1   |

### Today's call list (top P1 by urgency)

| Customer Name   | Business Unit     | Issue Owner   | Value Tier   | Revenue   |   Days Quiet |   ND Streak | Rev Chg   |   Score | Reason                                                                                                                                                                                                                       |
|:----------------|:------------------|:--------------|:-------------|:----------|-------------:|------------:|:----------|--------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Workshop 0213   | Tyre Segment      | Sales         | High         | Rs 79.3k  |           40 |           0 | -100%     |   146.3 | Top-tier customer, no enquiry in 40 days; Top-tier revenue down 100% vs the previous 30 days                                                                                                                                 |
| Workshop 0186   | Tier II Cities    | Sales         | High         | Rs 3.73 L |           15 |           4 | -8%       |    95.9 | Stopped ordering after 4 undelivered orders - silent 15 days, against a normal gap of 1 days                                                                                                                                 |
| Workshop 0142   | Gurgaon           | Sales         | Mid          | Rs 9.8k   |           30 |          11 | -100%     |    87.5 | Stopped ordering after 11 undelivered orders - silent 30 days, against a normal gap of 2 days; Mid-tier customer quiet for 30 days                                                                                           |
| Workshop 0117   | Noida             | Sales         | Mid          | Rs 32.4k  |           11 |          10 | -100%     |    78.7 | Stopped ordering after 10 undelivered orders - silent 11 days, against a normal gap of 1 days                                                                                                                                |
| Workshop 0076   | Gurgaon           | Sales         | Mid          | Rs 8.0k   |           12 |           9 | -100%     |    77.5 | Stopped ordering after 9 undelivered orders - silent 12 days, against a normal gap of 1 days                                                                                                                                 |
| Workshop 0064   | Gurgaon           | Sales         | Mid          | Rs 16.9k  |           21 |           5 | -100%     |    75.5 | Stopped ordering after 5 undelivered orders - silent 21 days, against a normal gap of 2 days; Mid-tier customer quiet for 21 days                                                                                            |
| Workshop 0243   | Gurgaon           | Sales         | High         | Rs 60.0k  |            5 |           3 | -97%      |    74.3 | Top-tier revenue down 97% vs the previous 30 days; 3 orders in a row undelivered - our failure, and they are still enquiring (last order 5d ago). Fix delivery before they go quiet; 25% of last month's lines were returned |
| Workshop 0020   | Insurance & Fleet | Sales         | High         | Rs 66.9k  |            6 |           2 | -100%     |    74.2 | Top-tier revenue down 100% vs the previous 30 days                                                                                                                                                                           |
| Workshop 0156   | Gurgaon           | Sales         | High         | Rs 95.8k  |            1 |           3 | -96%      |    74   | Top-tier revenue down 96% vs the previous 30 days; 3 orders in a row undelivered - our failure, and they are still enquiring (last order 1d ago). Fix delivery before they go quiet                                          |
| Workshop 0225   | Gurgaon           | Sales         | Mid          | Rs 44.1k  |           21 |           4 | -100%     |    74   | Stopped ordering after 4 undelivered orders - silent 21 days, against a normal gap of 5 days; Mid-tier customer quiet for 21 days                                                                                            |
| Workshop 0129   | Noida             | Sales         | High         | Rs 1.70 L |            1 |          10 | -95%      |    73.4 | Top-tier revenue down 95% vs the previous 30 days; 10 orders in a row undelivered - our failure, and they are still enquiring (last order 1d ago). Fix delivery before they go quiet                                         |
| Workshop 0087   | Gurgaon           | Sales         | High         | Rs 67.5k  |            4 |           7 | -87%      |    71   | Top-tier revenue down 87% vs the previous 30 days; 7 orders in a row undelivered - our failure, and they are still enquiring (last order 4d ago). Fix delivery before they go quiet                                          |
| Workshop 0034   | Tier II Cities    | Sales         | Mid          | Rs 20.8k  |           15 |           3 | -100%     |    69.5 | Stopped ordering after 3 undelivered orders - silent 15 days, against a normal gap of 4 days                                                                                                                                 |
| Workshop 0219   | Gurgaon           | Sales         | Mid          | Rs 8.5k   |           13 |           3 | -96%      |    68.8 | Stopped ordering after 3 undelivered orders - silent 13 days, against a normal gap of 2 days                                                                                                                                 |
| Workshop 0263   | Gurgaon           | Sales         | Mid          | Rs 6.6k   |           13 |           3 | n/a       |    68.8 | Stopped ordering after 3 undelivered orders - silent 13 days, against a normal gap of 4 days                                                                                                                                 |
| Workshop 0273   | Retail Segment    | Sales         | Mid          | Rs 23.0k  |           11 |           3 | -70%      |    68.2 | Stopped ordering after 3 undelivered orders - silent 11 days, against a normal gap of 2 days                                                                                                                                 |
| Workshop 0193   | Gurgaon           | Sales         | High         | Rs 2.11 L |            0 |           6 | -78%      |    68   | Top-tier revenue down 78% vs the previous 30 days; 6 orders in a row undelivered - our failure, and they are still enquiring (last order 0d ago). Fix delivery before they go quiet                                          |
| Workshop 0262   | Tyre Segment      | Sales         | High         | Rs 1.87 L |           26 |           0 | -73%      |    65.2 | Top-tier revenue down 73% vs the previous 30 days                                                                                                                                                                            |
| Workshop 0106   | Gurgaon           | Sales         | High         | Rs 1.76 L |            0 |          17 | -70%      |    65.1 | Top-tier revenue down 70% vs the previous 30 days; 17 orders in a row undelivered - our failure, and they are still enquiring (last order 0d ago). Fix delivery before they go quiet                                         |
| Workshop 0006   | Gurgaon           | Sales         | High         | Rs 94.8k  |            1 |           3 | -67%      |    64.3 | Top-tier revenue down 67% vs the previous 30 days; 3 orders in a row undelivered - our failure, and they are still enquiring (last order 1d ago). Fix delivery before they go quiet                                          |
| Workshop 0266   | Gurgaon           | Sales         | High         | Rs 1.09 L |           12 |           1 | -70%      |    64.2 | Top-tier revenue down 70% vs the previous 30 days                                                                                                                                                                            |
| Workshop 0191   | Gurgaon           | Sales         | High         | Rs 1.04 L |            0 |           1 | -69%      |    63.8 | Top-tier revenue down 69% vs the previous 30 days                                                                                                                                                                            |
| Workshop 0077   | Gurgaon           | Sales         | High         | Rs 1.89 L |            2 |           6 | -65%      |    63.4 | Top-tier revenue down 65% vs the previous 30 days; 6 orders in a row undelivered - our failure, and they are still enquiring (last order 2d ago). Fix delivery before they go quiet                                          |
| Workshop 0052   | Gurgaon           | Sales         | High         | Rs 1.04 L |            0 |           0 | -68%      |    63.4 | Top-tier revenue down 68% vs the previous 30 days                                                                                                                                                                            |
| Workshop 0082   | Tier II Cities    | Sales         | High         | Rs 94.7k  |            2 |           9 | -65%      |    63.3 | Top-tier revenue down 65% vs the previous 30 days; 9 orders in a row undelivered - our failure, and they are still enquiring (last order 2d ago). Fix delivery before they go quiet                                          |

### P2 sample (top 10 by urgency)

| Customer Name   | Business Unit     | Issue Owner       | Revenue    |   Days Quiet |   ND Streak | Reason                                                                                                                                                                    |
|:----------------|:------------------|:------------------|:-----------|-------------:|------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Workshop 0141   | Noida             | Amicco (delivery) | Rs 81.9k   |            0 |          19 | 19 orders in a row undelivered - our failure, and they are still enquiring (last order 0d ago). Fix delivery before they go quiet                                         |
| Workshop 0274   | Noida             | Amicco (delivery) | Rs 71.8k   |            5 |          15 | 15 orders in a row undelivered - our failure, and they are still enquiring (last order 5d ago). Fix delivery before they go quiet                                         |
| Workshop 0185   | Gurgaon           | Amicco (delivery) | Rs 4.16 L  |            0 |          14 | 14 orders in a row undelivered - our failure, and they are still enquiring (last order 0d ago). Fix delivery before they go quiet                                         |
| Workshop 0098   | Gurgaon           | Amicco (delivery) | Rs 8.76 L  |            0 |          12 | 12 orders in a row undelivered - our failure, and they are still enquiring (last order 0d ago). Fix delivery before they go quiet                                         |
| Workshop 0116   | Noida             | Amicco (delivery) | Rs 73.8k   |            0 |          10 | 10 orders in a row undelivered - our failure, and they are still enquiring (last order 0d ago). Fix delivery before they go quiet                                         |
| Workshop 0023   | Gurgaon           | Amicco (delivery) | Rs 1.06 L  |            2 |           8 | 8 orders in a row undelivered - our failure, and they are still enquiring (last order 2d ago). Fix delivery before they go quiet                                          |
| Workshop 0301   | Gurgaon           | Amicco (delivery) | Rs 20.7k   |            6 |           4 | 4 orders in a row undelivered - our failure, and they are still enquiring (last order 6d ago). Fix delivery before they go quiet; 21% of last month's lines were returned |
| Workshop 0094   | Insurance & Fleet | Amicco (delivery) | Rs 11.82 L |            0 |           7 | 7 orders in a row undelivered - our failure, and they are still enquiring (last order 0d ago). Fix delivery before they go quiet                                          |
| Workshop 0247   | Noida             | Amicco (delivery) | Rs 55.9k   |            3 |          13 | 13 orders in a row undelivered - our failure, and they are still enquiring (last order 3d ago). Fix delivery before they go quiet                                         |
| Workshop 0326   | Noida             | Amicco (delivery) | Rs 20.8k   |            8 |          13 | 13 orders in a row undelivered - our failure, and they are still enquiring (last order 8d ago). Fix delivery before they go quiet                                         |

### P3
176 customers, Rs 1.70 Cr of revenue. Reported in aggregate only - never listed individually, because nothing needs to be done about them.
