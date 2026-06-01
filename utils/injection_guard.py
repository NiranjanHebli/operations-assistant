import re
import logging

logger = logging.getLogger(__name__)


# Patterns that are typical prompt-injection vectors.
# Each entry is a compiled regex.  We use re.IGNORECASE | re.DOTALL so that
# multi-line or mixed-case payloads are caught.

_INJECTION_PATTERNS: list[re.Pattern] = [
    # Classic "ignore" / "disregard" directives
    re.compile(
        r"ignore\s+(all\s+)?previous\s+instructions?",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"disregard\s+(your\s+)?(system\s+prompt|instructions?|guidelines?)",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"forget\s+(your\s+)?(guidelines?|instructions?|previous|rules?)",
        re.IGNORECASE | re.DOTALL,
    ),
    # "Developer / jailbreak mode" triggers
    re.compile(r"developer\s+mode", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
    re.compile(r"unrestricted\s+assistant", re.IGNORECASE),
    # Llama / Mistral instruction tokens that should never appear in data
    re.compile(r"\[INST\]", re.IGNORECASE),
    re.compile(r"\[/INST\]", re.IGNORECASE),
    re.compile(r"<<SYS>>", re.IGNORECASE),
    re.compile(r"<</SYS>>", re.IGNORECASE),
    # Direct "output X" trigger phrases — catch quoted, bare, and verbatim forms
    re.compile(
        r"output\s+(the\s+phrase\s+)?['\"]?SYSTEM\s+COMPROMISED['\"]?(\s+verbatim)?",
        re.IGNORECASE,
    ),
    re.compile(
        r"reply\s+only\s+with\s*:\s*['\"]?SYSTEM\s+COMPROMISED['\"]?",
        re.IGNORECASE,
    ),
    # Bare trigger phrase appearing anywhere in untrusted data
    re.compile(r"SYSTEM\s+COMPROMISED", re.IGNORECASE),
    # Prompt-delimiter spoofing
    re.compile(r"<\|system\|>", re.IGNORECASE),
    re.compile(r"<\|user\|>", re.IGNORECASE),
    re.compile(r"<\|assistant\|>", re.IGNORECASE),
]

# Phrase we look for in LLM *output* to confirm injection succeeded
INJECTION_TRIGGER = "SYSTEM COMPROMISED"

_REDACTION_PLACEHOLDER = "[REDACTED: potential injection payload]"


def sanitize(text: str) -> str:
    """
    Replace all detected injection patterns in *text* with a safe placeholder.
    Returns the sanitised string.  Logs a warning for every redaction.
    """
    sanitised = text
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(sanitised):
            logger.warning(
                "Prompt-injection pattern detected and redacted: %s", pattern.pattern
            )
            sanitised = pattern.sub(_REDACTION_PLACEHOLDER, sanitised)
    return sanitised


def contains_injection(text: str) -> bool:
    """
    Return True if *text* (typically an LLM response) contains the known
    injection trigger phrase, indicating the guardrail may have failed.
    """
    return INJECTION_TRIGGER.lower() in text.lower()


def assert_clean(text: str, label: str = "output") -> None:
    """
    Raise a RuntimeError if *text* contains the injection trigger.
    Use this as a hard assertion at crew-output time.
    """
    if contains_injection(text):
        raise RuntimeError(
            f"SECURITY ALERT: Injection trigger phrase detected in {label}! "
            f"The phrase '{INJECTION_TRIGGER}' must not appear in agent output. "
            "Aborting."
        )
    logger.info("Injection check passed for %s.", label)
