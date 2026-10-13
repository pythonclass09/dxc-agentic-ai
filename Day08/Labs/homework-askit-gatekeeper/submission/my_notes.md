# My notes

Q1. D1 = no, D2 = on-call, D3 = 30 days. I chose no because a VIP reading a ticket or knowledge item is a low-risk action; I chose on-call because urgent night writes should still go to a live person rather than wait until morning; I chose 30 days as a practical retention window that balances helpful memory with privacy and operational risk.

Q2. I would never let an LLM decide whether to persist sensitive data in long-term memory on its own. The safe-to-remember rule is a high-stakes privacy control; a mistake can leak secrets or regulated data, so the decision should be deterministic and policy-driven, not model-generated.

Q3. I edited the spec first and then the code. The spec is the source of truth: it defines the policy, edge cases, and acceptance criteria, and changing code before the policy creates a mismatch that is hard to validate or defend.
