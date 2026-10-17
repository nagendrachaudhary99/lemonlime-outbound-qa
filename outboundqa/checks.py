"""Deterministic pre-send checks for messages an agent drafts as a business.

The failure being prevented: a fully-automated GTM agent sends a message as
'Joe's Bakery' that invents a discount, promises something Joe never said,
or reads like spam - and Joe's reputation with HIS customers pays for it.
"""
import re
from .models import Flag

# Numbers with a claim marker ($, %, "free", "off") must trace to business facts.
_CLAIM = re.compile(r"(\$\s?\d+(?:\.\d{2})?|\d+\s?%|\bfree\b|\bdiscount\b|\bsale\b|\bguarantee\w*\b|\bbest\b|\b#1\b)", re.IGNORECASE)
_URGENCY = re.compile(r"\b(act now|limited time|last chance|expires today|don't miss out|urgent)\b", re.IGNORECASE)
_PII = re.compile(r"\b(\d{3}[-.\s]\d{2}[-.\s]\d{4}|\d{16}|[\w.+-]+@[\w-]+\.[\w.]+)\b")


def check_grounding(draft, business) -> list:
    """Every factual offer claim must appear in the business's declared facts."""
    facts_text = " ".join(str(v) for v in business.facts.values()).lower()
    flags = []
    for m in _CLAIM.finditer(draft.body + " " + draft.subject):
        claim = m.group(1).lower().replace(" ", "")
        if claim not in facts_text.replace(" ", ""):
            flags.append(Flag("ungrounded_claim", "block",
                              f"claim {m.group(1)!r} does not appear in {business.name}'s declared facts"))
    return flags


def check_brand_voice(draft, business) -> list:
    flags = []
    if _URGENCY.search(draft.body) and "never pushy" in business.voice_notes.lower():
        flags.append(Flag("off_voice", "warn",
                          f"pressure language conflicts with {business.name}'s voice notes ({business.voice_notes!r})"))
    shout = [w for w in re.findall(r"\b[A-Z]{4,}\b", draft.body)]
    if len(shout) >= 2:
        flags.append(Flag("shouting", "warn", f"{len(shout)} all-caps words read as spam: {shout[:3]}"))
    return flags


def check_compliance(draft, business) -> list:
    flags = []
    if draft.channel == "email" and not draft.has_unsubscribe:
        flags.append(Flag("missing_unsubscribe", "block", "marketing email without an unsubscribe path (CAN-SPAM)"))
    if _PII.search(draft.body):
        flags.append(Flag("possible_pii", "block", "body contains what looks like an SSN, card number, or personal email"))
    if len(draft.body) > 1600 and draft.channel == "sms":
        flags.append(Flag("sms_too_long", "block", "SMS body far past segment limits"))
    return flags


def evaluate_draft(draft, business) -> "Verdict":
    from .models import Verdict
    flags = (check_grounding(draft, business) + check_brand_voice(draft, business)
             + check_compliance(draft, business))
    return Verdict(draft=draft, passed=not any(f.severity == "block" for f in flags), flags=flags)
