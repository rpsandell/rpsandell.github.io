#!/usr/bin/env python3
"""Static export of ryan-sandell.com (Wix) -> plain HTML tree."""
import os, re, sys, hashlib, subprocess, urllib.parse, json, shutil
from concurrent.futures import ThreadPoolExecutor

SCRATCH = os.path.dirname(os.path.abspath(__file__))
OUT     = "/Users/rpsandell/Desktop/Claude-Cowork/PROJECTS/Personal Website"
CACHE   = os.path.join(SCRATCH, "cache")
SITE    = "https://www.ryan-sandell.com"
UA_D = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
UA_M = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"

# (url path on live site, output directory relative to site root)
PAGES = [
 ("/",                                                              ""),
 ("/research",                                                      "research"),
 ("/teaching",                                                      "teaching"),
 ("/contact",                                                       "contact"),
 ("/phonology-morphology-interface",                                "phonology-morphology-interface"),
 ("/computational-and-corpus-linguistics",                          "computational-and-corpus-linguistics"),
 ("/data-homer",                                                    "data-homer"),
 ("/historical-and-indo-european-linguistics",                      "historical-and-indo-european-linguistics"),
 ("/linguistics-of-indic-germanic-greek",                           "linguistics-of-indic-germanic-greek"),
 ("/word-prosodic-systems",                                         "word-prosodic-systems"),
 ("/projects",                                                      "projects"),
 ("/projects/allomorphy-and-the-phonology-morphology-interface",    "projects/allomorphy-and-the-phonology-morphology-interface"),
 ("/projects/computational-and-corpus-linguistic-studies",          "projects/computational-and-corpus-linguistic-studies"),
 ("/projects/data-homer",                                           "projects/data-homer"),
 ("/projects/historical-and-indo-european-linguistics",             "projects/historical-and-indo-european-linguistics"),
 ("/projects/linguistics-and-philology-of-indic%2C-greek%2C-and-germanic",
                                                                    "projects/linguistics-and-philology-of-indic-greek-and-germanic"),
 ("/projects/word-prosodic-systems-and-prosodic-change",            "projects/word-prosodic-systems-and-prosodic-change"),
]

def sh(args, binary=False):
    r = subprocess.run(args, capture_output=True)
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")

def curl(url, ua, out, extra=None):
    a = ["curl","-sS","--compressed","-L","--retry","3","--retry-delay","1","-A",ua,"-o",out,"-w","%{http_code}"]
    if extra: a[1:1] = extra
    return sh(a + [url]).strip()

# ---------------------------------------------------------------- phase 1: fetch
def fetch_all():
    os.makedirs(CACHE, exist_ok=True)
    jobs = []
    for path, outdir in PAGES:
        for kind, ua in (("d", UA_D), ("m", UA_M)):
            slug = (outdir or "home").replace("/", "__")
            jobs.append((SITE + path, ua, os.path.join(CACHE, f"{kind}_{slug}.html"), f"{kind}:{outdir or '/'}"))
    def run(j):
        url, ua, dest, label = j
        if os.path.exists(dest) and os.path.getsize(dest) > 50000:
            return (label, "cached")
        return (label, curl(url, ua, dest))
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(run, jobs))
    bad = [r for r in res if r[1] not in ("200", "cached")]
    print(f"[fetch] {len(res)} documents, {len(bad)} problems")
    for b in bad: print("   FAIL", b)
    return not bad

# ---------------------------------------------------------------- phase 2: collect assets
RE_IMG  = re.compile(r'(?:https?:)?//static\.wixstatic\.com/media/[^"\'\\\s)>]+')
RE_PDF  = re.compile(r'(?:https://www\.ryan-sandell\.com)?/_files/ugd/[A-Za-z0-9_\-]+\.[A-Za-z0-9]+')

IMG_CAP = 1600

def cap_url(u, cap=IMG_CAP):
    """Wix will render any size; don't ship a 6000px hero."""
    m = re.search(r'/v1/fill/w_(\d+),h_(\d+)[^/]*/', u)
    if not m:
        return u
    w, hh = int(m.group(1)), int(m.group(2))
    if w <= cap:
        return u
    return u.replace(m.group(0), '/v1/fill/w_%d,h_%d,al_c,q_85/' % (cap, max(1, round(hh * cap / w))))

def placeholder_map(h):
    """Wix ships a blurred low-res <img> and swaps in the real one from JS.
    Map each blurred URL onto the best sharp rendition of the same media id."""
    by_id = {}
    for u in set(RE_IMG.findall(h)):
        m = re.search(r'/media/([^/]+)', u)
        if m:
            by_id.setdefault(m.group(1), []).append(u)
    def width(u):
        m = re.search(r'[/,]w_(\d+)', u)
        return int(m.group(1)) if m else 0
    out = {}
    for _, group in by_id.items():
        blurred = [u for u in group if 'blur_' in u]
        sharp   = [u for u in group if 'blur_' not in u]
        if blurred and sharp:
            best = cap_url(max(sharp, key=width))
            for b in blurred:
                out[b] = best
    return out

def cached_files():
    return sorted(os.path.join(CACHE, f) for f in os.listdir(CACHE) if f.endswith(".html"))

def collect():
    imgs, docs = set(), set()
    for f in cached_files():
        h = open(f, encoding="utf-8", errors="replace").read()
        for u in RE_IMG.findall(h):
            imgs.add(u)
        imgs.update(placeholder_map(h).values())
        for u in RE_PDF.findall(h):
            docs.add(u if u.startswith("http") else SITE + u)
    print(f"[collect] {len(imgs)} image URLs, {len(docs)} document URLs")
    return sorted(imgs), sorted(docs)

def norm(u):
    return ("https:" + u) if u.startswith("//") else u

def download_images(imgs):
    d = os.path.join(OUT, "assets", "img"); os.makedirs(d, exist_ok=True)
    mapping = {}
    def one(u):
        full = norm(u)
        ext = os.path.splitext(urllib.parse.urlparse(full).path)[1].lower()
        if ext not in (".jpg",".jpeg",".png",".gif",".svg",".webp"): ext = ".jpg"
        name = "img_" + hashlib.md5(full.encode()).hexdigest()[:12] + ext
        dest = os.path.join(d, name)
        code = "cached"
        if not (os.path.exists(dest) and os.path.getsize(dest) > 0):
            code = curl(full, UA_D, dest, ["-H","Accept: image/jpeg,image/png,image/gif,image/svg+xml,image/*;q=0.8"])
        return u, name, code
    with ThreadPoolExecutor(8) as ex:
        for u, name, code in ex.map(one, imgs):
            if code in ("200","cached"): mapping[u] = name
            else: print("   IMG FAIL", code, u[:100])
    print(f"[images] {len(mapping)}/{len(imgs)} saved")
    return mapping

def download_docs(docs):
    d = os.path.join(OUT, "files"); os.makedirs(d, exist_ok=True)
    mapping, used = {}, {}
    for u in docs:
        head = sh(["curl","-sSIL","-A",UA_D,u])
        m = re.search(r"filename\*=UTF-8''([^\r\n;]+)", head) or re.search(r'filename="([^"]+)"', head)
        raw = urllib.parse.unquote(m.group(1)) if m else os.path.basename(u)
        raw = re.sub(r'[\\/:*?"<>|]', "_", raw).strip()
        base, ext = os.path.splitext(raw)
        name = raw
        if name in used and used[name] != u:
            n = 2
            while f"{base}_{n}{ext}" in used: n += 1
            name = f"{base}_{n}{ext}"
        used[name] = u
        dest = os.path.join(d, name)
        code = "cached"
        if not (os.path.exists(dest) and os.path.getsize(dest) > 0):
            code = curl(u, UA_D, dest)
        if code in ("200","cached"):
            mapping[u] = name
        else:
            print("   DOC FAIL", code, u)
    print(f"[docs] {len(mapping)}/{len(docs)} saved")
    return mapping

if __name__ == "__main__":
    ok = fetch_all()
    imgs, docs = collect()
    im = download_images(imgs)
    dm = download_docs(docs)
    json.dump({"img": im, "doc": dm}, open(os.path.join(SCRATCH, "assetmap.json"), "w"), indent=1)
    print("[done] asset maps written")
