# Outbound QA Gate for Fully-Automated GTM

[![CI](https://github.com/nagendrachaudhary99/lemonlime-outbound-qa/actions/workflows/ci.yml/badge.svg)](https://github.com/nagendrachaudhary99/lemonlime-outbound-qa/actions/workflows/ci.yml)

"Fully automated GTM, no work required" means an agent writes and sends sales and marketing messages AS a small business - as Joe's Bakery, to Joe's customers, in Joe's name. One invented discount or pushy off-brand message, and Joe's reputation pays for the agent's mistake. This repo is the pre-send quality gate: nothing an agent drafts goes out until it passes checks for factual grounding, brand voice, and compliance.

## The checks

| check | verdict | what it catches |
|---|---|---|
| ungrounded_claim | block | "50% off everything" when the business never declared a 50% discount |
| missing_unsubscribe | block | marketing email with no unsubscribe path (CAN-SPAM) |
| possible_pii | block | SSN / card-number / personal-email patterns in a draft |
| sms_too_long | block | SMS body past segment limits |
| off_voice | warn | "ACT NOW, LIMITED TIME" from a business whose voice notes say never pushy |
| shouting | warn | all-caps spam patterns |

Blocking rule: any `block` flag stops the send and routes the draft back with the reason. Warnings go out with the message logged. A draft for a business with no facts on file is blocked outright - the agent may not write as a business it knows nothing about.

## Run it

```bash
pip install pytest
python -m pytest tests/ -q            # 11 tests
python -m outboundqa.cli --gate 0.4   # gate the bundled batch; CI runs this
```

Verified output on the bundled batch (5 agent drafts for 2 businesses):

```
drafts: 5 | passed: 2 (40%) | warned: 0 | blocked: 3
  [block] D2 (Joe's Bakery): ungrounded_claim: claim 'FREE' does not appear in Joe's Bakery's declared facts
  [warn]  D2 (Joe's Bakery): off_voice: pressure language conflicts with voice notes ('never pushy')
  [block] D3 (Bright Smile Dental): missing_unsubscribe
  [block] D5 (Joe's Bakery): ungrounded_claim: claim '50%' does not appear in declared facts
```

The two honest, on-brand drafts pass; the invented-discount, missing-unsubscribe, and spam-voice drafts are stopped with reasons. That ratio is the point of the gate: in a fully-automated system, most agent output is fine and some of it must never send.

## What's real vs. mocked

| Component | Status |
|---|---|
| Grounding / voice / compliance checks | Real, tested (11 tests in CI) |
| Business fact store as the only allowable claim source | Real (`data/businesses.json`) |
| Block/warn routing + pass-rate CI gate | Real |
| The drafting agent | **Not included** - the gate consumes drafts in a fixed shape; any generator (LLM or template) can feed it |
| Send integration | **Not included** - "passed" means cleared to send; nothing is sent |

Architecture and where the LLM drafter plugs in: [DESIGN.md](DESIGN.md).

Built by [Nagendra Chaudhary](https://www.linkedin.com/in/nagendra-nc/) - [nagendrachaudhary0308@gmail.com](mailto:nagendrachaudhary0308@gmail.com)
