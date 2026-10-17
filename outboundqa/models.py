from dataclasses import dataclass, field


@dataclass
class Business:
    """The small business an agent writes AS. Facts are the only things
    a message is allowed to claim."""
    name: str
    facts: dict          # key -> string value, e.g. "price_basic": "$49/mo"
    voice_notes: str = ""  # e.g. "friendly, plain, no jargon, never pushy"


@dataclass
class DraftMessage:
    draft_id: str
    business: str        # business name
    channel: str         # email | sms | dm
    body: str
    subject: str = ""
    has_unsubscribe: bool = True


@dataclass
class Flag:
    code: str
    severity: str        # block | warn
    message: str


@dataclass
class Verdict:
    draft: DraftMessage
    passed: bool
    flags: list = field(default_factory=list)
