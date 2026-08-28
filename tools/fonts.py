#!/usr/bin/env python3
"""Self-host free fonts and alias them onto the Wix family names."""
import os, re, subprocess, hashlib
from concurrent.futures import ThreadPoolExecutor

SCRATCH = os.path.dirname(os.path.abspath(__file__))
OUT = "/Users/rpsandell/Desktop/Claude-Cowork/PROJECTS/Personal Website"
FDIR = os.path.join(OUT, "assets", "fonts")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

GF = ("https://fonts.googleapis.com/css2?"
      "family=Poppins:wght@300;400;500;600;700"
      "&family=Nunito+Sans:wght@300;400;600;800"
      "&family=Barlow:wght@300;400;500&display=swap")

# Wix family name -> (free family, weight to use for every requested weight)
ALIAS = {
    "avenir-lt-w01_35-light1475496": ("Nunito Sans", "300"),
    "avenir-lt-w05_35-light":        ("Nunito Sans", "300"),
    "avenir-lt-w01_85-heavy1475544": ("Nunito Sans", "800"),
    "avenir-lt-w05_85-heavy":        ("Nunito Sans", "800"),
    "din-next-w01-light":            ("Barlow",      "300"),
    "din-next-w02-light":            ("Barlow",      "300"),
    "din-next-w10-light":            ("Barlow",      "300"),
    "poppins-semibold":              ("Poppins",     "600"),
    "poppins-extralight":            ("Poppins",     "300"),
    "poppins-medium":                ("Poppins",     "500"),
    "madefor-text":                  ("Poppins",     "400"),
    "wfont_812729_":                 ("Poppins",     "400"),
}

def sh(a, b=False):
    r = subprocess.run(a, capture_output=True)
    return r.stdout if b else r.stdout.decode("utf-8","replace")

os.makedirs(FDIR, exist_ok=True)
css = sh(["curl","-sS","-A",UA,GF])
rules = re.findall(r'@font-face\s*\{(.*?)\}', css, re.S)
print("google font-face rules:", len(rules))

parsed, urls = [], {}
for r in rules:
    fam = re.search(r"font-family:\s*'([^']+)'", r).group(1)
    wt  = re.search(r"font-weight:\s*(\d+)", r).group(1)
    src = re.search(r"url\((https://[^)]+)\)", r).group(1)
    ur  = re.search(r"unicode-range:\s*([^;]+);", r)
    name = f"{fam.replace(' ','')}-{wt}-{hashlib.md5(src.encode()).hexdigest()[:6]}.woff2"
    urls[src] = name
    parsed.append({"fam": fam, "wt": wt, "file": name, "range": ur.group(1).strip() if ur else None})

def dl(item):
    src, name = item
    dest = os.path.join(FDIR, name)
    if os.path.exists(dest) and os.path.getsize(dest) > 0: return "cached"
    return sh(["curl","-sS","-A",UA,"-o",dest,"-w","%{http_code}",src]).strip()

with ThreadPoolExecutor(8) as ex:
    codes = list(ex.map(dl, urls.items()))
print(f"[fonts] {sum(1 for c in codes if c in ('200','cached'))}/{len(urls)} woff2 saved")

def block(fam, wt, file, rng, weight_override=None):
    w = weight_override or wt
    s  = "@font-face{font-family:'%s';font-style:normal;font-weight:%s;font-display:swap;" % (fam, w)
    s += "src:url('%s') format('woff2');" % file
    if rng: s += "unicode-range:%s;" % rng
    return s + "}\n"

out = ["/* Self-hosted open-source fonts (SIL OFL 1.1).\n"
       "   Poppins is the site's real font. Nunito Sans substitutes Avenir LT and\n"
       "   Barlow substitutes DIN Next -- both were licensed to Wix, not to this site.\n"
       "   The Wix family names are aliased below so the original CSS resolves locally. */\n"]

for p in parsed:
    out.append(block(p["fam"], p["wt"], p["file"], p["range"]))

# lowercase bare aliases used directly by Wix CSS (font-family: poppins)
for p in parsed:
    if p["fam"] == "Poppins":
        out.append(block("poppins", p["wt"], p["file"], p["range"]))

# single-weight aliases: map every requested weight onto one file
for wix, (freefam, wt) in ALIAS.items():
    for p in parsed:
        if p["fam"] == freefam and p["wt"] == wt:
            for w in ("100","200","300","400","500","600","700","800","900"):
                out.append(block(wix, p["wt"], p["file"], p["range"], weight_override=w))

open(os.path.join(OUT, "assets", "fonts.css"), "w").write("".join(out))
print("[fonts] assets/fonts.css written,", len("".join(out)), "bytes")
