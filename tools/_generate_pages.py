#!/usr/bin/env python3
"""
ONE-OFF GENERATOR — kept for reference, not part of the normal workflow.

This is the script that produced the hand-editable index.html files in this
repository, replacing the original Wix snapshot. The generated HTML is now the
source of truth: edit the .html files directly. Re-running this script would
overwrite those edits.

To propagate a change to the shared header/nav/footer across all pages, use
tools/sync-chrome.py instead — that is the script meant for day-to-day use.
"""

import os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = "\t"

# ============================================================================
# SHARED CHROME
# ============================================================================

NAV = [
    ("About Me", "", None),
    ("Research", "research", [
        ("Phonology-Morphology Interface",        "phonology-morphology-interface"),
        ("Computational and Corpus Linguistics",  "computational-and-corpus-linguistics"),
        ("Data Homer",                            "data-homer"),
        ("Historical and Indo-European Linguistics", "historical-and-indo-european-linguistics"),
        ("Linguistics of Indic, Germanic, Greek", "linguistics-of-indic-germanic-greek"),
        ("Word Prosodic Systems",                 "word-prosodic-systems"),
    ]),
    ("Teaching", "teaching", None),
    ("Contact",  "contact",  None),
]

SOCIAL = [
    ("Google Scholar", "https://scholar.google.com/citations?user=NBH22UYAAAAJ&amp;hl=en&amp;oi=ao", "img_bd6e3752092a.png"),
    ("Academia.edu",   "https://lmu-munich.academia.edu/RyanSandell",       "img_cc4460ab9672.png"),
    ("GitHub",         "https://github.com/rpsandell",                      "img_b48756af7325.png"),
    ("LinkedIn",       "https://www.linkedin.com/in/ryan-sandell-808913a1/", "img_cec87551182e.png"),
]

EMAIL = "ryan.sandell@gmail.com"
COPYRIGHT = "&copy; 2024 Ryan Sandell"


def link(prefix, slug):
    """Relative URL from the current page to another page of the site."""
    return (prefix + slug + "/index.html") if slug else (prefix + "index.html")


def header_html(prefix, current, indent=1):
    p = T * indent
    L = []
    L.append(p + '<!-- ============================================================')
    L.append(p + '     SHARED HEADER  —  identical on every page.')
    L.append(p + '     Edit tools/_chrome/header.html and run tools/sync-chrome.py')
    L.append(p + '     to update all pages at once, or just edit each page by hand.')
    L.append(p + '     ============================================================ -->')
    L.append(p + '<!-- BEGIN SHARED HEADER -->')
    L.append(p + '<header class="site-header">')
    L.append(p + T + '<div class="wrap site-header__inner">')
    L.append(p + T*2 + '<!-- Wordmark: the blue square, your name, and your role. -->')
    L.append(p + T*2 + '<a class="brand" href="%s">' % link(prefix, ""))
    L.append(p + T*3 + '<span class="brand__square" aria-hidden="true"></span>')
    L.append(p + T*3 + '<span class="brand__name">Ryan Sandell</span>')
    L.append(p + T*3 + '<span class="brand__role">Linguist</span>')
    L.append(p + T*2 + '</a>')
    L.append('')
    L.append(p + T*2 + '<!-- Shown only on narrow screens; controlled by assets/site.js. -->')
    L.append(p + T*2 + '<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>')
    L.append('')
    L.append(p + T*2 + '<!-- EDIT: main navigation. Add or remove <li> items here. -->')
    L.append(p + T*2 + '<nav class="nav" id="site-nav" aria-label="Main">')
    L.append(p + T*3 + '<ul class="nav__list">')
    for label, slug, sub in NAV:
        cur = ' aria-current="page"' if slug == current else ''   # placed right after data-nav, matching sync-chrome.py
        L.append(p + T*4 + '<li class="nav__item">')
        L.append(p + T*5 + '<a class="nav__link" data-nav="%s"%s href="%s">%s</a>' % (slug or 'home', cur, link(prefix, slug), label.upper()))
        if sub:
            L.append(p + T*5 + '<!-- EDIT: Research drop-down. Opens on hover and on keyboard focus. -->')
            L.append(p + T*5 + '<ul class="nav__submenu">')
            for sl, ss in sub:
                L.append(p + T*6 + '<li><a href="%s">%s</a></li>' % (link(prefix, ss), sl))
            L.append(p + T*5 + '</ul>')
        L.append(p + T*4 + '</li>')
    L.append(p + T*3 + '</ul>')
    L.append(p + T*2 + '</nav>')
    L.append(p + T + '</div>')
    L.append(p + '</header>')
    L.append(p + '<!-- END SHARED HEADER -->')
    return "\n".join(L)


def social_html(prefix, indent, css_class="social"):
    p = T * indent
    L = [p + '<ul class="%s">' % css_class]
    for name, href, icon in SOCIAL:
        L.append(p + T + '<li>')
        L.append(p + T*2 + '<a href="%s" target="_blank" rel="noopener">' % href)
        L.append(p + T*3 + '<img src="%sassets/img/%s" alt="%s" width="21" height="21" loading="lazy">' % (prefix, icon, name))
        L.append(p + T*2 + '</a>')
        L.append(p + T + '</li>')
    L.append(p + '</ul>')
    return "\n".join(L)


def footer_html(prefix, indent=1):
    p = T * indent
    L = []
    L.append(p + '<!-- ============================================================')
    L.append(p + '     SHARED FOOTER  —  identical on every page.')
    L.append(p + '     ============================================================ -->')
    L.append(p + '<!-- BEGIN SHARED FOOTER -->')
    L.append(p + '<footer class="site-footer">')
    L.append(p + T + '<div class="wrap site-footer__inner">')
    L.append(p + T*2 + '<!-- EDIT: copyright line. -->')
    L.append(p + T*2 + '<p>%s</p>' % COPYRIGHT)
    L.append('')
    L.append(p + T*2 + '<div class="site-footer__group">')
    L.append(p + T*3 + '<span class="site-footer__label">Write</span>')
    L.append(p + T*3 + '<a href="mailto:%s">send an email</a>' % EMAIL)
    L.append(p + T*2 + '</div>')
    L.append('')
    L.append(p + T*2 + '<div class="site-footer__group">')
    L.append(p + T*3 + '<span class="site-footer__label">Follow</span>')
    L.append(social_html(prefix, indent + 3))
    L.append(p + T*2 + '</div>')
    L.append(p + T + '</div>')
    L.append(p + '</footer>')
    L.append(p + '<!-- END SHARED FOOTER -->')
    return "\n".join(L)


def page(slug, title, description, main_body, prefix, current, note=""):
    """Assemble one complete page."""
    L = []
    L.append('<!DOCTYPE html>')
    L.append('<html lang="en">')
    L.append('')
    L.append('<head>')
    L.append(T + '<!-- ============================================================')
    L.append(T + '     %s' % title)
    L.append(T + '     ' + '-' * 56)
    L.append(T + '     Plain, hand-editable HTML. No build step: save the file and')
    L.append(T + '     commit, and GitHub Pages publishes it.')
    L.append(T + '     Styling lives in assets/site.css — colours and spacing are')
    L.append(T + '     custom properties at the top of that file.')
    if note:
        L.append(T + '     ')
        for ln in note.strip().splitlines():
            L.append(T + '     ' + ln.strip())
    L.append(T + '     ============================================================ -->')
    L.append(T + '<meta charset="utf-8">')
    L.append(T + '<meta name="viewport" content="width=device-width, initial-scale=1">')
    L.append('')
    L.append(T + '<!-- EDIT: browser tab title and the summary search engines show. -->')
    L.append(T + '<title>%s</title>' % title)
    L.append(T + '<meta name="description" content="%s">' % description)
    L.append('')
    L.append(T + '<link rel="icon" href="%sassets/favicon.svg" type="image/svg+xml">' % prefix)
    L.append(T + '<link rel="stylesheet" href="%sassets/fonts.css">' % prefix)
    L.append(T + '<link rel="stylesheet" href="%sassets/site.css">' % prefix)
    L.append('</head>')
    L.append('')
    L.append('<body>')
    L.append(T + '<!-- Lets keyboard users jump past the navigation. -->')
    L.append(T + '<a class="skip-link" href="#main">Skip to content</a>')
    L.append('')
    L.append(header_html(prefix, current))
    L.append('')
    L.append(T + '<!-- ============================================================')
    L.append(T + '     PAGE CONTENT  —  everything unique to this page is below.')
    L.append(T + '     ============================================================ -->')
    L.append(T + '<main id="main">')
    L.append(main_body)
    L.append(T + '</main>')
    L.append('')
    L.append(footer_html(prefix))
    L.append('')
    L.append(T + '<script src="%sassets/site.js"></script>' % prefix)
    L.append('</body>')
    L.append('')
    L.append('</html>')
    out = "\n".join(L) + "\n"
    out = re.sub(r'\n{3,}', '\n\n', out)
    path = os.path.join(REPO, slug, 'index.html') if slug else os.path.join(REPO, 'index.html')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(out)
    return path, len(out)


# ============================================================================
# CONTENT
# ----------------------------------------------------------------------------
# Every string below was transcribed from the Wix snapshot. Italics inside
# citations use <em>, which is what the original marked with an italic span.
# ============================================================================

PUBS = {
 "phonology-morphology-interface": [
  ("2017", 'Allomorph Selection in Vedic Sanskrit Perfects of the Form C<sub>i</sub>e&#720;C<sub>j</sub>-. In Karen Jesney, Charlie O&rsquo;Hara, Caitlin Smith, and Rachel Walker (eds.), <em>Supplemental Proceedings of the 2016 Annual Meeting on Phonology</em>. Washington, DC: Linguistic Society of America.', "Sandell_2017_Allomorph_Selection.pdf"),
  ("2015", 'with Sam Zukoff. The Phonology of Morpheme Realization in the Germanic Strong Preterites. In Thuy Bui and Deniz &Ouml;zy&#305;ld&#305;z (eds.), <em>NELS 45: Proceedings of the 45th Annual North East Linguistics Society Conference</em>. In Amherst, MA: GLSA.', "The_Phonology_of_Morpheme_Realization_in.pdf"),
  ("2011", 'The Morphophonology of Reduplicated Presents in Vedic and Indo-European. In Stephanie Jamison, H. Craig Melchert, and Brent Vine (eds.), <em>Proceedings of the 22nd UCLA Indo-European Conference</em>, 223&ndash;54. Bremen: Hempen Verlag.', "Sandell_2011_The_Morphophonology_of_Reduplicated_Pres.pdf"),
 ],
 "computational-and-corpus-linguistics": [
  ("2022", 'with Olav Hackstein. The Rise of Colligations: English <em>can&rsquo;t stand</em> and German <em>nicht ausstehen k&ouml;nnen</em>. <em>International Journal of Corpus Linguistics</em> 28.60&ndash;90.', "HacksteinSandell_2022_with_appendices.pdf"),
  ("2016", 'R&#803;gvedic <em>&#347;&aacute;kt&#299;vant</em>: Accentuation and Statistical Learning of Allomorph Selection in Vedic <em>-mant/vant-</em> stems. In D. Goldstein, S. Jamison, and B. Vine (eds.), <em>Proceedings of the 27th UCLA Indo-European Conference</em>. Bremen: Hempen Verlag.', "Sandell_2016_Rgvedic_saktivant_Accentuation_and_Stat.pdf"),
  ("2015", '<em>Productivity in Historical Linguistics: Computational Perspectives on Word Formation in Ancient Greek and Sanskrit</em>. Ph.D. diss., University of California, Los Angeles.', "SandellDissertation.pdf"),
 ],
 "data-homer": [
  ("2022", 'with Chiara Bozzone. One or Many Homers? Using Quantitative Authorship Analysis to Study the Homeric Question. In David Goldstein, Stephanie Jamison, and Brent Vine (eds.), <em>Proceedings of the 32nd West Coast Indo-European Conference</em>, 21&ndash;48. Hamburg: Buske.', "BozzoneSandell_2022_One_or_Many_Homers.pdf"),
 ],
 "historical-and-indo-european-linguistics": [
  ("2018", 'Vedic <em>d&#257;&#347;v&#257;&#769;&#7747;s-</em> &lsquo;pious one&rsquo;, Homeric <em>&#7936;&delta;&eta;&kappa;&oacute;&tau;&epsilon;&sigmaf;</em> &lsquo;inattentive&rsquo;, and the &ldquo;Long-Vowel&rdquo; Perfects of Proto-Indo-European. <em>Indo-European Linguistics</em> 6:117&ndash;51.', "Sandell_2018_Vedic_dasvams.pdf"),
  ("2014", 'Compensatory Lengthening in Vedic and the Outcomes of Proto-Indo-Iranian *[az] and *[a&#382;]. In S. Jamison, H.C. Melchert, and B. Vine (eds.), <em>Proceedings of the 25th UCLA Indo-European Conference</em>, 183&ndash;201. Bremen: Hempen Verlag.', "Sandell_2014_Compensatory_Lengthening_in_Vedic_and_th.pdf"),
  ("2011", 'Evidence for Acrostatic Presents in Old Irish?. In D. Furchtgott, M. Holmberg, A. Joseph McMullen, and N. Sumner (eds), <em>Proceedings of the 31st Harvard Celtic Colloquium</em>, 282&ndash;304. Cambridge, MA: Department of Celtic Languages and Literatures, Harvard University.', "Sandell_2012_Evidence_for_Indo_European_Acrostatic_Pr.pdf"),
 ],
 "linguistics-of-indic-germanic-greek": [
  ("Accepted", 'Reflexive and Middle in Gothic. In G&ouml;tz Keydana, Wolfgang Hock, and Paul Widmer (eds.), <em>Reflexive and Middle in Indo-European</em>. Berlin: De Gruyter Mouton.', None),
  ("Accepted", 'with Nelson Goering. Gothic. In G&ouml;tz Keydana, Saverio Dalpedri, and Stavros Skopeteas (eds.), <em>A Handbook of Ancient Indo-European Grammars</em>. Cambridge: Cambridge University Press.', None),
 ],
 "word-prosodic-systems": [
  ("2023", '<em>Towards a Dynamics of Prosodic Change: Computational and Corpus-Based Studies in the Synchronic and Diachronic Prosodic Phonology of Indic, Greek, and Germanic</em>. Habilitationsschrift, Ludwig-Maximilians-Universit&auml;t M&uuml;nchen.', "SandellHabilitation_Final_28_02.pdf"),
  ("2023", 'Towards a Prosodic History of Indic: A Parametric Analysis of the &ldquo;Classical Sanskrit Stress Rule&rdquo;. In D. Goldstein, S. Jamison, and T. Yates (eds.), <em>Proceedings of the 33rd Annual UCLA Indo-European Conference</em>, 157&ndash;82. Bremen: Buske Verlag.', "sandell_2023_C_Skt_Stress.pdf"),
  ("In Revision", 'with Dieter Gunkel. On the Representation and Realization of the Ancient Greek Acute: Evidence from Tone-Tune Mappings in Ancient Greek Music. <span class="publication__note"><a href="mailto:%s">Please contact me for a draft!</a></span>' % EMAIL, None),
  ("2023", '(Presentation) An Updated Treatment of Recessive Accentuation in Attic-Ionic Greek: Optimizing the Golstonian Analysis. 42nd East Coast Indo-European Conference, 23 June 2023.', "Sandell_2023_An_Updated_Treatment_of_Recessive_Accent.pdf"),
 ],
}

SUBPAGES = [
 ("phonology-morphology-interface", "Phonology-Morphology Interface | Ryan Sandell",
  "Allomorphy and the Phonology-Morphology Interface",
  "What components of the grammar are responsible for controlling allomorphy, and under what conditions does one component exercise control in determining or selecting allomorphs?",
  "Research on allomorphy and the phonology-morphology interface, with publications by Ryan Sandell."),
 ("computational-and-corpus-linguistics", "Computational and Corpus Linguistics | Ryan Sandell",
  "Computational and Corpus-Linguistic Studies", None,
  "Computational and corpus-linguistic studies by Ryan Sandell, with downloadable publications."),
 ("data-homer", "Data Homer | Ryan Sandell", "Data Homer",
  "How can quantitative and computational methods contribute to the study of the &quot;Homeric Question&quot;?",
  "Quantitative and computational approaches to the Homeric Question."),
 ("historical-and-indo-european-linguistics", "Historical and Indo-European Linguistics | Ryan Sandell",
  "Historical and Indo-European Linguistics",
  "How has the Indo-European language family changed and diversified over the millennia? What generalizations about language change generally can be drawn from this wealth of data?",
  "Research in historical and Indo-European linguistics by Ryan Sandell."),
 ("linguistics-of-indic-germanic-greek", "Linguistics of Indic, Germanic, Greek | Ryan Sandell",
  "Linguistics and Philology of Indic, Greek, and Germanic",
  "Descriptive and theoretical work on the phonology, morphology, and syntax of (older) Indo-European languages.",
  "Descriptive and theoretical work on Indic, Greek, and Germanic."),
 ("word-prosodic-systems", "Word Prosodic Systems | Ryan Sandell",
  "Word Prosodic Systems and Prosodic Change",
  "How do the grammars for calculating word-level prominence (stress, accent, tone) function, what types of such grammars can exist, and how do they change diachronically?",
  "Word-prosodic systems and prosodic change: stress, accent, and tone."),
]

RESEARCH_CARDS = [
 ("word-prosodic-systems", "Word Prosodic Systems and Prosodic Change",
  "How do the grammars for calculating word-level prominence (stress, accent, tone) function, what types of such grammars can exist, and how do they change diachronically?", "img_64745a15980a.jpg"),
 ("phonology-morphology-interface", "Allomorphy and the Phonology-Morphology Interface",
  "What components of the grammar are responsible for controlling allomorphy, and under what conditions does one component exercise control in determining or selecting allomorphs?", "img_8ce595bd1555.jpg"),
 ("computational-and-corpus-linguistics", "Computational and Corpus-Linguistic Studies",
  "Applications of computational and corpus-linguistic techniques to an array of diverse linguistic problems.", "img_1aaa000416dc.jpg"),
 ("data-homer", "Data Homer",
  "How can quantitative and computational methods contribute to the study of the &quot;Homeric Question&quot;?", "img_df8e486745f0.jpg"),
 ("historical-and-indo-european-linguistics", "Historical and Indo-European Linguistics",
  "How has the Indo-European language family changed and diversified over the millennia? What generalizations about language change generally can be drawn from this wealth of data?", "img_d3d3d616b5e1.jpg"),
 ("linguistics-of-indic-germanic-greek", "Linguistics and Philology of Indic, Greek, and Germanic",
  "Descriptive and theoretical work, often with a quantitative element, on the phonology, morphology, and syntax of (older) Indo-European languages.", "img_55a6995968cb.jpg"),
]

TEACHING = [
 ("General Linguistics", [
   ("Ludwig-Maximilians-Universit&auml;t M&uuml;nchen", [
     "Optimality Theory and Phonological Learnability (Summer 2024, Summer 2026)",
     "Introduction to Phonology and Phonological Analysis (Summer 2020&ndash;2026)",
     "Morphology (Winter 2017&ndash;2026)",
     "Introduction to the Study of Language (Winter 2019&ndash;2026)"]),
   ("University of California, Los Angeles", [
     "Introduction to Phonology",
     "Introduction to Linguistic Analysis",
     "Introduction to Historical Linguistics"]),
 ]),
 ("Indo-European and Historical Linguistics", [
   ("Ludwig-Maximilians-Universit&auml;t M&uuml;nchen", [
     "Indo-European Linguistics (Summer 2018&ndash;2019)",
     "Indo-European Phonology (Winter 2017&ndash;2026)",
     "Historical Grammar of Anatolian Languages (Summer 2025)",
     "Historical Grammar of Indo-Iranian Languages (Winter 2023)",
     "Linguistics and Philology of Greek (Summer 2018)",
     "Research Seminar on Indo-European Linguistics (Summer 2021, Summer 2026)"]),
   ("University of California, Los Angeles", [
     "Indo-European Phonology",
     "Indo-European Morphology"]),
 ]),
 ("Computational and Corpus Linguistics", [
   ("Ludwig-Maximilians-Universit&auml;t M&uuml;nchen", [
     "Optimality Theory and Phonological Learnability (Summer 2024, 2026)",
     "Introduction to Computational Linguistics and Quantitative Corpus Linguistics (Winter 2017&ndash;2023; Winter 2025&ndash;2026)"]),
 ]),
]


# ============================================================================
# PAGE BODIES
# ============================================================================

def build_home():
    p = T * 2
    L = []
    L.append(T + '<!-- ---------- HERO: portrait card + introduction ---------- -->')
    L.append(T + '<section class="band-beige">')
    L.append(p + '<div class="wrap hero">')
    L.append('')
    L.append(p + T + '<!-- EDIT: portrait card. Photo lives in assets/img/. -->')
    L.append(p + T + '<div class="profile-card">')
    L.append(p + T*2 + '<img class="profile-card__photo" src="assets/img/img_c7b8c8142d70.jpg" alt="Ryan Sandell" width="190" height="190">')
    L.append(p + T*2 + '<p class="profile-card__name">Ryan Sandell</p>')
    L.append(p + T*2 + '<hr class="profile-card__rule">')
    L.append(p + T*2 + '<p class="profile-card__role">Linguist</p>')
    L.append(p + T*2 + '<!-- EDIT: profile links. Same list appears in the footer. -->')
    L.append(social_html("", 5))
    L.append(p + T + '</div>')
    L.append('')
    L.append(p + T + '<!-- EDIT: headline, buttons, and the introduction below. -->')
    L.append(p + T + '<div class="hero__intro">')
    L.append(p + T*2 + '<h1>Welcome! I&rsquo;m Ryan Sandell, a (computational) phonologist and historical linguist.</h1>')
    L.append('')
    L.append(p + T*2 + '<div class="btn-row">')
    L.append(p + T*3 + '<a class="btn btn--solid" href="files/SandellCV.pdf">CV</a>')
    L.append(p + T*3 + '<a class="btn btn--outline" href="research/index.html">Research</a>')
    L.append(p + T*2 + '</div>')
    L.append('')
    L.append(p + T*2 + '<p>I am a UCLA-trained phonologist with a focus on historical linguistics and computational methods.</p>')
    L.append('')
    L.append(p + T*2 + '<p>')
    L.append(p + T*3 + 'I am currently an Akademischer Oberrat (fixed-term Associate Professor) at the')
    L.append(p + T*3 + 'Ludwig-Maximilians-Universit&auml;t M&uuml;nchen (LMU Munich) in the')
    L.append(p + T*3 + '<a href="https://www.indogermanistik.uni-muenchen.de/index.html" target="_blank" rel="noopener">Institut f&uuml;r Vergleichende und Historische Sprachwissenschaft sowie Albanologie</a>.')
    L.append(p + T*3 + 'I was first appointed as Akademischer Rat (fixed-term Assistant Professor) at the LMU in 2017,')
    L.append(p + T*3 + 'and prior to that, I was a Lecturer for the Department of Linguistics and Program in')
    L.append(p + T*3 + 'Indo-European Studies at the University of California, Los Angeles (UCLA), where I also')
    L.append(p + T*3 + 'carried out my doctoral studies (in')
    L.append(p + T*3 + '<a href="https://pies.ucla.edu/" target="_blank" rel="noopener">Indo-European Studies</a> and')
    L.append(p + T*3 + '<a href="https://linguistics.ucla.edu/" target="_blank" rel="noopener">Linguistics</a>).')
    L.append(p + T*2 + '</p>')
    L.append('')
    L.append(p + T*2 + '<p>')
    L.append(p + T*3 + 'My current principal area of research lies with the computational modeling of phonological')
    L.append(p + T*3 + 'phenomena and their implications for phonological theory, with particular attention to')
    L.append(p + T*3 + 'language change and learnability theory, employing corpus-linguistic and quantitative')
    L.append(p + T*3 + 'methods across the board. Data from some of the earliest-attested Indo-European languages')
    L.append(p + T*3 + '(e.g., Sanskrit, Ancient Greek, Gothic) form the empirical core of my work.')
    L.append(p + T*2 + '</p>')
    L.append('')
    L.append(p + T*2 + '<p>')
    L.append(p + T*3 + '<a href="word-prosodic-systems/index.html">My most recent book-length project</a> was a')
    L.append(p + T*3 + 'study of prosodic change in stress and lexical accent systems. This project constituted my')
    L.append(p + T*3 + 'Habilitation thesis at the LMU Munich.')
    L.append(p + T*2 + '</p>')
    L.append(p + T + '</div>')
    L.append('')
    L.append(p + '</div>')
    L.append(T + '</section>')
    return "\n".join(L)


def build_research():
    p = T * 2
    L = []
    L.append(T + '<section class="wrap page-head">')
    L.append(p + '<h1>Research</h1>')
    L.append(T + '</section>')
    L.append('')
    L.append(T + '<!-- ---------- RESEARCH AREAS ----------')
    L.append(T + '     EDIT: one <li> per research area. To add another, copy a whole')
    L.append(T + '     <li> block, change the link, image, title and description.')
    L.append(T + '     Images are decorative; alt="" keeps screen readers from')
    L.append(T + '     announcing them. Add real alt text if you swap in a meaningful')
    L.append(T + '     picture.')
    L.append(T + '     ---------------------------------------------------------- -->')
    L.append(T + '<section class="wrap section--tight">')
    L.append(p + '<ul class="cards">')
    for slug, title, desc, img in RESEARCH_CARDS:
        L.append('')
        L.append(p + T + '<li>')
        L.append(p + T*2 + '<a class="card" href="../%s/index.html">' % slug)
        L.append(p + T*3 + '<img class="card__image" src="../assets/img/%s" alt="" loading="lazy">' % img)
        L.append(p + T*3 + '<span class="card__body">')
        L.append(p + T*4 + '<span class="card__title">%s</span>' % title)
        L.append(p + T*4 + '<span class="card__text">%s</span>' % desc)
        L.append(p + T*4 + '<span class="card__more">Read more</span>')
        L.append(p + T*3 + '</span>')
        L.append(p + T*2 + '</a>')
        L.append(p + T + '</li>')
    L.append(p + '</ul>')
    L.append(T + '</section>')
    return "\n".join(L)


def build_teaching():
    p = T * 2
    L = []
    L.append(T + '<section class="wrap page-head">')
    L.append(p + '<h1>Teaching</h1>')
    L.append(p + '<!-- EDIT: the paragraph describing what you are teaching this term. -->')
    L.append(p + '<p>')
    L.append(p + T + 'In the current Winter term at the LMU M&uuml;nchen (Wintersemester 2026/-26), I&rsquo;m')
    L.append(p + T + 'offering an MA-level introduction to computational, quantitative, and corpus methods for')
    L.append(p + T + 'linguists, plus a graduate seminar Indo-European and Indo-Iranian phonology, and two')
    L.append(p + T + 'undergraduate lecture courses: an introduction to linguistics, and an introduction to')
    L.append(p + T + 'morphology.')
    L.append(p + '</p>')
    L.append(T + '</section>')
    L.append('')
    L.append(T + '<!-- ---------- COURSES ----------')
    L.append(T + '     EDIT: courses are grouped by subject, then by institution.')
    L.append(T + '     To add a course, copy one <li> line into the right list.')
    L.append(T + '     To add a whole subject, copy a complete <section class="course-group">.')
    L.append(T + '     ------------------------------------------------------------ -->')
    L.append(T + '<div class="wrap section--tight">')
    for group, institutions in TEACHING:
        L.append('')
        L.append(p + '<section class="course-group">')
        L.append(p + T + '<h2>%s</h2>' % group)
        for inst, courses in institutions:
            L.append(p + T + '<h3 class="course-institution">%s</h3>' % inst)
            L.append(p + T + '<ul class="course-list">')
            for c in courses:
                L.append(p + T*2 + '<li>%s</li>' % c)
            L.append(p + T + '</ul>')
        L.append(p + '</section>')
    L.append(T + '</div>')
    return "\n".join(L)


def build_contact():
    p = T * 2
    L = []
    L.append(T + '<section class="wrap page-head">')
    L.append(p + '<h1>Contact</h1>')
    L.append(p + '<!-- EDIT: contact details. -->')
    L.append(p + '<p>')
    L.append(p + T + 'The quickest way to reach me is by email:')
    L.append(p + T + '<a href="mailto:%s">%s</a>.' % (EMAIL, EMAIL))
    L.append(p + '</p>')
    L.append(p + '<p>You can also find me on the platforms linked in the footer below.</p>')
    L.append(T + '</section>')
    return "\n".join(L)


def build_subpage(slug, heading, lede):
    p = T * 2
    L = []
    L.append(T + '<section class="wrap page-head">')
    L.append(p + '<!-- EDIT: page heading and the one-line summary underneath it. -->')
    L.append(p + '<h1>%s</h1>' % heading)
    if lede:
        L.append(p + '<p>%s</p>' % lede)
    L.append(T + '</section>')
    L.append('')
    L.append(T + '<!-- ---------- PUBLICATIONS ----------')
    L.append(T + '     EDIT: one <li class="publication"> per item, newest first.')
    L.append(T + '     To add a publication, copy a whole <li> block and change:')
    L.append(T + '       publication__year  the year, or a word such as "Accepted"')
    L.append(T + '       publication__cite  the citation; <em>...</em> marks italics')
    L.append(T + '       publication__pdf   the file in /files, or delete the line')
    L.append(T + '                          entirely if there is nothing to link')
    L.append(T + '     ---------------------------------------------------------- -->')
    L.append(T + '<section class="wrap section--tight">')
    L.append(p + '<h2>Publications</h2>')
    L.append(p + '<ul class="publications">')
    for year, cite, pdf in PUBS[slug]:
        L.append('')
        L.append(p + T + '<li class="publication">')
        L.append(p + T*2 + '<span class="publication__year">%s</span>' % year)
        L.append(p + T*2 + '<p class="publication__cite">%s</p>' % cite)
        if pdf:
            L.append(p + T*2 + '<a class="publication__pdf" href="../files/%s">PDF</a>' % pdf)
        L.append(p + T + '</li>')
    L.append(p + '</ul>')
    L.append(T + '</section>')
    return "\n".join(L)


# ============================================================================
# RUN
# ============================================================================

def main():
    written = []
    written.append(page("", "Ryan Sandell, Linguist",
        "Ryan Sandell is a phonologist and historical linguist, currently Associate Professor (Akademischer Oberrat) at the Ludwig-Maximilians-Universit&auml;t M&uuml;nchen.",
        build_home(), "", ""))
    written.append(page("research", "Research | Ryan Sandell",
        "Research areas of Ryan Sandell: prosody, allomorphy, computational and corpus linguistics, Indo-European linguistics.",
        build_research(), "../", "research"))
    written.append(page("teaching", "Teaching | Ryan Sandell",
        "Courses taught by Ryan Sandell at LMU M&uuml;nchen and UCLA.",
        build_teaching(), "../", "teaching"))
    written.append(page("contact", "Contact | Ryan Sandell",
        "How to contact Ryan Sandell.",
        build_contact(), "../", "contact"))
    for slug, title, heading, lede, desc in SUBPAGES:
        written.append(page(slug, title, desc, build_subpage(slug, heading, lede), "../", "research"))
    for path, n in written:
        print("%6.1f KB  %s" % (n / 1024, os.path.relpath(path, REPO)))
    print("\n%d pages written" % len(written))


if __name__ == "__main__":
    main()
