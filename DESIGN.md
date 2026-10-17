# DESIGN: Outbound QA Gate

## Problem

Fully-automated GTM means the agent, not the business owner, writes the message. The failure mode is asymmetric: a hundred decent drafts build nothing, and one draft that invents a discount, breaks a compliance rule, or reads like a spammer burns the business's reputation with its own customers. Automation at this layer needs a gate that assumes the generator will sometimes be wrong.

## Architecture

```
agent drafts -> gate (grounding, voice, compliance) -> send | return with reasons
```

**The fact store is the contract.** A business's declared facts (prices, hours, specials, insurance accepted) are the ONLY source a message may claim from. This turns "is this draft truthful?" into a checkable containment question instead of a judgment call. When the store has no entry for a business, the gate blocks - an agent may not speak for a business it knows nothing about.

**Three check families, different severity philosophies.** Grounding and compliance block: an untrue claim or a CAN-SPAM violation is never a judgment call. Voice warns: "pushy" is a spectrum, and the business's own voice notes are the reference. The split is deliberate - the gate blocks on facts, advises on taste.

**Deterministic over smart.** Regex-level claim extraction misses paraphrases; the design accepts that. A semantic claim-matcher (embeddings or an LLM judge) is the documented next tier, and it would slot behind the same Flag/Verdict interface - but the first line of defense must be a check nobody has to trust, only verify.

## Key decisions

- **Fail toward the business, not the sender.** A blocked good draft costs a regeneration; a sent bad one costs a customer relationship. Every ambiguity resolves to block or warn-with-log, never silent pass.
- **Reasons travel with the block.** Every flag carries the exact claim and the fact gap, so the drafter (human or agent) can fix it in one iteration.
- **Pass-rate as a health metric, not a target.** The CI gate floors the pass rate on a known batch so a drafter regression (a prompt change that starts inventing offers) fails the build. A 100% pass rate on real traffic would be suspicious, not good - it would mean the gate stopped being tested.

## Failure handling

- Claims are extracted with claim markers ($, %, free, discount, guarantee, best, #1); text without markers carries no checkable offer and passes grounding by construction.
- All-caps detection requires 2+ words to avoid false-warning on legitimate short emphasis.
- PII detection is pattern-based and intentionally over-broad; it blocks and a human clears false positives.

## Scaling

- **LLM drafter behind the gate:** the gate's input is a fixed DraftMessage shape; a drafter change touches nothing here. Measure drafter quality by watching block rates over time.
- **Semantic grounding tier:** embedding match of claims against the fact store, calibrated so its false-block rate is measured before it can block alone.
- **Per-channel policies:** SMS/email/DM rules become data (length, required disclosures), not code branches.
- **Learning voice:** voice notes today are hand-written; a future step infers them from the business's past sent messages, still as data the gate checks against.

## Known limits

- Claim extraction is pattern-based; "half price" slips through where "50% off" is caught.
- Facts are key-value strings; structured offers (date-bounded specials) are not modeled.
- No send integration: the gate stops at cleared/blocked, wiring to an ESP is downstream.
