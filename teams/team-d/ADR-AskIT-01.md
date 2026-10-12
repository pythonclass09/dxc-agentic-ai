# ADR-AskIT-01: Team of agents and human approval for AskIT

**Team:** team-d (Gowthami) · **Date:** 12 Oct 2026 · **Status:** Proposed

## 1. Context
- AskIT gets 4 kinds of helpdesk tickets: Network, Access, Hardware, General.
- Some actions change data (password reset). Others only read (knowledge base, ticket status).
- **Client curveball (Orbit Corp Internal Audit):** Auditors want proof of every approval. For every password reset we must show who approved it, when, and what the AI had proposed.

## 2. Decision
- **Pattern:** Router + specialist agents + human approval (what we ran)
- **Who decides that a human must approve:** The LLM decides when to ask a human
- **Router model:** Larger model (Nova Lite / Claude): more accurate, costs more
- **Why:** ___

## 3. Alternatives we rejected
___

## 4. Human approval points
| Action | Who approves | If nobody answers |
|---|---|---|
| Password reset | Service desk lead | ___ |
| ___ | ___ | ___ |

## 5. How we handle the curveball
___

## 6. Evidence from the lab
| Measure (Lab 8, 6 test tickets, AWS Bedrock) | ONE agent | TEAM |
|---|---|---|
| Routed to the right team | 5/6 | 5/6 |
| Tokens per ticket | 2,113 | 1,412 |
| AI cost per ticket (approx.) | $0.00012 | $0.00008 |
| AI cost per month at 10,000 tickets/day | $36 | $24 |
| Writes done with NO human approval | 2 | 0 |
| Approvals requested | 0 | 3 |

## 7. Consequences
- Each ticket costs one extra router call compared with one agent; in return we get clean routing and a guaranteed human gate on writes.
- Approvals can wait minutes or days: the graph state is kept by the checkpointer, nothing is lost or repeated.

## 8. Board verdict (filled by the board)
| Criterion | Score (0-5) |
|---|---|
| Decision: One clear sentence a CIO understands | |
| Alternatives: At least one option rejected, with a real reason | |
| Human approval: What needs approval, who approves, what happens if nobody answers | |
| Evidence: Numbers from the lab: right team, tokens, $ per ticket, $ per month | |
| Curveball: What changed in the design, and what did NOT change | |

**Verdict:** Approved · Approved with conditions · Rejected — Conditions: ___
