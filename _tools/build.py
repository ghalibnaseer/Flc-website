"""Assemble the FLC & Associates LLP website from page bodies and shared parts.

Usage: python3 build.py <portfolio_dir> <out_dir>
"""
import re
import sys

from pathlib import Path

PORTFOLIO = Path(sys.argv[1])
OUT = Path(sys.argv[2])

SITE = "https://flcassociates.com"
MEMBERS_URL = "https://caselawdatabase.flcassociates.com/"
EMAIL = "info@flcassociates.com"
UPDATED_ISO = "2026-11-13"
UPDATED = "13 November 2026"

OFFICES = [
    ("Head Office, Multan", "Ali Street, New North Gulgasht Colony, Multan"),
    ("Multan Courts", "4-Bashir Khan Block, District and Sessions Courts, Multan"),
    ("Lahore", "3rd Floor, Al-Ghaffar Law Building, 7-Turner Road, Lahore"),
    ("Rawalpindi", "Hamza Plaza, Awan Market, Rawalpindi"),
]

NAV = [
    ("./", "The Firm"),
    ("practice.html", "Practice"),
    ("team.html", "Team"),
    ("contact.html", "Contact"),
]


def head(title, description, path):
    full_title = "FLC &amp; Associates LLP" if path == "index.html" else f"{title} | FLC &amp; Associates LLP"
    canonical = f"{SITE}/" if path == "index.html" else f"{SITE}/{path}"
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{full_title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="FLC &amp; Associates LLP">
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<link rel="icon" type="image/png" href="favicon.png">
<link rel="apple-touch-icon" href="img/apple-touch-icon.png">
<link rel="preload" href="fonts/libre-caslon-display-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/libre-caslon-text-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="site.css">
"""


def topbar(current):
    links = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == current or (href == "./" and current == "index.html") else ""
        links.append(f'      <a href="{href}"{cur}>{label}</a>')
    links.append(f'      <a class="members" href="{MEMBERS_URL}" target="_blank" rel="nofollow noopener" title="Case Law Database (members only, opens in a new tab)"><span class="m-hide">Case Law </span>Database</a>')
    nav = "\n".join(links)
    return f"""<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <div class="wrap">
    <a class="brand" href="./"><img src="img/emblem-480.png" width="480" height="410" alt=""><span>FLC &amp; Associates LLP</span></a>
    <nav class="nav" aria-label="Site">
{nav}
    </nav>
  </div>
</header>
"""


def offices_list():
    items = "\n".join(
        f'        <li><p class="where">{w}</p><address>{a}</address></li>' for w, a in OFFICES
    )
    return f'      <ul class="offices">\n{items}\n      </ul>'


def contact_band(note="For enquiries about instructing the firm, write to us or use the contact form."):
    return f"""<section class="contact" id="contact" aria-labelledby="contact-h">
  <div class="wrap">
    <h2 id="contact-h">Contact</h2>
    <div>
      <p class="note">{note}</p>
      <dl>
        <div><dt>Email</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
        <div><dt>Telephone</dt><dd><a href="tel:+923071114701">+92 307 1114701</a></dd></div>
        <div><dt>Head Office</dt><dd>{OFFICES[0][1]}</dd></div>
      </dl>
      <div class="actions">
        <a class="btn btn-solid" href="contact.html#form">Send an enquiry</a>
        <a class="btn" href="mailto:{EMAIL}">Write an email</a>
      </div>
    </div>
  </div>
</section>
"""


def footer():
    year = UPDATED_ISO[:4]
    return f"""<footer class="site">
  <div class="wrap">
    <span>© {year} FLC &amp; Associates LLP. All rights reserved.</span>
    <nav aria-label="Legal">
      <a href="legal-notice.html">Legal notice</a>
      <a href="privacy.html">Privacy notice</a>
      <a href="{MEMBERS_URL}" target="_blank" rel="nofollow noopener">Case Law Database (members)</a>
    </nav>
  </div>
</footer>
"""


def page(path, title, description, body, extra_head="", scripts="", with_contact=True):
    if path == "404.html":
        extra_head = '<base href="/">\n<meta name="robots" content="noindex">\n' + extra_head
    html = head(title, description, path) + extra_head + "</head>\n" + topbar(path)
    html += '<main id="main">\n' + body + "\n</main>\n"
    if with_contact:
        html += contact_band()
    html += footer() + scripts + "</body>\n</html>\n"
    (OUT / path).write_text(html, encoding="utf-8")


# ---------------------------------------------------------------- Home
ORG_JSONLD = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LegalService",
  "@id": "https://flcassociates.com/#firm",
  "name": "FLC & Associates LLP",
  "url": "https://flcassociates.com/",
  "logo": "https://flcassociates.com/img/emblem-480.png",
  "email": "info@flcassociates.com",
  "telephone": "+92-307-1114701",
  "foundingDate": "1996",
  "areaServed": "Pakistan",
  "address": [
    { "@type": "PostalAddress", "streetAddress": "Ali Street, New North Gulgasht Colony", "addressLocality": "Multan", "addressCountry": "PK" },
    { "@type": "PostalAddress", "streetAddress": "4-Bashir Khan Block, District and Sessions Courts", "addressLocality": "Multan", "addressCountry": "PK" },
    { "@type": "PostalAddress", "streetAddress": "3rd Floor, Al-Ghaffar Law Building, 7-Turner Road", "addressLocality": "Lahore", "addressCountry": "PK" },
    { "@type": "PostalAddress", "streetAddress": "Hamza Plaza, Awan Market", "addressLocality": "Rawalpindi", "addressCountry": "PK" }
  ]
}
</script>
"""

home = f"""<section class="firm-hero" aria-label="Introduction">
  <div class="wrap">
    <div>
      <p class="eyebrow">Barristers, Lawyers &amp; Consultants</p>
      <h1>FLC &amp; Associates LLP</h1>
      <p class="lede">A law firm practising across Pakistan since 1996, with offices in Multan, Lahore and Rawalpindi.</p>
      <div class="facts">
        <p><b>1996</b>Established</p>
        <p><b>4</b>Offices in three cities</p>
        <p><b>LLP</b>Registered with the SECP</p>
      </div>
      <div class="actions">
        <a class="btn btn-solid" href="practice.html">Practice areas</a>
        <a class="btn" href="contact.html">Contact the firm</a>
      </div>
    </div>
    <img class="emblem" src="img/emblem-480.png" width="480" height="410" alt="FLC &amp; Associates LLP emblem: the figure of Justice within a laurel wreath">
  </div>
</section>

<section class="section" id="firm" aria-labelledby="firm-h">
  <div class="wrap">
    <h2 id="firm-h">The Firm</h2>
    <div class="prose">
      <p class="lead">FLC &amp; Associates LLP was established in 1996 and is a limited liability partnership registered with the Securities and Exchange Commission of Pakistan.</p>
      <p>The firm practises in all areas of law, with particular depth in criminal, corporate, family, civil and constitutional matters. It advises clients, conducts litigation before courts and tribunals throughout Pakistan, acts as in-house counsel for businesses and organisations, and has a dedicated mediation team.</p>
      <p>The firm appears before every judicial forum in the country, from the District and Sessions Courts to the High Courts, the Federal Constitutional Court and the Supreme Court of Pakistan.</p>
      <div class="more"><a href="practice.html">Practice and services</a><a href="team.html">The team</a></div>
    </div>
  </div>
</section>

<section class="section" id="specialisms" aria-labelledby="spec-h">
  <div class="wrap">
    <h2 id="spec-h">Specialisms</h2>
    <div>
      <ul class="practice">
        <li><h3>Criminal Law</h3><p>Bail, trial, appeals and revisions, from the trial court to the Supreme Court.</p></li>
        <li><h3>Corporate</h3><p>Company and LLP incorporation, corporate compliance, commercial contracts and corporate disputes.</p></li>
        <li><h3>Family Law</h3><p>Dissolution of marriage, dower and maintenance, custody and guardianship.</p></li>
        <li><h3>Civil Law</h3><p>Civil suits, property and rent matters, injunctions and the execution of decrees.</p></li>
        <li><h3>Constitutional Matters</h3><p>Constitutional petitions for the enforcement of fundamental rights and the review of public action.</p></li>
        <li><h3>All other areas</h3><p>The firm accepts instructions across the full range of practice areas.</p></li>
      </ul>
      <div class="more"><a href="practice.html">More on each practice area</a></div>
    </div>
  </div>
</section>

<section class="section band" aria-labelledby="conf-h">
  <div class="wrap">
    <h2 id="conf-h">Confidentiality</h2>
    <div>
      <blockquote><p>The firm treats every client matter as confidential. For that reason this website does not describe past cases or name clients.</p></blockquote>
    </div>
  </div>
</section>

<section class="section" id="offices" aria-labelledby="offices-h">
  <div class="wrap">
    <h2 id="offices-h">Offices</h2>
    <div>
{offices_list()}
    </div>
  </div>
</section>
"""
page("index.html", "The Firm",
     "FLC &amp; Associates LLP is a law firm established in 1996 with offices in Multan, Lahore and Rawalpindi, practising in criminal, corporate, family, civil and constitutional law before every court in Pakistan.",
     home, extra_head=ORG_JSONLD)

# ---------------------------------------------------------------- Practice
practice = """<section class="page-head" aria-labelledby="ph">
  <div class="wrap">
    <p class="eyebrow">Practice</p>
    <h1 id="ph">Practice areas and services</h1>
    <p class="sub">The firm accepts instructions in all areas of law. Its specialist practice covers five fields.</p>
  </div>
</section>

<section class="section" id="areas" aria-labelledby="areas-h">
  <div class="wrap">
    <h2 id="areas-h">Specialisms</h2>
    <div>
      <ul class="practice">
        <li><h3>Criminal Law</h3><p>Pre-arrest and post-arrest bail, trials, appeals and revisions, quashment proceedings and private complaints, for complainants and for accused persons, at every stage from the trial court to the Supreme Court of Pakistan.</p></li>
        <li><h3>Corporate</h3><p>Incorporation of companies and limited liability partnerships, corporate and regulatory compliance and filings with the Securities and Exchange Commission of Pakistan, drafting and review of commercial contracts, and corporate and commercial disputes.</p></li>
        <li><h3>Family Law</h3><p>Dissolution of marriage, dower and maintenance, recovery of dowry articles, and custody and guardianship of minors, before the Family Courts and in appeal and constitutional proceedings.</p></li>
        <li><h3>Civil Law</h3><p>Suits for declaration, possession, specific performance and recovery, property and rent matters, temporary and permanent injunctions, and the execution of decrees.</p></li>
        <li><h3>Constitutional Matters</h3><p>Constitutional petitions for the enforcement of fundamental rights and against unlawful action by public bodies, and related appeals, before the High Courts and the Federal Constitutional Court.</p></li>
        <li><h3>All other areas</h3><p>Matters outside the specialist fields, including tax, service and banking matters, are handled by the firm or with counsel it instructs.</p></li>
      </ul>
    </div>
  </div>
</section>

<section class="section" id="services" aria-labelledby="services-h">
  <div class="wrap">
    <h2 id="services-h">Services</h2>
    <div>
      <ul class="practice">
        <li><h3>Advisory</h3><p>Written opinions and advice on rights, liabilities and options, before a dispute arises or while one is under way.</p></li>
        <li><h3>Litigation</h3><p>Drafting, filing and arguing cases before courts and tribunals at every level, including appeals and constitutional proceedings.</p></li>
        <li><h3>In-house Counsel</h3><p>Retained legal support for businesses and organisations, covering contracts, compliance and day-to-day legal questions.</p></li>
        <li><h3>Mediation</h3><p>A dedicated mediation team that assists parties to resolve disputes by agreement.</p></li>
      </ul>
    </div>
  </div>
</section>

<section class="section" id="forums" aria-labelledby="forums-h">
  <div class="wrap">
    <h2 id="forums-h">Courts and Forums</h2>
    <div>
      <p class="intro">The firm appears before every judicial forum in Pakistan, including:</p>
      <ul class="forums">
        <li>Federal Constitutional Court of Pakistan</li>
        <li>Supreme Court of Pakistan</li>
        <li>All High Courts</li>
        <li>District and Sessions Courts</li>
        <li>Rent Tribunals</li>
        <li>Tax Tribunals</li>
        <li>Service Tribunals</li>
        <li>Other courts, tribunals and judicial forums</li>
      </ul>
    </div>
  </div>
</section>
"""
page("practice.html", "Practice",
     "Practice areas and services of FLC &amp; Associates LLP: criminal, corporate, family, civil and constitutional law; advisory, litigation, in-house counsel and mediation; before every court and tribunal in Pakistan.",
     practice)

# ---------------------------------------------------------------- Team
sys.path.insert(0, str(Path(__file__).resolve().parent))
from names import NAMES, ASC, AHC, ADV

# Former offices are shown in narrative form only. Rule 174-A of the Pakistan Legal
# Practitioners and Bar Councils Rules, 1976 restricts the use of ex-designations:
# set to False to remove every former office from the site in one step.
SHOW_FORMER_OFFICES = True
# A former judicial office is held back until the partners decide (Rule 174-A names "Ex Judge").
SHOW_FORMER_JUDICIAL_OFFICE = False

def person(role, name, enrolment, bio="", photo=None, more=None):
    words = [w for w in re.sub(r"[^A-Za-z ]", "", name).split() if w[0].isupper()]
    initials = words[0][0] + words[-1][0]
    if photo:
        img = (f'<picture><source srcset="{photo}.webp" type="image/webp">'
               f'<img src="{photo}.png" width="600" height="626" alt="Portrait of {name}" loading="lazy"></picture>')
    else:
        img = f'<span class="ring" aria-hidden="true"><span class="initials">{initials}</span></span>'
    btn = f'\n          <a class="btn" href="{more}">For more information</a>' if more else ""
    bio_html = f'\n          <p class="bio">{bio}</p>' if bio else ""
    return f"""        <li class="person">
          <div class="photo">{img}</div>
          <p class="role">{role}</p>
          <h3>{name}</h3>
          <p class="quals">{enrolment}</p>{bio_html}{btn}
        </li>"""

nat_bio = "Founded the firm in 1996. His practice is in criminal trials and litigation before the District and Sessions Courts, the High Courts and the Supreme Court of Pakistan, and he has conducted more than 10,000 cases."
if SHOW_FORMER_OFFICES:
    nat_bio += " He has served as President of the High Court Bar Association Multan."
mzs_bio = ""
if SHOW_FORMER_OFFICES:
    offices = ["Deputy Attorney General for Pakistan"]
    if SHOW_FORMER_JUDICIAL_OFFICE:
        offices.append("Chairman of the Drug Court")
    offices += ["Senior Vice-President of the High Court Bar Association Multan",
                "Vice-President of the District Bar Association Multan"]
    mzs_bio = "He has served as " + ", ".join(offices[:-1]) + " and " + offices[-1] + "."

partners = "\n".join([
    person("Managing Partner", "Naseer Ahmad Thaheem", "Advocate Supreme Court of Pakistan", nat_bio, photo="img/team/naseer-ahmad-thaheem"),
    person("Senior Partner", "Mehr Zamir Hussain Sandhal", "Advocate Supreme Court of Pakistan", mzs_bio),
    person("Partner", "Ghalib Naseer", "Advocate",
           "LLB (Hons), University of London. Barrister under training at the Honourable Society of the Middle Temple. Practises in criminal, family and corporate matters.",
           photo="img/team/ghalib-naseer", more="ghalib-naseer.html"),
])
associates = "\n".join([
    person("Senior Associate, Civil Litigation", "Shoaib Ashraf", "Advocate High Court",
           "More than ten years of legal experience.", photo="img/team/shoaib-ashraf"),
    person("Senior Associate, Criminal Litigation", "Shafqat Raza Thaheem", "Advocate High Court",
           "More than ten years of experience in litigation before the District Courts and the High Court.", photo="img/team/shafqat-raza-thaheem"),
    person("Senior Associate, Tax and Corporate Compliance", "Naveed Sikander Bhatti", "Advocate High Court",
           "Leads the firm\u2019s tax and corporate compliance work.", photo="img/team/naveed-sikander-bhatti"),
])
profiled = {"Naseer Ahmad Thaheem", "Mehr Zamir Hussain Sandhal", "Malik Shafqat Raza Thaheem",
            "Chaudhry Muhammad Shoaib Ashraf Arain", "Naveed Sikander Bhatti"}
asc = [e for u, e, d, n in NAMES if d == ASC and e not in profiled]
ahc = [e for u, e, d, n in NAMES if d == AHC and e not in profiled]
adv = [e for u, e, d, n in NAMES if d == ADV and e not in profiled]
def namelist(items):
    return "\n".join(f"        <li>{x}</li>" for x in items)

team = f"""<section class="page-head" aria-labelledby="th">
  <div class="wrap">
    <p class="eyebrow">Team</p>
    <h1 id="th">The team</h1>
    <p class="sub">The partners, senior associates and advocates of FLC &amp; Associates LLP.</p>
  </div>
</section>

<section class="section first" id="partners" aria-labelledby="partners-h">
  <div class="wrap">
    <h2 id="partners-h">Partners</h2>
    <ul class="team">
{partners}
    </ul>
  </div>
</section>

<section class="section" id="associates" aria-labelledby="assoc-h">
  <div class="wrap">
    <h2 id="assoc-h">Senior Associates</h2>
    <ul class="team">
{associates}
    </ul>
  </div>
</section>

<section class="section" id="advocates" aria-labelledby="adv-h">
  <div class="wrap">
    <h2 id="adv-h">Advocates</h2>
    <div>
      <h3 class="list-head">Advocates Supreme Court</h3>
      <ul class="names">
{namelist(asc)}
      </ul>
      <h3 class="list-head">Advocates High Court</h3>
      <ul class="names">
{namelist(ahc)}
      </ul>
      <h3 class="list-head">Advocates</h3>
      <ul class="names">
{namelist(adv)}
      </ul>
    </div>
  </div>
</section>
"""
page("team.html", "Team", "The partners, senior associates and advocates of FLC &amp; Associates LLP.", team)

# ---------------------------------------------------------------- Contact
contact = f"""<section class="page-head" aria-labelledby="ch">
  <div class="wrap">
    <p class="eyebrow">Contact</p>
    <h1 id="ch">Contact the firm</h1>
    <p class="sub">Write to <a href="mailto:{EMAIL}">{EMAIL}</a>, visit one of the offices, or use the form below.</p>
  </div>
</section>

<section class="section first" id="form" aria-labelledby="form-h">
  <div class="wrap">
    <h2 id="form-h">Enquiry</h2>
    <div>
      <p class="form-warning">Please do not send confidential or sensitive details of your matter through this form. Sending a message does not create an advocate and client relationship with the firm. See the <a href="privacy.html">privacy notice</a> for how your details are used.</p>
      <form class="form" id="enquiry" action="#" method="post" novalidate>
        <div><label for="f-name">Name</label><input id="f-name" name="name" type="text" autocomplete="name" required maxlength="120"></div>
        <div><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" required maxlength="160"></div>
        <div><label for="f-phone">Telephone <span style="font-weight:400">(optional)</span></label><input id="f-phone" name="phone" type="tel" autocomplete="tel" maxlength="40"></div>
        <div><label for="f-area">Area of law</label>
          <select id="f-area" name="area">
            <option>Criminal Law</option><option>Corporate</option><option>Family Law</option>
            <option>Civil Law</option><option>Constitutional Matters</option><option>Mediation</option>
            <option>In-house counsel</option><option>Other</option>
          </select></div>
        <div class="full"><label for="f-msg">Message</label><textarea id="f-msg" name="message" required maxlength="3000" placeholder="A short description of what you need help with"></textarea></div>
        <div class="hp" aria-hidden="true"><label for="f-web">Leave this field empty</label><input id="f-web" name="website" type="text" tabindex="-1" autocomplete="off"></div>
        <div class="full"><label class="check"><input type="checkbox" name="consent" required> I have read the privacy notice and agree that the firm may use these details to reply to my enquiry.</label></div>
        <div class="full"><button class="btn btn-solid" type="submit">Send enquiry</button></div>
        <p class="form-status" id="form-status" role="status" aria-live="polite"></p>
      </form>
    </div>
  </div>
</section>

<section class="section" id="offices" aria-labelledby="offices-h">
  <div class="wrap">
    <h2 id="offices-h">Offices</h2>
    <div>
{offices_list()}
    </div>
  </div>
</section>
"""
FORM_JS = """<script>
/* Contact form. FORM_ENDPOINT is the Google Apps Script web app URL; until it is set,
   the form opens the visitor's email program with the message filled in. */
(function () {
  var FORM_ENDPOINT = "";
  var form = document.getElementById("enquiry");
  var status = document.getElementById("form-status");
  if (!form) return;
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (form.website.value) return;
    if (!form.checkValidity()) { status.textContent = "Please complete the name, email and message fields and tick the box."; form.reportValidity(); return; }
    var data = { name: form.name.value, email: form.email.value, phone: form.phone.value, area: form.area.value, message: form.message.value };
    if (!FORM_ENDPOINT) {
      var body = "Name: " + data.name + "\\nEmail: " + data.email + "\\nTelephone: " + data.phone + "\\nArea: " + data.area + "\\n\\n" + data.message;
      window.location.href = "mailto:info@flcassociates.com?subject=" + encodeURIComponent("Enquiry: " + data.area) + "&body=" + encodeURIComponent(body);
      return;
    }
    status.textContent = "Sending\\u2026";
    fetch(FORM_ENDPOINT, { method: "POST", mode: "no-cors", headers: { "Content-Type": "text/plain;charset=utf-8" }, body: JSON.stringify(data) })
      .then(function () { form.reset(); status.textContent = "Thank you. Your enquiry has been sent and the firm will reply by email."; })
      .catch(function () { status.textContent = "The message could not be sent. Please email info@flcassociates.com."; });
  });
})();
</script>
"""
page("contact.html", "Contact", "Contact FLC &amp; Associates LLP: offices in Multan, Lahore and Rawalpindi; email info@flcassociates.com.",
     contact, scripts=FORM_JS, with_contact=False)

# ---------------------------------------------------------------- Legal notice
legal = f"""<section class="page-head" aria-labelledby="lh">
  <div class="wrap">
    <p class="eyebrow">Legal</p>
    <h1 id="lh">Legal notice</h1>
  </div>
</section>
<section class="section first single" aria-labelledby="l-h">
  <div class="wrap">
    <h2 id="l-h" class="sr-only">Terms</h2>
    <div class="legal">
      <h3 style="margin-top:0">Copyright</h3>
      <p>All content on this website, including its text, design, logo, emblem, photographs and the arrangement of its material, is the property of FLC &amp; Associates LLP or is used with permission. All rights are reserved.</p>
      <p>No part of this website may be copied, reproduced, republished, distributed, adapted or stored in any form or by any means without the prior written permission of FLC &amp; Associates LLP. Requests for permission should be sent to <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
      <h3>Purpose of this website</h3>
      <p>This website provides information about FLC &amp; Associates LLP, its practice and its team. It is not intended to solicit professional work or to advertise the services of any advocate.</p>
      <h3>No legal advice</h3>
      <p>Nothing on this website is legal advice. You should not act, or refrain from acting, on the basis of anything on this website without taking advice on your particular circumstances.</p>
      <h3>No advocate and client relationship</h3>
      <p>Visiting this website, or contacting the firm through it, does not create an advocate and client relationship. That relationship begins only when the firm confirms in writing that it has accepted your instructions.</p>
      <h3>Case Law Database</h3>
      <p>The firm\u2019s case law database is restricted to persons authorised by the firm. Any attempt to obtain access without authorisation is prohibited.</p>
      <h3>Links</h3>
      <p>Links to other websites are provided for convenience. The firm is not responsible for the content of those websites.</p>
      <p class="note-small">Last updated <time datetime="{UPDATED_ISO}">{UPDATED}</time>.</p>
    </div>
  </div>
</section>
"""
page("legal-notice.html", "Legal notice", "Legal notice, copyright and terms of use for the FLC &amp; Associates LLP website.", legal, with_contact=False)

# ---------------------------------------------------------------- Privacy
privacy = f"""<section class="page-head" aria-labelledby="prh">
  <div class="wrap">
    <p class="eyebrow">Legal</p>
    <h1 id="prh">Privacy notice</h1>
  </div>
</section>
<section class="section first single" aria-labelledby="p-h">
  <div class="wrap">
    <h2 id="p-h" class="sr-only">Privacy</h2>
    <div class="legal">
      <h3 style="margin-top:0">Who we are</h3>
      <p>This website is operated by FLC &amp; Associates LLP, Ali Street, New North Gulgasht Colony, Multan. Questions about this notice may be sent to <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
      <h3>What we collect</h3>
      <p>If you use the enquiry form, we receive the name, email address, telephone number (if given), area of law and message that you enter. If you email us, we receive your email and its contents.</p>
      <p>This website does not use cookies, advertising or visitor tracking. The company that hosts the website may record technical information such as IP addresses in its server logs for security purposes.</p>
      <h3>How we use it</h3>
      <ul>
        <li>to reply to your enquiry and to consider whether the firm can act for you;</li>
        <li>to check for conflicts of interest before accepting instructions; and</li>
        <li>to keep a record of enquiries received.</li>
      </ul>
      <p>We do not sell your details or use them for marketing.</p>
      <h3>Where it is kept and who sees it</h3>
      <p>Enquiries are delivered to the firm’s email account and kept in the firm’s own records. They are seen only by partners and staff of the firm who need them to deal with your enquiry.</p>
      <h3>How long we keep it</h3>
      <p>If the firm does not act for you, your enquiry is deleted one week after it is received. If the firm does act for you, it becomes part of the client file and is kept with the firm\u2019s records of the matter.</p>
      <h3>Your choices</h3>
      <p>You may ask to see the details we hold about you, or ask us to correct or delete them, by writing to <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
      <p class="note-small">Last updated <time datetime="{UPDATED_ISO}">{UPDATED}</time>.</p>
    </div>
  </div>
</section>
"""
page("privacy.html", "Privacy notice", "How FLC &amp; Associates LLP uses details sent through its website.", privacy, with_contact=False)

# ---------------------------------------------------------------- Ghalib Naseer profile (from the portfolio)
def section_block(file, sid):
    s = (PORTFOLIO / file).read_text(encoding="utf-8")
    m = re.search(rf'  <section class="section[^"]*" id="{sid}".*?\n  </section>', s, flags=re.S)
    if not m:
        raise SystemExit(f"section {sid} not found in {file}")
    block = m.group(0).replace('class="section first"', 'class="section"')
    # internal links in the portfolio point to its own pages; repoint to anchors here
    block = (block.replace('href="career.html#', 'href="#').replace('href="career.html"', 'href="#appointments"')
                  .replace('href="publications.html"', 'href="#publications"')
                  .replace('href="commentary.html"', 'href="#commentary"')
                  .replace('href="index.html#contact"', 'href="#contact"'))
    block = re.sub(r"<h1([^>]*)>(.*?)</h1>", r"<h2\1>\2</h2>", block)
    return block

blocks = [section_block("index.html", "profile")]
for f, sid in [("career.html", "appointments"), ("career.html", "advocacy"), ("career.html", "recognition"),
               ("publications.html", "publications"), ("commentary.html", "commentary")]:
    blocks.append(section_block(f, sid))

profile_hero = """<p class="crumb wrap"><a href="team.html">Team</a> / Ghalib Naseer</p>
<section class="hero" id="top" aria-label="Introduction">
  <div class="wrap">
    <div>
      <h1>Ghalib Naseer</h1>
      <p class="fullname">Malik Ghalib Naseer Thaheem</p>
      <p class="calling">Lawyer and legal scholar working on constitutionalism, international law, jurisprudence and legal theory. Barrister under training at the Middle Temple.</p>
      <div class="firm">
        <img src="img/emblem-480.png" width="480" height="410" alt="">
        <div>
          <p class="firm-role">Partner, FLC &amp; Associates LLP</p>
          <p class="firm-place">Multan, Lahore and Rawalpindi</p>
        </div>
      </div>
      <ul class="also" aria-label="Other current positions">
        <li><b>Regional Partner</b>, HS Legal LLP, Islamabad</li>
        <li><b>Visiting Faculty</b>, The Millennium Universal College (TMUC), Multan</li>
      </ul>
      <nav class="jump" aria-label="On this page">
        <a href="#profile">Profile</a><a href="#appointments">Career</a><a href="#advocacy">Advocacy</a>
        <a href="#recognition">Recognition</a><a href="#publications">Publications</a><a href="#commentary">Commentary</a>
      </nav>
    </div>
    <div class="hero-portrait">
      <picture>
        <source srcset="img/portrait.webp" type="image/webp">
        <img class="portrait" src="img/portrait.png" width="800" height="834" alt="Portrait of Ghalib Naseer in a dark suit, framed by a brass ring" decoding="async">
      </picture>
    </div>
  </div>
</section>
"""
profiles_dl = """<section class="section" id="elsewhere" aria-labelledby="else-h">
  <div class="wrap">
    <h2 id="else-h">Elsewhere</h2>
    <div>
      <ul class="forums">
        <li><a href="https://ghalibnaseer.github.io/">Personal website</a></li>
        <li><a href="https://www.linkedin.com/in/ghalib-naseer-thaheem-2202a82a6/">LinkedIn</a></li>
        <li><a href="https://orcid.org/0009-0005-2123-7191">ORCID 0009-0005-2123-7191</a></li>
        <li><a href="https://www.wikidata.org/wiki/Q141632011">Wikidata Q141632011</a></li>
        <li><a href="https://www.thefridaytimes.com/contributor/ghalib-naseer">The Friday Times contributor page</a></li>
        <li><a href="https://zenodo.org/search?q=%22Ghalib%20Naseer%22">Zenodo</a></li>
      </ul>
    </div>
  </div>
</section>
"""
body = profile_hero + "\n".join(blocks) + "\n" + profiles_dl
page("ghalib-naseer.html", "Ghalib Naseer",
     "Ghalib Naseer, Partner at FLC &amp; Associates LLP: profile, career, advocacy, publications and commentary.",
     body)

# ---------------------------------------------------------------- robots, sitemap, 404, CNAME
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
urls = ["", "practice.html", "team.html", "ghalib-naseer.html", "contact.html", "legal-notice.html", "privacy.html"]
(OUT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{SITE}/{u}</loc><lastmod>{UPDATED_ISO}</lastmod></url>\n" for u in urls)
    + "</urlset>\n")
page("404.html", "Page not found", "Page not found.",
     """<section class="page-head"><div class="wrap"><p class="eyebrow">404</p><h1>Page not found</h1>
<p class="sub">The page you asked for does not exist. <a href="./">Return to the home page</a>.</p></div></section>""",
     with_contact=False)
(OUT / "CNAME").write_text("flcassociates.com\n")
print("built", sorted(x.name for x in OUT.glob("*.html")))
