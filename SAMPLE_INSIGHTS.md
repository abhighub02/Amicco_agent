# Sample Insights

Generated from `Raw_Data.xlsx` on data up to **31 August 2026** (34,971 enquiry lines, 330 customers).  
Every number below is computed by `insights.py`. Nothing here is hand-written or model-generated.

---

## 1. The daily morning brief

This is what lands in front of the BU head each morning.

### Morning brief - Monday 31 August 2026

Yesterday was a strong day: 684 enquiries from 85 customers across 326 orders, against a typical 586 for a Monday. 221 lines were delivered, worth Rs 5.79 L.

*Enquiries raised in the last 3 days have not had time to convert, so today's conversion figure will rise.*

**What matters this morning**

1. **Retail Segment conversion fell off a cliff: 73.5% to 4.0%.**  
On 99 enquiries this month against 49 last month. A drop of 70 points is not noise.  
*What to do:* Worth a direct look at what changed in sourcing or pricing there.

2. **Battery conversion fell off a cliff: 80.3% to 34.1%.**  
On 375 enquiries this month against 173 last month. A drop of 46 points is not noise.  
*What to do:* Worth a direct look at what changed in sourcing or pricing there.

3. **29 customers stopped ordering after we failed to deliver to them.**  
They carry Rs 5.59 L between them. The clearest case is Workshop 0186 (Tier II Cities, Rs 3.73 L): 4 undelivered orders, then silence for 15 days, a customer who normally orders every day.  
*What to do:* These are the calls that matter today - we know exactly what went wrong, and the window to win them back is closing.

4. **101 customers are still enquiring despite 3+ undelivered orders in a row.**  
Rs 94.71 L of revenue sits behind them. Worst is Workshop 0141 (Noida, Rs 81.9k) at 19 in a row, and they ordered again 0 days ago.  
*What to do:* This is an operations problem, not a sales one. They have not left yet - fix the sourcing before they do.

5. **6,246 enquiries were never even priced.**  
That is 17.9% of everything customers asked for. Separately, 14,154 lines (40.5%) were quoted and still lost. These are two different problems: the first is response speed and coverage, the second is price or availability.  
*What to do:* Fixing the unquoted pile needs no pricing decision at all - it is the cheapest conversion available.


---

## 2. Answers to the questions in the brief

### *"How has conversion changed over the last couple of months, and why?"*

**Retail Segment conversion fell off a cliff: 73.5% to 4.0%.**  
On 99 enquiries this month against 49 last month. A drop of 70 points is not noise.  
*What to do:* Worth a direct look at what changed in sourcing or pricing there.

**Battery conversion fell off a cliff: 80.3% to 34.1%.**  
On 375 enquiries this month against 173 last month. A drop of 46 points is not noise.  
*What to do:* Worth a direct look at what changed in sourcing or pricing there.

**6,246 enquiries were never even priced.**  
That is 17.9% of everything customers asked for. Separately, 14,154 lines (40.5%) were quoted and still lost. These are two different problems: the first is response speed and coverage, the second is price or availability.  
*What to do:* Fixing the unquoted pile needs no pricing decision at all - it is the cheapest conversion available.

### *"Which customers are new, growing, or slipping away?"*

**29 customers stopped ordering after we failed to deliver to them.**  
They carry Rs 5.59 L between them. The clearest case is Workshop 0186 (Tier II Cities, Rs 3.73 L): 4 undelivered orders, then silence for 15 days, a customer who normally orders every day.  
*What to do:* These are the calls that matter today - we know exactly what went wrong, and the window to win them back is closing.

**101 customers are still enquiring despite 3+ undelivered orders in a row.**  
Rs 94.71 L of revenue sits behind them. Worst is Workshop 0141 (Noida, Rs 81.9k) at 19 in a row, and they ordered again 0 days ago.  
*What to do:* This is an operations problem, not a sales one. They have not left yet - fix the sourcing before they do.

**38 new customers this month, 50 have gone quiet.**  
107 customers are growing and 85 are shrinking. We are losing customers faster than we are adding them.

### *"Where is the business changing by category?"*

**Battery conversion fell off a cliff: 80.3% to 34.1%.**  
On 375 enquiries this month against 173 last month. A drop of 46 points is not noise.  
*What to do:* Worth a direct look at what changed in sourcing or pricing there.

**Battery is the biggest drag on conversion this month.**  
It pulled overall conversion down 0.14 points. Its own conversion went from 80.3% to 34.1% on 375 enquiries. The cause is both a weaker close rate and a shift in volume, in roughly equal measure (rate effect -1.05 pts, mix effect +0.91 pts).

### *"How is delivery performance across regions?"*

**Insurance & Fleet is the biggest drag on conversion this month.**  
It pulled overall conversion down 0.58 points. Its own conversion went from 35.5% to 31.8% on 1,234 enquiries. The cause is both a weaker close rate and a shift in volume, in roughly equal measure (rate effect -0.27 pts, mix effect -0.30 pts).

**Tier II Cities takes 3.6 days to deliver against 0.02 in Tyre Segment.**  
Measured across 586 delivered lines, so it is a settled pattern rather than a bad week. Everywhere else is effectively same-day.  
*What to do:* A customer who waits days learns to call someone else first.

### *"Who should my team call today?"*

**29 customers stopped ordering after we failed to deliver to them.**  
They carry Rs 5.59 L between them. The clearest case is Workshop 0186 (Tier II Cities, Rs 3.73 L): 4 undelivered orders, then silence for 15 days, a customer who normally orders every day.  
*What to do:* These are the calls that matter today - we know exactly what went wrong, and the window to win them back is closing.

**101 customers are still enquiring despite 3+ undelivered orders in a row.**  
Rs 94.71 L of revenue sits behind them. Worst is Workshop 0141 (Noida, Rs 81.9k) at 19 in a row, and they ordered again 0 days ago.  
*What to do:* This is an operations problem, not a sales one. They have not left yet - fix the sourcing before they do.

**51 customers need a call today.**  
Top three by urgency: Workshop 0213 (Tyre Segment, Rs 79.3k); Workshop 0186 (Tier II Cities, Rs 3.73 L); Workshop 0142 (Gurgaon, Rs 9.8k).  
*What to do:* Full list on the Priority tab; it holds Rs 42.93 L of revenue.

---

## 3. Every finding the agent can surface, ranked by severity

The agent leads with what matters rather than reciting metrics in schema order.

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

## 4. Supporting tables

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

Rate effect = the same segment converting differently. Mix effect = volume shifting between segments. They sum exactly to the total change.

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

`Complete = False` marks a week that is not yet fully observed. The agent is instructed never to report it as a decline.

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

## 5. Sales Priority Flag - example output

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

| Customer Name   | Business Unit     | Revenue    |   Days Quiet |   ND Streak | Reason                                                                                                                                                                    |
|:----------------|:------------------|:-----------|-------------:|------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Workshop 0141   | Noida             | Rs 81.9k   |            0 |          19 | 19 orders in a row undelivered - our failure, and they are still enquiring (last order 0d ago). Fix delivery before they go quiet                                         |
| Workshop 0274   | Noida             | Rs 71.8k   |            5 |          15 | 15 orders in a row undelivered - our failure, and they are still enquiring (last order 5d ago). Fix delivery before they go quiet                                         |
| Workshop 0185   | Gurgaon           | Rs 4.16 L  |            0 |          14 | 14 orders in a row undelivered - our failure, and they are still enquiring (last order 0d ago). Fix delivery before they go quiet                                         |
| Workshop 0098   | Gurgaon           | Rs 8.76 L  |            0 |          12 | 12 orders in a row undelivered - our failure, and they are still enquiring (last order 0d ago). Fix delivery before they go quiet                                         |
| Workshop 0116   | Noida             | Rs 73.8k   |            0 |          10 | 10 orders in a row undelivered - our failure, and they are still enquiring (last order 0d ago). Fix delivery before they go quiet                                         |
| Workshop 0023   | Gurgaon           | Rs 1.06 L  |            2 |           8 | 8 orders in a row undelivered - our failure, and they are still enquiring (last order 2d ago). Fix delivery before they go quiet                                          |
| Workshop 0301   | Gurgaon           | Rs 20.7k   |            6 |           4 | 4 orders in a row undelivered - our failure, and they are still enquiring (last order 6d ago). Fix delivery before they go quiet; 21% of last month's lines were returned |
| Workshop 0094   | Insurance & Fleet | Rs 11.82 L |            0 |           7 | 7 orders in a row undelivered - our failure, and they are still enquiring (last order 0d ago). Fix delivery before they go quiet                                          |
| Workshop 0247   | Noida             | Rs 55.9k   |            3 |          13 | 13 orders in a row undelivered - our failure, and they are still enquiring (last order 3d ago). Fix delivery before they go quiet                                         |
| Workshop 0326   | Noida             | Rs 20.8k   |            8 |          13 | 13 orders in a row undelivered - our failure, and they are still enquiring (last order 8d ago). Fix delivery before they go quiet                                         |

### P3
176 customers, Rs 1.70 Cr of revenue. Reported in aggregate only - never listed individually, because nothing needs to be done about them.
