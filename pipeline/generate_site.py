"""Generate the static site (HTML) from site/data/waste.json.

Run with: uv run --with pandas --with xlrd python3 pipeline/generate_site.py
(re-run build_site_data.py first if data/processed/waste.csv changed)
"""

import json
import os
import shutil

DATA_PATH = "site/data/waste.json"
OUT_DIR = "site"
LAST_YEAR_FALLBACK_DEPTH = 3  # how many years back to look for a reported value

NAV_ITEMS = [
    ("index.html", "דירוג רשויות"),
    ("national.html", "תמונת מצב ארצית"),
    ("wall-of-silence.html", "חומת השתיקה"),
    ("methodology.html", "מתודולוגיה"),
]


def shell(title: str, active: str, body: str, root_prefix: str = "", extra_head: str = "") -> str:
    nav_html = "\n".join(
        f'<a href="{root_prefix}{href}" class="{"active" if href == active else ""}">{label}</a>'
        for href, label in NAV_ITEMS
    )
    return f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="{root_prefix}style.css">
{extra_head}
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <h1><a href="{root_prefix}index.html">מדד הפסולת</a></h1>
    <nav class="site-nav">{nav_html}</nav>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    נתונים מהלשכה המרכזית לסטטיסטיקה ומ-data.gov.il ·
    <a href="{root_prefix}methodology.html">מקורות ומתודולוגיה</a>
  </div>
</footer>
</body>
</html>
"""


def latest_reported_year(authority: dict, years: list[str]) -> str | None:
    for y in reversed(years):
        if authority["years"].get(str(y), {}).get("reported"):
            return str(y)
    return None


def fmt_pct(v):
    return "—" if v is None else f"{v:.1f}%"


def fmt_num(v):
    return "—" if v is None else f"{v:,.0f}"


def build_index_page(data: dict) -> str:
    years = data["years"]
    latest_year = str(years[-1])
    body = f"""
<h2>דירוג רשויות מקומיות</h2>
<p class="lede">אחוז מיחזור, ק"ג פסולת לנפש ליום, ומגמה לעומת השנה הקודמת, לפי רשות מקומית. נתוני {latest_year} (או השנה האחרונה שדווחה).</p>
<div class="caveat">
  רשויות עם "לא דיווח/ה" לא מסרו נתונים לשנה זו — ראו <a href="wall-of-silence.html">חומת השתיקה</a>. חלק מהרשויות חסר להן נתוני אוכלוסייה מדויקים (ראו מתודולוגיה).
</div>
<div class="controls">
  <input type="search" id="search" placeholder="חיפוש רשות...">
  <select id="pop-filter">
    <option value="">כל גדלי האוכלוסייה</option>
    <option value="under_5k">עד 5,000</option>
    <option value="5k_20k">5,000&ndash;20,000</option>
    <option value="20k_50k">20,000&ndash;50,000</option>
    <option value="50k_100k">50,000&ndash;100,000</option>
    <option value="over_100k">מעל 100,000</option>
  </select>
  <span id="result-count" class="badge"></span>
</div>
<div class="card">
<div class="table-scroll">
<table class="ranked" id="ranked-table">
  <thead>
    <tr>
      <th data-key="name_he">רשות מקומית</th>
      <th data-key="population">אוכלוסייה</th>
      <th data-key="total_waste_tons">סך טונות</th>
      <th data-key="pct_recycled" class="sorted">% מיחזור</th>
      <th data-key="kg_per_capita_day">ק"ג לנפש ליום</th>
      <th data-key="trend">מגמה</th>
      <th data-key="data_year">שנת נתונים</th>
    </tr>
  </thead>
  <tbody></tbody>
</table>
</div>
</div>
<script src="vendor/chart.umd.min.js"></script>
<script src="app.js"></script>
<script src="index.js"></script>
"""
    return shell("מדד הפסולת — דירוג רשויות מקומיות", "index.html", body)


def build_authority_page(authority: dict, years: list[str]) -> str:
    name_he = authority["name_he"]
    name_en = authority["name_en"]
    ly = latest_reported_year(authority, years)
    latest = authority["years"].get(ly, {}) if ly else {}
    pop = authority["population"]

    stat_tiles = f"""
<div class="stat-row">
  <div class="stat-tile"><div class="value">{fmt_pct(latest.get('pct_recycled'))}</div><div class="label">מיחזור והשבה ({ly or '—'})</div></div>
  <div class="stat-tile"><div class="value">{fmt_num(latest.get('total_waste_tons'))}</div><div class="label">טונות פסולת ({ly or '—'})</div></div>
  <div class="stat-tile"><div class="value">{latest.get('kg_per_capita_day') if latest.get('kg_per_capita_day') is not None else '—'}</div><div class="label">ק"ג לנפש ליום</div></div>
  <div class="stat-tile"><div class="value">{fmt_num(pop)}</div><div class="label">אוכלוסייה (אמדן 2022)</div></div>
</div>
"""
    not_current = ""
    if ly and ly != str(years[-1]):
        not_current = f'<div class="caveat">הרשות לא דיווחה נתונים החל משנת {int(ly)+1} — מוצגים נתוני {ly}, הנתונים העדכניים ביותר הזמינים.</div>'
    elif not ly:
        not_current = '<div class="caveat">לרשות זו אין נתוני מיחזור מדווחים בכל השנים הזמינות (2014&ndash;2024).</div>'

    body = f"""
<a class="back-link" href="index.html">&rarr; חזרה לדירוג</a>
<h2>{name_he}</h2>
<p class="lede">{name_en}</p>
{not_current}
{stat_tiles}
<h3>מגמה רב-שנתית: אחוז מיחזור לעומת יעד 2030 וממוצע ארצי</h3>
<div class="legend">
  <span><span class="swatch" style="background:var(--series-1)"></span>{name_he}</span>
  <span><span class="swatch" style="background:var(--text-muted)"></span>ממוצע ארצי</span>
  <span><span class="swatch" style="background:var(--series-3)"></span>יעד 2030 (54%)</span>
</div>
<div class="card"><div class="chart-box"><canvas id="trend-chart"></canvas></div></div>
<h3>נתונים מלאים לפי שנה</h3>
<div class="card">
<div class="table-scroll">
<table class="ranked">
<thead><tr><th>שנה</th><th>% מיחזור</th><th>% הטמנה</th><th>טונות</th><th>ק"ג לנפש ליום</th></tr></thead>
<tbody id="authority-year-rows"></tbody>
</table>
</div>
</div>
<script src="../vendor/chart.umd.min.js"></script>
<script src="../app.js"></script>
<script>window.AUTHORITY_SLUG = {json.dumps(authority['slug'])};</script>
<script src="../authority.js"></script>
"""
    return shell(f"{name_he} — מדד הפסולת", "", body, root_prefix="../")


def build_national_page(data: dict) -> str:
    years = data["years"]
    latest_year = str(years[-1])
    n = data["national"][latest_year]
    targets = data["targets_2030"]
    body = f"""
<h2>תמונת מצב ארצית</h2>
<p class="lede">סך הכל פסולת, יחס מיחזור מול הטמנה, והפער ליעדי 2030, על בסיס השורה הרשמית של הלמ"ס (לא סכימה של נתוני הרשויות הבודדות — ראו מתודולוגיה).</p>
<div class="stat-row">
  <div class="stat-tile"><div class="value">{fmt_num(n['total_waste_tons'])}</div><div class="label">סך טונות פסולת, {latest_year}</div></div>
  <div class="stat-tile"><div class="value">{fmt_pct(n['pct_recycled'])}</div><div class="label">מיחזור והשבה</div></div>
  <div class="stat-tile"><div class="value">{fmt_pct(n['pct_landfilled'])}</div><div class="label">הטמנה</div></div>
  <div class="stat-tile"><div class="value">{targets['pct_landfilled']}%</div><div class="label">יעד הטמנה 2030</div></div>
</div>
<h3>מיחזור מול הטמנה, 2014&ndash;2024</h3>
<div class="legend">
  <span><span class="swatch" style="background:var(--series-1)"></span>מיחזור והשבה</span>
  <span><span class="swatch" style="background:var(--series-6)"></span>הטמנה</span>
</div>
<div class="card"><div class="chart-box"><canvas id="national-chart"></canvas></div></div>
<h3>הפער ליעד 2030</h3>
<p class="lede">יעד הממשלה: 20% הטמנה / 54% מיחזור עד 2030. המצב הנוכחי ({latest_year}): {fmt_pct(n['pct_landfilled'])} הטמנה, {fmt_pct(n['pct_recycled'])} מיחזור.</p>
<div class="card"><div class="chart-box chart-box-short"><canvas id="gap-chart"></canvas></div></div>

<h3>מה בעצם ממחזרים?</h3>
<p class="lede">פירוט ארצי (לא לפי רשות) של החומרים המועברים למחזור והשבה. <strong>חומר אורגני</strong> &mdash; שיירי מזון וגזם המתאימים לקומפוסטציה &mdash; הוא הרכיב הגדול ביותר, ומהווה כ-41% מכלל החומרים הממוחזרים ב-2024.</p>
<div class="caveat">פירוט זה זמין רק ברמה הארצית (מסך כל הרשויות יחד), ולא לפי רשות מקומית בודדת &mdash; הלמ"ס אינה מפרסמת פילוח חומרים ברמת הרשות.</div>
<div class="card"><div class="chart-box"><canvas id="materials-chart"></canvas></div></div>

<h3>רקע כלכלי ומדיניות: מחיר ההטמנה</h3>
<p class="lede">
היטל הטמנה הונהג בישראל ב-2007 כדי ליצור תמריץ שלילי להטמנה. עם זאת, לפי המשרד להגנת הסביבה, תעריף ההטמנה כיום (כולל ההיטל) עדיין נמוך משמעותית מהתעריף במדינות אירופה שבהן נאסרה הטמנה &mdash; מה שמותיר את ההטמנה זולה יחסית למתקני מיחזור והשבה. בשל כך, "קרן הניקיון" (הממומנת מהיטל ההטמנה) מסבסדת חלק ממתקני המיחזור וההשבה כדי לשמור על מחיר תחרותי מול הטמנה, אך לפי המשרד מנגנון זה לא יוכל להתרחב עם גידול מספר המתקנים העתידי.
</p>
<div class="caveat">אין בידינו נתוני עלות מדויקים (ש"ח לטונה) עבור הטמנה מול מיחזור ברמת רשות או ברמה ארצית &mdash; הפירוט לעיל הוא תיאור מדיניות איכותני, לא נתון מספרי. מקור: דוח מרכז המחקר והמידע של הכנסת, ינואר 2026.</div>
<script src="vendor/chart.umd.min.js"></script>
<script src="app.js"></script>
<script src="national.js"></script>
"""
    return shell("תמונת מצב ארצית — מדד הפסולת", "national.html", body)


def build_wall_of_silence_page(data: dict) -> str:
    years = data["years"]
    latest_year = str(years[-1])
    non_reporting = [
        a for a in data["authorities"] if not a["years"].get(latest_year, {}).get("reported")
    ]
    non_reporting.sort(key=lambda a: a["name_he"])
    rows = "\n".join(
        f'<tr><td class="name"><a href="authority/{a["slug"]}.html">{a["name_he"]}</a></td>'
        f'<td>{fmt_num(a["population"])}</td>'
        f'<td>{latest_reported_year(a, years) or "מעולם לא"}</td></tr>'
        for a in non_reporting
    )
    body = f"""
<h2>חומת השתיקה</h2>
<p class="lede">{len(non_reporting)} מתוך {len(data['authorities'])} רשויות מקומיות לא דיווחו נתוני פסולת ומיחזור ללמ"ס עבור {latest_year}. אי-דיווח הוא ממצא בפני עצמו.</p>
<div class="card">
<div class="table-scroll">
<table class="ranked">
<thead><tr><th>רשות מקומית</th><th>אוכלוסייה</th><th>דיווח אחרון</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</div>
</div>
"""
    return shell("חומת השתיקה — מדד הפסולת", "wall-of-silence.html", body)


def build_methodology_page(data: dict) -> str:
    generated_at = data["generated_at"][:10]
    body = f"""
<h2>מקורות ומתודולוגיה</h2>
<p class="lede">כל מספר באתר הזה מקושר למקור הרשמי שלו. עודכן לאחרונה: {generated_at}.</p>

<h3>מקורות נתונים</h3>
<dl class="methodology-source">
  <dt>פסולת לפי רשות מקומית (2014&ndash;2024)</dt>
  <dd>הלשכה המרכזית לסטטיסטיקה (למ"ס), "פסולת ביתית ומסחרית שנאספה, לפי אופן טיפול ורשות מקומית". פורסם: 4.11.2025.</dd>
  <dd><a href="https://www.cbs.gov.il/he/publications/Pages/2019/פסולת-שנאספה-ברשויות-המקומיות-2014-2017.aspx" target="_blank" rel="noopener">cbs.gov.il</a></dd>

  <dt>אוכלוסייה לפי יישוב</dt>
  <dd>למ"ס, מפקד האוכלוסין והדיור 2022, "אוכלוסייה ומשקי בית לפי יישוב".</dd>
  <dd><a href="https://data.gov.il" target="_blank" rel="noopener">data.gov.il</a> (dataset 3bd97fde-6cc3-456d-ab63-1caad16b2b6a)</dd>
</dl>

<h3>איך מחשבים כל מספר</h3>
<ul>
  <li><strong>% מיחזור</strong> — "אחוז מסך הפסולת" המועברת למחזור והשבה, כפי שמחושב ומפורסם ישירות על-ידי הלמ"ס לכל רשות.</li>
  <li><strong>% הטמנה</strong> — טונות שהועברו להטמנה חלקי סך הפסולת, כפי שמדווח בטבלת הלמ"ס.</li>
  <li><strong>ק"ג לנפש ליום</strong> — מחושב ומפורסם ישירות על-ידי הלמ"ס.</li>
  <li><strong>אוכלוסייה</strong> — עבור ערים ומועצות מקומיות: נלקחת ישירות מקובץ האוכלוסייה של הלמ"ס (מפקד 2022) לפי שם הרשות. עבור מועצות אזוריות: סוכמת מאוכלוסיית כל היישובים החברים במועצה (לפי הצלבה עם קובץ האשכולות החברתיים-כלכליים 2019).</li>
</ul>

<h3>שיעור הדיווח של הרשויות</h3>
<p class="lede">"רשות שלא דיווחה" באתר זה = רשות שהלמ"ס לא פרסמה עבורה נתון מספרי בסקר פסולת ומחזור ברשויות המקומיות לאותה שנה. בפועל, 226&ndash;253 מתוך 255&ndash;257 רשויות מדווחות נתוני פסולת כלשהם בכל שנה בין 2014 ל-2024 (18 מתוך 257 לא דיווחו ב-2024) &mdash; שיעור דיווח גבוה בהרבה ממה שנפוץ בשיח הציבורי.</p>
<div class="caveat">תיקון: טיוטה מוקדמת של מסמך הפרויקט ציטטה נתון של "כ-120&ndash;125 מתוך כ-255 רשויות מדווחות", שמקורו התברר כדוח מרכז המחקר והמידע של הכנסת <strong>מיוני 2008</strong> ("פסולת ביתית בישראל") &mdash; דוח העוסק בעמידה בדרישת דיווח רגולטורית שונה למשרד להגנת הסביבה (לא בסקר הלמ"ס שעליו מבוסס אתר זה), ומתאר מצב לפני כ-18 שנה. שני הנתונים נכונים כל אחד להקשרו, אך אינם ניתנים להשוואה ישירה. פירוט מלא ב-<code>data/CONFLICTS.md</code> במאגר הקוד.</div>

<h3>מגבלות ידועות</h3>
<div class="caveat"><strong>סך הפסולת הארצי.</strong> סכימה של נתוני כל הרשויות הבודדות נמוכה בכ-7&ndash;8% מהשורה הרשמית שמפרסמת הלמ"ס עצמה, מכיוון שהלמ"ס כוללת בסך הארצי הערכה לרשויות שאינן מדווחות בנפרד. לכן עמוד "תמונת מצב ארצית" משתמש בשורת הסך הרשמית של הלמ"ס, ולא בסכימה של נתוני הרשויות.</div>
<div class="caveat"><strong>מחוז.</strong> טרם נמצא מקור נתונים למיפוי רשות&larr;מחוז. שדה זה חסר כרגע באתר (אין סינון לפי מחוז ב-v1).</div>
<div class="caveat"><strong>אשכול חברתי-כלכלי.</strong> מקור הנתונים היחיד שנמצא מכסה רק יישובים בתוך מועצות אזוריות (995 יישובים, 54 מועצות) &mdash; ללא כיסוי לערים ומועצות מקומיות, שהן רוב הרשויות המוצגות באתר. לכן שדה זה אינו מוצג כלל ב-v1, כדי לא להציג נתון חלקי ומטעה.</div>
<div class="caveat"><strong>שתי רשויות ללא נתוני אוכלוסייה</strong>: שדות דן ושער שומרון &mdash; לא נמצאו באף אחד ממקורות האוכלוסייה שנבדקו.</div>
<div class="caveat"><strong>מיחזור מול השבה אחרת</strong>: טבלת הלמ"ס משלבת "מיחזור" ו"השבה אחרת" (כגון השבת אנרגיה) למדד אחד. לא ניתן להפריד ביניהם עם המקור הנוכחי.</div>

<h3>עדכון הנתונים</h3>
<p>עודכן לאחרונה: {generated_at}. הנתונים אינם מתעדכנים אוטומטית &mdash; עדכון עתידי ידרוש הרצה חוזרת של תהליך העיבוד כאשר הלמ"ס מפרסמת נתונים חדשים.</p>
"""
    return shell("מתודולוגיה — מדד הפסולת", "methodology.html", body)


def main():
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs(f"{OUT_DIR}/authority", exist_ok=True)

    with open(f"{OUT_DIR}/index.html", "w", encoding="utf-8") as f:
        f.write(build_index_page(data))
    with open(f"{OUT_DIR}/national.html", "w", encoding="utf-8") as f:
        f.write(build_national_page(data))
    with open(f"{OUT_DIR}/wall-of-silence.html", "w", encoding="utf-8") as f:
        f.write(build_wall_of_silence_page(data))
    with open(f"{OUT_DIR}/methodology.html", "w", encoding="utf-8") as f:
        f.write(build_methodology_page(data))

    for authority in data["authorities"]:
        path = f"{OUT_DIR}/authority/{authority['slug']}.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(build_authority_page(authority, data["years"]))

    print(f"generated index/national/wall-of-silence/methodology + {len(data['authorities'])} authority pages")


if __name__ == "__main__":
    main()
