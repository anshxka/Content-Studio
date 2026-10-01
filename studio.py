"""GenZMarketer Content Studio (standalone).
Every day: reads fresh marketing, AI, career and job-search news ->
  1. suggests non-generic LinkedIn topic ideas (a mix of all your pillars)
  2. writes full LinkedIn posts in your framework: Hook -> Story -> Problem -> Solution -> CTA
  3. on newsletter day: writes a full issue of your weekly newsletter for people new to marketing
Publishes everything to docs/index.html (GitHub Pages).
"""
import datetime as dt
import html
import json
import os
import re
import time
from pathlib import Path

import feedparser
import requests

from settings import (ABOUT_ME, AUTHOR, BRAND, CURRICULUM, FEEDS, FRAMEWORK, IDEAS_PER_DAY, INSTAGRAM, LINKEDIN,
                      NEWSLETTER_DAY, NEWSLETTER_NAME, NEWSLETTER_START, PER_FEED, PILLARS, POSTS_PER_DAY)

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
ROOT = Path(__file__).parent
DOCS = ROOT / "docs"
DATA = DOCS / "data"
esc = html.escape

HONESTY = f"""About the author: {AUTHOR} ({BRAND}). {ABOUT_ME}
Honesty rules (very important):
- Never invent personal experiences, clients, results or numbers for the author. When a post needs a personal
  detail, put a clearly marked placeholder in square brackets, e.g. [your own example: a campaign where CPA doubled],
  or tell it as a scenario ("Picture this...").
- Only use facts and numbers that appear in the headlines given. Never invent statistics, studies or quotes."""


# ================= news =================
def clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def fetch_headlines():
    seen, items = set(), []
    for source, url in FEEDS:
        try:
            feed = feedparser.parse(url, agent="Mozilla/5.0 (genzmarketer-studio)")
        except Exception as e:
            print(f"skip {source}: {e}")
            continue
        n = 0
        for e in feed.entries:
            if n >= PER_FEED:
                break
            title = clean(e.get("title", ""))
            key = re.sub(r"\W+", "", title.lower())[:60]
            if not title or key in seen:
                continue
            seen.add(key)
            n += 1
            items.append({"source": source, "title": title})
        print(f"{source}: {n}")
    return items


def load_week():
    items = []
    for f in sorted(DATA.glob("20??-??-??.json"), reverse=True)[:7]:
        try:
            items += json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            pass
    return items


def history():
    try:
        return json.loads((DATA / "history.json").read_text(encoding="utf-8"))
    except Exception:
        return []


# ================= AI providers =================
def call_gemini(prompt):
    models = [os.getenv("GEMINI_MODEL", "gemini-3.8-flash"), "gemini-flash-lite-latest", "gemini-flash-latest"]
    last = ""
    for model in models:
        for attempt in range(3):
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                params={"key": os.environ["GEMINI_API_KEY"]},
                json={"contents": [{"parts": [{"text": prompt}]}],
                      "generationConfig": {"responseMimeType": "application/json", "temperature": 0.7,
                                           "maxOutputTokens": 16000}},
                timeout=300)
            if r.status_code == 200:
                return "".join(p.get("text", "") for p in r.json()["candidates"][0]["content"]["parts"])
            last = f"{model} error {r.status_code}: {r.text[:300]}"
            print(last)
            if r.status_code in (500, 502, 503, 504):
                print(f"Gemini busy - waiting {30 * (attempt + 1)}s...")
                time.sleep(30 * (attempt + 1))
                continue
            break
    raise RuntimeError(last)


def call_groq(prompt):
    models = [os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"), "openai/gpt-oss-120b"]
    last = ""
    for model in models:
        for attempt in range(3):
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                              headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
                              json={"model": model, "temperature": 0.8, "response_format": {"type": "json_object"},
                                    "messages": [{"role": "user", "content": prompt}]}, timeout=300)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            last = f"groq {model} error {r.status_code}: {r.text[:300]}"
            print(last)
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(30 * (attempt + 1))
                continue
            break
    raise RuntimeError(last)


def call_claude(prompt):
    r = requests.post("https://api.anthropic.com/v1/messages",
                      headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01",
                               "content-type": "application/json"},
                      json={"model": os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5"), "max_tokens": 8000,
                            "messages": [{"role": "user", "content": prompt}]}, timeout=300)
    r.raise_for_status()
    return "".join(b.get("text", "") for b in r.json()["content"])


def parse_json(text):
    """Read the AI's JSON answer, repairing common small mistakes (trailing commas, code fences, stray text)."""
    text = re.sub(r"^```(?:json)?|```$", "", (text or "").strip(), flags=re.M).strip()
    text = text[text.find("{"): text.rfind("}") + 1]
    for attempt in (text, re.sub(r",\s*([}\]])", r"\1", text)):
        try:
            return json.loads(attempt, strict=False)
        except json.JSONDecodeError:
            continue
    raise ValueError("AI reply was not valid JSON")


def ask_ai(prompt):
    """Uses whichever keys you added, in order: Gemini, Groq, Claude. Retries if the reply is broken."""
    errors = []
    for env, fn in (("GEMINI_API_KEY", call_gemini), ("GROQ_API_KEY", call_groq), ("ANTHROPIC_API_KEY", call_claude)):
        if not os.getenv(env):
            continue
        for attempt in range(3):
            try:
                return parse_json(fn(prompt))
            except ValueError as e:
                print(f"{fn.__name__}: broken reply (attempt {attempt + 1}/3), asking again...")
                errors.append(str(e))
                time.sleep(10)
            except Exception as e:
                print(f"{fn.__name__} failed, trying next: {e}")
                errors.append(str(e))
                break
    raise SystemExit("All AI providers failed:\n" + "\n".join(errors or ["No API key found - add GEMINI_API_KEY"]))


# ================= content =================
def make_ideas(headlines):
    news = "\n".join(f'- {h["title"]} ({h["source"]})' for h in headlines)
    avoid = "\n".join(f"- {t}" for t in history()[:80]) or "- (none yet)"
    return ask_ai(f"""You are a sharp LinkedIn content strategist for {BRAND}.
{HONESTY}

Content pillars to mix: {", ".join(PILLARS)}.

Fresh headlines from the last two days (marketing, AI, careers, job search, LinkedIn):
{news}

Give {IDEAS_PER_DAY} LinkedIn post ideas. Rules:
- A MIX of pillars: cover at least 5 different pillars.
- NOT generic. Banned: "X tips to...", "importance of networking", "AI will not replace you", "how to write a
  resume", "consistency is key", "personal branding matters", "update your LinkedIn", or anything a thousand
  people already posted this week.
- Each idea needs a specific, rarely-discussed ANGLE: a contrarian take, a hidden second-order effect of a news
  story, an unspoken industry truth, a behind-the-scenes explanation, or a surprising link between two stories.
- At least half must be tied to something in the headlines (trending, but discussed from an angle nobody took).
- Do not repeat these recent topics:
{avoid}

Reply with ONLY valid JSON:
{{"ideas": [{{"pillar": "Marketing", "title": "...", "angle": "1-2 sentences: the take nobody is saying",
  "why_now": "which headline makes it timely, or 'evergreen'", "hooks": ["hook option 1", "hook option 2"],
  "score": 9}}]}}
"score" = 1-10 for how fresh and engaging the idea is.""").get("ideas", [])


def write_posts(ideas):
    picked = sorted(ideas, key=lambda i: -int(i.get("score") or 0))[:POSTS_PER_DAY]
    brief = "\n".join(f'{n + 1}. [{i.get("pillar")}] {i.get("title")} - angle: {i.get("angle")} - timely because: '
                      f'{i.get("why_now")}' for n, i in enumerate(picked))
    return ask_ai(f"""Write one LinkedIn post for each idea below, for {AUTHOR} ({BRAND}).
{HONESTY}

{FRAMEWORK}

Ideas:
{brief}

Reply with ONLY valid JSON:
{{"posts": [{{"title": "...", "pillar": "...", "hook": "...", "story": "...", "problem": "...",
  "solution": "...", "cta": "...", "hashtags": "#... #... #..."}}]}}
Use \\n for line breaks inside each part.""").get("posts", [])


def lesson_for(day):
    week = max(0, (day.date() - dt.date.fromisoformat(NEWSLETTER_START)).days // 7)
    field, lesson = CURRICULUM[week % len(CURRICULUM)]
    return week + 1, field, lesson


def write_newsletter(day):
    issue, field, lesson = lesson_for(day)
    week_news = "\n".join(f'- {h["title"]} ({h["source"]})' for h in load_week())[:12000]
    nl = ask_ai(f"""Write issue #{issue} of "{NEWSLETTER_NAME}", a weekly newsletter by {AUTHOR} ({BRAND}) for
people who are new to marketing or early in their career (students, freshers, career switchers).
{HONESTY}

Tone: warm and clear, like a smart senior explaining things over chai. Explain every jargon word.
Open the issue in the author's style: a hook that stops the reader, then a short story.

This week's lesson ({field}): "{lesson}"

This week's headlines (choose only from these for the news section):
{week_news}

Write these keys:
- "subject": an email subject line that gets opened (curious, not clickbait).
- "intro": 3-5 short lines: hook, then a mini story leading into the lesson.
- "lesson_title" and "lesson": the main lesson, 450-650 words. Explain the concept simply, use one Indian brand or
  everyday example, list common beginner mistakes, and end with how it shows up in a real marketing job.
  Separate paragraphs with \\n\\n. Sub-headings allowed as lines starting with "## ".
- "news": the 5 most useful stories of the week for a beginner: [{{"headline": "...",
  "explain": "2 sentences: what happened + what a beginner should learn from it"}}].
- "career_tip": one specific, non-generic career or job-search tip linked to this week's headlines (60-100 words).
- "homework": one practical exercise readers can do in 15 minutes.
- "cta": a closing line asking readers to reply, share it with a friend, and follow {BRAND} on LinkedIn and Instagram.
Reply with ONLY valid JSON with exactly those keys.""")
    return issue, field, lesson, nl


# ================= pages =================
CSS = """:root{--bg:#FFF5F8;--card:#fff;--ink:#3A1430;--muted:#8A5A78;--line:#F7D3E1;--rose:#E8457C;--blush:#FFE4EE;
--soft:#FFF0F5;--serif:"Playfair Display",Georgia,serif;--sans:"DM Sans",system-ui,-apple-system,"Segoe UI",sans-serif}
@media (prefers-color-scheme:dark){:root{--bg:#1C0E18;--card:#28141F;--ink:#FBE8F1;--muted:#C99AB4;--line:#44243A;
--blush:#3A1B2F;--soft:#2F1727}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 var(--sans);
background-image:radial-gradient(circle at 15% 0%,var(--blush) 0,transparent 40%);background-repeat:no-repeat}
.wrap{max-width:920px;margin:auto;padding:36px 20px 70px}
header{text-align:center;margin-bottom:24px}
.kicker{font-size:12px;letter-spacing:.26em;text-transform:uppercase;color:var(--rose);font-weight:700;margin:0}
h1{font:italic 600 clamp(36px,7vw,62px)/1.08 var(--serif);margin:8px 0}
.muted{color:var(--muted);font-size:14px}
.byline{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;align-items:center;margin-top:12px;color:var(--muted)}
.byline em{font:italic 600 17px var(--serif);color:var(--rose)}.byline b{color:var(--ink)}
.social a{display:inline-flex;align-items:center;gap:6px;text-decoration:none;color:var(--ink);font-size:14px;
background:var(--card);border:1px solid var(--line);border-radius:999px;padding:5px 12px 5px 8px;margin:0 3px}
.social svg{width:18px;height:18px}
nav{position:sticky;top:0;z-index:5;background:var(--bg);display:flex;gap:8px;justify-content:center;padding:10px 0;flex-wrap:wrap}
nav a{text-decoration:none;color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:999px;
padding:7px 15px;font-size:14px;font-weight:500}nav a:hover{border-color:var(--rose);color:var(--rose)}
h2{font:600 30px var(--serif);margin:40px 0 14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:22px 24px;margin-bottom:16px;
box-shadow:0 10px 30px -20px rgba(194,24,91,.4)}
.ideas{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:14px}
.idea h3{font:600 19px/1.3 var(--serif);margin:8px 0}.idea p{margin:6px 0;font-size:15px}
.pill{display:inline-block;font-size:12px;font-weight:700;color:var(--rose);background:var(--blush);border-radius:999px;padding:3px 11px}
.hooks{margin:8px 0 0;padding-left:18px;font-size:14px;color:var(--muted)}
.post h3{font:600 22px var(--serif);margin:8px 0 0}
.text{white-space:pre-wrap;background:var(--soft);border-radius:16px;padding:18px 20px;margin:14px 0;font-size:15.5px}
.part{font-size:11px;font-weight:700;letter-spacing:.14em;color:var(--rose);text-transform:uppercase;display:block;margin-top:10px}
.part:first-child{margin-top:0}
button{font:600 14px var(--sans);color:#fff;background:var(--rose);border:0;border-radius:999px;padding:9px 18px;cursor:pointer}
button:focus-visible,a:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
.nl{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:28px 30px}
.nl h3{font:600 24px var(--serif);margin:26px 0 8px}.nl h4{font:600 18px var(--serif);margin:18px 0 4px}
.nl .tag{color:var(--rose);font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:.14em;margin:24px 0 0}
.nl .subject{background:var(--blush);border-radius:12px;padding:10px 14px}.nl li{margin-bottom:10px}
.links a{display:inline-block;margin:4px 6px 0 0;text-decoration:none;color:var(--ink);background:var(--card);
border:1px solid var(--line);border-radius:999px;padding:5px 12px;font-size:14px}
footer{text-align:center;color:var(--muted);font-size:13px;margin-top:40px}"""

IG_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true"><defs><linearGradient id="ig" x1="0" y1="1" x2="1" y2="0">'
          '<stop offset="0" stop-color="#FEDA75"/><stop offset=".35" stop-color="#FA7E1E"/><stop offset=".6" '
          'stop-color="#D62976"/><stop offset=".85" stop-color="#962FBF"/><stop offset="1" stop-color="#4F5BD5"/>'
          '</linearGradient></defs><rect x="2" y="2" width="20" height="20" rx="6" fill="url(#ig)"/><circle cx="12" '
          'cy="12" r="4.3" fill="none" stroke="#fff" stroke-width="2"/><circle cx="17.4" cy="6.6" r="1.3" fill="#fff"/></svg>')
LI_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="2" width="20" height="20" rx="4" fill="#0A66C2"/>'
          '<rect x="6" y="10" width="2.6" height="8" fill="#fff"/><circle cx="7.3" cy="7" r="1.5" fill="#fff"/>'
          '<path d="M11 10h2.5v1.2c.5-.8 1.5-1.4 2.8-1.4 2.2 0 3 1.4 3 3.6V18h-2.6v-4.1c0-1-.3-1.8-1.4-1.8s-1.7.8-1.7 '
          '1.9V18H11z" fill="#fff"/></svg>')


def shell(title, body, prefix=""):
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>✍️</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,600&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><div class="wrap">
<header><p class="kicker">{esc(BRAND)} · content studio</p><h1>{esc(title)}</h1>
<div class="byline"><span>Curated by <em>{esc(BRAND)}</em> · <b>{esc(AUTHOR)}</b></span><span class="social">
<a href="{INSTAGRAM}" target="_blank" rel="noopener">{IG_SVG} Instagram</a>
<a href="{LINKEDIN}" target="_blank" rel="noopener">{LI_SVG} LinkedIn</a></span></div></header>
{body}
<footer>Drafts are AI-written. Fill in anything in [square brackets] with your real experience before posting. 🌸</footer>
</div>
<script>
document.querySelectorAll('[data-copy]').forEach(function(b){{b.addEventListener('click',function(){{
 var label=b.textContent;var t=document.getElementById(b.dataset.copy).innerText;
 navigator.clipboard.writeText(t).then(function(){{b.textContent='Copied ✓';setTimeout(function(){{b.textContent=label}},1800)}});
}})}});
</script></body></html>'''


def fix(text):
    return (text or "").replace("\\n", "\n").strip()


def post_card(p, n):
    parts = [("Hook", p.get("hook")), ("Story", p.get("story")), ("Problem", p.get("problem")),
             ("Solution", p.get("solution")), ("CTA", p.get("cta"))]
    plain = "\n\n".join(fix(v) for _, v in parts if fix(v)) + ("\n\n" + fix(p.get("hashtags")) if p.get("hashtags") else "")
    labelled = "".join(f'<span class="part">{k}</span>{esc(fix(v))}\n' for k, v in parts if fix(v))
    return f'''<div class="card post"><span class="pill">{esc(p.get("pillar", ""))}</span>
<h3>{esc(p.get("title", ""))}</h3>
<div class="text">{labelled}<span class="part">Hashtags</span>{esc(fix(p.get("hashtags")))}</div>
<div id="post{n}" hidden>{esc(plain)}</div>
<button data-copy="post{n}">Copy post</button></div>'''


def idea_card(i):
    return f'''<div class="card idea"><span class="pill">{esc(i.get("pillar", ""))}</span>
<h3>{esc(i.get("title", ""))}</h3><p><b>Angle:</b> {esc(i.get("angle", ""))}</p>
<p class="muted"><b>Why now:</b> {esc(i.get("why_now", ""))}</p>
<ul class="hooks">{"".join(f"<li>{esc(h)}</li>" for h in i.get("hooks", []))}</ul></div>'''


def newsletter_block(issue, field, lesson, nl, day):
    def paras(text):
        out = []
        for block in re.split(r"\n\s*\n", fix(text)):
            block = block.strip()
            if block.startswith("## "):
                out.append(f"<h4>{esc(block[3:])}</h4>")
            elif block:
                out.append("<p>" + "<br>".join(esc(x) for x in block.split("\n")) + "</p>")
        return "".join(out)
    news = "".join(f'<li><b>{esc(x.get("headline", ""))}</b><br>{esc(x.get("explain", ""))}</li>'
                   for x in nl.get("news", []))
    return f'''<div class="nl" id="newsletter"><p class="kicker">{esc(NEWSLETTER_NAME)} · Issue #{issue} · {day:%d %B %Y}</p>
<p class="subject"><b>Subject line:</b> {esc(nl.get("subject", ""))}</p>
<div id="nltext">{paras(nl.get("intro"))}
<p class="tag">This week's lesson · {esc(field)}</p><h3>{esc(nl.get("lesson_title") or lesson)}</h3>{paras(nl.get("lesson"))}
<h3>This week in marketing</h3><ol>{news}</ol>
<h3>Career corner</h3>{paras(nl.get("career_tip"))}
<h3>Your 15-minute homework</h3>{paras(nl.get("homework"))}
{paras(nl.get("cta"))}</div>
<button data-copy="nltext">Copy newsletter</button></div>'''


def main():
    day = dt.datetime.now(IST)
    DATA.mkdir(parents=True, exist_ok=True)
    headlines = fetch_headlines()
    print(f"headlines: {len(headlines)}")
    if not headlines:
        raise SystemExit("No headlines found - check FEEDS in settings.py")
    (DATA / f"{day:%Y-%m-%d}.json").write_text(json.dumps(headlines, ensure_ascii=False), encoding="utf-8")

    ideas = make_ideas(headlines)
    print(f"ideas: {len(ideas)}")
    time.sleep(10)
    posts = write_posts(ideas) if ideas else []
    print(f"posts: {len(posts)}")
    new_history = ([i.get("title", "") for i in ideas] + history())[:150]
    (DATA / "history.json").write_text(json.dumps(new_history, ensure_ascii=False), encoding="utf-8")

    letters = DOCS / "newsletter"
    letters.mkdir(parents=True, exist_ok=True)
    latest = DATA / "newsletter_latest.html"
    want = day.weekday() == NEWSLETTER_DAY or not latest.exists() or os.getenv("NEWSLETTER_NOW", "").lower() == "yes"
    if want:
        time.sleep(10)
        try:
            issue, field, lesson, nl = write_newsletter(day)
            block = newsletter_block(issue, field, lesson, nl, day)
            latest.write_text(block, encoding="utf-8")
            (letters / f"{day:%Y-%m-%d}.html").write_text(
                shell(f"{NEWSLETTER_NAME} #{issue}", block), encoding="utf-8")
            print(f"newsletter issue #{issue} written")
        except SystemExit as e:
            print(f"newsletter skipped: {e}")
    block = latest.read_text(encoding="utf-8") if latest.exists() else "<p class='muted'>Your first issue will appear here.</p>"
    past = "".join(f'<a href="newsletter/{f.name}">{f.stem}</a>' for f in sorted(letters.glob("*.html"), reverse=True)[:20])

    body = f'''<p class="muted" style="text-align:center">{day:%A, %d %B %Y} · Hook → Story → Problem → Solution → CTA</p>
<nav><a href="#posts">✍️ Posts</a><a href="#ideas">💡 Topic ideas</a><a href="#newsletter">💌 Newsletter</a></nav>
<h2 id="posts">✍️ Ready-to-post LinkedIn drafts</h2>
<p class="muted">Copy, fill in any [square brackets] with your real example, and post.</p>
{"".join(post_card(p, n) for n, p in enumerate(posts)) or "<p class='muted'>No posts today - check the run log.</p>"}
<h2 id="ideas">💡 Fresh topic ideas</h2>
<div class="ideas">{"".join(idea_card(i) for i in ideas)}</div>
<h2>💌 {esc(NEWSLETTER_NAME)}</h2>{block}
<p class="links" style="margin-top:14px"><b>Past issues:</b> {past or "<span class='muted'>none yet</span>"}</p>'''
    (DOCS / "index.html").write_text(shell("Today's content", body), encoding="utf-8")
    print("Studio written to docs/index.html")


if __name__ == "__main__":
    main()
