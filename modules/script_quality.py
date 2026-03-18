"""
Script Quality Checker
Validates and scores scripts before video creation.
Ensures hooks are strong, length is right, and content is engaging.
"""

import re
from typing import Tuple
from modules.ai_engine import ask_gemini
from utils import get_logger

log = get_logger("quality")

# Ideal ranges
MIN_WORDS = 40
MAX_WORDS = 100
MIN_SENTENCES = 3
MAX_SENTENCES = 12
IDEAL_HOOK_MAX_WORDS = 12


def check_word_count(script: str) -> Tuple[bool, str]:
    """Check if script word count is in the ideal range."""
    words = len(script.split())
    if words < MIN_WORDS:
        return False, f"Too short ({words} words, need {MIN_WORDS}+)"
    if words > MAX_WORDS:
        return False, f"Too long ({words} words, max {MAX_WORDS})"
    return True, f"Word count OK ({words})"


def check_hook_strength(script: str) -> Tuple[bool, str]:
    """Check if the opening hook is strong."""
    first_sentence = script.split(".")[0].strip() if "." in script else script[:60]
    word_count = len(first_sentence.split())

    if word_count > IDEAL_HOOK_MAX_WORDS:
        return False, f"Hook too long ({word_count} words, max {IDEAL_HOOK_MAX_WORDS})"

    # Check for weak openings
    weak_starts = ["hi", "hello", "welcome", "today", "in this video", "so", "well",
                   "let me", "i want to", "have you ever"]
    first_lower = first_sentence.lower()
    for weak in weak_starts:
        if first_lower.startswith(weak):
            return False, f"Weak hook start: '{weak}...'"

    return True, f"Hook looks strong ({word_count} words)"


def check_has_question(script: str) -> Tuple[bool, str]:
    """Check if script ends with a question (for engagement/loop)."""
    last_sentence = script.strip().split(".")[-1].strip()
    if not last_sentence:
        sentences = script.strip().split(".")
        last_sentence = sentences[-2].strip() if len(sentences) > 1 else ""

    has_question = "?" in script[-100:]  # Check last 100 chars
    if has_question:
        return True, "Ends with engagement question"
    return False, "Missing engagement question at the end"


def check_no_filler(script: str) -> Tuple[bool, str]:
    """Check for filler words that hurt retention."""
    filler_words = ["basically", "actually", "literally", "kind of", "sort of",
                    "you know", "like", "um", "uh", "so yeah"]
    found = []
    lower = script.lower()
    for filler in filler_words:
        if filler in lower:
            found.append(filler)

    if found:
        return False, f"Filler words found: {', '.join(found)}"
    return True, "No filler words"


def validate_script(script: str) -> dict:
    """
    Run all quality checks on a script.
    Returns dict with overall score and details.
    """
    checks = {
        "word_count": check_word_count(script),
        "hook_strength": check_hook_strength(script),
        "engagement_question": check_has_question(script),
        "no_filler": check_no_filler(script),
    }

    passed = sum(1 for ok, _ in checks.values() if ok)
    total = len(checks)
    score = round((passed / total) * 100)

    result = {
        "score": score,
        "passed": passed,
        "total": total,
        "checks": {name: {"pass": ok, "message": msg} for name, (ok, msg) in checks.items()},
        "approved": score >= 50,  # At least half must pass
    }

    log.info(f"Script quality: {score}% ({passed}/{total} checks passed)")
    for name, (ok, msg) in checks.items():
        icon = "✓" if ok else "✗"
        log.debug(f"  {icon} {name}: {msg}")

    return result


def ai_quality_score(script: str) -> int:
    """Use AI to score the script 1-10."""
    prompt = f"""Rate this YouTube Shorts script from 1-10 for viral potential.

SCRIPT: {script}

Consider:
- Hook strength (does it stop the scroll?)
- Curiosity (does it create an open loop?)
- Pacing (short punchy sentences?)
- Twist (is there a surprising element?)
- Engagement (does it encourage comments/shares?)

Return ONLY a single number from 1 to 10. Nothing else:"""

    response = ask_gemini(prompt)
    try:
        # Extract number from response
        numbers = re.findall(r'\d+', response)
        if numbers:
            score = int(numbers[0])
            return min(max(score, 1), 10)
    except Exception:
        pass
    return 5  # Default middle score


def improve_script(script: str, issues: list) -> str:
    """Ask AI to fix specific issues in the script."""
    issues_text = "\n".join([f"- {issue}" for issue in issues])

    prompt = f"""Rewrite this YouTube Shorts script fixing these issues:

ISSUES:
{issues_text}

CURRENT SCRIPT:
{script}

Rules:
- Keep it 60-80 words
- Strong hook under 10 words
- End with an engagement question
- No filler words
- Short punchy sentences

Return ONLY the rewritten script, nothing else:"""

    improved = ask_gemini(prompt)
    if improved and len(improved) > 20:
        return improved
    return script  # Return original if improvement fails


if __name__ == "__main__":
    test_script = (
        "This AI just replaced 1000 employees overnight. "
        "A major tech company quietly deployed an AI system that handles "
        "all customer support. The crazy part? Customer satisfaction actually "
        "went up by 30 percent. Nobody noticed the difference. "
        "What job do you think AI will replace next?"
    )

    print("Validating script...")
    result = validate_script(test_script)
    print(f"\nScore: {result['score']}%")
    for name, check in result["checks"].items():
        icon = "✓" if check["pass"] else "✗"
        print(f"  {icon} {name}: {check['message']}")
