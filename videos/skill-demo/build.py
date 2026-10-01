"""Build the talking-head-recut composition for the skill demo.

Writes storyboard.json, public/cards/card-XX.html (one fragment per card,
motion declared with data-anim-* attributes) and public/index.html (the
assembled composition with every data-anim compiled into one GSAP timeline).
Card timings come from the corrected Whisper transcript (transcript.json).
"""

import html
import json
import os

FPS = 30
W, H = 1080, 1920
DURATION = 486.4
VIDEO_H = 702
RAIL_TOP = 736
CARD_TOP = 872
CARD_H = H - CARD_TOP

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(HERE, "public")

# ── helpers ────────────────────────────────────────────────────────────────

CUR = {"id": None, "start": 0.0, "anims": []}


def q(t):
    return round(round(t * FPS) / FPS, 4)


def an(name, kind, at, dur=0.5, **kw):
    """Declare an animated element. `at` is ABSOLUTE seconds; the attribute
    stores it relative to the card start, as the card contract requires."""
    rel = round(at - CUR["start"], 3)
    assert rel >= 0, (CUR["id"], name, at)
    el_id = f'{CUR["id"]}-{name}'
    CUR["anims"].append({"id": el_id, "kind": kind, "at": at, "dur": dur, **kw})
    attrs = [f'id="{el_id}"', f'data-anim="{kind}"', f'data-anim-at="{rel}"', f'data-anim-duration="{dur}"']
    for k, v in kw.items():
        v = json.dumps(v) if isinstance(v, dict) else str(v)
        attrs.append(f'data-anim-{k.replace("_", "-")}="{html.escape(v)}"')
    return " ".join(attrs)


def esc(s):
    return html.escape(s, quote=False)


def chars(text):
    """Per-character spans grouped by word so lines only break between words."""
    words = []
    for w in text.split(" "):
        cs = "".join(f'<span class="char">{esc(c)}</span>' for c in w)
        words.append(f'<span class="w">{cs}</span>')
    return " ".join(words)


def title(name, text, at, dur=0.6, cls="title", stagger=0.025):
    return f'<h1 class="{cls}" {an(name, "kinetic-chars", at, dur, stagger=stagger, pattern="pop")}>{chars(text)}</h1>'


def kicker(text, at):
    return f'<div class="kicker" {an("kicker", "fade-in", at, 0.4)}>{esc(text)}</div>'


ICONS = {
    "folder": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linejoin="round"><path d="M6 16a4 4 0 0 1 4-4h14l6 7h24a4 4 0 0 1 4 4v27a4 4 0 0 1-4 4H10a4 4 0 0 1-4-4z"/><path d="M6 26h52"/></svg>',
    "doc": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linejoin="round"><path d="M14 6h26l12 12v40H14z"/><path d="M40 6v12h12"/><path d="M22 32h22M22 41h22M22 50h14"/></svg>',
    "check": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"><path d="M14 33l12 12 24-26"/></svg>',
    "x": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="6" stroke-linecap="round"><path d="M18 18l28 28M46 18L18 46"/></svg>',
    "arrow-r": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"><path d="M10 32h42M38 18l14 14-14 14"/></svg>',
    "arrow-d": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"><path d="M32 8v46M18 40l14 14 14-14"/></svg>',
    "upload": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"><path d="M32 42V10M20 22l12-12 12 12"/><path d="M10 40v12a4 4 0 0 0 4 4h36a4 4 0 0 0 4-4V40"/></svg>',
    "download": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"><path d="M32 8v32M20 28l12 12 12-12"/><path d="M10 40v12a4 4 0 0 0 4 4h36a4 4 0 0 0 4-4V40"/></svg>',
    "search": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round"><circle cx="28" cy="28" r="16"/><path d="M40 40l14 14"/></svg>',
    "shield": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round"><path d="M32 6l22 8v16c0 14-9 24-22 28C19 54 10 44 10 30V14z"/></svg>',
    "spark": '<svg viewBox="0 0 64 64" fill="currentColor"><path d="M32 4l6 20 20 8-20 8-6 20-6-20-20-8 20-8z"/></svg>',
    "image": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round"><rect x="8" y="12" width="48" height="40" rx="5"/><circle cx="24" cy="26" r="5"/><path d="M8 46l15-14 11 10 8-7 14 13"/></svg>',
    "mail": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round"><rect x="8" y="14" width="48" height="36" rx="5"/><path d="M8 18l24 18 24-18"/></svg>',
    "form": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"><rect x="12" y="6" width="40" height="52" rx="5"/><path d="M20 20h24M20 32h24M20 44h12"/></svg>',
    "send": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"><path d="M32 52V14M18 28l14-14 14 14"/></svg>',
    "megaphone": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round"><path d="M10 26v12h10l22 12V14L20 26z"/><path d="M50 24c4 4 4 12 0 16"/></svg>',
    "chat": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round"><path d="M8 12h48v32H28l-12 10V44H8z"/></svg>',
    "unlink": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4.5" stroke-linecap="round"><path d="M26 20l4-4a10 10 0 0 1 14 14l-4 4"/><path d="M38 44l-4 4a10 10 0 0 1-14-14l4-4"/><path d="M12 12l6 6M46 46l6 6M30 8v6M8 30h6"/></svg>',
    "repeat": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 30a18 18 0 0 1 32-11l4 5"/><path d="M50 12v12H38"/><path d="M50 34a18 18 0 0 1-32 11l-4-5"/><path d="M14 52V40h12"/></svg>',
    "calendar": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round"><rect x="8" y="12" width="48" height="44" rx="5"/><path d="M8 24h48M20 6v12M44 6v12"/></svg>',
    "user": '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4"><circle cx="32" cy="24" r="10"/><path d="M12 56c2-11 10-16 20-16s18 5 20 16"/></svg>',
}


def icon(name, size=56, extra=""):
    return f'<span class="ico" style="width:{size}px;height:{size}px;{extra}">{ICONS[name]}</span>'


def check_path(name, at, size=64, dur=0.5):
    return (
        f'<svg class="ico" style="width:{size}px;height:{size}px" viewBox="0 0 64 64" fill="none" stroke="currentColor" '
        f'stroke-width="6" stroke-linecap="round" stroke-linejoin="round"><path pathLength="1" d="M14 33l12 12 24-26" '
        f'{an(name, "draw-path", at, dur)}/></svg>'
    )


# ── cards ──────────────────────────────────────────────────────────────────

CARDS = []


def card(cid, start, end, accent, intent, hints, body, css=""):
    CARDS.append(
        {
            "id": cid,
            "start": start,
            "end": end,
            "accent": accent,
            "intent": intent,
            "hints": hints,
            "body": body,
            "css": css,
            "anims": list(CUR["anims"]),
        }
    )


def begin(cid, start):
    CUR.update(id=cid, start=start, anims=[])


# 01 ─ what a skill is
begin("card-01", 0.4)
card(
    "card-01", 0.4, 11.4, 0,
    "Define a skill: a repeatable prompt",
    {"kicker": "Claude · skills", "title": "¿Qué es una skill?", "detail": "skill = prompt repetible"},
    f"""
{kicker("Claude · skills", 0.6)}
{title("title", "¿Qué es una skill?", 0.8, 0.7)}
<div class="eq" {an("eq", "blur-in", 6.2, 0.6)}>
  <span class="chip big">skill</span><span class="eq-sign">=</span><span class="eq-txt">prompt <span class="acc">repetible</span></span>
</div>
<div class="stack">
  <div class="pcard p3" {an("p3", "slide-in", 8.3, 0.5, **{"from": "bottom", "distance": 60})}></div>
  <div class="pcard p2" {an("p2", "slide-in", 7.9, 0.5, **{"from": "bottom", "distance": 60})}></div>
  <div class="pcard p1" {an("p1", "scale-pop", 7.1, 0.5)}>
    <div class="ptag mono">prompt</div>
    <div class="bar" style="width:86%"></div><div class="bar" style="width:72%"></div><div class="bar" style="width:80%"></div><div class="bar" style="width:54%"></div>
  </div>
  <div class="badge" {an("badge", "scale-pop", 8.0, 0.5)}>{icon("repeat", 44)}<span>repetible</span></div>
</div>
""",
    """
.card[data-card-id="card-01"] .eq { display:flex; align-items:center; gap:24px; margin-top:8px; }
.card[data-card-id="card-01"] .eq-sign { font:700 64px/1 'Inter'; color:var(--muted); }
.card[data-card-id="card-01"] .eq-txt { font:700 56px/1 'Inter'; }
.card[data-card-id="card-01"] .stack { position:relative; height:470px; margin-top:24px; }
.card[data-card-id="card-01"] .pcard { position:absolute; left:120px; width:620px; height:330px; border-radius:28px; background:var(--panel); border:2px solid var(--line); padding:40px 44px; display:flex; flex-direction:column; gap:22px; }
.card[data-card-id="card-01"] .p3 { top:0; left:200px; opacity:.45; }
.card[data-card-id="card-01"] .p2 { top:40px; left:160px; opacity:.7; }
.card[data-card-id="card-01"] .p1 { top:80px; border-color:var(--acc); }
.card[data-card-id="card-01"] .ptag { font-size:26px; color:var(--acc); letter-spacing:.1em; text-transform:uppercase; }
.card[data-card-id="card-01"] .bar { height:22px; border-radius:11px; background:var(--panel-2); }
.card[data-card-id="card-01"] .badge { position:absolute; right:40px; top:300px; }
""",
)

# 02 ─ works in Claude and ChatGPT, same behaviour every time
begin("card-02", 11.4)
card(
    "card-02", 11.4, 22.4, 1,
    "Same skill runs in Claude and ChatGPT and behaves the same every time",
    {"title": "Siempre de la misma manera", "detail": "También funciona en ChatGPT"},
    f"""
{kicker("Funciona en", 11.6)}
<div class="diagram">
  <div class="node src" {an("src", "scale-pop", 11.8, 0.5)}>{icon("doc", 64)}<span class="mono">SKILL</span></div>
  <svg class="links" viewBox="0 0 984 300" fill="none" stroke-width="5" stroke-linecap="round">
    <path pathLength="1" d="M492 70 C492 160 250 150 250 230" {an("l1", "draw-path", 12.0, 0.6)}/>
    <path pathLength="1" d="M492 70 C492 160 734 150 734 230" {an("l2", "draw-path", 15.2, 0.6)}/>
  </svg>
  <div class="chip big t1" {an("t1", "scale-pop", 12.5, 0.5)}>Claude</div>
  <div class="chip big t2" {an("t2", "scale-pop", 15.6, 0.5)}>ChatGPT</div>
</div>
{title("title", "Siempre de la misma manera", 16.3, 0.7, cls="title sm")}
<div class="outs">
  <div class="out" {an("o1", "slide-in", 17.2, 0.45, **{"from": "left", "distance": 60})}><div class="ob" style="width:70%"></div>{icon("check", 40, "color:var(--accent-2)")}</div>
  <div class="out" {an("o2", "slide-in", 17.6, 0.45, **{"from": "left", "distance": 60})}><div class="ob" style="width:70%"></div>{icon("check", 40, "color:var(--accent-2)")}</div>
  <div class="out" {an("o3", "slide-in", 18.0, 0.45, **{"from": "left", "distance": 60})}><div class="ob" style="width:70%"></div>{icon("check", 40, "color:var(--accent-2)")}</div>
</div>
""",
    """
.card[data-card-id="card-02"] .diagram { position:relative; height:330px; }
.card[data-card-id="card-02"] .src { position:absolute; left:372px; top:0; width:240px; height:88px; justify-content:center; }
.card[data-card-id="card-02"] .links { position:absolute; left:0; top:20px; width:984px; height:300px; stroke:var(--acc); }
.card[data-card-id="card-02"] .t1 { position:absolute; left:130px; top:244px; }
.card[data-card-id="card-02"] .t2 { position:absolute; left:604px; top:244px; }
.card[data-card-id="card-02"] .outs { display:flex; flex-direction:column; gap:18px; }
.card[data-card-id="card-02"] .out { display:flex; align-items:center; justify-content:space-between; padding:22px 28px; border-radius:18px; background:var(--panel); border:2px solid var(--line); }
.card[data-card-id="card-02"] .ob { height:22px; border-radius:11px; background:var(--panel-2); }
""",
)

# 03 ─ the folder of material
begin("card-03", 22.4)
card(
    "card-03", 22.4, 42.1, 2,
    "The source material: a folder of documents for writing an ad brief, and who uses a brief",
    {"title": "Un folder para hacer un brief publicitario", "detail": "editores de video, estrategas creativos, marketing"},
    f"""
{kicker("El material", 22.6)}
<div class="folder" {an("folder", "scale-pop", 23.6, 0.6)}>{icon("folder", 150)}<span class="mono fname">folder / documentos</span></div>
{title("title", "Un folder para hacer un brief publicitario", 27.2, 0.8, cls="title sm")}
<p class="lead" {an("who", "fade-in", 34.7, 0.4)}>Lo que se entrega a:</p>
<div class="chips">
  <span class="chip" {an("c1", "scale-pop", 36.0, 0.45)}>{icon("user", 34)}Editores de video</span>
  <span class="chip" {an("c2", "scale-pop", 37.5, 0.45)}>{icon("spark", 30)}Estrategas creativos</span>
  <span class="chip" {an("c3", "scale-pop", 40.1, 0.45)}>{icon("megaphone", 34)}Estrategia de marketing</span>
</div>
""",
    """
.card[data-card-id="card-03"] .folder { display:flex; align-items:center; gap:32px; color:var(--acc); }
.card[data-card-id="card-03"] .fname { font-size:30px; color:var(--muted); }
.card[data-card-id="card-03"] .chips { display:flex; flex-wrap:wrap; gap:18px; }
""",
)


def doc_row(name, num, text, at, sub=None, sub_at=None, extra=""):
    s = ""
    if sub:
        s = f'<div class="sub" {an(name + "-sub", "fade-in", sub_at, 0.4)}>{esc(sub)}</div>'
    return (
        f'<div class="row" {an(name, "slide-in", at, 0.45, **{"from": "left", "distance": 70})}>'
        f'<span class="num">{num}</span>{icon("doc", 44, "color:var(--muted)")}'
        f'<div class="grow"><div class="txt">{esc(text)}</div>{s}</div>{extra}</div>'
    )


# 04 ─ folder contents, part 1
begin("card-04", 42.1)
card(
    "card-04", 42.1, 59.3, 2,
    "Folder contents: what a brief is, questions, structure, video brief, writing rules",
    {"title": "Qué hay dentro (1/2)"},
    f"""
{kicker("Dentro del folder", 42.2)}
<div class="rows">
{doc_row("r1", "01", "Qué es un brief", 42.2)}
{doc_row("r2", "02", "Preguntas antes de crear un brief", 44.4, "Las que hace la estrategia creativa", 46.8)}
{doc_row("r3", "03", "Estructura del brief", 51.0)}
{doc_row("r4", "04", "Brief para video", 52.4)}
{doc_row("r5", "05", "Reglas de redacción", 53.5)}
</div>
<div class="note" {an("note", "blur-in", 54.6, 0.6)}>{icon("spark", 40, "color:var(--acc)")}<span>Las mejores prácticas de la industria publicitaria</span></div>
""",
    """
.card[data-card-id="card-04"] .rows { display:flex; flex-direction:column; gap:16px; }
.card[data-card-id="card-04"] .note { display:flex; align-items:center; gap:18px; font:700 34px/1.25 'Inter'; margin-top:6px; }
""",
)

# 05 ─ folder contents, part 2
begin("card-05", 59.3)
card(
    "card-05", 59.3, 88.5, 3,
    "Folder contents: researched with Claude, checklist, examples, organic reels explained",
    {"title": "Qué hay dentro (2/2)"},
    f"""
{kicker("Dentro del folder", 59.4)}
<div class="badge" {an("badge", "scale-pop", 60.4, 0.5)}>{icon("search", 40)}<span>Investigado con Claude</span></div>
<div class="rows">
{doc_row("r6", "06", "Checklist de un buen brief", 64.0, extra='<div class="ticks">' + "".join(f'<span class="tick" {an(f"t{i}", "scale-pop", t, 0.35)}>{ICONS["check"]}</span>' for i, t in enumerate([66.5, 68.1, 70.7])) + '</div>')}
{doc_row("r7", "07", "Ejemplos de video y estáticos", 74.3, "Sacados de internet", 77.7)}
{doc_row("r8", "08", "Reels y posts orgánicos explicados", 82.4, "También hecho con Claude", 86.9)}
</div>
""",
    """
.card[data-card-id="card-05"] .rows { display:flex; flex-direction:column; gap:18px; margin-top:8px; }
.card[data-card-id="card-05"] .ticks { display:flex; gap:10px; }
.card[data-card-id="card-05"] .tick { width:46px; height:46px; border-radius:12px; background:var(--accent-2); color:#141312; display:flex; align-items:center; justify-content:center; }
.card[data-card-id="card-05"] .tick svg { width:34px; height:34px; }
""",
)

# 06 ─ university context and AI rules
begin("card-06", 88.5)
card(
    "card-06", 88.5, 108.1, 4,
    "University context: the skill follows the university's AI-use regulation",
    {"title": "Adaptada a la universidad", "detail": "Reglamento de uso de IA, Universidad de Boyacá"},
    f"""
{kicker("+ Contexto", 88.6)}
{title("title", "Adaptada a la universidad", 89.4, 0.7)}
<span class="chip why" {an("why", "scale-pop", 94.9, 0.45)}>¿Por qué?</span>
<div class="reg" {an("reg", "slide-in", 98.9, 0.55, **{"from": "right", "distance": 80})}>
  <div class="shield">{icon("shield", 120)}</div>
  <div>
    <div class="rk mono">Reglamento</div>
    <div class="rt">Uso de inteligencia artificial</div>
    <div class="ru" {an("uni", "fade-in", 106.4, 0.4)}>Universidad de Boyacá</div>
  </div>
</div>
<div class="follow"><span class="okc">{check_path("chk", 101.6, 56)}</span><span {an("follow", "fade-in", 101.4, 0.4)}>Cada brief sigue la normativa</span></div>
""",
    """
.card[data-card-id="card-06"] .why { align-self:flex-start; }
.card[data-card-id="card-06"] .reg { display:flex; align-items:center; gap:36px; padding:36px; border-radius:28px; background:var(--panel); border:2px solid var(--acc); }
.card[data-card-id="card-06"] .shield { color:var(--acc); }
.card[data-card-id="card-06"] .rk { font-size:24px; color:var(--acc); letter-spacing:.14em; text-transform:uppercase; }
.card[data-card-id="card-06"] .rt { font:700 44px/1.15 'Inter'; margin-top:8px; }
.card[data-card-id="card-06"] .ru { font:400 32px/1.3 'Inter'; color:var(--muted); margin-top:8px; }
.card[data-card-id="card-06"] .follow { display:flex; align-items:center; gap:20px; font:700 40px/1.2 'Inter'; }
.card[data-card-id="card-06"] .okc { width:72px; height:72px; border-radius:50%; background:var(--accent-2); color:#141312; display:flex; align-items:center; justify-content:center; }
""",
)

# 07 ─ upload the folder, type /skill-creator
begin("card-07", 108.1)
card(
    "card-07", 108.1, 119.0, 0,
    "Upload the folder to the chat and call /skill-creator",
    {"title": "Sube el folder", "detail": "/skill-creator"},
    f"""
{kicker("Crear la skill", 108.3)}
{title("title", "Sube el folder al chat", 108.4, 0.6)}
<div class="chatwin">
  <div class="att" {an("att", "slide-in", 109.1, 0.5, **{"from": "top", "distance": 90})}>{icon("folder", 54)}<div class="grow"><div class="an">folder / documentos</div><div class="track"><div class="fill" {an("fill", "morph-to", 109.6, 1.4, **{"from": {"scaleX": 0}, "props": {"scaleX": 1}})}></div></div></div><span class="okc" {an("ok", "scale-pop", 111.1, 0.4)}>{ICONS["check"]}</span></div>
  <div class="input mono"><span class="tw" {an("cmd", "typewriter", 116.1, 1.5)}>{chars("/skill-creator")}</span></div>
</div>
""",
    """
.card[data-card-id="card-07"] .chatwin { display:flex; flex-direction:column; gap:22px; padding:30px; border-radius:30px; background:var(--panel); border:2px solid var(--line); margin-top:10px; }
.card[data-card-id="card-07"] .att { display:flex; align-items:center; gap:24px; padding:24px; border-radius:20px; background:var(--panel-2); color:var(--acc); }
.card[data-card-id="card-07"] .an { font:700 30px/1.2 'Inter'; color:var(--text); margin-bottom:14px; }
.card[data-card-id="card-07"] .track { height:12px; border-radius:6px; background:#3a3632; overflow:hidden; }
.card[data-card-id="card-07"] .fill { width:100%; height:100%; background:var(--acc); transform-origin:left center; }
.card[data-card-id="card-07"] .okc { width:56px; height:56px; border-radius:50%; background:var(--accent-2); color:#141312; display:flex; align-items:center; justify-content:center; }
.card[data-card-id="card-07"] .okc svg { width:36px; height:36px; }
.card[data-card-id="card-07"] .input { font-size:52px; min-height:150px; display:flex; align-items:center; color:var(--acc); }
""",
)

# 08 ─ skill-creator ships with Claude
begin("card-08", 119.0)
card(
    "card-08", 119.0, 131.5, 1,
    "skill-creator is built into Claude by default and its job is to create skills",
    {"title": "Una skill que crea skills", "detail": "viene por defecto"},
    f"""
{kicker("Ya viene en Claude", 119.2)}
<div class="cmdbig mono" {an("cmd", "scale-pop", 119.4, 0.55)}><span class="sl">/</span>skill-creator</div>
<div class="tags">
  <span class="chip" {an("tag1", "fade-in", 123.7, 0.4)}>Desde que descargas Claude</span>
  <span class="chip solid" {an("tag2", "scale-pop", 127.0, 0.45)}>Por defecto</span>
</div>
<div class="loop">
  <div class="blk" {an("b1", "scale-pop", 129.3, 0.45)}>skill</div>
  <div class="arr" {an("arr", "mask-reveal", 129.8, 0.4, direction="left")}>{icon("arrow-r", 90)}<span class="mono">crea</span></div>
  <div class="blk acc-b" {an("b2", "scale-pop", 130.4, 0.45)}>skill</div>
</div>
{title("title", "Una skill que crea skills", 129.0, 0.6, cls="title sm")}
""",
    """
.card[data-card-id="card-08"] .cmdbig { font-size:84px; font-weight:700; padding:36px 40px; border-radius:28px; background:#0e0d0c; border:2px solid var(--acc); align-self:flex-start; }
.card[data-card-id="card-08"] .sl { color:var(--acc); }
.card[data-card-id="card-08"] .tags { display:flex; gap:18px; flex-wrap:wrap; }
.card[data-card-id="card-08"] .loop { display:flex; align-items:center; gap:30px; margin-top:14px; }
.card[data-card-id="card-08"] .blk { width:220px; height:150px; border-radius:26px; background:var(--panel); border:2px solid var(--line); display:flex; align-items:center; justify-content:center; font:700 44px/1 'JetBrains Mono'; }
.card[data-card-id="card-08"] .acc-b { border-color:var(--acc); color:var(--acc); }
.card[data-card-id="card-08"] .arr { display:flex; flex-direction:column; align-items:center; gap:6px; color:var(--muted); font-size:26px; }
""",
)

# 09 ─ the prompt being typed
prompt = "/skill-creator con el folder que acabo de subir"
begin("card-09", 131.5)
card(
    "card-09", 131.5, 145.7, 0,
    "The exact prompt typed: /skill-creator with the uploaded folder",
    {"detail": prompt},
    f"""
{kicker("Lo que escribes", 131.7)}
{title("title", "Un solo mensaje", 131.8, 0.5)}
<div class="input big mono"><span class="tw" {an("prompt", "typewriter", 133.3, 10.4)}>{chars(prompt)}</span></div>
<div class="sendrow"><span class="lead">Claude recibe el folder y el comando</span><span class="send" {an("send", "scale-pop", 144.0, 0.4)}>{ICONS["send"]}</span></div>
""",
    """
.card[data-card-id="card-09"] .input.big { font-size:50px; line-height:1.35; min-height:330px; padding:40px; color:var(--text); }
.card[data-card-id="card-09"] .input.big .w:first-child { color:var(--acc); }
.card[data-card-id="card-09"] .sendrow { display:flex; align-items:center; justify-content:space-between; gap:24px; }
.card[data-card-id="card-09"] .send { width:96px; height:96px; border-radius:50%; background:var(--acc); color:#141312; display:flex; align-items:center; justify-content:center; flex:none; }
.card[data-card-id="card-09"] .send svg { width:56px; height:56px; }
""",
)

# 10 ─ Claude builds the skill
begin("card-10", 145.7)
card(
    "card-10", 145.7, 176.1, 2,
    "Claude builds the skill: material + skill-creator produce prompt structure, skill parts, best prompt; acts like an agent",
    {"title": "Claude arma la skill"},
    f"""
{kicker("Claude trabaja", 145.9)}
{title("title", "Claude arma la skill", 146.0, 0.6)}
<div class="inrow">
  <div class="node" {an("n1", "slide-in", 146.9, 0.5, **{"from": "left", "distance": 60})}>{icon("folder", 48, "color:var(--muted)")}<span>Material</span></div>
  <span class="plus" {an("plus", "fade-in", 154.4, 0.3)}>+</span>
  <div class="node mono acc-n" {an("n2", "scale-pop", 154.6, 0.5)}>/skill-creator</div>
</div>
<div class="down" {an("down", "mask-reveal", 156.2, 0.5, direction="top")}>{icon("arrow-d", 70)}</div>
<div class="skillbox">
  <div class="sbh mono">SKILL</div>
  <div class="layer" {an("l1", "slide-in", 160.0, 0.45, **{"from": "bottom", "distance": 40})}><span class="ln mono">1</span>Estructura de prompt</div>
  <div class="layer" {an("l2", "slide-in", 163.4, 0.45, **{"from": "bottom", "distance": 40})}><span class="ln mono">2</span>Las partes de la skill</div>
  <div class="layer best" {an("l3", "slide-in", 167.4, 0.45, **{"from": "bottom", "distance": 40})}><span class="ln mono">3</span>La mejor prompt</div>
</div>
<div class="badge agent" {an("agent", "scale-pop", 172.4, 0.5)}>{icon("repeat", 44)}<span>Repetible: actúa como un agente</span></div>
""",
    """
.card[data-card-id="card-10"] .inrow { display:flex; align-items:center; gap:22px; }
.card[data-card-id="card-10"] .node { display:flex; align-items:center; gap:16px; padding:22px 30px; border-radius:20px; background:var(--panel); border:2px solid var(--line); font:700 34px/1 'Inter'; }
.card[data-card-id="card-10"] .acc-n { font-family:'JetBrains Mono'; color:var(--acc); border-color:var(--acc); }
.card[data-card-id="card-10"] .plus { font:700 48px/1 'Inter'; color:var(--muted); }
.card[data-card-id="card-10"] .down { color:var(--acc); align-self:center; height:70px; }
.card[data-card-id="card-10"] .skillbox { padding:26px; border-radius:28px; border:3px solid var(--acc); background:var(--panel); display:flex; flex-direction:column; gap:14px; }
.card[data-card-id="card-10"] .sbh { font-size:24px; letter-spacing:.2em; color:var(--acc); }
.card[data-card-id="card-10"] .layer { display:flex; align-items:center; gap:20px; padding:20px 24px; border-radius:16px; background:var(--panel-2); font:700 34px/1.2 'Inter'; }
.card[data-card-id="card-10"] .layer.best { background:var(--acc); color:#141312; }
.card[data-card-id="card-10"] .ln { font-size:26px; opacity:.75; }
.card[data-card-id="card-10"] .agent { align-self:flex-start; }
""",
)

# 11 ─ two ways a skill gets used
begin("card-11", 176.1)
card(
    "card-11", 176.1, 207.7, 3,
    "Two ways to trigger a skill: you call it with a slash, or Claude uses it on its own",
    {"title": "Dos formas de usar una skill"},
    f"""
{kicker("Cómo se activa", 176.2)}
{title("title", "Dos formas de usar una skill", 176.3, 0.7, cls="title sm")}
<div class="opt" {an("o1", "slide-in", 177.9, 0.5, **{"from": "left", "distance": 70})}>
  <span class="onum">1</span>
  <div class="grow"><div class="ot">Tú la llamas</div><div class="input mono slash"><span class="acc">/</span><span {an("o1c", "fade-in", 182.8, 0.5)}> búscala y ponla</span></div></div>
</div>
<div class="opt" {an("o2", "slide-in", 187.0, 0.5, **{"from": "left", "distance": 70})}>
  <span class="onum">2</span>
  <div class="grow"><div class="ot">Claude la usa solo</div><div class="os" {an("o2s", "fade-in", 189.0, 0.4)}>Es autónomo: sabe cuándo le sirve una skill</div></div>
</div>
<div class="bubble" {an("bubble", "scale-pop", 198.3, 0.5)}>«Me acuerdo de esta skill. Voy a utilizarla.»</div>
<span class="chip solid nopide" {an("nopide", "blur-in", 202.2, 0.5)}>Sin que se lo pidas</span>
""",
    """
.card[data-card-id="card-11"] .opt { display:flex; gap:26px; padding:28px; border-radius:24px; background:var(--panel); border:2px solid var(--line); }
.card[data-card-id="card-11"] .onum { width:68px; height:68px; flex:none; border-radius:50%; background:var(--acc); color:#141312; font:700 36px/68px 'Inter'; text-align:center; }
.card[data-card-id="card-11"] .ot { font:700 40px/1.2 'Inter'; }
.card[data-card-id="card-11"] .os { font:400 30px/1.3 'Inter'; color:var(--muted); margin-top:10px; }
.card[data-card-id="card-11"] .slash { font-size:34px; margin-top:16px; padding:18px 24px; min-height:0; }
.card[data-card-id="card-11"] .bubble { position:relative; align-self:flex-end; max-width:760px; padding:28px 34px; border-radius:28px 28px 6px 28px; background:var(--panel-2); border:2px solid var(--acc); font:700 36px/1.3 'Inter'; }
.card[data-card-id="card-11"] .nopide { align-self:flex-end; }
""",
)

# 12 ─ skill saved; save by clicking the button
begin("card-12", 207.7)
card(
    "card-12", 207.7, 221.9, 2,
    "Skill saved; first way to save it is clicking the button",
    {"title": "Skill guardada", "detail": "Dos maneras de guardarla"},
    f"""
<div class="saved"><span class="bigok">{check_path("chk", 207.9, 110, 0.6)}</span>{title("title", "Skill guardada", 208.4, 0.6)}</div>
<p class="lead" {an("two", "fade-in", 211.4, 0.4)}>Dos maneras de guardarla:</p>
<div class="opt" {an("o1", "slide-in", 215.3, 0.5, **{"from": "left", "distance": 70})}>
  <span class="onum">1</span><div class="ot grow">Pinchar el botón</div>
  <div class="btnwrap"><span class="ripple" {an("ripple", "morph-to", 217.4, 0.7, **{"from": {"scale": 0.2, "opacity": 0.8}, "props": {"scale": 2.2, "opacity": 0}})}></span><span class="btn">Guardar</span></div>
</div>
<p class="lead tease" {an("tease", "fade-in", 218.8, 0.5)}>Y hay otra cosa interesante...</p>
""",
    """
.card[data-card-id="card-12"] .saved { display:flex; align-items:center; gap:34px; margin-top:20px; }
.card[data-card-id="card-12"] .bigok { width:150px; height:150px; flex:none; border-radius:50%; background:var(--acc); color:#141312; display:flex; align-items:center; justify-content:center; }
.card[data-card-id="card-12"] .opt { display:flex; align-items:center; gap:26px; padding:30px; border-radius:24px; background:var(--panel); border:2px solid var(--line); }
.card[data-card-id="card-12"] .onum { width:68px; height:68px; flex:none; border-radius:50%; background:var(--acc); color:#141312; font:700 36px/68px 'Inter'; text-align:center; }
.card[data-card-id="card-12"] .ot { font:700 40px/1.2 'Inter'; }
.card[data-card-id="card-12"] .btnwrap { position:relative; }
.card[data-card-id="card-12"] .btn { position:relative; display:inline-block; padding:20px 36px; border-radius:14px; background:var(--text); color:#141312; font:700 32px/1 'Inter'; }
.card[data-card-id="card-12"] .ripple { position:absolute; left:50%; top:50%; width:140px; height:140px; margin:-70px 0 0 -70px; border-radius:50%; border:4px solid var(--acc); }
.card[data-card-id="card-12"] .tease { color:var(--text); }
""",
)

# 13 ─ upload other people's skills
begin("card-13", 221.9)
card(
    "card-13", 221.9, 234.4, 3,
    "Second way: upload skills from other people via Customize > Add > Skill",
    {"title": "Sube skills de otras personas", "detail": "Customize > Agregar > Skill"},
    f"""
{kicker("Manera 2", 222.0)}
{title("title", "Sube skills de otras personas", 222.1, 0.7)}
<div class="path">
  <span class="chip big" {an("p1", "scale-pop", 229.2, 0.45)}>Customize</span>
  <span class="sep" {an("s1", "fade-in", 230.3, 0.3)}>{icon("arrow-r", 56)}</span>
  <span class="chip big" {an("p2", "scale-pop", 230.6, 0.45)}>Agregar</span>
  <span class="sep" {an("s2", "fade-in", 231.8, 0.3)}>{icon("arrow-r", 56)}</span>
  <span class="chip big solid" {an("p3", "scale-pop", 232.1, 0.45)}>{icon("upload", 40)}Skill</span>
</div>
""",
    """
.card[data-card-id="card-13"] .path { display:flex; flex-wrap:wrap; align-items:center; gap:16px; margin-top:40px; }
.card[data-card-id="card-13"] .sep { color:var(--muted); }
""",
)

# 14 ─ skills shared on social, file formats
begin("card-14", 234.4)
card(
    "card-14", 234.4, 251.0, 1,
    "Skills shared on social media come as zip, skill file or MD file; you upload them and they work",
    {"title": "Ya vienen listas", "detail": ".zip / skill file / .md"},
    f"""
{kicker("En redes sociales", 234.6)}
<div class="post" {an("post", "scale-pop", 234.8, 0.5)}>
  <span class="av">{ICONS["user"]}</span>
  <div class="pb">«Comenta y te envío mis skills»</div>
</div>
<p class="lead" {an("lead", "fade-in", 240.2, 0.4)}>Muchas veces ya vienen listas en:</p>
<div class="files">
  <div class="file" {an("f1", "scale-pop", 243.6, 0.45)}>{icon("doc", 70)}<span class="mono">.zip</span></div>
  <div class="file" {an("f2", "scale-pop", 244.8, 0.45)}>{icon("doc", 70)}<span class="mono">skill file</span></div>
  <div class="file" {an("f3", "scale-pop", 246.0, 0.45)}>{icon("doc", 70)}<span class="mono">.md</span></div>
</div>
<div class="works"><span class="okc">{check_path("chk", 247.8, 44)}</span><span {an("w", "fade-in", 247.7, 0.4)}>Las subes y funcionan sin problema</span></div>
""",
    """
.card[data-card-id="card-14"] .post { display:flex; align-items:flex-start; gap:22px; }
.card[data-card-id="card-14"] .av { width:76px; height:76px; flex:none; border-radius:50%; background:var(--panel-2); color:var(--muted); display:flex; align-items:center; justify-content:center; }
.card[data-card-id="card-14"] .av svg { width:46px; height:46px; }
.card[data-card-id="card-14"] .pb { padding:26px 32px; border-radius:6px 28px 28px 28px; background:var(--panel); border:2px solid var(--acc); font:700 40px/1.25 'Inter'; }
.card[data-card-id="card-14"] .files { display:flex; gap:20px; }
.card[data-card-id="card-14"] .file { flex:1; display:flex; flex-direction:column; align-items:center; gap:16px; padding:30px 10px; border-radius:24px; background:var(--panel); border:2px solid var(--line); color:var(--acc); font-size:32px; }
.card[data-card-id="card-14"] .file .mono { color:var(--text); font-weight:700; }
.card[data-card-id="card-14"] .works { display:flex; align-items:center; gap:20px; font:700 38px/1.2 'Inter'; }
.card[data-card-id="card-14"] .okc { width:64px; height:64px; flex:none; border-radius:50%; background:var(--accent-2); color:#141312; display:flex; align-items:center; justify-content:center; }
""",
)

# 15 ─ launch the skill in the chat
begin("card-15", 251.0)
card(
    "card-15", 251.0, 274.3, 0,
    "Back in the chat, launch the new skill",
    {"title": "Ahora toca usarla"},
    f"""
{kicker("Usar la skill", 251.2)}
{title("title", "Ahora toca usarla", 251.3, 0.6)}
<div class="chatline" {an("back", "fade-in", 253.0, 0.4)}>{icon("chat", 44, "color:var(--muted)")}<span>De vuelta al último chat</span></div>
<div class="pop" {an("pop", "slide-in", 262.2, 0.5, **{"from": "bottom", "distance": 50})}>
  <div class="it"><span class="sk"></span></div>
  <div class="it hl" {an("hl", "morph-to", 265.6, 0.4, **{"from": {"opacity": 0.35}, "props": {"opacity": 1}})}>{icon("spark", 34)}<span>Tu skill nueva</span></div>
  <div class="it"><span class="sk" style="width:46%"></span></div>
</div>
<div class="input mono"><span class="acc">/</span><span class="caret"></span></div>
<span class="chip solid launch" {an("launch", "scale-pop", 268.6, 0.5)}>Lanzar la skill</span>
""",
    """
.card[data-card-id="card-15"] .chatline { display:flex; align-items:center; gap:18px; font:400 34px/1.2 'Inter'; color:var(--muted); }
.card[data-card-id="card-15"] .pop { display:flex; flex-direction:column; gap:10px; padding:18px; border-radius:22px; background:var(--panel); border:2px solid var(--line); }
.card[data-card-id="card-15"] .it { display:flex; align-items:center; gap:16px; padding:20px 22px; border-radius:14px; font:700 34px/1 'Inter'; }
.card[data-card-id="card-15"] .it.hl { background:var(--panel-2); border:2px solid var(--acc); color:var(--acc); }
.card[data-card-id="card-15"] .it.hl span:last-child { color:var(--text); }
.card[data-card-id="card-15"] .sk { display:block; width:60%; height:20px; border-radius:10px; background:var(--panel-2); }
.card[data-card-id="card-15"] .input { font-size:48px; padding:24px 32px; min-height:0; }
.card[data-card-id="card-15"] .caret { display:inline-block; width:4px; height:52px; background:var(--text); margin-left:6px; vertical-align:middle; }
.card[data-card-id="card-15"] .launch { align-self:flex-start; }
""",
)

# 16 ─ the key question, revealed word by word with the speech
qwords = [("Lo", 274.4), ("que", 275.9), ("tenemos", 277.3), ("que", 278.8), ("pensar", 280.2), ("en", 281.7), ("esta", 283.1), ("pieza", 284.6), ("publicitaria", 286.0), ("es que...", 287.1)]
QCLS = ["qw hot" if i in (7, 8) else "qw" for i in range(len(qwords))]
begin("card-16", 274.3)
card(
    "card-16", 274.3, 292.4, 4,
    "The key question for the ad piece, revealed word by word as it is spoken",
    {"title": "Lo que tenemos que pensar en esta pieza publicitaria es que..."},
    f"""
{kicker("La pieza publicitaria", 274.5)}
<div class="mega">{icon("megaphone", 130)}</div>
<h1 class="q">{" ".join(f'<span class="{QCLS[i]}" {an(f"w{i}", "blur-in", t, 0.5)}>{esc(w)}</span>' for i, (w, t) in enumerate(qwords))}</h1>
""",
    """
.card[data-card-id="card-16"] .mega { color:var(--acc); margin-top:20px; }
.card[data-card-id="card-16"] .q { font:700 96px/1.06 'Inter'; letter-spacing:-0.03em; margin:0; }
.card[data-card-id="card-16"] .qw { display:inline-block; }
.card[data-card-id="card-16"] .qw.hot { color:var(--acc); }
""",
)


def field(name, label, value, at, cls=""):
    return (
        f'<div class="fld {cls}"><div class="fl mono" {an(name + "-l", "fade-in", at - 0.2, 0.3)}>{esc(label)}</div>'
        f'<div class="fv" {an(name, "slide-in", at, 0.45, **{"from": "left", "distance": 50})}>{value}</div></div>'
    )


BRIEF_CSS = """
.card[data-card-id="{cid}"] .doc {{ display:flex; flex-direction:column; padding:30px 34px; border-radius:28px; background:#F3EEE6; color:#1d1b19; }}
.card[data-card-id="{cid}"] .dh {{ display:flex; align-items:center; justify-content:space-between; padding-bottom:18px; border-bottom:3px solid #1d1b19; margin-bottom:6px; }}
.card[data-card-id="{cid}"] .dh .dt {{ font:700 40px/1 'Inter'; letter-spacing:-0.01em; }}
.card[data-card-id="{cid}"] .dh .dk {{ font:700 22px/1 'JetBrains Mono'; letter-spacing:.14em; color:#9a4a2e; }}
.card[data-card-id="{cid}"] .fld {{ padding:16px 0; border-bottom:2px solid #d9d2c6; }}
.card[data-card-id="{cid}"] .fld:last-child {{ border-bottom:0; }}
.card[data-card-id="{cid}"] .fl {{ font-size:20px; letter-spacing:.14em; text-transform:uppercase; color:#6b655d; margin-bottom:8px; }}
.card[data-card-id="{cid}"] .fv {{ font:700 32px/1.25 'Inter'; }}
.card[data-card-id="{cid}"] .no .fv {{ color:#a3311c; }}
"""

# 17 ─ brief: objective, channel, reaction, logo, approval, restrictions
begin("card-17", 292.4)
card(
    "card-17", 292.4, 339.1, 0,
    "The brief fills in: objective, channel, expected reaction, mandatory logo, approval, what cannot appear",
    {"title": "Brief: lo esencial"},
    f"""
<div class="doc" {an("doc", "slide-in", 292.5, 0.5, **{"from": "bottom", "distance": 60})}>
  <div class="dh"><span class="dt">Brief · Evento de Navidad</span><span class="dk">BORRADOR</span></div>
  {field("f1", "Objetivo", "Que los estudiantes vayan al evento de Navidad", 293.4)}
  {field("f2", "Canal", "Redes de la universidad + envío a todos los estudiantes", 302.7)}
  {field("f3", "Reacción esperada", "Que quieran ir al evento", 311.1)}
  {field("f4", "Logo obligatorio", "Logo de la universidad", 315.7)}
  {field("f5", "Aprobación", "Se envía en noviembre para que lo aprueben", 318.7)}
  {field("f6", "No puede aparecer", "Nada fuera de la guía de IA de la universidad", 326.2, "no")}
  {field("f7", "No puede aparecer", "Nada explícito ni grosero", 335.9, "no")}
</div>
""",
    BRIEF_CSS.format(cid="card-17"),
)

# 18 ─ the event: attendance, date, place (corrected), time, insight
begin("card-18", 339.1)
card(
    "card-18", 339.1, 381.5, 1,
    "Event facts: 100 students, 1 December, Building 5 corrected to the Paraninfo, 10 a.m., nobody knows the event exists",
    {"title": "El evento"},
    f"""
{kicker("Brief · el evento", 339.3)}
<div class="grid">
  <div class="tile" {an("t1", "scale-pop", 339.4, 0.45)}><div class="tv"><span class="num" {an("n100", "count-up", 342.6, 1.2, **{"from": 0, "to": 100, "format": ",d"})}>0</span></div><div class="tl">estudiantes, mínimo</div></div>
  <div class="tile" {an("t2", "scale-pop", 346.0, 0.45)}><div class="tv"><span {an("date", "blur-in", 347.5, 0.5)}>1 dic</span></div><div class="tl">fecha</div></div>
  <div class="tile wide" {an("t3", "scale-pop", 352.6, 0.45)}>
    <div class="places">
      <span class="old" {an("old", "slide-in", 355.2, 0.4, **{"from": "left", "distance": 40})}><span {an("olddim", "morph-to", 358.6, 0.4, **{"from": {"opacity": 1}, "props": {"opacity": 0.4}})}>Edificio 5</span><span class="strike" {an("strike", "morph-to", 358.4, 0.4, **{"from": {"scaleX": 0}, "props": {"scaleX": 1}})}></span></span>
      <span class="new" {an("new", "slide-in", 361.2, 0.45, **{"from": "right", "distance": 50})}>Paraninfo</span>
    </div>
    <div class="tl">lugar</div>
  </div>
  <div class="tile wide" {an("t4", "scale-pop", 364.4, 0.45)}><div class="tv"><span {an("hour", "blur-in", 365.9, 0.5)}>10:00 a.m.</span></div><div class="tl">hora</div></div>
</div>
<div class="insight" {an("ins", "slide-in", 370.1, 0.5, **{"from": "bottom", "distance": 40})}>{icon("megaphone", 56)}<span>No saben que existe: hay que promocionarlo bastante</span></div>
""",
    """
.card[data-card-id="card-18"] .grid { display:grid; grid-template-columns:1fr 1fr; gap:18px; }
.card[data-card-id="card-18"] .tile { padding:26px 30px; border-radius:24px; background:var(--panel); border:2px solid var(--line); }
.card[data-card-id="card-18"] .tile.wide { grid-column:span 2; }
.card[data-card-id="card-18"] .tv { font:700 92px/1 'Inter'; letter-spacing:-0.03em; color:var(--acc); font-variant-numeric:tabular-nums; }
.card[data-card-id="card-18"] .tl { font:400 28px/1.2 'Inter'; color:var(--muted); margin-top:12px; }
.card[data-card-id="card-18"] .places { display:flex; align-items:center; gap:30px; font:700 64px/1 'Inter'; }
.card[data-card-id="card-18"] .old { position:relative; color:var(--muted); }
.card[data-card-id="card-18"] .strike { position:absolute; left:-6px; right:-6px; top:50%; height:6px; margin-top:-3px; background:var(--accent-1); border-radius:3px; transform-origin:left center; }
.card[data-card-id="card-18"] .new { color:var(--acc); }
.card[data-card-id="card-18"] .insight { display:flex; align-items:center; gap:22px; padding:26px 30px; border-radius:24px; background:var(--acc); color:#141312; font:700 34px/1.25 'Inter'; }
""",
)

# 19 ─ the piece: static, channels, form, AI images, logo
begin("card-19", 381.5)
card(
    "card-19", 381.5, 411.0, 2,
    "The piece: static image for Instagram and university email, sign-up form, made with AI images, logo from the website",
    {"title": "La pieza"},
    f"""
{kicker("Brief · la pieza", 381.7)}
<div class="hero" {an("hero", "scale-pop", 382.4, 0.5)}>{icon("image", 110)}<div><div class="ht">Pieza estática</div><div class="hs">Una imagen, no video</div></div></div>
<div class="chans">
  <span class="chip big" {an("ig", "scale-pop", 386.7, 0.45)}>{icon("image", 38)}Instagram</span>
  <span class="chip big" {an("mail", "scale-pop", 388.1, 0.45)}>{icon("mail", 38)}Correo de la universidad</span>
</div>
<div class="lines">
  <div class="li" {an("form", "slide-in", 392.3, 0.45, **{"from": "left", "distance": 50})}>{icon("form", 46)}<span>Inscripción en formulario para confirmar asistencia</span></div>
  <div class="li" {an("d20", "slide-in", 399.6, 0.45, **{"from": "left", "distance": 50})}>{icon("calendar", 46)}<span>Se entrega el 20 de noviembre</span></div>
  <div class="li" {an("ai", "slide-in", 403.2, 0.45, **{"from": "left", "distance": 50})}>{icon("spark", 46)}<span>Se produce con imágenes de IA</span></div>
  <div class="li" {an("logo", "slide-in", 406.1, 0.45, **{"from": "left", "distance": 50})}>{icon("search", 46)}<span>Logo: de la página de la universidad</span></div>
</div>
""",
    """
.card[data-card-id="card-19"] .hero { display:flex; align-items:center; gap:32px; padding:28px 32px; border-radius:26px; background:var(--panel); border:2px solid var(--acc); color:var(--acc); }
.card[data-card-id="card-19"] .ht { font:700 54px/1.05 'Inter'; color:var(--text); }
.card[data-card-id="card-19"] .hs { font:400 30px/1.3 'Inter'; color:var(--muted); margin-top:8px; }
.card[data-card-id="card-19"] .chans { display:flex; flex-wrap:wrap; gap:16px; }
.card[data-card-id="card-19"] .lines { display:flex; flex-direction:column; gap:14px; }
.card[data-card-id="card-19"] .li { display:flex; align-items:center; gap:22px; padding:20px 26px; border-radius:18px; background:var(--panel); font:700 32px/1.25 'Inter'; color:var(--text); }
.card[data-card-id="card-19"] .li .ico { color:var(--acc); flex:none; }
""",
)

# 20 ─ calendar and loose ends
begin("card-20", 411.0)
card(
    "card-20", 411.0, 433.9, 3,
    "Calendar (20 Nov delivery, 27 Nov sign-ups close, 1 Dec event) plus approver, form link, activities",
    {"title": "Calendario"},
    f"""
{kicker("Brief · calendario", 411.2)}
<div class="tline">
  <div class="rail"><div class="railfill" {an("rail", "morph-to", 411.3, 1.0, **{"from": {"scaleX": 0}, "props": {"scaleX": 1}})}></div></div>
  <div class="ev e1" {an("e1", "scale-pop", 411.6, 0.45)}><span class="dot"></span><div class="ed">20 nov</div><div class="el">Entrega para aprobación</div></div>
  <div class="ev e2" {an("e2", "scale-pop", 430.6, 0.5)}><span class="dot hot"></span><div class="ed">27 nov</div><div class="el">Cierran inscripciones</div></div>
  <div class="ev e3" {an("e3", "scale-pop", 412.0, 0.45)}><span class="dot"></span><div class="ed">1 dic</div><div class="el">Evento, 10:00 a.m.</div></div>
</div>
<div class="kv">
  <div class="k" {an("k1", "slide-in", 413.9, 0.45, **{"from": "left", "distance": 50})}><span class="kk mono">Aprueba</span><span class="vv">Rectoría</span></div>
  <div class="k" {an("k2", "slide-in", 416.6, 0.45, **{"from": "left", "distance": 50})}><span class="kk mono">Enlace del formulario</span><span class="vv">Va en el copy</span></div>
  <div class="k" {an("k3", "slide-in", 425.8, 0.45, **{"from": "left", "distance": 50})}><span class="kk mono">Actividades</span><span class="vv">Sorpresa</span></div>
</div>
""",
    """
.card[data-card-id="card-20"] .tline { position:relative; height:290px; margin-top:10px; }
.card[data-card-id="card-20"] .rail { position:absolute; left:20px; right:20px; top:40px; height:8px; border-radius:4px; background:var(--panel-2); }
.card[data-card-id="card-20"] .railfill { width:100%; height:100%; border-radius:4px; background:var(--acc); transform-origin:left center; }
.card[data-card-id="card-20"] .ev { position:absolute; top:22px; width:300px; }
.card[data-card-id="card-20"] .e1 { left:0; }
.card[data-card-id="card-20"] .e2 { left:342px; }
.card[data-card-id="card-20"] .e3 { left:684px; }
.card[data-card-id="card-20"] .dot { display:block; width:44px; height:44px; border-radius:50%; background:var(--bg); border:6px solid var(--acc); }
.card[data-card-id="card-20"] .dot.hot { background:var(--acc); }
.card[data-card-id="card-20"] .ed { font:700 64px/1 'Inter'; letter-spacing:-0.02em; margin-top:26px; }
.card[data-card-id="card-20"] .el { font:400 28px/1.25 'Inter'; color:var(--muted); margin-top:12px; }
.card[data-card-id="card-20"] .kv { display:flex; flex-direction:column; gap:14px; }
.card[data-card-id="card-20"] .k { display:flex; align-items:center; justify-content:space-between; gap:20px; padding:24px 28px; border-radius:18px; background:var(--panel); border:2px solid var(--line); }
.card[data-card-id="card-20"] .kk { font-size:22px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); }
.card[data-card-id="card-20"] .vv { font:700 38px/1.1 'Inter'; color:var(--acc); }
""",
)

# 21 ─ the brief as a PDF
begin("card-21", 433.9)
card(
    "card-21", 433.9, 444.2, 0,
    "Ask for the brief as a PDF, it arrives, download it",
    {"title": "Brief en PDF"},
    f"""
{kicker("Resultado", 434.0)}
<div class="ask input"><span class="tw" {an("ask", "typewriter", 434.0, 2.4)}>{chars("Dame el brief como un PDF")}</span></div>
<div class="pdf" {an("pdf", "scale-pop", 437.7, 0.6)}>
  <div class="page"><div class="pt mono">PDF</div><div class="pl"></div><div class="pl" style="width:70%"></div><div class="pl"></div><div class="pl" style="width:55%"></div></div>
  <div><div class="ready">Brief listo</div><div class="dl" {an("dl", "slide-in", 441.2, 0.45, **{"from": "top", "distance": 40})}>{icon("download", 52)}<span>Descargar</span></div></div>
</div>
""",
    """
.card[data-card-id="card-21"] .ask { font:700 42px/1.3 'Inter'; align-self:flex-end; border-color:var(--acc); }
.card[data-card-id="card-21"] .pdf { display:flex; align-items:center; gap:44px; margin-top:20px; }
.card[data-card-id="card-21"] .page { width:300px; height:390px; flex:none; border-radius:16px; background:#F3EEE6; padding:30px; display:flex; flex-direction:column; gap:20px; }
.card[data-card-id="card-21"] .pt { align-self:flex-start; padding:8px 14px; border-radius:8px; background:var(--accent-0); color:#141312; font-size:24px; font-weight:700; }
.card[data-card-id="card-21"] .pl { height:16px; border-radius:8px; background:#d9d2c6; }
.card[data-card-id="card-21"] .ready { font:700 64px/1.05 'Inter'; letter-spacing:-0.02em; }
.card[data-card-id="card-21"] .dl { display:inline-flex; align-items:center; gap:16px; margin-top:26px; padding:18px 28px; border-radius:16px; background:var(--acc); color:#141312; font:700 32px/1 'Inter'; }
""",
)

hprompt = "Por favor realiza esta pieza gráfica utilizando el conector de Higgsfield"
# 22 ─ a fresh chat with no context
begin("card-22", 444.2)
card(
    "card-22", 444.2, 471.1, 4,
    "Test in a new chat with no prior context: drop the PDF and ask for the graphic via the Higgsfield connector",
    {"title": "En otro chat", "detail": hprompt},
    f"""
{kicker("La prueba", 444.4)}
{title("title", "En otro chat, sin contexto", 448.2, 0.7, cls="title sm")}
<div class="chats">
  <div class="cw old" {an("c1", "fade-in", 444.6, 0.4)}><div class="ch mono">chat 1</div><div class="mini">PDF</div></div>
  <div class="gap"><span {an("unlink", "scale-pop", 466.4, 0.5)}>{icon("unlink", 74)}</span></div>
  <div class="cw new" {an("c2", "scale-pop", 449.0, 0.5)}><div class="ch mono">chat 2 · nuevo</div><div class="mini" {an("pdf2", "slide-in", 451.0, 0.5, **{"from": "left", "distance": 120})}>PDF</div></div>
</div>
<div class="input big"><span class="tw" {an("prompt", "typewriter", 454.9, 4.8)}>{chars(hprompt)}</span></div>
<div class="foot"><span class="lead" {an("noctx", "fade-in", 466.4, 0.4)}>No tiene el contexto del chat anterior</span><span class="send" {an("send", "scale-pop", 461.6, 0.4)}>{ICONS["send"]}</span></div>
""",
    """
.card[data-card-id="card-22"] .chats { display:flex; align-items:center; gap:18px; }
.card[data-card-id="card-22"] .cw { flex:1; height:190px; padding:22px; border-radius:24px; background:var(--panel); border:2px solid var(--line); display:flex; flex-direction:column; gap:18px; }
.card[data-card-id="card-22"] .cw.old { opacity:.55; }
.card[data-card-id="card-22"] .cw.new { border-color:var(--acc); }
.card[data-card-id="card-22"] .ch { font-size:24px; color:var(--muted); letter-spacing:.08em; }
.card[data-card-id="card-22"] .mini { align-self:flex-start; padding:16px 22px; border-radius:12px; background:#F3EEE6; color:#141312; font:700 28px/1 'JetBrains Mono'; }
.card[data-card-id="card-22"] .gap { color:var(--accent-1); width:80px; display:flex; justify-content:center; }
.card[data-card-id="card-22"] .input.big { font:700 38px/1.35 'Inter'; min-height:220px; }
.card[data-card-id="card-22"] .foot { display:flex; align-items:center; justify-content:space-between; gap:20px; }
.card[data-card-id="card-22"] .send { width:90px; height:90px; flex:none; border-radius:50%; background:var(--acc); color:#141312; display:flex; align-items:center; justify-content:center; }
.card[data-card-id="card-22"] .send svg { width:52px; height:52px; }
""",
)

# 23 ─ brief to finished graphic
begin("card-23", 471.1)
card(
    "card-23", 471.1, 481.2, 2,
    "After reading the brief, Claude made the graphic with the Higgsfield connector",
    {"title": "Del brief a la pieza"},
    f"""
{kicker("Resultado", 471.2)}
<div class="flow">
  <div class="fn" {an("b", "scale-pop", 471.3, 0.45)}><span class="mini">PDF</span><span>Brief</span></div>
  <div class="fa" {an("read", "mask-reveal", 473.4, 0.5, direction="left")}>{icon("arrow-r", 80)}<span class="mono">lee</span></div>
  <div class="fn art" {an("art", "scale-pop", 476.4, 0.6)}>{icon("image", 120)}<span>Pieza gráfica</span></div>
</div>
<div class="via" {an("via", "blur-in", 478.8, 0.5)}>{icon("spark", 44)}<span>Hecha con el conector de Higgsfield</span></div>
""",
    """
.card[data-card-id="card-23"] .flow { display:flex; align-items:center; justify-content:space-between; margin-top:60px; }
.card[data-card-id="card-23"] .fn { display:flex; flex-direction:column; align-items:center; gap:22px; padding:36px 30px; border-radius:28px; background:var(--panel); border:2px solid var(--line); font:700 36px/1 'Inter'; min-width:260px; }
.card[data-card-id="card-23"] .fn .mini { padding:22px 30px; border-radius:12px; background:#F3EEE6; color:#141312; font:700 34px/1 'JetBrains Mono'; }
.card[data-card-id="card-23"] .fn.art { border-color:var(--acc); color:var(--acc); min-width:330px; }
.card[data-card-id="card-23"] .fn.art span { color:var(--text); }
.card[data-card-id="card-23"] .fa { display:flex; flex-direction:column; align-items:center; color:var(--muted); font-size:26px; }
.card[data-card-id="card-23"] .via { display:flex; align-items:center; gap:20px; align-self:center; margin-top:40px; padding:24px 34px; border-radius:999px; background:var(--acc); color:#141312; font:700 34px/1 'Inter'; }
""",
)

# 24 ─ recap
begin("card-24", 481.2)
card(
    "card-24", 481.2, DURATION, 0,
    "Recap: that is how a skill is made",
    {"title": "Así se crea una skill"},
    f"""
{title("title", "Así se crea una skill", 481.3, 0.6)}
<div class="steps">
  <div class="st" {an("s1", "slide-in", 482.2, 0.4, **{"from": "left", "distance": 60})}><span class="sn mono">1</span>Junta el material en un folder</div>
  <div class="st" {an("s2", "slide-in", 482.6, 0.4, **{"from": "left", "distance": 60})}><span class="sn mono">2</span><span class="mono acc">/skill-creator</span></div>
  <div class="st" {an("s3", "slide-in", 483.0, 0.4, **{"from": "left", "distance": 60})}><span class="sn mono">3</span>Guarda la skill</div>
  <div class="st" {an("s4", "slide-in", 483.4, 0.4, **{"from": "left", "distance": 60})}><span class="sn mono">4</span>Úsala en cualquier chat</div>
</div>
""",
    """
.card[data-card-id="card-24"] .steps { display:flex; flex-direction:column; gap:18px; margin-top:20px; }
.card[data-card-id="card-24"] .st { display:flex; align-items:center; gap:26px; padding:28px 30px; border-radius:22px; background:var(--panel); border:2px solid var(--line); font:700 40px/1.2 'Inter'; }
.card[data-card-id="card-24"] .sn { width:62px; height:62px; flex:none; border-radius:50%; background:var(--acc); color:#141312; font-size:30px; line-height:62px; text-align:center; }
""",
)

CHAPTERS = [
    ("Qué es una skill", 0.0, 22.4),
    ("El material", 22.4, 108.1),
    ("Crear la skill", 108.1, 207.7),
    ("Guardar y compartir", 207.7, 251.0),
    ("Usar la skill", 251.0, 433.9),
    ("El resultado", 433.9, DURATION),
]

# ── compile data-anim declarations into GSAP ───────────────────────────────


def js(v):
    return json.dumps(v, ensure_ascii=False)


def compile_anim(cid, a):
    sel = js(f'.card[data-card-id="{cid}"] #{a["id"]}')
    T = q(a["at"])
    D = a["dur"]
    k = a["kind"]
    if k == "fade-in":
        return f"tl.fromTo({sel},{{opacity:0}},{{opacity:1,duration:{D},ease:'power2.out'}},{T});"
    if k == "slide-in":
        dist = a.get("distance", 80)
        frm = a.get("from", "left")
        axis, sign = {"left": ("x", -1), "right": ("x", 1), "top": ("y", -1), "bottom": ("y", 1)}[frm]
        return f"tl.fromTo({sel},{{opacity:0,{axis}:{sign * dist}}},{{opacity:1,{axis}:0,duration:{D},ease:'power3.out'}},{T});"
    if k == "kinetic-chars":
        s = a.get("stagger", 0.03)
        csel = js('.card[data-card-id="' + cid + '"] #' + a["id"] + " .char")
        return f"tl.fromTo({csel},{{opacity:0,y:24,scale:0.85}},{{opacity:1,y:0,scale:1,duration:{D},ease:'power3.out',stagger:{s}}},{T});"
    if k == "typewriter":
        n = a["_nchars"]
        s = round(D / max(n, 1), 4)
        csel = js('.card[data-card-id="' + cid + '"] #' + a["id"] + " .char")
        return f"tl.fromTo({csel},{{opacity:0}},{{opacity:1,duration:0.01,ease:'none',stagger:{s}}},{T});"
    if k == "count-up":
        return (
            f"(function(){{const o={{v:{a['from']}}};tl.to(o,{{v:{a['to']},duration:{D},ease:'power2.out',"
            f"onUpdate:function(){{const el=document.querySelector({sel});if(el)el.textContent=__fmt(o.v,{js(a['format'])});}}}},{T});}})();"
        )
    if k == "draw-path":
        return f"tl.fromTo({sel},{{strokeDasharray:1,strokeDashoffset:1}},{{strokeDashoffset:0,duration:{D},ease:'power2.inOut'}},{T});"
    if k == "scale-pop":
        return f"tl.fromTo({sel},{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:{D},ease:'back.out(1.6)'}},{T});"
    if k == "blur-in":
        return f"tl.fromTo({sel},{{opacity:0,filter:'blur(14px)'}},{{opacity:1,filter:'blur(0px)',duration:{D},ease:'power2.out'}},{T});"
    if k == "mask-reveal":
        start = {"left": "inset(0 100% 0 0)", "right": "inset(0 0 0 100%)", "top": "inset(0 0 100% 0)", "bottom": "inset(100% 0 0 0)"}[a.get("direction", "left")]
        return f"tl.fromTo({sel},{{clipPath:'{start}'}},{{clipPath:'inset(0% 0% 0% 0%)',duration:{D},ease:'power2.inOut'}},{T});"
    if k == "morph-to":
        frm, props = a["from"], a["props"]
        return f"tl.fromTo({sel},{js(frm)},{{...{js(props)},duration:{D},ease:'power2.out'}},{T});"
    raise ValueError(k)


def count_chars(body, el_id):
    seg = body.split(f'id="{el_id}"', 1)[1]
    seg = seg.split("</div>", 1)[0]
    return seg.count('class="char"')


# ── write files ────────────────────────────────────────────────────────────

os.makedirs(os.path.join(PUB, "cards"), exist_ok=True)

storyboard = {
    "schemaVersion": 3,
    "composition": {"fps": FPS, "width": W, "height": H, "durationSeconds": DURATION, "layout": "portrait", "themeId": "custom-warm-dark", "seed": 42},
    "videoTrack": {"sourcePath": "input-video.mp4", "startSec": 0, "endSec": DURATION, "bounds": {"x": 0, "y": 0, "width": W, "height": VIDEO_H}},
    "subtitles": {"enabled": False},
    "cards": [
        {"id": c["id"], "intent": c["intent"], "startSec": c["start"], "endSec": c["end"], "accentIndex": c["accent"], "zone": "lower-third", "contentHints": c["hints"]}
        for c in CARDS
    ],
}
with open(os.path.join(HERE, "storyboard.json"), "w") as f:
    json.dump(storyboard, f, ensure_ascii=False, indent=2)

hosts = []
script_lines = []
for i, c in enumerate(CARDS):
    cid = c["id"]
    frag = (
        f'<div class="card" data-card-id="{cid}">\n<style>{c["css"]}\n'
        f'.card[data-card-id="{cid}"] {{ --acc: var(--accent-{c["accent"]}); }}\n</style>\n'
        f'<div class="root">{c["body"]}</div>\n</div>\n'
    )
    with open(os.path.join(PUB, "cards", f"{cid}.html"), "w") as f:
        f.write(frag)
    dur = round(c["end"] - c["start"], 4)
    hosts.append(
        f'<div class="card-host clip" id="host-{cid}" data-card-id="{cid}" data-start="{c["start"]}" data-duration="{dur}" '
        f'data-track-index="{2 + i % 2}" style="left:0;top:{CARD_TOP}px;width:{W}px;height:{CARD_H}px;">\n{frag}</div>'
    )
    card_sel = js(f'.card[data-card-id="{cid}"]')
    script_lines.append(f"// {cid} [{c['start']}, {c['end']}]")
    script_lines.append(f"tl.fromTo({card_sel},{{opacity:0,y:36}},{{opacity:1,y:0,duration:0.45,ease:'power3.out'}},{q(c['start'])});")
    for a in c["anims"]:
        if a["kind"] == "typewriter":
            a["_nchars"] = count_chars(c["body"], a["id"])
        script_lines.append(compile_anim(cid, a))
    if c["end"] < DURATION:
        script_lines.append(f"tl.to({card_sel},{{opacity:0,y:-24,duration:0.35,ease:'power2.in'}},{q(c['end'] - 0.35)});")

# chapter rail
rail_titles = "".join(f'<span class="ct" id="ct-{i}">{esc(t)}</span>' for i, (t, _, _) in enumerate(CHAPTERS))
rail_nums = "".join(f'<span class="cn" id="cn-{i}">{i + 1:02d}</span>' for i in range(len(CHAPTERS)))
rail_segs = "".join(f'<div class="seg"><div class="segfill" id="sf-{i}"></div></div>' for i in range(len(CHAPTERS)))
script_lines.append("// chapter rail")
for i, (_, s, e) in enumerate(CHAPTERS):
    s_q, e_q = q(s), q(e)
    script_lines.append(f"tl.fromTo('#sf-{i}',{{scaleX:0}},{{scaleX:1,duration:{round(e_q - s_q, 4)},ease:'none'}},{s_q});")
    script_lines.append(f"tl.fromTo('#ct-{i}',{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.5,ease:'power3.out'}},{s_q});")
    script_lines.append(f"tl.fromTo('#cn-{i}',{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.5,ease:'power3.out'}},{s_q});")
    if e < DURATION:
        script_lines.append(f"tl.to('#ct-{i}',{{opacity:0,y:-30,duration:0.35,ease:'power2.in'}},{q(e - 0.35)});")
        script_lines.append(f"tl.to('#cn-{i}',{{opacity:0,y:-30,duration:0.35,ease:'power2.in'}},{q(e - 0.35)});")

INDEX = f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8" />
    <style>
      @font-face {{ font-family: "Inter"; src: url("fonts/Inter-400-latin.woff2") format("woff2"); font-weight: 400; font-display: block; }}
      @font-face {{ font-family: "Inter"; src: url("fonts/Inter-700-latin.woff2") format("woff2"); font-weight: 700; font-display: block; }}
      @font-face {{ font-family: "JetBrains Mono"; src: url("fonts/JetBrainsMono-400.woff2") format("woff2"); font-weight: 400; font-display: block; }}
      @font-face {{ font-family: "JetBrains Mono"; src: url("fonts/JetBrainsMono-700.woff2") format("woff2"); font-weight: 700; font-display: block; }}
      :root {{
        --bg: #141312; --panel: #211f1d; --panel-2: #2c2926; --line: #3a3632;
        --text: #f3eee6; --muted: #a39e96;
        --accent-0: #e07f5d; --accent-1: #e9b872; --accent-2: #8cc49a; --accent-3: #8fb8f2; --accent-4: #c9a3e6;
      }}
      * {{ box-sizing: border-box; }}
      html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: var(--bg);
        font-family: "Inter", "JetBrains Mono", ui-sans-serif, system-ui, sans-serif; color: var(--text); }}
      #stage {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: var(--bg); }}
      .backdrop {{ position: absolute; left: 0; top: {VIDEO_H}px; width: {W}px; height: {H - VIDEO_H}px;
        background-image: linear-gradient(rgba(243,238,230,0.035) 2px, transparent 2px), linear-gradient(90deg, rgba(243,238,230,0.035) 2px, transparent 2px);
        background-size: 54px 54px; background-position: 0 0; }}
      .video-wrapper {{ position: absolute; left: 0; top: 0; width: {W}px; height: {VIDEO_H}px; overflow: hidden; background: #000; }}
      .video-wrapper video {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
      .seam {{ position: absolute; left: 0; top: {VIDEO_H}px; width: {W}px; height: 6px; background: var(--accent-0); }}
      .rail {{ position: absolute; left: 48px; top: {RAIL_TOP}px; width: {W - 96}px; height: 110px; }}
      .rail .head {{ position: relative; height: 56px; }}
      .rail .cnw {{ position: absolute; left: 0; top: 6px; width: 140px; height: 44px; overflow: hidden; font: 700 24px/44px "JetBrains Mono"; letter-spacing: .14em; color: var(--muted); }}
      .rail .cnw .lbl {{ position: absolute; left: 0; top: 0; }}
      .rail .cn {{ position: absolute; left: 92px; top: 0; color: var(--accent-0); }}
      .rail .ctw {{ position: absolute; left: 150px; right: 0; top: 0; height: 56px; overflow: hidden; }}
      .rail .ct {{ position: absolute; left: 0; top: 0; font: 700 40px/56px "Inter"; letter-spacing: -0.01em; white-space: nowrap; }}
      .rail .segs {{ display: flex; gap: 10px; margin-top: 18px; }}
      .rail .seg {{ flex: 1; height: 8px; border-radius: 4px; background: var(--panel-2); overflow: hidden; }}
      .rail .segfill {{ width: 100%; height: 100%; background: var(--accent-0); transform-origin: left center; }}
      .card-host {{ position: absolute; pointer-events: none; overflow: hidden; }}
      .card-host .card {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      .card-host .root {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; padding: 0 48px 48px; display: flex; flex-direction: column; justify-content: center; gap: 30px; color: var(--text); font-family: "Inter"; }}
      .card-host .char {{ display: inline-block; }}
      .card-host .w {{ display: inline-block; white-space: nowrap; }}
      .card-host .grow {{ flex: 1; min-width: 0; }}
      .card-host .mono {{ font-family: "JetBrains Mono"; }}
      .card-host .acc {{ color: var(--acc); }}
      .card-host .ico {{ display: inline-flex; flex: none; }}
      .card-host .ico svg {{ width: 100%; height: 100%; }}
      .card-host .kicker {{ font: 700 22px/1 "JetBrains Mono"; letter-spacing: .16em; text-transform: uppercase; color: var(--acc); padding-left: 42px; position: relative; }}
      .card-host .kicker::before {{ content: ""; position: absolute; left: 0; top: 9px; width: 28px; height: 4px; border-radius: 2px; background: var(--acc); }}
      .card-host .title {{ font: 700 84px/1.04 "Inter"; letter-spacing: -0.03em; margin: 0; }}
      .card-host .title.sm {{ font-size: 64px; line-height: 1.08; }}
      .card-host .lead {{ font: 400 34px/1.3 "Inter"; color: var(--muted); margin: 0; }}
      .card-host .chip {{ display: inline-flex; align-items: center; gap: 14px; padding: 16px 26px; border-radius: 999px; background: var(--panel); border: 2px solid var(--line); font: 700 32px/1 "Inter"; color: var(--text); white-space: nowrap; }}
      .card-host .chip.big {{ font-size: 40px; padding: 22px 34px; }}
      .card-host .chip.solid {{ background: var(--acc); border-color: var(--acc); color: #141312; }}
      .card-host .chip .ico {{ color: var(--acc); }}
      .card-host .chip.solid .ico {{ color: #141312; }}
      .card-host .badge {{ display: inline-flex; align-items: center; gap: 14px; padding: 16px 26px; border-radius: 999px; background: var(--acc); color: #141312; font: 700 32px/1 "Inter"; align-self: flex-start; }}
      .card-host .node {{ display: flex; align-items: center; gap: 16px; padding: 18px 28px; border-radius: 20px; background: var(--panel); border: 2px solid var(--acc); color: var(--acc); font: 700 32px/1 "Inter"; }}
      .card-host .row {{ display: flex; align-items: center; gap: 24px; padding: 22px 28px; border-radius: 20px; background: var(--panel); border: 2px solid var(--line); }}
      .card-host .row .num {{ font: 700 28px/1 "JetBrains Mono"; color: var(--acc); }}
      .card-host .row .txt {{ font: 700 36px/1.2 "Inter"; }}
      .card-host .row .sub {{ font: 400 27px/1.3 "Inter"; color: var(--muted); margin-top: 6px; }}
      .card-host .input {{ padding: 30px 34px; border-radius: 24px; background: #0e0d0c; border: 2px solid var(--line); font: 400 40px/1.35 "JetBrains Mono"; color: var(--text); }}
    </style>
  </head>
  <body>
    <div id="stage" data-composition-id="talking-head-recut" data-start="0" data-duration="{DURATION}" data-fps="{FPS}" data-width="{W}" data-height="{H}">
      <div class="backdrop"></div>
      <div class="video-wrapper" id="video-wrap">
        <video id="bg-video" src="input-video.mp4" muted playsinline data-start="0" data-duration="{DURATION}" data-track-index="1"></video>
      </div>
      <audio id="source-audio" src="input-video.mp4" data-start="0" data-duration="{DURATION}" data-track-index="10" data-volume="1"></audio>
      <div class="seam"></div>
      <div class="rail">
        <div class="head"><div class="cnw"><span class="lbl">PASO</span>{rail_nums}</div><div class="ctw">{rail_titles}</div></div>
        <div class="segs">{rail_segs}</div>
      </div>
{chr(10).join(hosts)}
      <script src="vendor/gsap.min.js"></script>
      <script>
        (function () {{
          window.__fmt = function (v, fmt) {{
            if (typeof fmt === "string" && /^\\.[0-9]+f$/.test(fmt)) return Number(v).toFixed(Number(fmt.slice(1, -1)));
            if (fmt === ",d") return Math.round(v).toLocaleString("es");
            return String(Math.round(v));
          }};
          const tl = window.gsap.timeline({{ paused: true }});
          {(chr(10) + "          ").join(script_lines)}
          window.__timelines["talking-head-recut"] = tl;
        }})();
      </script>
    </div>
  </body>
</html>
"""
with open(os.path.join(PUB, "index.html"), "w") as f:
    f.write(INDEX)

print(f"{len(CARDS)} cards, {sum(len(c['anims']) for c in CARDS)} anims")
for c in CARDS:
    for a in c["anims"]:
        if not (c["start"] <= a["at"] < c["end"]):
            print("WARN anim outside card window", c["id"], a["id"], a["at"])
for a, b in zip(CARDS, CARDS[1:]):
    if abs(a["end"] - b["start"]) > 0.01:
        print("gap/overlap", a["id"], b["id"], a["end"], b["start"])
