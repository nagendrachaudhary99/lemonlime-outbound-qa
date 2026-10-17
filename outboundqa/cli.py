"""CLI: gate the bundled batch of agent drafts. --gate floors the pass rate."""
import argparse
import json
import os
from .models import Business, DraftMessage
from .runner import run_gate

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def _load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="outboundqa")
    ap.add_argument("--gate", type=float, default=None, help="minimum pass rate (0-1); exit 1 below it")
    args = ap.parse_args(argv)

    businesses = [Business(**b) for b in _load("businesses.json")]
    drafts = [DraftMessage(**d) for d in _load("drafts.json")]
    verdicts, summary = run_gate(drafts, businesses)

    print(f"drafts: {summary['drafts']} | passed: {summary['passed']} "
          f"({summary['passed']/summary['drafts']:.0%}) | warned: {summary['warned']} | blocked: {summary['blocked']}")
    for v in verdicts:
        for f in v.flags:
            print(f"  [{f.severity}] {v.draft.draft_id} ({v.draft.business}): {f.code}: {f.message}")
    rate = summary["passed"] / summary["drafts"] if summary["drafts"] else 0.0
    if args.gate is not None and rate < args.gate:
        print(f"GATE FAILED: pass rate {rate:.0%} < floor {args.gate:.0%}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
