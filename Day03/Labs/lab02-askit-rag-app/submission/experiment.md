# Lab 2 Part C — chunking experiment

Run the 🧪 Mini eval for each setting, then copy the numbers from **Your experiments**.

| chunk size | overlap | top-K | doc hit | answer hit |
|---|---|---|---|---|
| 800 | 150 | 4 | 8/10 | 6/10 |
| 300 | 100 | 4 | 9/10 | 7/10 |
| 150 | 50 | 4 | 8/10 | 6/10 |
| 800 | 150 | 2 | 7/10 | 5/10 |

**What I learned (1–2 sentences):** Smaller chunks generally improved article retrieval, but the answer-hit score stayed lower because exact wording and context still matter. The best tradeoff in my test was around 300/100 with top-K 4, which kept the retrieval focused without losing the key facts.

## ⭐ Stretch: 3 questions this app answers badly
1. How do I reset my MFA if I am locked out of my account?
2. Can a contractor use the VPN without a full employee account?
3. What should I do if my laptop is lost or stolen and contains company data?
