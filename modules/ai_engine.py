"""
AI Engine - Gemini Integration
Handles all AI generation: ideas, scripts, SEO, hook optimization.
Uses the Gemini API via Google's REST endpoint.

STRATEGY: English scripts + Hindi voice = best quality + maximum reach
"""

import re

import requests

from config.settings import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_URL
from utils import get_logger

log = get_logger("ai_engine")


def ask_gemini(prompt: str, max_retries: int = 3) -> str:
    """Send a prompt to Gemini and return the generated text."""
    if not GEMINI_API_KEY:
        log.error("Missing GEMINI_API_KEY. Add it to your environment or config/settings.py")
        return ""

    url = f"{GEMINI_URL}/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.8,
            "topP": 0.9,
            "maxOutputTokens": 1500,
        },
    }

    for attempt in range(max_retries):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=180)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    text = "".join(part.get("text", "") for part in parts).strip()
                    if text:
                        return text
                log.warning("Gemini response did not contain text content")
            else:
                log.warning(f"Gemini returned status {resp.status_code}: {resp.text[:300]}")
        except Exception as exc:
            log.warning(f"Gemini attempt {attempt + 1} failed: {exc}")

    return ""


def generate_viral_idea(trending_topics: list, niche: dict) -> str:
    """Generate a viral YouTube Shorts idea from trending topics."""
    topics_text = "\n".join([f"- {t['title']}" for t in trending_topics[:10]])
    niche_name = niche.get("name", "Technology")
    keywords = ", ".join(niche.get("keywords", []))

    prompt = f"""You are a viral YouTube Shorts content strategist.

TRENDING TOPICS RIGHT NOW:
{topics_text}

YOUR NICHE: {niche_name}
KEYWORDS: {keywords}

Generate ONE viral YouTube Shorts video idea in ENGLISH.

Rules:
- Must be SHOCKING, curious, or surprising
- Must target young audience (18-35 age)
- Must make people STOP scrolling
- Must create curiosity gap
- Under 12 words
- Write in ENGLISH only

Good examples:
- "AI Just Replaced 10 Million Jobs And Nobody Noticed"
- "This Psychology Trick Makes Anyone Trust You Instantly"
- "Scientists Found Something Terrifying Under The Ocean"
- "The Dark Secret Behind Every Billionaire Success Story"

Return ONLY the video idea title (one line, English). Nothing else:"""

    idea = ask_gemini(prompt)
    idea = idea.strip().strip('"').strip("'").strip("*").strip("#")
    lines = idea.split("\n")
    idea = lines[0].strip() if lines else idea
    idea = re.sub(r'^\d+[\.\)]\s*', '', idea)

    log.info(f"Generated idea: {idea}")
    return idea


def generate_script(idea: str) -> str:
    """Generate a 45-55 second YouTube Shorts script in English."""
    prompt = f"""You are an expert YouTube Shorts scriptwriter. Write scripts that get MILLIONS of views.

VIDEO IDEA: {idea}

Write a YouTube Shorts script. Target duration: 45-55 seconds when spoken.
That means exactly 120-150 words.

VIRAL SCRIPT STRUCTURE:

HOOK (0-3 sec): One shocking sentence that stops the scroll. Under 12 words.

CURIOSITY (4-10 sec): Create an open loop. Tease what's coming. Make them NEED to keep watching.

BODY (11-35 sec): Deliver the main content in SHORT punchy sentences.
- Each sentence 5-10 words MAX
- Use numbers and specific facts
- Create mini-cliffhangers between sentences
- Build tension gradually

TWIST (36-48 sec): Reveal something unexpected. The "wait, WHAT?" moment.

CTA (49-55 sec): End with a provocative question that forces comments.

STRICT RULES:
- Write ONLY the spoken words
- NO labels (no "HOOK:", "BODY:", etc.)
- NO stage directions
- NO asterisks or formatting
- Short punchy sentences ONLY
- Every single sentence must add value
- Use dramatic pauses (new sentence = pause)
- Total: 120-150 words exactly
- Language: ENGLISH only
- Sound like a confident, dramatic narrator
- Make the listener feel like they're learning a SECRET

Write the script now:"""

    script = ask_gemini(prompt)
    lines = script.split("\n")
    clean_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        skip_patterns = [
            "HOOK:", "CURIOSITY:", "BODY:", "TWIST:", "CTA:",
            "Hook:", "Curiosity:", "Body:", "Twist:", "Cta:",
            "EXPLANATION:", "LOOP:", "OPENING:", "CLOSING:",
            "**", "##", "---", "```", "Scene", "SCENE",
            "[", "(Note", "(note", "Word count",
        ]
        should_skip = False
        for pattern in skip_patterns:
            if line.startswith(pattern):
                line = line.replace(pattern, "")
                if not line.strip():
                    should_skip = True
        if should_skip:
            continue

        line = line.strip().strip("*").strip("#").strip("-").strip('"').strip()
        line = re.sub(r'^\d+[\.\)]\s*', '', line)
        line = re.sub(r'\[.*?\]', '', line)
        line = re.sub(r'\(.*?\)', '', line)
        line = line.strip()
        if line and len(line) > 3:
            clean_lines.append(line)

    script = " ".join(clean_lines)
    log.info(f"Generated script ({len(script.split())} words): {script[:120]}...")
    return script


def optimize_hook(script: str) -> str:
    """Rewrite the hook (first sentence) to maximize retention."""
    sentences = re.split(r'[.!?]', script)
    first_sentence = sentences[0].strip() if sentences else script[:60]

    prompt = f"""You are the world's best YouTube Shorts hook writer.

CURRENT HOOK: "{first_sentence}"

Rewrite this hook to be IMPOSSIBLY viral. It must stop someone mid-scroll.

Rules:
- Maximum 10 words
- Must create INSTANT curiosity
- Must feel like a secret being revealed
- Use power words: "shocking", "never", "secret", "just discovered", "nobody knows"
- Language: ENGLISH only

Best performing hook patterns:
- "Nobody is talking about this [shocking thing]"
- "This [thing] just changed everything we know"
- "You've been lied to about [topic] your whole life"
- "Scientists just discovered something terrifying"
- "This is why [surprising claim]"

Return ONLY the new hook. One sentence. Nothing else:"""

    new_hook = ask_gemini(prompt)
    new_hook = new_hook.strip().strip('"').strip("'").split("\n")[0]
    new_hook = re.sub(r'^\d+[\.\)]\s*', '', new_hook).strip()

    if new_hook and len(new_hook) > 5 and len(new_hook.split()) <= 15:
        rest_parts = re.split(r'[.!?]', script, 1)
        rest = rest_parts[1].strip() if len(rest_parts) > 1 else ""
        if rest:
            script = f"{new_hook}. {rest}"
        else:
            script = f"{new_hook}. {script}"

    log.info(f"Optimized hook: {new_hook}")
    return script


def generate_seo(idea: str, script: str) -> dict:
    """Generate SEO metadata. ALWAYS IN ENGLISH."""
    prompt = f"""You are a YouTube SEO expert who creates viral titles.

VIDEO IDEA: {idea}
SCRIPT PREVIEW: {script[:250]}

Generate SEO metadata in ENGLISH for this YouTube Shorts video.

Return in this EXACT format:
TITLE: [clickbait English title, under 55 chars, start with emoji, end with #Shorts]
DESCRIPTION: [3 English sentences with keywords, end with hashtags]
TAGS: [20 comma-separated English tags]
HASHTAGS: #Shorts #Viral #Facts #Trending #MindBlown #Amazing #Education

Examples of PERFECT titles:
TITLE: 😱 AI Just Stole 10 Million Jobs Overnight #Shorts
TITLE: 🧠 This Mind Trick Controls Anyone Instantly #Shorts
TITLE: 💰 Why Rich People Wake Up At 4AM #Shorts
TITLE: 🔬 Scientists Found Something Terrifying #Shorts

Return ONLY the metadata:"""

    response = ask_gemini(prompt)
    seo = {
        "title": f"😱 {idea} #Shorts",
        "description": f"{idea}. Watch this incredible short! #Shorts #Viral #Facts",
        "tags": [
            "shorts", "viral", "facts", "trending", "amazing", "mind blown",
            "education", "science", "technology", "motivation",
        ],
        "hashtags": ["#Shorts", "#Viral", "#Facts", "#Trending", "#Amazing"],
    }

    for line in response.split("\n"):
        line = line.strip()
        if line.upper().startswith("TITLE:"):
            title = line.split(":", 1)[1].strip()[:100]
            clean = "".join(c for c in title if not ('\u0900' <= c <= '\u097F'))
            if clean.strip():
                seo["title"] = clean.strip()
        elif line.upper().startswith("DESCRIPTION:"):
            desc = line.split(":", 1)[1].strip()
            clean = "".join(c for c in desc if not ('\u0900' <= c <= '\u097F'))
            if clean.strip():
                seo["description"] = clean.strip()
        elif line.upper().startswith("TAGS:"):
            tags_str = line.split(":", 1)[1].strip()
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]
            if tags:
                seo["tags"] = tags
        elif line.upper().startswith("HASHTAG"):
            ht_str = line.split(":", 1)[1].strip()
            hts = [h.strip() for h in ht_str.split() if h.startswith("#")]
            if hts:
                seo["hashtags"] = hts

    if "#Shorts" not in seo["hashtags"]:
        seo["hashtags"].insert(0, "#Shorts")
    if "#Shorts" not in seo["title"]:
        seo["title"] = seo["title"].rstrip() + " #Shorts"

    log.info(f"Generated SEO - Title: {seo['title']}")
    return seo


def generate_search_keywords(script: str) -> list:
    """Generate search keywords for finding stock footage."""
    prompt = f"""You need to find stock video clips for a YouTube Short.

SCRIPT: {script[:300]}

Return exactly 5 search keywords for Pexels stock video website.
Each keyword must be a VISUAL thing that can be filmed.

Rules:
- 1-3 words each
- Must be something you can SEE in a video
- Good: "robot arm", "stock market screen", "brain scan", "dark city night", "person typing"
- Bad: "innovation", "concept", "idea", "future"
- Make keywords SPECIFIC not generic
- Each keyword on its own line

Return ONLY 5 keywords:"""

    response = ask_gemini(prompt)
    keywords = []
    for line in response.split("\n"):
        kw = line.strip().strip("-").strip("*").strip("0123456789.").strip()
        kw = re.sub(r'^\d+[\.\)]\s*', '', kw).strip()
        kw = kw.strip('"').strip("'")
        if kw and len(kw) > 1 and len(kw) < 30 and not kw.startswith("("):
            keywords.append(kw)

    if not keywords:
        keywords = ["technology", "future city", "robot", "digital screen", "person thinking"]

    log.info(f"Search keywords: {keywords[:5]}")
    return keywords[:5]


if __name__ == "__main__":
    print("Testing Gemini connection...")
    result = ask_gemini("Say 'AI Engine is working!' in one line.")
    print(f"Response: {result}")
