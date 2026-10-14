# Lab 9 answers

Saved 2026-10-13 13:11 · model: AWS Bedrock

**Q1. Same agent, three homes (tab 2): what changed in the answer, and what changed in the speed? Why?**

 The answer stayed the same; only the speed changed.
stdio was fastest, HTTP slower, and Lambda slowest

**Q2. In tab 3 which description made the model pick a wrong tool? Why is a description part of your security design?**

The vague/misleading/too-long description set caused wrong tool picks.
A tool description is part of security because it controls what the model is allowed to discover and choose, so bad descriptions can expose or misroute actions

**Q3. In tab 6 which timeout and retry settings did you choose, and what would you tell the user if the tool still fails?**

 Use the settings that made the call finish within the limit: 
client timeout 3s and retries tuned to beat the slow/flaky server.
If it still fails, tell the user the ticket system is busy, wait a moment, and try again.
