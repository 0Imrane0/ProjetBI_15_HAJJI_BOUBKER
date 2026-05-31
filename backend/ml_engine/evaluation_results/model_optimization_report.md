# Model Evaluation and Optimization Report

## Project Objective

The goal of the recommendation engine is to suggest the most relevant Metabase
reports for each BI user from historical navigation behavior and report
metadata.

This evaluation answers one practical question: which model should power the
API and stored batch recommendations for the local demo?

## Evaluation Setup

- Data source: PostgreSQL tables `navigation_logs` and `reports`
- Interactions: 9,911 navigation events
- Users: 100
- Reports: 40
- Split strategy: temporal train/test split per user
- Train events: 7,891
- Test events: 2,020
- Evaluated users: 100

The temporal split is important because the model learns from older events and
is evaluated against later user behavior. This is closer to the real production
problem than a random split.

## Metrics

- Precision@K: among the K recommended reports, how many were actually relevant?
- Recall@K: among the relevant reports, how many did we recover?
- HitRate@K: did the user receive at least one relevant recommendation?
- NDCG@K: were relevant reports ranked near the top?
- Catalog Coverage@K: how much of the report catalog appears in recommendations?

## Final Offline Results

| Model | K | Precision@K | Recall@K | HitRate@K | NDCG@K | Coverage@K |
|---|---:|---:|---:|---:|---:|---:|
| hybrid_knn_content | 5 | 0.140 | 0.062 | 0.49 | 0.132 | 0.875 |
| tuned_surprise_svd | 5 | 0.130 | 0.056 | 0.50 | 0.121 | 0.625 |
| tuned_surprise_knn | 5 | 0.124 | 0.053 | 0.47 | 0.132 | 0.950 |
| baseline_user_based_cf | 5 | 0.124 | 0.054 | 0.48 | 0.120 | 0.575 |
| content_based_tfidf | 5 | 0.122 | 0.054 | 0.49 | 0.119 | 0.750 |
| tuned_surprise_knn | 10 | 0.117 | 0.102 | 0.69 | 0.128 | 0.950 |
| hybrid_knn_content | 10 | 0.116 | 0.101 | 0.70 | 0.121 | 0.950 |
| content_based_tfidf | 10 | 0.114 | 0.099 | 0.71 | 0.116 | 0.925 |
| tuned_surprise_svd | 10 | 0.106 | 0.092 | 0.69 | 0.109 | 0.925 |
| baseline_user_based_cf | 10 | 0.106 | 0.092 | 0.69 | 0.110 | 0.925 |

## Selected Model

Selected model: `hybrid_knn_content`

Configuration:

- Collaborative component: Surprise KNN
- Content component: TF-IDF report profile
- Collaborative weight: 0.6
- Content weight: 0.4

Why this model:

- Best Precision@5, which matters because the API returns top-5 recommendations.
- Strong NDCG@5, meaning relevant reports are ranked near the top.
- Good catalog coverage at top-5, avoiding over-recommendation of only a few
  popular reports.
- More robust than pure collaborative filtering because report metadata helps
  when user behavior alone is limited.

## A/B Test Proposal

For a future live validation, split users into two groups:

- Group A: current Metabase experience or popularity baseline
- Group B: hybrid recommendations

Recommended online metrics:

- Click-through rate on recommended reports
- Repeat usage of recommended reports within 7 days
- Average dwell time after recommendation click
- User-level diversity of consumed reports
- Manual feedback if available: useful / not useful

Suggested rollout:

1. Start with 20% of users in Group B.
2. Monitor for one week.
3. Increase to 50% if CTR and repeat usage improve.
4. Roll back if recommendations concentrate too much on the same reports.

## Current Limitations

- Durations are simulated because Metabase does not expose reliable dwell time
  in the available logs.
- The dataset is synthetic/small: 100 users and 40 reports.
- Report metadata quality strongly affects content-based performance.
- Offline metrics estimate relevance but do not replace real user feedback.

## Optimization Roadmap

Short term:

- Keep `hybrid_knn_content` as the serving model.
- Use batch recommendations for demo stability and fast API reads.
- Track clicked recommendations in the `recommendations.clicked` column.

Medium term:

- Add real client-side events for view start, view end, and dwell time.
- Improve report descriptions and business categories.
- Add freshness features so recent reports can be promoted.

Long term:

- Add online feedback loops from clicks and dismissals.
- Compare matrix factorization, item-item KNN, and learning-to-rank.
- Add drift monitoring for users, reports, and category popularity.
