#!/usr/bin/env python3
"""Turn the cached Wix documents into a self-contained static tree."""
import os, re, json, html, urllib.parse
from build import PAGES, CACHE, OUT, SITE, RE_IMG, RE_PDF, norm, placeholder_map

SCRATCH = os.path.dirname(os.path.abspath(__file__))
AM = json.load(open(os.path.join(SCRATCH, "assetmap.json")))
IMG, DOC = AM["img"], AM["doc"]

# live path -> output directory
PATHMAP = {}
for p, outdir in PAGES:
    for v in {p, p.rstrip("/"), urllib.parse.unquote(p), urllib.parse.unquote(p).rstrip("/")}:
        PATHMAP[v or "/"] = outdir
PATHMAP["/"] = ""
PATHMAP[""] = ""

EXCLUDED = re.compile(r'^/courses(/|$)')

def prefix_for(kind, outdir):
    depth = (len(outdir.split("/")) if outdir else 0) + (1 if kind == "m" else 0)
    return "../" * depth

def page_link(kind, outdir_self, target):
    pre = prefix_for(kind, outdir_self)
    mid = "m/" if kind == "m" else ""
    tail = (target + "/") if target else ""
    return pre + mid + tail + "index.html"

SITE_CSS = """/* Hand-written for this static export. Restores the two navigation
   behaviours that lived in the Wix JavaScript bundle, and nothing else. */

/* Wix's overflow "More" item. Its container is empty -- the overflow logic ran
   in JS -- so nothing hides behind it. */
nav li[id$="__more__"], nav [id$="dropWrapper"] { display: none !important; }

/* ---- Desktop RESEARCH drop-down -----------------------------------------
   The export rebuilds Wix's nested submenu as .rs-submenu (see transform.py).
   `all: revert` drops every inherited Wix declaration back to the browser
   default first, so the menu is styled only by the rules below. */
/* The menu component is a 35px box with overflow:hidden, and Wix positions the
   <nav> absolutely inside it. The drop-down has to be allowed out of that box. */
.wixui-dropdown-menu, .HvW69V { overflow: visible !important; }

nav li { position: relative; }

.rs-submenu {
  all: revert;
  display: none;
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 9999;
  min-width: 262px;
  margin: 0;
  padding: 8px 0;
  list-style: none;
  background: #fff;
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 2px;
  box-shadow: 0 6px 24px rgba(0,0,0,.14);
  text-align: left;
}

nav li:hover > .rs-submenu,
nav li:focus-within > .rs-submenu { display: block; }

.rs-submenu li {
  all: revert;
  display: block;
  margin: 0;
  padding: 0;
  list-style: none;
}

.rs-submenu a {
  all: revert;
  display: block;
  padding: 9px 18px;
  font-family: poppins, "Poppins", Helvetica, Arial, sans-serif;
  font-size: 13px;
  line-height: 1.35;
  letter-spacing: .01em;
  color: #2b2b2b;
  text-decoration: none;
  white-space: nowrap;
  cursor: pointer;
}

.rs-submenu a:hover { background: #f2f2f2; color: #0050ff; }
.rs-submenu a:focus-visible { outline: 2px solid #0050ff; outline-offset: -2px; }

/* ---- /projects card grid (rebuilt; see README) -------------------------- */
.rs-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 28px;
  max-width: 980px;
  margin: 0 auto;
  padding: 8px 20px 60px;
  font-family: poppins, "Poppins", Helvetica, Arial, sans-serif;
}
.rs-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 26px 24px 22px;
  background: #fff;
  border: 1px solid rgba(0,0,0,.10);
  border-radius: 2px;
  text-decoration: none;
  color: inherit;
  transition: box-shadow .15s ease, transform .15s ease;
}
.rs-card:hover { box-shadow: 0 8px 28px rgba(0,0,0,.10); transform: translateY(-2px); }
.rs-card:focus-visible { outline: 2px solid #0050ff; outline-offset: 2px; }
.rs-card-title { font-size: 19px; font-weight: 600; line-height: 1.3; color: #111; }
.rs-card-desc  { font-size: 14px; line-height: 1.55; color: #4a4a4a; flex: 1; }
.rs-card-more  { font-size: 13px; font-weight: 600; color: #0050ff; }

/* ---- Mobile -------------------------------------------------------------
   Keep the RESEARCH sub-pages reachable even with scripting off. */
.wixui-vertical-menu__submenu { display: block !important; }
.wixui-vertical-menu__submenu a { padding-left: 28px !important; }
"""

SITE_JS = """/* Mobile menu toggle. Wix's own handler lived in the stripped bundle;
   #MENU_AS_CONTAINER is shown/hidden purely by the data-undisplayed attribute
   (its rule is [data-undisplayed=true]{display:none} in Wix's inline CSS). */
(function () {
  var toggle = document.getElementById('MENU_AS_CONTAINER_TOGGLE');
  var panel  = document.getElementById('MENU_AS_CONTAINER');
  if (!toggle || !panel) return;

  function setOpen(open) {
    if (open) panel.removeAttribute('data-undisplayed');
    else panel.setAttribute('data-undisplayed', 'true');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  setOpen(false);

  toggle.addEventListener('click', function (e) {
    e.preventDefault();
    setOpen(panel.getAttribute('data-undisplayed') === 'true');
  });
  toggle.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle.click(); }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') setOpen(false);
  });
  panel.addEventListener('click', function (e) {
    if (e.target.closest('a')) setOpen(false);
  });
})();
"""

def switch_script(kind, outdir):
    """Send phones to the mobile tree and desktops to the desktop tree, once."""
    other = page_link("m" if kind == "d" else "d", outdir, outdir)
    if kind == "d":
        other = prefix_for("d", outdir) + "m/" + ((outdir + "/") if outdir else "") + "index.html"
    else:
        other = prefix_for("m", outdir) + ((outdir + "/") if outdir else "") + "index.html"
    is_m = "true" if kind == "m" else "false"
    return ('<script>/* viewport switch: Wix served separate desktop and mobile documents */'
            '(function(){try{var g="vpsw";'
            'if(sessionStorage.getItem(g)){sessionStorage.removeItem(g);return;}'
            'if(location.search.indexOf("nosw")>-1)return;'
            'var isM=%s,want=(screen.width<768);'
            'if(want!==isM){sessionStorage.setItem(g,"1");'
            'location.replace("%s"+location.hash);}}catch(e){}})();</script>' % (is_m, other))

RE_SCRIPT = re.compile(r'<script\b(?![^>]*application/ld\+json)[^>]*>.*?</script>', re.S | re.I)
RE_SCRIPT_SELF = re.compile(r'<script\b(?![^>]*application/ld\+json)[^>]*/>', re.I)
RE_FONTFACE = re.compile(r'@font-face\s*\{[^}]*parastorage[^}]*\}', re.I)
def element_span(h, start):
    """Balanced span of the <div> that opens at `start`."""
    i = h.index('>', start) + 1
    depth = 1
    for m in re.finditer(r'<(/?)div\b[^>]*>', h[i:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return start, i + m.end()
    return None

REPEATER_ID = 'comp-lemw85ju3_wrapper'

def rebuild_projects(h):
    """/projects is a Wix repeater whose grid is laid out by the JS runtime, so
    it cannot survive a static export. The card content is in the SSR markup;
    re-emit it as a plain CSS grid. This is the one page that is rebuilt rather
    than snapshotted -- see README."""
    i = h.find('id="' + REPEATER_ID + '"')
    if i == -1:
        return h
    start = h.rfind('<div', 0, i)
    span = element_span(h, start)
    if not span:
        return h
    inner = h[span[0]:span[1]]
    cards, seen = [], set()
    for block in re.split(r'(?=<div[^>]*id="comp-lemw85jz2__)', inner):
        href = re.search(r'href="([^"]*/projects/[^"]*)"', block)
        if not href or href.group(1) in seen:
            continue
        texts = [re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', t))).strip()
                 for t in re.findall(r'<(?:h[1-6]|p)[^>]*>(.*?)</(?:h[1-6]|p)>', block, re.S)]
        texts = [t for t in texts if t and t.lower() != 'read more']
        if len(texts) < 2:
            continue
        seen.add(href.group(1))
        cards.append('<a class="rs-card" href="%s"><span class="rs-card-title">%s</span>'
                     '<span class="rs-card-desc">%s</span>'
                     '<span class="rs-card-more">Read More</span></a>'
                     % (href.group(1), html.escape(texts[0]), html.escape(texts[1])))
    if not cards:
        return h
    return h[:span[0]] + '<div class="rs-cards">' + ''.join(cards) + '</div>' + h[span[1]:]

RE_SUBMENU = re.compile(r'<ul aria-hidden="true"[^>]*>(.*?)</ul>', re.S)

def rebuild_submenu(m):
    """Wix's nested drop-down <ul> is styled by CSS that assumes its JS ran.
    Re-emit it as plain markup under our own class so site.css fully owns it."""
    items = re.findall(r'<a\b([^>]*)>(.*?)</a>', m.group(1), re.S)
    out = ['<ul class="rs-submenu">']
    for attrs, text in items:
        href = re.search(r'href="([^"]*)"', attrs)
        out.append('<li><a href="%s">%s</a></li>' % (href.group(1) if href else '#',
                                                     re.sub(r'<[^>]+>', '', text).strip()))
    out.append('</ul>')
    return ''.join(out)

RE_SOURCEMAP = re.compile(r'/\*#\s*sourceMappingURL=[^*]*\*/')
RE_FAVICON = re.compile(r'<link[^>]*rel=["\'](?:icon|shortcut icon|apple-touch-icon|mask-icon)["\'][^>]*>', re.I)
RE_DEADLINK = re.compile(
    r'<link[^>]+rel=["\'](?:preload|prefetch|preconnect|dns-prefetch|canonical|alternate|manifest|prerender)["\'][^>]*>',
    re.I)

def transform(kind, outdir, src_path):
    h = open(src_path, encoding="utf-8", errors="replace").read()
    pre = prefix_for(kind, outdir)

    h = RE_SCRIPT.sub("", h)
    h = RE_SCRIPT_SELF.sub("", h)
    h = RE_DEADLINK.sub("", h)
    h = RE_FONTFACE.sub("", h)
    h = RE_SOURCEMAP.sub("", h)
    h = RE_FAVICON.sub("", h)
    # inert provenance attributes on inline <style> tags; no requests, but strip for clarity
    h = re.sub(r'(<style)([^>]*?)\s+data-(?:url|href)="[^"]*"', r'\1\2', h)
    h = RE_SUBMENU.sub(rebuild_submenu, h)
    if outdir in ("projects",):
        h = rebuild_projects(h)

    for blurred, sharp in placeholder_map(h).items():
        h = h.replace(blurred, sharp)

    # ---- assets -> local
    def img_sub(m):
        u = m.group(0)
        name = IMG.get(u) or IMG.get(u.replace("https:", "", 1)) or IMG.get("//" + u.split("//", 1)[-1])
        return (pre + "assets/img/" + name) if name else u
    h = RE_IMG.sub(img_sub, h)

    def doc_sub(m):
        u = m.group(0)
        full = u if u.startswith("http") else SITE + u
        name = DOC.get(full)
        return (pre + "files/" + urllib.parse.quote(name)) if name else u
    h = RE_PDF.sub(doc_sub, h)

    # ---- internal page links -> relative
    def href_sub(m):
        quote, url = m.group(1), m.group(2)
        raw = html.unescape(url)
        if raw.startswith(SITE):
            path = raw[len(SITE):] or "/"
        elif raw.startswith("http") or raw.startswith("//") or raw.startswith("mailto:") or raw.startswith("#"):
            return m.group(0)
        elif raw.startswith("/"):
            path = raw
        else:
            return m.group(0)
        path, _, frag = path.partition("#")
        path = path or "/"
        if path.startswith("/assets/") or path.startswith("/files/") or "/_files/" in path:
            return m.group(0)
        if EXCLUDED.match(path):
            return 'href=%s%s%s' % (quote, page_link(kind, outdir, ""), quote)
        key = path.rstrip("/") or "/"
        target = PATHMAP.get(key, PATHMAP.get(urllib.parse.unquote(key)))
        if target is None:
            return m.group(0)
        link = page_link(kind, outdir, target) + (("#" + frag) if frag else "")
        return 'href=%s%s%s' % (quote, link, quote)
    h = re.sub(r'href=(["\'])([^"\']*)\1', href_sub, h)

    # ---- head injections
    h = re.sub(r'<html([^>]*)\slang="[^"]*"', r'<html\1 lang="en"', h, count=1)
    if 'lang=' not in h[:h.find('>', h.find('<html'))+1]:
        h = h.replace('<html', '<html lang="en"', 1)

    inject = ('<link rel="icon" href="%sassets/favicon.svg" type="image/svg+xml">' % pre
              + switch_script(kind, outdir)
              + '<link rel="stylesheet" href="%sassets/fonts.css">' % pre
              + '<link rel="stylesheet" href="%sassets/site.css">' % pre)
    if "<head>" in h:
        h = h.replace("<head>", "<head>" + inject, 1)
    else:
        h = re.sub(r'(<head[^>]*>)', r'\1' + inject.replace("\\", "\\\\"), h, count=1)

    h = h.replace("</body>", '<script src="%sassets/site.js"></script></body>' % pre, 1)
    return h

def main():
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    open(os.path.join(OUT, "assets", "site.css"), "w").write(SITE_CSS)
    open(os.path.join(OUT, "assets", "site.js"), "w").write(SITE_JS)

    n = 0
    for path, outdir in PAGES:
        slug = (outdir or "home").replace("/", "__")
        for kind in ("d", "m"):
            src = os.path.join(CACHE, f"{kind}_{slug}.html")
            dest_dir = os.path.join(OUT, *( (["m"] if kind == "m" else []) + (outdir.split("/") if outdir else []) ))
            os.makedirs(dest_dir, exist_ok=True)
            out = transform(kind, outdir, src)
            open(os.path.join(dest_dir, "index.html"), "w", encoding="utf-8").write(out)
            n += 1
    print(f"[transform] {n} pages written")

if __name__ == "__main__":
    main()
