"""Builds one HTML scene per day for the animated Telegram cards. Run via tools/build.py (reads config.json)."""
import json, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(HERE, "..", "..", "config.json")))
BUILD = os.path.join(HERE, "build"); os.makedirs(BUILD, exist_ok=True)
HAS_LEG = os.path.exists(os.path.join(HERE, "leg.webp"))
NAME = CFG["character"]["name"]
try:
    from PIL import Image
    _w, _h = Image.open(os.path.join(HERE, "base.webp")).size
    ASPECT = _w / _h
except Exception:
    ASPECT = 0.5
DOGW = 190 if ASPECT <= 0.62 else 270      # wide characters (a lying dog, an envelope) get more room

C = dict(tomato="#d9583b", butter="#f3d98b", sage="#9fb39a", sky="#a9c4d8", blush="#efc7bd", plum="#6b3f5e",
         forest="#2f4b3c", ochre="#c98b2b", cream="#f6efe2", navy="#23304a", mint="#cfe1d0", lilac="#cdbbe0",
         cocoa="#6e4a36", rust="#b4532f", burgundy="#8e2c2a", midnight="#1d2742", gold="#d8b062", white="#fffaf2")

# Card palettes. "festive" is the default set; the others recolour the same designs.
PALETTES = {
    "festive": {},
    "nordic": dict(tomato="#5b86ad", butter="#e6edf3", sage="#a9bfcf", sky="#c9dbe8", blush="#d9e4ee", plum="#33496a", forest="#2d4a5e",
                   ochre="#8fb0c9", cream="#f4f7fa", navy="#1f3350", mint="#cfe0e8", lilac="#c4d0e6", cocoa="#46607a", rust="#3f6a8f",
                   burgundy="#27456a", midnight="#17263d", gold="#d5dde8", white="#ffffff"),
    "warm": dict(tomato="#c4552d", butter="#f0d69a", sage="#b7b58c", sky="#e3c9a3", blush="#eac2a8", plum="#6a3d3a", forest="#4d4a2e",
                 ochre="#c98b2b", cream="#f7eddc", navy="#4a2f26", mint="#d9d6b0", lilac="#d9b9a8", cocoa="#6e4a36", rust="#a84a28",
                 burgundy="#7e2a22", midnight="#33211c", gold="#d8a94f", white="#fff7ea"),
}
C.update(PALETTES.get(CFG.get("style", {}).get("cards", "festive"), {}))

WORDS = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty twenty-one twenty-two twenty-three twenty-four".split()

# Paper-cut motifs (viewBox 0 0 100 100)
M = {
 "star":  '<polygon points="50,4 62,38 98,38 69,59 80,94 50,73 20,94 31,59 2,38 38,38" fill="{c}"/>',
 "heart": '<path d="M50 88 C10 60 4 32 22 18 C36 8 48 18 50 28 C52 18 64 8 78 18 C96 32 90 60 50 88Z" fill="{c}"/>',
 "flower":'<g fill="{c}"><circle cx="50" cy="24" r="17"/><circle cx="75" cy="42" r="17"/><circle cx="66" cy="72" r="17"/><circle cx="34" cy="72" r="17"/><circle cx="25" cy="42" r="17"/></g><circle cx="50" cy="50" r="13" fill="{c2}"/>',
 "sprig": '<path d="M20 95 Q45 55 80 8" stroke="{c}" stroke-width="5" fill="none"/><g fill="{c}"><ellipse cx="36" cy="66" rx="15" ry="7" transform="rotate(-60 36 66)"/><ellipse cx="52" cy="62" rx="15" ry="7" transform="rotate(25 52 62)"/><ellipse cx="52" cy="40" rx="14" ry="6.5" transform="rotate(-60 52 40)"/><ellipse cx="67" cy="38" rx="14" ry="6.5" transform="rotate(25 67 38)"/><ellipse cx="78" cy="14" rx="12" ry="6" transform="rotate(-40 78 14)"/></g>',
 "moon":  '<path d="M64 8 A44 44 0 1 0 92 70 A36 36 0 1 1 64 8Z" fill="{c}"/>',
 "sun":   '<g fill="{c}"><circle cx="50" cy="50" r="24"/>' + "".join(f'<polygon points="50,2 56,20 44,20" transform="rotate({a} 50 50)"/>' for a in range(0,360,30)) + '</g>',
 "paw":   '<g fill="{c}"><ellipse cx="50" cy="66" rx="22" ry="18"/><ellipse cx="22" cy="40" rx="9" ry="12" transform="rotate(-20 22 40)"/><ellipse cx="40" cy="24" rx="9" ry="12"/><ellipse cx="60" cy="24" rx="9" ry="12"/><ellipse cx="78" cy="40" rx="9" ry="12" transform="rotate(20 78 40)"/></g>',
 "bone":  '<g fill="{c}"><rect x="22" y="40" width="56" height="20" rx="6"/><circle cx="20" cy="38" r="12"/><circle cx="20" cy="62" r="12"/><circle cx="80" cy="38" r="12"/><circle cx="80" cy="62" r="12"/></g>',
 "candle":'<rect x="38" y="40" width="24" height="56" rx="4" fill="{c}"/><path d="M50 6 C62 22 62 34 50 38 C38 34 38 22 50 6Z" fill="{c2}"/>',
 "boot":  '<path d="M30 6 H62 V58 Q62 66 70 68 L88 72 Q96 74 96 84 V94 H24 Q22 94 22 90 V60 Q30 56 30 46Z" fill="{c}"/><rect x="26" y="4" width="40" height="14" rx="4" fill="{c2}"/>',
 "cup":   '<path d="M18 40 H72 V70 Q72 92 46 92 Q18 92 18 70Z" fill="{c}"/><path d="M72 48 Q90 48 90 62 Q90 76 70 76" stroke="{c}" stroke-width="7" fill="none"/><path d="M34 32 Q28 22 36 14 M50 32 Q44 22 52 12" stroke="{c}" stroke-width="5" fill="none" stroke-linecap="round"/>',
 "ladybug":'<circle cx="50" cy="56" r="34" fill="{c}"/><circle cx="50" cy="20" r="13" fill="#2b2a33"/><line x1="50" y1="24" x2="50" y2="90" stroke="#2b2a33" stroke-width="3"/><g fill="#2b2a33"><circle cx="34" cy="48" r="6"/><circle cx="66" cy="48" r="6"/><circle cx="32" cy="70" r="5"/><circle cx="68" cy="70" r="5"/></g>',
 "snow":  '<g stroke="{c}" stroke-width="7" stroke-linecap="round">' + "".join(f'<g transform="rotate({a} 50 50)"><line x1="50" y1="8" x2="50" y2="92"/><line x1="50" y1="22" x2="40" y2="12"/><line x1="50" y1="22" x2="60" y2="12"/></g>' for a in (0,60,120)) + '</g>',
 "tree":  '<g fill="{c}"><polygon points="50,4 76,40 24,40"/><polygon points="50,26 84,66 16,66"/><polygon points="50,48 92,94 8,94"/></g>',
}

# day: bg, ink(for text), numeral fill [kind, c1, c2], layout, motifs [(name, color, color2)], border, backdrop colour (arch/circle)
D = {
 1:  ("sky","navy",   ("gingham","navy","cream"),  "A", [("star","navy","")], "scallop", None),
 2:  ("blush","plum", ("dots","plum","cream"),     "B", [("moon","plum",""),("star","cream","")], "stitch", None),
 3:  ("butter","rust",("stripes","tomato","cream"),"C", [("heart","tomato","")], "double", "sage"),
 4:  ("tomato","white",("gingham","butter","cream"),"D", [("star","butter","")], "none", "butter"),
 5:  ("sage","forest",("flowers","blush","cream"), "A", [("boot","tomato","cream")], "scallop", None),
 6:  ("burgundy","gold",("gold","",""),            "C", [("boot","gold","cream"),("star","gold","")], "stitch", "gold"),
 7:  ("mint","forest",("dots","ochre","cream"),    "B", [("flower","ochre","tomato"),("flower","tomato","butter")], "stitch", None),
 8:  ("ochre","cocoa",("paws","cocoa","cream"),    "A", [("paw","cocoa",""),("bone","cream","")], "scallop", None),
 9:  ("cream","navy", ("stripes","navy","cream"),  "D", [("cup","navy","")], "double", "sky"),
 10: ("lilac","forest",("leaves","forest","cream"),"B", [("sprig","forest","")], "none", None),
 11: ("navy","cream", ("dots","cream","sky"),      "C", [("snow","cream","")], "stitch", "sky"),
 12: ("sky","navy",   ("gingham","tomato","cream"),"D", [("snow","white","")], "scallop", "cream"),
 13: ("plum","butter",("dots","gold","butter"),    "A", [("candle","cream","butter")], "stitch", None),
 14: ("butter","rust",("stripes","tomato","cream"),"D", [("sun","tomato","")], "scallop", "cream"),
 15: ("sage","cocoa", ("paws","cocoa","cream"),    "B", [("paw","cocoa",""),("sprig","forest","")], "double", None),
 16: ("mint","forest",("dots","tomato","cream"),   "C", [("ladybug","tomato","")], "none", "blush"),
 17: ("blush","plum", ("gingham","plum","cream"),  "A", [("heart","tomato","")], "stitch", None),
 18: ("navy","butter",("dots","butter","navy"),    "B", [("moon","butter",""),("star","butter","")], "stitch", None),
 19: ("cream","rust", ("flowers","tomato","blush"),"C", [("flower","tomato","butter"),("flower","sky","butter"),("flower","ochre","cream")], "scallop", "blush"),
 20: ("lilac","plum", ("dots","plum","cream"),     "D", [("moon","plum",""),("star","plum","")], "double", "cream"),
 21: ("midnight","gold",("gold","",""),            "D", [("star","gold","")], "stitch", "gold"),
 22: ("mint","rust",  ("stripes","tomato","cream"),"A", [("heart","tomato","")], "scallop", None),
 23: ("butter","forest",("gingham","forest","cream"),"B", [("star","tomato",""),("sprig","forest","")], "double", None),
 0:  ("sage","forest",("paws","cocoa","cream"),  "D", [("paw","cocoa",""),("bone","cream","")], "scallop", "cream"),
 24: ("forest","gold",("gold","",""),              "C", [("tree","cream",""),("star","gold","")], "stitch", "gold"),
}
SPECIAL = {6, 21, 24}

def svgurl(s):
    import urllib.parse
    return "url('data:image/svg+xml," + urllib.parse.quote(s, safe="") + "')"

def fill(kind, c1, c2):
    a, b = C.get(c1, c1), C.get(c2, c2)
    if kind == "gold":    return "background:linear-gradient(135deg,#f6e3a8 0%,#d8b062 35%,#a9802f 55%,#f1d78f 75%,#c99a45 100%)"
    if kind == "gingham": return f"background-color:{b};background-image:linear-gradient(90deg,{a}99 50%,transparent 50%),linear-gradient({a}99 50%,transparent 50%);background-size:28px 28px"
    if kind == "dots":    return f"background:radial-gradient(circle,{a} 5px,transparent 5.5px) 0 0/24px 24px,radial-gradient(circle,{a} 5px,transparent 5.5px) 12px 12px/24px 24px,{b}"
    if kind == "stripes": return f"background:repeating-linear-gradient(90deg,{b} 0 16px,{a} 16px 22px,{b} 22px 26px,{a} 26px 29px)"
    if kind == "flowers": return f"background:{b} " + svgurl(f"<svg xmlns='http://www.w3.org/2000/svg' width='40' height='40'><g fill='{a}'><circle cx='10' cy='5' r='4'/><circle cx='15' cy='10' r='4'/><circle cx='12' cy='16' r='4'/><circle cx='7' cy='16' r='4'/><circle cx='4' cy='10' r='4'/></g><circle cx='10' cy='11' r='2.6' fill='#c98b2b'/><circle cx='30' cy='30' r='3' fill='{a}'/></svg>") + " 0 0/40px 40px"
    if kind == "paws":    return f"background:{b} " + svgurl(f"<svg xmlns='http://www.w3.org/2000/svg' width='44' height='44'><g fill='{a}'><ellipse cx='14' cy='18' rx='6' ry='5'/><circle cx='7' cy='11' r='2.6'/><circle cx='12' cy='7' r='2.6'/><circle cx='17' cy='7' r='2.6'/><circle cx='22' cy='11' r='2.6'/><ellipse cx='34' cy='38' rx='5' ry='4'/><circle cx='28' cy='32' r='2.2'/><circle cx='33' cy='29' r='2.2'/><circle cx='38' cy='30' r='2.2'/><circle cx='41' cy='34' r='2.2'/></g></svg>") + " 0 0/44px 44px"
    if kind == "leaves":  return f"background:{b} " + svgurl(f"<svg xmlns='http://www.w3.org/2000/svg' width='46' height='46'><path d='M6 40 Q20 24 36 6' stroke='{a}' stroke-width='2' fill='none'/><g fill='{a}'><ellipse cx='16' cy='28' rx='6' ry='3' transform='rotate(-60 16 28)'/><ellipse cx='23' cy='29' rx='6' ry='3' transform='rotate(25 23 29)'/><ellipse cx='25' cy='17' rx='6' ry='3' transform='rotate(-60 25 17)'/><ellipse cx='32' cy='18' rx='6' ry='3' transform='rotate(25 32 18)'/></g></svg>") + " 0 0/46px 46px"
    return f"background:{a}"

def rnd(seed):
    x = seed * 9301 + 49297
    while True:
        x = (x * 9301 + 49297) % 233280
        yield x / 233280

def scatter(day, motifs, layout, special):
    """Place paper-cut motifs around the dog, never over the text band."""
    r = rnd(day)
    out = []
    # candidate zones (x, y in px on a 720 canvas), chosen by layout so the dog and numeral stay clear
    zones = {
        "A": [(70,90),(150,60),(600,70),(640,170),(610,330),(80,380),(640,450),(560,40)],
        "B": [(640,90),(560,60),(80,70),(60,190),(90,330),(630,380),(70,460),(170,40)],
        "C": [(70,80),(640,80),(60,250),(650,250),(90,430),(630,430),(200,40),(520,40)],
        "D": [(70,80),(650,90),(60,300),(660,300),(110,470),(610,470),(360,40),(250,60)],
    }[layout]
    count = 6 if special else 5
    if motifs[0][0] in ("sun","cup","ladybug","boot","candle","tree","heart") and layout in ("C","D"):
        count = 5
    for i in range(count):
        name, c, c2 = motifs[i % len(motifs)]
        x, y = zones[i]
        size = int(62 + next(r) * 52)
        if i in (0,3) and name in ("sun","moon","cup","boot","candle","ladybug","tree","heart","flower"): size = int(size * 1.5)
        rot = int(next(r) * 50 - 25)
        delay = round(-next(r) * 3.2, 2)
        anim = "twinkle" if name in ("star","snow","flower","sun") else "sway"
        body = M[name].format(c=C.get(c, c), c2=C.get(c2, c2) if c2 else C["cream"])
        out.append(f'<svg class="motif {anim}" style="left:{x-size//2}px;top:{y-size//2}px;width:{size}px;height:{size}px;--r:{rot}deg;animation-delay:{delay}s" viewBox="0 0 100 100"><g filter="url(#rough)">{body}</g></svg>')
    if special:
        for i in range(22):
            x = int(next(r) * 700); s = int(10 + next(r) * 16); delay = round(-next(r) * 3.2, 2); dur = 3.2
            col = C["gold"] if i % 3 else C["cream"]
            out.append(f'<svg class="fall" style="left:{x}px;width:{s}px;height:{s}px;animation-delay:{delay}s" viewBox="0 0 100 100">{M["star"].format(c=col)}</svg>')
    return "\n".join(out)

def border(kind, col):
    if kind == "scallop":
        return (f'<div class="sc t" style="--c:{col}"></div><div class="sc b" style="--c:{col}"></div>'
                f'<div class="sc l" style="--c:{col}"></div><div class="sc r" style="--c:{col}"></div>')
    if kind == "stitch":  return f'<div class="stitch" style="border-color:{col}"></div>'
    if kind == "double":  return f'<div class="dbl" style="border-color:{col}"></div><div class="dbl two" style="border-color:{col}"></div>'
    return ""

def page(day):
    bg, ink, (fk, f1, f2), layout, motifs, bkind, back = D[day]
    special = day in SPECIAL
    bgc, inkc = C[bg], C[ink]
    trim = C["cream"] if bg not in ("cream","butter","mint") else C["tomato"] if bg != "mint" else C["forest"]
    if special: trim = C["gold"]
    word = WORDS[day-1]
    title = f"Door {word}"
    sub = "A special one. Tap below to open it." if special else "is here. Tap below to open it."
    if day == 0:
        title, sub = f"{NAME}, reporting for duty", "One delivery a day, 1 to 24 December."
    numfill = fill(fk, f1, f2)
    # layout pieces
    dog_left = {"A": 410, "B": 120, "C": 265, "D": 265}[layout] - (DOGW - 190) // 2
    numeral = ""
    if layout in ("A", "B"):
        nx = 40 if layout == "A" else 330
        numeral = f'<div class="num big" style="left:{nx}px;{numfill};-webkit-background-clip:text;background-clip:text;color:transparent">{day}</div><div class="num big ghost" style="left:{nx+8}px;color:{C["cream"] if bg in ("navy","plum","midnight","forest","burgundy","tomato") else "rgba(43,42,51,.18)"}">{day}</div>'
    else:
        bx = 56 if layout == "C" else 560
        numeral = f'<div class="badge" style="left:{bx}px;{numfill}"><span>{day}</span></div>' if day else ""
    backdrop = ""
    if layout == "C":
        backdrop = f'<div class="arch" style="{fill(fk,f1,f2) if not back else "background:"+C[back]}"></div>'
    if layout == "D":
        backdrop = f'<div class="disc" style="background:{C[back]}"></div>'
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Corm;font-style:normal;font-weight:400;src:url(../fonts/instrument-serif-latin-400-normal.woff)}}
@font-face{{font-family:CormI;font-style:italic;font-weight:400;src:url(../fonts/instrument-serif-latin-400-italic.woff)}}
@font-face{{font-family:Jost;font-weight:500;src:url(../fonts/jost-latin-500-normal.woff)}}
@font-face{{font-family:JostB;font-weight:700;src:url(../fonts/jost-latin-700-normal.woff)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:720px;height:720px;overflow:hidden;background:{bgc};position:relative}}
.grain{{position:absolute;inset:0;z-index:20;pointer-events:none;mix-blend-mode:multiply;opacity:.55;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' seed='{day}'/%3E%3CfeColorMatrix values='0 0 0 0 .4 0 0 0 0 .33 0 0 0 0 .25 0 0 0 .22 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}}
.sc{{position:absolute;z-index:6}}
.sc.t,.sc.b{{left:0;right:0;height:16px;background:radial-gradient(circle at 50% 0,var(--c) 11px,transparent 11.5px) 0 0/26px 16px repeat-x}}
.sc.t{{top:0}} .sc.b{{bottom:0;transform:rotate(180deg)}}
.sc.l,.sc.r{{top:0;bottom:0;width:16px;background:radial-gradient(circle at 0 50%,var(--c) 11px,transparent 11.5px) 0 0/16px 26px repeat-y}}
.sc.l{{left:0}} .sc.r{{right:0;transform:rotate(180deg)}}
.stitch{{position:absolute;inset:18px;border:3px dashed;border-radius:22px;z-index:6;opacity:.9}}
.dbl{{position:absolute;inset:16px;border:2px solid;border-radius:6px;z-index:6}} .dbl.two{{inset:24px;border-width:1px}}
.num{{position:absolute;top:60px;z-index:2;font-family:JostB;font-weight:700;font-size:{400 if day<10 else 290}px;line-height:1;-webkit-background-clip:text;background-clip:text;color:transparent;letter-spacing:-14px}}
.num.ghost{{z-index:1;top:70px;margin-left:4px;background:none !important}}
.badge{{position:absolute;top:44px;z-index:7;width:112px;height:112px;border-radius:50%;box-shadow:3px 5px 0 rgba(0,0,0,.18);display:flex;align-items:center;justify-content:center;transform:rotate(-6deg)}}
.badge span{{font-family:JostB;font-size:46px;line-height:1;color:{C["ink"] if "ink" in C else "#2b2a33"};background:{C["cream"]};width:78px;height:78px;border-radius:50%;display:flex;align-items:center;justify-content:center}}
.arch{{position:absolute;left:180px;top:110px;width:360px;height:470px;border-radius:180px 180px 10px 10px;z-index:1;box-shadow:inset 0 0 0 10px rgba(255,255,255,.35),6px 8px 0 rgba(0,0,0,.12)}}
.disc{{position:absolute;left:150px;top:90px;width:420px;height:420px;border-radius:50%;z-index:1;box-shadow:6px 8px 0 rgba(0,0,0,.12)}}
.motif{{position:absolute;z-index:4;filter:drop-shadow(2px 3px 0 rgba(0,0,0,.16));transform:rotate(var(--r))}}
.twinkle{{animation:twinkle 3.2s ease-in-out infinite}}
.sway{{animation:sway 3.2s ease-in-out infinite}}
@keyframes twinkle{{0%,100%{{transform:rotate(var(--r)) scale(1)}}50%{{transform:rotate(calc(var(--r) + 14deg)) scale(1.12)}}}}
@keyframes sway{{0%,100%{{transform:rotate(var(--r)) translateY(0)}}50%{{transform:rotate(calc(var(--r) - 8deg)) translateY(-6px)}}}}
.fall{{position:absolute;top:-30px;z-index:9;animation:fall 3.2s linear infinite}}
@keyframes fall{{from{{transform:translateY(0) rotate(0)}}to{{transform:translateY(780px) rotate(300deg)}}}}
.dog{{position:absolute;left:{dog_left}px;top:{168 if layout in ("C","D") else 150}px;width:{DOGW}px;height:374px;z-index:5;animation:bob 3.2s ease-in-out infinite;transform-origin:50% 100%}}
.dog img{{position:absolute;display:block}}
.dog .base{{left:0;top:0;width:{DOGW}px;height:374px;object-fit:contain;object-position:50% 100%}}
.dog .leg{{left:110.4px;top:262.7px;width:79.6px;transform-origin:40.9px 8px;animation:paw 3.2s ease-in-out infinite}}
.shadow{{position:absolute;left:{dog_left-20}px;top:{(168 if layout in ("C","D") else 150)+352}px;width:{DOGW+40}px;height:30px;border-radius:50%;background:rgba(0,0,0,.22);filter:blur(8px);z-index:3}}
@keyframes bob{{0%,18%,92%,100%{{transform:translateY(0) rotate(0)}}34%{{transform:translateY(-4px) rotate(-1.5deg)}}60%{{transform:translateY(-3px) rotate(1deg)}}78%{{transform:translateY(-2px) rotate(-.5deg)}}}}
@keyframes paw{{0%,16%,94%,100%{{transform:translateY(0) rotate(0) scaleY(1)}}32%{{transform:translateY(-5px) rotate(-17deg) scaleY(.66)}}42%{{transform:translateY(-4px) rotate(-11deg) scaleY(.7)}}52%{{transform:translateY(-6px) rotate(-18deg) scaleY(.64)}}62%{{transform:translateY(-4px) rotate(-12deg) scaleY(.7)}}74%{{transform:translateY(-5px) rotate(-16deg) scaleY(.66)}}86%{{transform:translateY(-1px) rotate(-4deg) scaleY(.92)}}}}
.text{{position:absolute;left:0;right:0;bottom:44px;z-index:8;text-align:{ "left" if layout=="A" else "right" if layout=="B" else "center"};padding:0 64px}}
.text h1{{font-family:Corm;font-weight:400;font-size:{62 if len(title)<14 else 54 if len(title)<20 else 46}px;line-height:1;letter-spacing:-.01em;color:{inkc}}}
.text p{{font-family:CormI;font-style:italic;font-size:28px;color:{inkc};opacity:.82;margin-top:6px}}
.band{{position:absolute;left:0;right:0;bottom:0;height:150px;z-index:7;background:linear-gradient(to top,{bgc} 55%,{bgc}00)}}
</style></head><body>
<svg width="0" height="0" style="position:absolute"><filter id="rough"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="{day}"/><feDisplacementMap in="SourceGraphic" scale="4"/></filter></svg>
{backdrop}
{numeral}
{scatter(day, motifs, layout, special)}
<div class="shadow"></div>
<div class="dog"><img class="base" src="../base.webp">{'<img class="leg" src="../leg.webp">' if HAS_LEG else ""}</div>
<div class="band"></div>
<div class="text"><h1>{title}</h1><p>{sub}</p></div>
{border(bkind, trim)}
<div class="grain"></div>
</body></html>'''

if __name__ == "__main__":
    days = [int(a) for a in sys.argv[1:]] or range(1, 25)
    for d in days:
        open(os.path.join(BUILD, f"day{d:02d}.html"), "w").write(page(d))
    print("built", list(days))
