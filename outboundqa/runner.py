"""Run the gate over a batch of agent-drafted messages and summarize."""
from .checks import evaluate_draft


def run_gate(drafts, businesses):
    by_name = {b.name: b for b in businesses}
    verdicts = []
    for d in drafts:
        biz = by_name.get(d.business)
        if biz is None:
            from .models import Flag, Verdict
            verdicts.append(Verdict(draft=d, passed=False,
                                    flags=[Flag("unknown_business", "block", f"no facts on file for {d.business!r}")]))
            continue
        verdicts.append(evaluate_draft(d, biz))
    summary = {
        "drafts": len(verdicts),
        "passed": sum(1 for v in verdicts if v.passed),
        "blocked": sum(1 for v in verdicts if not v.passed),
        "warned": sum(1 for v in verdicts if v.passed and v.flags),
    }
    return verdicts, summary
