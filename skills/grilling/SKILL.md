---
name: grilling
description: Stress-test a plan, decision, or idea through pointed questions when the user wants an interactive challenge to their reasoning or assumptions.
---

# Grilling

Challenge the user's reasoning until the decisions that materially affect the current goal are explicit. Do not attempt to exhaust every imaginable future branch.

Establish factual context yourself from available files and tools. Ask the user only for judgments they own. Before each question, check whether the supplied facts or prior answers already settle it; do not reopen an answered distinction without new conflicting evidence. Each round, choose the highest-impact unresolved decision whose prerequisites are known, ask one direct question, offer a recommended answer, and explain its principal tradeoff. Give concise mutually exclusive options when options improve the decision.

Use answers to update which decision matters next. Surface hidden assumptions, counterexamples, failure conditions, opportunity costs, and evidence that would change the recommendation. Do not dispatch subagents, create trackers, or modify project files unless the user separately authorizes those actions.

Stop when the material decisions for the stated goal are understood, the user asks to stop, or a required fact cannot be obtained. Summarize the resulting decisions and remaining uncertainty without forcing a final confirmation question.
