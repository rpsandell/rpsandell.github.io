# ryan-sandell.com — source for https://rpsandell.github.io

Plain, hand-editable HTML and CSS. **There is no build step and no framework.**
Edit a file, commit, push — the GitHub Actions workflow in `.github/workflows/`
publishes it.

## Layout

```
index.html                                  About Me (home page)
research/index.html                         Research index — the six cards
teaching/index.html                         Courses
contact/index.html                          Contact
phonology-morphology-interface/…            ┐
computational-and-corpus-linguistics/…      │ the six research areas,
data-homer/…                                │ each with its own
historical-and-indo-european-linguistics/…  │ publication list
linguistics-of-indic-germanic-greek/…       │
word-prosodic-systems/…                     ┘
assets/site.css        all styling — colours and spacing at the top
assets/site.js         opens the menu on phones; nothing else
assets/fonts.css       self-hosted Poppins / Nunito Sans / Barlow
assets/img/            11 images
files/                 14 PDFs
tools/                 optional helper scripts (see below)
404.html  robots.txt  sitemap.xml  .nojekyll
```

## Editing

Every page is one complete file, indented with tabs, with banner comments
marking each region and an `<!-- EDIT: … -->` marker on anything you're likely
to change. To find what you want, open the file and look for `EDIT`.

**Add a publication** — open the relevant research page and copy one whole
`<li class="publication">` block:

```html
<li class="publication">
	<span class="publication__year">2026</span>
	<p class="publication__cite">Title of the paper. <em>Journal Name</em> 12.1–20.</p>
	<a class="publication__pdf" href="../files/YourFile.pdf">PDF</a>
</li>
```

Drop the PDF in `files/` first. If there's nothing to link, delete the `<a>` line.
`<em>…</em>` marks italics.

**Add a course** — copy one `<li>` line into the right list in `teaching/index.html`.

**Change colours, fonts or spacing** — everything is a custom property in the
`:root` block at the top of `assets/site.css`. Change a value there and it applies
site-wide; you shouldn't need to touch anything below that block.

**Add a page** — copy the folder of an existing page, edit the content, then add
it to the navigation (see the next section).

## The shared header and footer

Each page carries its own copy of the navigation and footer — that's the price of
having standalone files with no build step. To change them everywhere at once:

1. Edit `tools/_chrome/header.html` or `tools/_chrome/footer.html`.
   Use `{{PREFIX}}` where a link needs `../` on sub-pages and nothing on the home page.
2. Run:

```bash
python3 tools/sync-chrome.py
```

It rewrites only the regions between `<!-- BEGIN SHARED HEADER -->` / `<!-- END SHARED HEADER -->`
(and the same for the footer) and leaves all page content untouched. `--check` shows
what would change without writing. Editing the header in one page by hand is also
fine — just don't run the sync afterwards, or it will be overwritten.

`tools/_generate_pages.py` is the one-off script that originally produced these
pages from the old Wix export. It is kept for reference only; **running it would
overwrite your edits.**

## What changed in this rebuild

Replaced the Wix snapshot (17 desktop pages plus a separate 17-page `/m` mobile
tree, ~130 KB each, 77% of every file being inlined Wix CSS) with 10 responsive
pages of 5–9 KB.

- **One responsive site.** The `/m` tree is gone. Wix served two separate documents
  and sniffed the browser; this site uses ordinary CSS, so there is one file per page.
  This also fixes a live bug: your Teaching edits had been applied to the desktop page
  only, so phone visitors were still seeing the old course list. The newer desktop
  content is now the single version.
- **`/projects` removed** at your instruction — the listing and its six detail pages.
  They duplicated the six research areas, and each carried the same placeholder
  publication from an unedited Wix collection. Old `/projects/…` URLs now hit `404.html`;
  add redirects if you want them preserved.
- **Fixed two Wix leftovers:** `research/` and `teaching/` both had
  `<title>PROJECTS | personal-resume</title>`. Every page now has a real title and a
  meta description — worth rewording to taste, they're marked `EDIT` in each file.
- **Recovered a lost PDF.** `Sandell_2018_Vedic_dāśvāms-.pdf` was referenced but not
  present in the repository: the accented filename existed in your history in two
  different Unicode normalisations (NFC in `0aa2513`, NFD in `961f832`) and neither
  survived to HEAD. It is restored from history as **`files/Sandell_2018_Vedic_dasvams.pdf`** —
  a plain-ASCII name, which avoids that whole class of problem. Prefer ASCII filenames
  for anything you add to `files/`.
- **Removed 104 unused images** (16.9 MB) left over from the Wix template, and one
  byte-identical duplicate PDF. All are recoverable from git history.
- **Fixed a double slash** (`rpsandell.github.io//`) that the search-and-replace left
  in `sitemap.xml` and `robots.txt`.

## Two things left as they are

Both were reproduced verbatim at your request — flagged here so they aren't forgotten:

1. **`teaching/index.html`** reads "Wintersemester 2026/-26", which looks like a slip
   for 2025/26.
2. **`historical-and-indo-european-linguistics/index.html`**: the entry dated 2011,
   "Evidence for Acrostatic Presents in Old Irish?", links to a file named
   `Sandell_2012_Evidence_for_Indo_European_Acrostatic_Pr.pdf`. Worth checking that the
   citation and the file match.

Also worth knowing: `computational-and-corpus-linguistics/` has no summary line under
its heading — the other five research pages do. The Research card describes it as
"Applications of computational and corpus-linguistic techniques to an array of diverse
linguistic problems," which you could paste in as a `<p>` under the `<h1>`.

## Fonts

Poppins is the site's real typeface and is open-source (SIL OFL), self-hosted here.
Avenir LT and DIN Next in the original were licensed to Wix rather than to you, so
they're substituted by Nunito Sans and Barlow (also OFL). All are served from
`assets/fonts/` — nothing is fetched from Google or Wix at runtime.

## Checks run after the rebuild

- 224 internal links and asset references — 0 broken
- No page scrolls horizontally at 500px or 1440px
- No reference to any Wix host remains
