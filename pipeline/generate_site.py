"""Generate the static site (HTML) from site/data/waste.json.

Run with: uv run --with pandas --with xlrd python3 pipeline/generate_site.py
(re-run build_site_data.py first if data/processed/waste.csv changed)
"""

import hashlib
import json
import os
import shutil

DATA_PATH = "site/data/waste.json"
OUT_DIR = "site"
LAST_YEAR_FALLBACK_DEPTH = 3  # how many years back to look for a reported value

def _compute_asset_version() -> str:
    h = hashlib.sha256()
    for name in sorted(os.listdir(OUT_DIR)):
        if name.endswith((".css", ".js")):
            with open(f"{OUT_DIR}/{name}", "rb") as f:
                h.update(f.read())
    return h.hexdigest()[:8]


ASSET_VERSION = _compute_asset_version()

NAV_ITEMS_HE = [
    ("index.html", "בית"),
    ("ranking.html", "דירוג רשויות"),
    ("national.html", "תמונת מצב ארצית"),
    ("wall-of-silence.html", "חומת השתיקה"),
    ("glossary.html", "מילון מונחים"),
    ("methodology.html", "מתודולוגיה"),
]

NAV_ITEMS_EN = [
    ("index.html", "Home"),
    ("ranking.html", "Rankings"),
    ("national.html", "National Overview"),
    ("wall-of-silence.html", "Wall of Silence"),
    ("glossary.html", "Glossary"),
    ("methodology.html", "Methodology"),
]

STRINGS = {
    "he": {
        "site_title": "מדד הפסולת",
        "lang_toggle": "English",
        "footer_source": 'נתונים מהלשכה המרכזית לסטטיסטיקה ומ-data.gov.il',
        "footer_methodology": "מקורות ומתודולוגיה",
        "hero_title": "מדד הפסולת",
        "hero_lede": "רואים כל רשות מקומית בישראל: כמה פסולת היא מייצרת, כמה ממוחזר וכמה מוטמן, ואיך זה מול יעדי 2030 של הממשלה. כל מספר מקושר למקור הרשמי שלו.",
        "stat_recycled_national": "מיחזור והשבה ארצי, {year}",
        "stat_landfilled_national": "הטמנה ארצית",
        "stat_target_2030": "יעד מיחזור 2030",
        "stat_non_reporting": "רשויות שלא דיווחו ({year})",
        "card_ranking_title": "דירוג רשויות",
        "card_ranking_desc": "טבלה מלאה, ניתנת למיון וסינון, של כל הרשויות המקומיות",
        "card_national_title": "תמונת מצב ארצית",
        "card_national_desc": "מגמות ארציות, פילוח חומרים, והפער ליעדי 2030",
        "card_silence_title": "חומת השתיקה",
        "card_silence_desc": "הרשויות שלא מדווחות נתוני פסולת בכלל",
        "card_glossary_title": "מילון מונחים",
        "card_glossary_desc": "שיטות הטיפול בפסולת, ההשפעה הסביבתית, והשוואה לעולם",
        "card_methodology_title": "מתודולוגיה",
        "card_methodology_desc": "כל המקורות, כל החישובים, כל המגבלות הידועות",
        "hebrew_only": "עברית בלבד",
        "ranking_title": "דירוג רשויות מקומיות",
        "ranking_lede": 'אחוז מיחזור, ק"ג פסולת לנפש ליום, ומגמה לעומת השנה הקודמת, לפי רשות מקומית. נתוני {year} (או השנה האחרונה שדווחה).',
        "ranking_caveat": 'רשויות עם "לא דיווח/ה" לא מסרו נתונים לשנה זו — ראו <a href="wall-of-silence.html">חומת השתיקה</a>. חלק מהרשויות חסר להן נתוני אוכלוסייה מדויקים (ראו מתודולוגיה).',
        "search_placeholder": "חיפוש רשות...",
        "pop_filter_all": "כל גדלי האוכלוסייה",
        "pop_under_5k": "עד 5,000",
        "pop_5k_20k": "5,000–20,000",
        "pop_20k_50k": "20,000–50,000",
        "pop_50k_100k": "50,000–100,000",
        "pop_over_100k": "מעל 100,000",
        "th_authority": "רשות מקומית",
        "th_population": "אוכלוסייה",
        "th_total_tons": "סך טונות",
        "th_pct_recycled": "% מיחזור",
        "th_kg_capita": 'ק"ג לנפש ליום',
        "th_trend": "מגמה",
        "th_data_year": "שנת נתונים",
        "national_title": "תמונת מצב ארצית",
        "national_lede": 'סך הכל פסולת, יחס מיחזור מול הטמנה, והפער ליעדי 2030, על בסיס השורה הרשמית של הלמ"ס (לא סכימה של נתוני הרשויות הבודדות — ראו מתודולוגיה).',
        "stat_total_tons": "סך טונות פסולת, {year}",
        "stat_recycled": "מיחזור והשבה",
        "stat_landfilled": "הטמנה",
        "stat_target_landfill_2030": "יעד הטמנה 2030",
        "chart_recycled_vs_landfilled": 'מיחזור מול הטמנה, <bdi dir="ltr">2014&ndash;2024</bdi>',
        "legend_recycled": "מיחזור והשבה",
        "legend_landfilled": "הטמנה",
        "gap_title": "הפער ליעד 2030",
        "gap_lede": "יעד הממשלה: 20% הטמנה / 54% מיחזור עד 2030. המצב הנוכחי ({year}): {landfilled} הטמנה, {recycled} מיחזור.",
        "gap_current": "מצב נוכחי ({year})",
        "gap_target": "יעד 2030",
        "leaders_title": "המובילות והמפגרות",
        "leaders_lede": "עשר הרשויות עם אחוז המיחזור הגבוה והנמוך ביותר ב-{year}, מבין הרשויות שדיווחו נתונים.",
        "leaders_label": "המיחזרות הטובות ביותר",
        "laggards_label": "המיחזרות הפחות טובות",
        "scatter_title": "אוכלוסייה מול שיעור מיחזור",
        "scatter_lede": "האם רשויות גדולות יותר נוטות למחזר יותר? כל נקודה היא רשות מקומית אחת, {year}.",
        "scatter_x_label": "אוכלוסייה (סקאלה לוגריתמית)",
        "scatter_y_label": "% מיחזור",
        "scatter_tooltip": "{name}: {pop} תושבים, {pct}%",
        "materials_title": "מה בעצם ממחזרים?",
        "materials_lede": 'פירוט ארצי (לא לפי רשות) של החומרים המועברים למחזור והשבה. <strong>חומר אורגני</strong> — שיירי מזון וגזם המתאימים לקומפוסטציה — הוא הרכיב הגדול ביותר, ומהווה כ-41% מכלל החומרים הממוחזרים ב-2024.',
        "materials_caveat": 'פירוט זה זמין רק ברמה הארצית (מסך כל הרשויות יחד), ולא לפי רשות מקומית בודדת — הלמ"ס אינה מפרסמת פילוח חומרים ברמת הרשות.',
        "material_other": "אחר",
        "material_yard_waste": "גזם",
        "material_organic": "חומר אורגני",
        "material_glass": "זכוכית",
        "material_metal": "מתכת",
        "material_plastic": "פלסטיק",
        "material_cardboard": "קרטון",
        "material_paper": "נייר",
        "policy_title": "רקע כלכלי ומדיניות: מחיר ההטמנה",
        "policy_text": 'היטל הטמנה הונהג בישראל ב-2007 כדי ליצור תמריץ שלילי להטמנה. עם זאת, לפי המשרד להגנת הסביבה, תעריף ההטמנה כיום (כולל ההיטל) עדיין נמוך משמעותית מהתעריף במדינות אירופה שבהן נאסרה הטמנה — מה שמותיר את ההטמנה זולה יחסית למתקני מיחזור והשבה. בשל כך, "קרן הניקיון" (הממומנת מהיטל ההטמנה) מסבסדת חלק ממתקני המיחזור וההשבה כדי לשמור על מחיר תחרותי מול הטמנה, אך לפי המשרד מנגנון זה לא יוכל להתרחב עם גידול מספר המתקנים העתידי.',
        "policy_caveat": 'אין בידינו נתוני עלות מדויקים (ש"ח לטונה) עבור הטמנה מול מיחזור ברמת רשות או ברמה ארצית — הפירוט לעיל הוא תיאור מדיניות איכותני, לא נתון מספרי. מקור: <a href="https://fs.knesset.gov.il/25/Committees/25_cs_mmm_11061789.pdf" target="_blank" rel="noopener">דוח מרכז המחקר והמידע של הכנסת, ינואר 2026</a> (PDF).',
        "further_reading_title": "קריאה נוספת",
        "further_reading_lede": "כתבות רקע מהתקשורת הישראלית על משבר הפסולת.",
        "wos_title": "חומת השתיקה",
        "wos_lede": '{reported} מתוך {total} רשויות מקומיות לא דיווחו נתוני פסולת ומיחזור ללמ"ס עבור {year}. אי-דיווח הוא ממצא בפני עצמו.',
        "wos_never": "מעולם לא",
        "th_wos_last_report": "דיווח אחרון",
    },
    "en": {
        "site_title": "Israel Waste Index",
        "lang_toggle": "עברית",
        "footer_source": "Data from Israel's Central Bureau of Statistics and data.gov.il",
        "footer_methodology": "Sources & Methodology",
        "hero_title": "Israel Waste Index",
        "hero_lede": "See every local authority in Israel: how much waste it generates, how much gets recycled vs. landfilled, and how that compares to the government's 2030 targets. Every number links to its official source.",
        "stat_recycled_national": "National recycling, {year}",
        "stat_landfilled_national": "National landfill",
        "stat_target_2030": "2030 recycling target",
        "stat_non_reporting": "Non-reporting authorities ({year})",
        "card_ranking_title": "Rankings",
        "card_ranking_desc": "A full, sortable, filterable table of every local authority",
        "card_national_title": "National Overview",
        "card_national_desc": "National trends, material breakdown, and the gap to the 2030 targets",
        "card_silence_title": "Wall of Silence",
        "card_silence_desc": "Authorities that don't report waste data at all",
        "card_glossary_title": "Glossary",
        "card_glossary_desc": "Waste treatment methods, their environmental impact, and international comparison",
        "card_methodology_title": "Methodology",
        "card_methodology_desc": "Every source, every calculation, every known limitation",
        "hebrew_only": "Hebrew only",
        "ranking_title": "Local Authority Rankings",
        "ranking_lede": "% recycled, kg of waste per person per day, and year-over-year trend, by local authority. {year} data (or the most recent year reported).",
        "ranking_caveat": 'Authorities marked "not reported" did not submit data for this year — see the <a href="wall-of-silence.html">Wall of Silence</a>. Some authorities are missing exact population figures (see Methodology).',
        "search_placeholder": "Search authority...",
        "pop_filter_all": "All population sizes",
        "pop_under_5k": "Under 5,000",
        "pop_5k_20k": "5,000–20,000",
        "pop_20k_50k": "20,000–50,000",
        "pop_50k_100k": "50,000–100,000",
        "pop_over_100k": "Over 100,000",
        "th_authority": "Local Authority",
        "th_population": "Population",
        "th_total_tons": "Total Tons",
        "th_pct_recycled": "% Recycled",
        "th_kg_capita": "Kg/capita/day",
        "th_trend": "Trend",
        "th_data_year": "Data Year",
        "national_title": "National Overview",
        "national_lede": "Total waste, recycling vs. landfill, and the gap to the 2030 targets, based on CBS's own official total (not a sum of individual authorities — see Methodology).",
        "stat_total_tons": "Total waste tons, {year}",
        "stat_recycled": "Recycling & recovery",
        "stat_landfilled": "Landfill",
        "stat_target_landfill_2030": "2030 landfill target",
        "chart_recycled_vs_landfilled": 'Recycling vs. landfill, <bdi dir="ltr">2014&ndash;2024</bdi>',
        "legend_recycled": "Recycling & recovery",
        "legend_landfilled": "Landfill",
        "gap_title": "The gap to the 2030 target",
        "gap_lede": "Government target: 20% landfill / 54% recycling by 2030. Current state ({year}): {landfilled} landfill, {recycled} recycling.",
        "gap_current": "Current ({year})",
        "gap_target": "2030 target",
        "leaders_title": "Leaders and laggards",
        "leaders_lede": "The ten authorities with the highest and lowest recycling rates in {year}, among those that reported data.",
        "leaders_label": "Best recyclers",
        "laggards_label": "Worst recyclers",
        "scatter_title": "Population vs. recycling rate",
        "scatter_lede": "Do bigger authorities tend to recycle more? Each point is one local authority, {year}.",
        "scatter_x_label": "Population (logarithmic scale)",
        "scatter_y_label": "% recycled",
        "scatter_tooltip": "{name}: {pop} residents, {pct}%",
        "materials_title": "What actually gets recycled?",
        "materials_lede": 'National breakdown (not by authority) of materials transferred to recycling and recovery. <strong>Organic material</strong> — food scraps and yard waste suitable for composting — is the largest single component, making up about 41% of everything recycled in 2024.',
        "materials_caveat": "This breakdown is only available at the national level (all authorities combined), not per individual authority — CBS does not publish a material breakdown at the authority level.",
        "material_other": "Other",
        "material_yard_waste": "Yard waste",
        "material_organic": "Organic material",
        "material_glass": "Glass",
        "material_metal": "Metal",
        "material_plastic": "Plastic",
        "material_cardboard": "Cardboard",
        "material_paper": "Paper",
        "policy_title": "Economic & policy background: the price of landfill",
        "policy_text": 'A landfill levy was introduced in Israel in 2007 to create a financial disincentive for landfilling. Even so, according to the Ministry of Environmental Protection, today’s landfill tariff (including the levy) is still significantly lower than in European countries that have banned landfilling — which keeps landfilling relatively cheap compared to recycling and recovery facilities. As a result, the "Cleanliness Fund" (funded by the landfill levy) subsidizes some recycling and recovery facilities to keep them price-competitive with landfilling, though the Ministry says this mechanism won’t be able to scale as more facilities come online.',
        "policy_caveat": 'We do not have exact cost data (NIS per ton) for landfilling vs. recycling at the authority or national level — the description above is a qualitative policy summary, not a numeric figure. Source: <a href="https://fs.knesset.gov.il/25/Committees/25_cs_mmm_11061789.pdf" target="_blank" rel="noopener">Knesset Research and Information Center report, January 2026</a> (PDF).',
        "further_reading_title": "Further Reading",
        "further_reading_lede": "Background coverage from the Israeli press on the waste crisis (Hebrew).",
        "wos_title": "Wall of Silence",
        "wos_lede": "{reported} out of {total} local authorities did not report waste and recycling data to the CBS for {year}. Non-reporting is a finding in itself.",
        "wos_never": "Never",
        "th_wos_last_report": "Last Report",
    },
}

FURTHER_READING = [
    {
        "title": "תחזית מדאיגה עד 2040: היקף זיהום הפלסטיק צפוי להכפיל את עצמו",
        "outlet": "זווית",
        "date": "מאי 2026",
        "desc": "סקירה של דוח Pew על זיהום פלסטיק עולמי, עם התייחסות למדיניות מיחזור בישראל.",
        "url": "https://www.zavit.org.il/%D7%AA%D7%97%D7%96%D7%99%D7%AA-%D7%9E%D7%93%D7%90%D7%99%D7%92%D7%94-%D7%A2%D7%93-2040-%D7%94%D7%99%D7%A7%D7%A3-%D7%96%D7%99%D7%94%D7%95%D7%9D-%D7%94%D7%A4%D7%9C%D7%A1%D7%98%D7%99%D7%A7-%D7%99%D7%A9/",
    },
    {
        "title": "ישראל בדרך למשבר פסולת לאומי: האם האשפה תיערם ברחובות?",
        "outlet": "כלכליסט",
        "date": "אוגוסט 2026",
        "desc": 'דעה מאת ראובן לדיאנסקי, יו"ר איגוד ערים חבל דן (חיריה) וסגן ראש עיריית תל אביב-יפו, על משבר קיבולת ההטמנה.',
        "url": "https://www.calcalist.co.il/local_news/article/s1ruftx8fl",
    },
    {
        "title": "הנתונים של נפח ההטמנה נחשפים. הרפורמה בענף תקועה",
        "outlet": "infospot",
        "date": "יולי 2025",
        "desc": "סיכום דוח מעקב של מבקר המדינה על משבר קיבולת ההטמנה ותקיעת רפורמת משק הפסולת.",
        "url": "https://infospot.co.il/n/state_comptroller_municipal_waste_report",
    },
    {
        "title": "משבר משק הפסולת: פרויקט לאומי",
        "outlet": "מכון שמואל נאמן",
        "date": "יוני 2023",
        "desc": 'מסמך המלצות מדיניות: להכריז על משק הפסולת כפרויקט לאומי, להקים רשות ייעודית, ולתכנן לטווח של 20 שנה ומעלה.',
        "url": "https://www.neaman.org.il/the-waste-management-crisis-a-national-project/",
    },
    {
        "title": "שלושה צעדים להתחיל לתקן את משבר הפסולת בישראל",
        "outlet": "שקוף",
        "date": "יוני 2026",
        "desc": 'מאת מרב אבדי, מנהלת רגולציה באדם טבע ודין: קיבוע מתאן ממטמנות, הפרדת פסולת אורגנית במגזר המוסדי, ואכיפה נגד שריפות פסולת בלתי חוקיות.',
        "url": "https://shakuf.co.il/63559",
    },
]

ICON_SUN = '<svg class="icon-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>'
ICON_MOON = '<svg class="icon-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z"/></svg>'

ICON_RANKING = '<svg class="icon" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 17V9M12 17V5M16 17v-4"/></svg>'
ICON_NATIONAL = '<svg class="icon" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 15l3-4 3 2 4-6"/></svg>'
ICON_SILENCE = '<svg class="icon" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5 6 9H2v6h4l5 4V5Z"/><path d="M17 9a3 3 0 0 1 0 6M20 6a7 7 0 0 1 0 12" opacity="0.35"/><path d="M2 2l20 20" opacity="0.6"/></svg>'
ICON_METHOD = '<svg class="icon" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M9 13h6M9 17h6"/></svg>'
ICON_GLOSSARY = '<svg class="icon" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 4h7a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2Z"/><path d="M22 4h-7a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h8Z"/></svg>'

ICON_RECYCLE = '<svg class="icon-sm" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 2l4 4-4 4"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><path d="M7 22l-4-4 4-4"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>'
ICON_LANDFILL = '<svg class="icon-sm" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/></svg>'
ICON_TARGET = '<svg class="icon-sm" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/></svg>'
ICON_POPULATION = '<svg class="icon-sm" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="7" r="3"/><path d="M2 21v-1a6 6 0 0 1 6-6h2a6 6 0 0 1 6 6v1"/><circle cx="17" cy="8" r="2.5"/><path d="M23 21v-1a5 5 0 0 0-4-4.9"/></svg>'
ICON_TONS = '<svg class="icon-sm" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8l-9-5-9 5 9 5 9-5Z"/><path d="M3 8v8l9 5 9-5V8"/><path d="M12 13v8"/></svg>'
ICON_SILENCE_SM = '<svg class="icon-sm" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5 6 9H2v6h4l5 4V5Z"/><path d="M2 2l20 20" opacity="0.6"/></svg>'


def shell(
    title: str,
    active: str,
    body: str,
    root_prefix: str = "",
    extra_head: str = "",
    lang: str = "he",
    nav_prefix: str | None = None,
    lang_toggle_href: str | None = None,
) -> str:
    s = STRINGS[lang]
    nav_items = NAV_ITEMS_EN if lang == "en" else NAV_ITEMS_HE
    if nav_prefix is None:
        nav_prefix = root_prefix
    nav_html = "\n".join(
        f'<a href="{nav_prefix}{href}" class="{"active" if href == active else ""}">{label}</a>'
        for href, label in nav_items
    )
    lang_toggle_html = (
        f'<a href="{lang_toggle_href}" class="lang-toggle">{s["lang_toggle"]}</a>' if lang_toggle_href else ""
    )
    dir_attr = "rtl" if lang == "he" else "ltr"
    return f"""<!doctype html>
<html lang="{lang}" dir="{dir_attr}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="{root_prefix}style.css?v={ASSET_VERSION}">
<script>(function(){{try{{var t=localStorage.getItem('theme');if(t)document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();</script>
{extra_head}
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <h1><a href="{nav_prefix}index.html">{s["site_title"]}</a></h1>
    <nav class="site-nav">{nav_html}</nav>
    <div class="header-controls">
      {lang_toggle_html}
      <button id="theme-toggle" class="theme-toggle" type="button">{ICON_SUN}{ICON_MOON}</button>
    </div>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    {s["footer_source"]} ·
    <a href="{root_prefix}methodology.html">{s["footer_methodology"]}</a>
  </div>
</footer>
<script src="{root_prefix}theme.js?v={ASSET_VERSION}"></script>
<script data-goatcounter="https://adinap.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
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


def build_home_page(data: dict, lang: str = "he") -> str:
    s = STRINGS[lang]
    years = data["years"]
    latest_year = str(years[-1])
    n = data["national"][latest_year]
    non_reporting = sum(
        1 for a in data["authorities"] if not a["years"].get(latest_year, {}).get("reported")
    )
    root_prefix = "" if lang == "he" else "../"
    body = f"""
<div class="hero hero-photo" style="background-image: url('{root_prefix}images/hero.jpg?v={ASSET_VERSION}')">
<div class="hero-inner">
<h2>{s['hero_title']}</h2>
<p class="lede">{s['hero_lede']}</p>
</div>
</div>
<div class="stat-row">
  <div class="stat-tile">{ICON_RECYCLE}<div class="value">{fmt_pct(n['pct_recycled'])}</div><div class="label">{s['stat_recycled_national'].format(year=latest_year)}</div></div>
  <div class="stat-tile">{ICON_LANDFILL}<div class="value">{fmt_pct(n['pct_landfilled'])}</div><div class="label">{s['stat_landfilled_national']}</div></div>
  <div class="stat-tile">{ICON_TARGET}<div class="value">54%</div><div class="label">{s['stat_target_2030']}</div></div>
  <div class="stat-tile">{ICON_SILENCE_SM}<div class="value">{non_reporting}</div><div class="label">{s['stat_non_reporting'].format(year=latest_year)}</div></div>
</div>
<div class="feature-grid">
  <a class="feature-card" href="ranking.html">
    <div class="feature-card-head">{ICON_RANKING}<h3>{s['card_ranking_title']}</h3></div>
    <p>{s['card_ranking_desc']}</p>
  </a>
  <a class="feature-card" href="national.html">
    <div class="feature-card-head">{ICON_NATIONAL}<h3>{s['card_national_title']}</h3></div>
    <p>{s['card_national_desc']}</p>
  </a>
  <a class="feature-card" href="{root_prefix}wall-of-silence.html">
    <div class="feature-card-head">{ICON_SILENCE}<h3>{s['card_silence_title']}</h3></div>
    <p>{s['card_silence_desc']}</p>
  </a>
  <a class="feature-card" href="{root_prefix}glossary.html">
    <div class="feature-card-head">{ICON_GLOSSARY}<h3>{s['card_glossary_title']}</h3></div>
    <p>{s['card_glossary_desc']}</p>
  </a>
  <a class="feature-card" href="{root_prefix}methodology.html">
    <div class="feature-card-head">{ICON_METHOD}<h3>{s['card_methodology_title']}</h3></div>
    <p>{s['card_methodology_desc']}</p>
  </a>
</div>
"""
    title = "מדד הפסולת — נתוני פסולת ומיחזור לפי רשות מקומית" if lang == "he" else "Israel Waste Index — waste and recycling data by local authority"
    lang_toggle_href = "en/index.html" if lang == "he" else "../index.html"
    return shell(title, "index.html", body, root_prefix=root_prefix, nav_prefix="", lang=lang, lang_toggle_href=lang_toggle_href)


def build_ranking_page(data: dict, lang: str = "he") -> str:
    s = STRINGS[lang]
    years = data["years"]
    latest_year = str(years[-1])
    root_prefix = "" if lang == "he" else "../"
    body = f"""
<h2>{s['ranking_title']}</h2>
<p class="lede">{s['ranking_lede'].format(year=latest_year)}</p>
<div class="caveat">
  {s['ranking_caveat'].replace('href="wall-of-silence.html"', f'href="{root_prefix}wall-of-silence.html"')}
</div>
<div class="controls">
  <input type="search" id="search" placeholder="{s['search_placeholder']}">
  <select id="pop-filter">
    <option value="">{s['pop_filter_all']}</option>
    <option value="under_5k">{s['pop_under_5k']}</option>
    <option value="5k_20k">{s['pop_5k_20k']}</option>
    <option value="20k_50k">{s['pop_20k_50k']}</option>
    <option value="50k_100k">{s['pop_50k_100k']}</option>
    <option value="over_100k">{s['pop_over_100k']}</option>
  </select>
  <span id="result-count" class="badge"></span>
</div>
<div class="card">
<div class="table-scroll">
<table class="ranked" id="ranked-table">
  <thead>
    <tr>
      <th data-key="name">{s['th_authority']}</th>
      <th data-key="population">{s['th_population']}</th>
      <th data-key="total_waste_tons">{s['th_total_tons']}</th>
      <th data-key="pct_recycled" class="sorted">{s['th_pct_recycled']}</th>
      <th data-key="kg_per_capita_day">{s['th_kg_capita']}</th>
      <th data-key="trend">{s['th_trend']}</th>
      <th data-key="data_year">{s['th_data_year']}</th>
    </tr>
  </thead>
  <tbody></tbody>
</table>
</div>
</div>
<script src="{root_prefix}vendor/chart.umd.min.js"></script>
<script src="{root_prefix}app.js?v={ASSET_VERSION}"></script>
<script>window.SITE_LANG = {json.dumps(lang)};</script>
<script src="{root_prefix}ranking.js?v={ASSET_VERSION}"></script>
"""
    title = "מדד הפסולת — דירוג רשויות מקומיות" if lang == "he" else "Israel Waste Index — Local Authority Rankings"
    lang_toggle_href = "en/ranking.html" if lang == "he" else "../ranking.html"
    return shell(title, "ranking.html", body, root_prefix=root_prefix, nav_prefix="", lang=lang, lang_toggle_href=lang_toggle_href)


def build_authority_page(authority: dict, years: list[str]) -> str:
    name_he = authority["name_he"]
    name_en = authority["name_en"]
    ly = latest_reported_year(authority, years)
    latest = authority["years"].get(ly, {}) if ly else {}
    pop = authority["population"]

    stat_tiles = f"""
<div class="stat-row">
  <div class="stat-tile">{ICON_RECYCLE}<div class="value">{fmt_pct(latest.get('pct_recycled'))}</div><div class="label">מיחזור והשבה ({ly or '—'})</div></div>
  <div class="stat-tile">{ICON_TONS}<div class="value">{fmt_num(latest.get('total_waste_tons'))}</div><div class="label">טונות פסולת ({ly or '—'})</div></div>
  <div class="stat-tile">{ICON_TONS}<div class="value">{latest.get('kg_per_capita_day') if latest.get('kg_per_capita_day') is not None else '—'}</div><div class="label">ק"ג לנפש ליום</div></div>
  <div class="stat-tile">{ICON_POPULATION}<div class="value">{fmt_num(pop)}</div><div class="label">אוכלוסייה (אמדן 2022)</div></div>
</div>
"""
    not_current = ""
    if ly and ly != str(years[-1]):
        not_current = f'<div class="caveat">הרשות לא דיווחה נתונים החל משנת {int(ly)+1} — מוצגים נתוני {ly}, הנתונים העדכניים ביותר הזמינים.</div>'
    elif not ly:
        not_current = '<div class="caveat">לרשות זו אין נתוני מיחזור מדווחים בכל השנים הזמינות (<bdi dir="ltr">2014&ndash;2024</bdi>).</div>'

    body = f"""
<a class="back-link" href="ranking.html">&rarr; חזרה לדירוג</a>
<h2>{name_he}</h2>
<p class="lede">{name_en}</p>
{not_current}
{stat_tiles}
<h3>{ICON_RECYCLE}מגמה רב-שנתית: אחוז מיחזור לעומת יעד 2030 וממוצע ארצי</h3>
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
<script src="../app.js?v={ASSET_VERSION}"></script>
<script>window.AUTHORITY_SLUG = {json.dumps(authority['slug'])};</script>
<script src="../authority.js?v={ASSET_VERSION}"></script>
"""
    return shell(f"{name_he} — מדד הפסולת", "", body, root_prefix="../")


def build_national_page(data: dict, lang: str = "he") -> str:
    s = STRINGS[lang]
    years = data["years"]
    latest_year = str(years[-1])
    n = data["national"][latest_year]
    targets = data["targets_2030"]
    root_prefix = "" if lang == "he" else "../"
    hebrew_note = "" if lang == "he" else f' <span class="hebrew-only-tag">{s["hebrew_only"]}</span>'
    reading_html = "\n".join(
        f'<a class="reading-item" href="{item["url"]}" target="_blank" rel="noopener">'
        f'<div class="reading-meta">{item["outlet"]} &middot; {item["date"]}{hebrew_note}</div>'
        f'<h4>{item["title"]}</h4>'
        f'<p>{item["desc"]}</p>'
        f"</a>"
        for item in FURTHER_READING
    )
    body = f"""
<h2>{s['national_title']}</h2>
<p class="lede">{s['national_lede']}</p>
<div class="stat-row">
  <div class="stat-tile">{ICON_TONS}<div class="value">{fmt_num(n['total_waste_tons'])}</div><div class="label">{s['stat_total_tons'].format(year=latest_year)}</div></div>
  <div class="stat-tile">{ICON_RECYCLE}<div class="value">{fmt_pct(n['pct_recycled'])}</div><div class="label">{s['stat_recycled']}</div></div>
  <div class="stat-tile">{ICON_LANDFILL}<div class="value">{fmt_pct(n['pct_landfilled'])}</div><div class="label">{s['stat_landfilled']}</div></div>
  <div class="stat-tile">{ICON_TARGET}<div class="value">{targets['pct_landfilled']}%</div><div class="label">{s['stat_target_landfill_2030']}</div></div>
</div>
<h3>{s['chart_recycled_vs_landfilled']}</h3>
<div class="legend">
  <span><span class="swatch" style="background:var(--series-1)"></span>{s['legend_recycled']}</span>
  <span><span class="swatch" style="background:var(--series-6)"></span>{s['legend_landfilled']}</span>
</div>
<div class="card"><div class="chart-box"><canvas id="national-chart"></canvas></div></div>
<h3>{ICON_TARGET}{s['gap_title']}</h3>
<p class="lede">{s['gap_lede'].format(year=latest_year, landfilled=fmt_pct(n['pct_landfilled']), recycled=fmt_pct(n['pct_recycled']))}</p>
<div class="card"><div class="chart-box chart-box-short"><canvas id="gap-chart"></canvas></div></div>

<h3>{ICON_RECYCLE}{s['leaders_title']}</h3>
<p class="lede">{s['leaders_lede'].format(year=latest_year)}</p>
<div class="legend"><span><strong>{s['leaders_label']}</strong></span></div>
<div class="card"><div class="chart-box chart-box-tall"><canvas id="leaders-chart"></canvas></div></div>
<div class="legend"><span><strong>{s['laggards_label']}</strong></span></div>
<div class="card"><div class="chart-box chart-box-tall"><canvas id="laggards-chart"></canvas></div></div>

<h3>{ICON_POPULATION}{s['scatter_title']}</h3>
<p class="lede">{s['scatter_lede'].format(year=latest_year)}</p>
<div class="card"><div class="chart-box"><canvas id="scatter-chart"></canvas></div></div>

<h3>{ICON_RECYCLE}{s['materials_title']}</h3>
<p class="lede">{s['materials_lede']}</p>
<div class="caveat">{s['materials_caveat']}</div>
<div class="card"><div class="chart-box"><canvas id="materials-chart"></canvas></div></div>

<h3>{s['policy_title']}</h3>
<p class="lede">
{s['policy_text']}
</p>
<div class="caveat">{s['policy_caveat']}</div>

<h3>{s['further_reading_title']}</h3>
<p class="lede">{s['further_reading_lede']}</p>
<div class="reading-list">
{reading_html}
</div>
<script src="{root_prefix}vendor/chart.umd.min.js"></script>
<script src="{root_prefix}app.js?v={ASSET_VERSION}"></script>
<script>window.SITE_LANG = {json.dumps(lang)};</script>
<script src="{root_prefix}national.js?v={ASSET_VERSION}"></script>
"""
    title = "תמונת מצב ארצית — מדד הפסולת" if lang == "he" else "National Overview — Israel Waste Index"
    lang_toggle_href = "en/national.html" if lang == "he" else "../national.html"
    return shell(title, "national.html", body, root_prefix=root_prefix, nav_prefix="", lang=lang, lang_toggle_href=lang_toggle_href)


def build_wall_of_silence_page(data: dict, lang: str = "he") -> str:
    s = STRINGS[lang]
    years = data["years"]
    latest_year = str(years[-1])
    root_prefix = "" if lang == "he" else "../"
    name_key = "name_he" if lang == "he" else "name_en"
    authority_href_prefix = "authority/" if lang == "he" else "../authority/"
    non_reporting = [
        a for a in data["authorities"] if not a["years"].get(latest_year, {}).get("reported")
    ]
    non_reporting.sort(key=lambda a: a[name_key])
    rows = []
    for a in non_reporting:
        ly = latest_reported_year(a, years)
        pop_sort = a["population"] if a["population"] is not None else -1
        year_sort = int(ly) if ly else 0
        name = a[name_key]
        rows.append(
            f'<tr><td class="name" data-sort="{name}"><a href="{authority_href_prefix}{a["slug"]}.html">{name}</a></td>'
            f'<td data-sort="{pop_sort}">{fmt_num(a["population"])}</td>'
            f'<td data-sort="{year_sort}">{ly or s["wos_never"]}</td></tr>'
        )
    rows_html = "\n".join(rows)
    lede = s["wos_lede"].format(reported=len(non_reporting), total=len(data["authorities"]), year=latest_year)
    body = f"""
<h2>{s['wos_title']}</h2>
<p class="lede">{lede}</p>
<div class="card">
<div class="table-scroll">
<table class="ranked" id="wos-table">
<thead><tr><th data-key="name" class="sorted asc">{s['th_authority']}</th><th data-key="population">{s['th_population']}</th><th data-key="year">{s['th_wos_last_report']}</th></tr></thead>
<tbody>{rows_html}</tbody>
</table>
</div>
</div>
<script src="{root_prefix}app.js?v={ASSET_VERSION}"></script>
<script>document.addEventListener('DOMContentLoaded', () => makeSortableTable(document.getElementById('wos-table')));</script>
"""
    title = "חומת השתיקה — מדד הפסולת" if lang == "he" else "Wall of Silence — Israel Waste Index"
    lang_toggle_href = "en/wall-of-silence.html" if lang == "he" else "../wall-of-silence.html"
    return shell(title, "wall-of-silence.html", body, root_prefix=root_prefix, nav_prefix="", lang=lang, lang_toggle_href=lang_toggle_href)


def build_glossary_page(data: dict, lang: str = "he") -> str:
    root_prefix = "" if lang == "he" else "../"
    if lang == "en":
        body = f"""
<h2>Glossary</h2>
<p class="lede">How waste is treated in Israel, what each method means for the environment and cost, and how it compares internationally.</p>

<h3>Waste treatment methods</h3>
<dl class="methodology-source">
  <dt>Source separation</dt>
  <dd>Sorting waste into separate streams (organic, dry recyclables, residual) at home or business, before collection. Under Israel's reform: brown bins for organic waste, orange bins for dry recyclables, green bins for residual waste. Source separation is a precondition for high-quality compost and effective recycling &mdash; waste that arrives already mixed is far harder to sort.</dd>

  <dt>Transfer station</dt>
  <dd>An intermediate facility where collected waste is consolidated, and sometimes partially sorted, before continuing on to recycling, recovery, or landfill.</dd>

  <dt>Recycling</dt>
  <dd>Reprocessing materials &mdash; paper, cardboard, plastic, glass, metal &mdash; into raw material for reuse. Saves natural resources and new mining/manufacturing.</dd>

  <dt>Composting / organic waste treatment</dt>
  <dd>Processing food scraps and yard waste into compost. Returns organic material to the soil instead of burying it &mdash; which prevents the methane emissions produced when organic matter decomposes without oxygen in a landfill. Per this site's data, it's the single largest component of everything transferred to recycling and recovery in Israel.</dd>

  <dt>Energy recovery (thermal recovery)</dt>
  <dd>Burning waste (or fuel derived from it) to generate energy. In Israel this currently happens mainly through a partnership between the Hiriya recycling park and the Nesher cement plant, which uses fuel derived from waste. Ranked in the hierarchy below recycling but above landfill.</dd>

  <dt>Landfill</dt>
  <dd>Burying waste in the ground. Currently the cheapest method in Israel, but the most problematic environmentally: buried organic waste emits methane &mdash; a greenhouse gas far more potent than carbon dioxide &mdash; and there's a risk of groundwater contamination from leachate. It also occupies land that can't be used for anything else.</dd>

  <dt>Landfill levy</dt>
  <dd>A fee the state charges on every ton of waste sent to landfill, introduced in 2007 to make landfilling more expensive and encourage alternatives. Even so, according to the Ministry of Environmental Protection, landfilling in Israel is still significantly cheaper than in European countries that have banned it &mdash; see more in the <a href="{root_prefix}national.html">National Overview</a>.</dd>
</dl>

<h3>The waste treatment hierarchy</h3>
<p class="lede">The EU (and also the policy of Israel's Ministry of Environmental Protection) ranks waste treatment methods by environmental preference, from best to worst:</p>
<ol>
  <li><strong>Prevention and reduction</strong> &mdash; not creating the waste in the first place</li>
  <li><strong>Preparation for reuse and recycling</strong> &mdash; turning waste into raw material</li>
  <li><strong>Recovery</strong> &mdash; including energy recovery</li>
  <li><strong>Landfill</strong> &mdash; last resort</li>
</ol>
<p class="lede">Source: Knesset Research and Information Center, <a href="https://fs.knesset.gov.il/25/Committees/25_cs_mmm_11061789.pdf" target="_blank" rel="noopener">January 2026</a> (PDF), based on EU publications.</p>

<h3>Cost to society</h3>
<p class="lede">Beyond the direct financial cost of collection and disposal, every treatment method carries an indirect environmental and social cost: methane emissions and air-quality harm from landfilling, risk of soil and groundwater contamination, transportation burden from hauling waste long distances, and the loss of land that could have been used for other purposes.</p>
<div class="caveat">As noted in the <a href="{root_prefix}national.html">National Overview</a>: we do not have exact cost data (NIS per ton) at the authority or national level for a direct landfill-vs-recycling comparison. What is known: Israel's landfill tariff, including the levy, is significantly lower than in European countries that have banned landfilling &mdash; which makes the more environmentally friendly alternatives comparatively more expensive.</div>

<h3>How this compares internationally</h3>
<p class="lede">Israel landfills about 76% of its municipal waste (2024) &mdash; significantly higher than the average among developed countries. Israel ranks 20th out of 22 OECD countries that report recycling data (25.3% in 2023), compared to an OECD average of about 57%. Countries like Germany, Sweden, and Austria aim for (and sometimes reach) near-zero landfill rates, mainly through a combination of extensive source separation, energy recovery, and recycling.</p>
<p class="lede">For further reading on the international comparison:</p>
<ul>
  <li><a href="https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Municipal_waste_statistics" target="_blank" rel="noopener">Eurostat &mdash; Municipal waste statistics</a></li>
  <li><a href="https://data.oecd.org/waste/municipal-waste.htm" target="_blank" rel="noopener">OECD &mdash; Municipal waste data</a></li>
</ul>
"""
    else:
        body = f"""
<h2>מילון מונחים</h2>
<p class="lede">איך פסולת מטופלת בישראל, מה כל שיטה אומרת לסביבה ולעלות, ואיך זה נראה במדינות אחרות.</p>

<h3>שיטות הטיפול בפסולת</h3>
<dl class="methodology-source">
  <dt>הפרדה במקור</dt>
  <dd>הפרדת הפסולת לזרמים שונים (אורגני, יבש למיחזור, שארי) כבר בבית או בעסק, לפני האיסוף. ברפורמה הישראלית: פח חום לאורגני, פח כתום למיחזור יבש, פח ירוק לשארי. הפרדה במקור היא התנאי ההכרחי לקומפוסט איכותי ולמיחזור יעיל &mdash; פסולת שמגיעה מעורבת קשה הרבה יותר למיין.</dd>

  <dt>תחנת מעבר</dt>
  <dd>מתקן ביניים שבו פסולת שנאספה מרוכזת, ולעיתים ממוינת חלקית, לפני שהיא ממשיכה למיחזור, להשבה או להטמנה.</dd>

  <dt>מיחזור</dt>
  <dd>עיבוד חוזר של חומרים &mdash; נייר, קרטון, פלסטיק, זכוכית, מתכת &mdash; לחומר גלם לשימוש חוזר. חוסך משאבים טבעיים וכרייה/ייצור חדש.</dd>

  <dt>קומפוסטציה / טיפול בפסולת אורגנית</dt>
  <dd>עיבוד שיירי מזון וגזם לקומפוסט. מחזיר חומרים אורגניים לקרקע במקום לקבור אותם &mdash; וכך מונע את פליטת המתאן שנוצרת כשחומר אורגני מתפרק בהטמנה ללא חמצן. לפי נתוני האתר, זהו הרכיב הגדול ביותר מבין כל מה שמועבר למיחזור והשבה בישראל.</dd>

  <dt>השבת אנרגיה (השבה תרמית)</dt>
  <dd>שריפת פסולת (או דלק שמופק ממנה) לייצור אנרגיה. בישראל מתבצע כיום בעיקר בשיתוף בין פארק המיחזור חיריה למפעל המלט נשר, שמשתמש בדלק המופק מפסולת. מדורג בהיררכיה מתחת למיחזור אך מעל הטמנה.</dd>

  <dt>הטמנה</dt>
  <dd>קבורת פסולת בקרקע. השיטה הזולה ביותר כיום בישראל, אך הבעייתית ביותר סביבתית: פסולת אורגנית שנקברת פולטת מתאן &mdash; גז חממה חזק בהרבה מפחמן דו-חמצני &mdash; ויש סיכון לזיהום מי תהום מתשטיפים. גם תופסת שטח קרקע שלא ניתן להשתמש בו לדברים אחרים.</dd>

  <dt>היטל הטמנה</dt>
  <dd>תשלום שגובה המדינה על כל טונת פסולת שמוטמנת, שהונהג ב-2007 כדי להפוך הטמנה ליקרה יותר ולעודד חלופות. עדיין, לפי המשרד להגנת הסביבה, ההטמנה בישראל זולה משמעותית מאשר במדינות אירופה שאסרו עליה &mdash; ראו הרחבה ב<a href="{root_prefix}national.html">תמונת מצב ארצית</a>.</dd>
</dl>

<h3>היררכיית הטיפול בפסולת</h3>
<p class="lede">האיחוד האירופי (וגם מדיניות משרד הגנת הסביבה בישראל) מדרגים שיטות טיפול בפסולת לפי העדפה סביבתית, מהטוב ביותר לגרוע ביותר:</p>
<ol>
  <li><strong>מניעה וצמצום</strong> &mdash; לא ליצור את הפסולת מלכתחילה</li>
  <li><strong>הכנה לשימוש חוזר ומיחזור</strong> &mdash; הפיכת הפסולת לחומר גלם</li>
  <li><strong>השבה</strong> &mdash; כולל השבת אנרגיה</li>
  <li><strong>הטמנה</strong> &mdash; מוצא אחרון</li>
</ol>
<p class="lede">מקור: מרכז המחקר והמידע של הכנסת, <a href="https://fs.knesset.gov.il/25/Committees/25_cs_mmm_11061789.pdf" target="_blank" rel="noopener">ינואר 2026</a> (PDF), בהתבסס על פרסומי האיחוד האירופי.</p>

<h3>עלות לחברה</h3>
<p class="lede">מעבר לעלות הכספית הישירה של איסוף ופינוי, לכל שיטת טיפול יש עלות סביבתית וחברתית עקיפה: פליטות מתאן ופגיעה באיכות האוויר מהטמנה, סיכון לזיהום קרקע ומי תהום, עומס תחבורתי משינוע פסולת למרחקים, ואובדן קרקע שאפשר היה לייעד לשימושים אחרים.</p>
<div class="caveat">כפי שמצוין ב<a href="{root_prefix}national.html">תמונת מצב ארצית</a>: אין בידינו נתוני עלות מדויקים (ש"ח לטונה) ברמת רשות או ברמה ארצית להשוואה ישירה בין הטמנה למיחזור. מה שכן ידוע: תעריף ההטמנה בישראל, כולל ההיטל, נמוך משמעותית מהתעריף במדינות אירופיות שאסרו הטמנה &mdash; מה שמייקר יחסית את החלופות הידידותיות יותר לסביבה.</div>

<h3>איך זה נראה בעולם</h3>
<p class="lede">ישראל מטמינה כ-76% מהפסולת העירונית שלה (2024) &mdash; שיעור גבוה משמעותית מהממוצע במדינות המפותחות. ישראל מדורגת 20 מתוך 22 מדינות ה-OECD שמדווחות נתוני מיחזור (25.3% ב-2023), לעומת ממוצע OECD של כ-57%. מדינות כמו גרמניה, שוודיה ואוסטריה שואפות (ולעיתים מגיעות) לשיעורי הטמנה קרובים לאפס, בעיקר באמצעות שילוב של הפרדה במקור נרחבת, השבת אנרגיה ומיחזור.</p>
<p class="lede">למי שרוצה להעמיק בהשוואה בינלאומית:</p>
<ul>
  <li><a href="https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Municipal_waste_statistics" target="_blank" rel="noopener">Eurostat &mdash; Municipal waste statistics</a></li>
  <li><a href="https://data.oecd.org/waste/municipal-waste.htm" target="_blank" rel="noopener">OECD &mdash; Municipal waste data</a></li>
</ul>
"""
    title = "מילון מונחים — מדד הפסולת" if lang == "he" else "Glossary — Israel Waste Index"
    lang_toggle_href = "en/glossary.html" if lang == "he" else "../glossary.html"
    return shell(title, "glossary.html", body, root_prefix=root_prefix, nav_prefix="", lang=lang, lang_toggle_href=lang_toggle_href)


def build_methodology_page(data: dict, lang: str = "he") -> str:
    generated_at = data["generated_at"][:10]
    root_prefix = "" if lang == "he" else "../"
    if lang == "en":
        body = f"""
<h2>Sources &amp; Methodology</h2>
<p class="lede">Every number on this site links to its official source. Last updated: {generated_at}.</p>

<h3>Data sources</h3>
<dl class="methodology-source">
  <dt>Waste by local authority (<bdi dir="ltr">2014&ndash;2024</bdi>)</dt>
  <dd>Israel's Central Bureau of Statistics (CBS), "Household and commercial waste collected, by treatment method and local authority." Published: November 4, 2025.</dd>
  <dd><a href="https://www.cbs.gov.il/he/publications/Pages/2019/פסולת-שנאספה-ברשויות-המקומיות-2014-2017.aspx" target="_blank" rel="noopener">cbs.gov.il</a></dd>

  <dt>Population by locality</dt>
  <dd>CBS, 2022 Population and Housing Census, "Population and households by locality."</dd>
  <dd><a href="https://data.gov.il" target="_blank" rel="noopener">data.gov.il</a> (dataset 3bd97fde-6cc3-456d-ab63-1caad16b2b6a)</dd>

  <dt>End-of-pipeline solutions for municipal waste in Israel &mdash; background and questions for discussion</dt>
  <dd>Knesset Research and Information Center, January 2026. Source for the economic/policy background on the landfill levy.</dd>
  <dd><a href="https://fs.knesset.gov.il/25/Committees/25_cs_mmm_11061789.pdf" target="_blank" rel="noopener">fs.knesset.gov.il (PDF)</a></dd>

  <dt>Household waste in Israel</dt>
  <dd>Knesset Research and Information Center, June 2008. Source of the historical reporting-rate figure (see "Reporting rate" below).</dd>
  <dd><a href="https://fs.knesset.gov.il/globaldocs/MMM/034c6b58-e9f7-e411-80c8-00155d010977/2_034c6b58-e9f7-e411-80c8-00155d010977_11_6689.pdf" target="_blank" rel="noopener">fs.knesset.gov.il (PDF)</a></dd>
</dl>

<h3>How each number is calculated</h3>
<ul>
  <li><strong>% recycled</strong> — the "percentage of total waste" transferred to recycling and recovery, calculated and published directly by CBS for each authority.</li>
  <li><strong>% landfilled</strong> — tons sent to landfill divided by total waste, as reported in the CBS table.</li>
  <li><strong>Kg per capita per day</strong> — calculated and published directly by CBS.</li>
  <li><strong>Population</strong> — for cities and local councils: taken directly from the CBS population file (2022 census) by authority name. For regional councils: summed from the population of all member localities (cross-referenced with the 2019 socioeconomic clusters file).</li>
</ul>

<h3>Authority reporting rate</h3>
<p class="lede">A "non-reporting authority" on this site = an authority for which CBS did not publish a numeric figure in the municipal waste and recycling survey for that year. In practice, 226&ndash;253 out of 255&ndash;257 authorities report some waste data in every year between 2014 and 2024 (18 out of 257 did not report in 2024) &mdash; a far higher reporting rate than what commonly circulates in public discussion.</p>
<div class="caveat">You may have come across a figure of "only about 120 authorities report," which occasionally circulates in public discussion. It originates from a <strong>June 2008</strong> Knesset Research and Information Center report (<a href="https://fs.knesset.gov.il/globaldocs/MMM/034c6b58-e9f7-e411-80c8-00155d010977/2_034c6b58-e9f7-e411-80c8-00155d010977_11_6689.pdf" target="_blank" rel="noopener">"Household Waste in Israel"</a>) &mdash; a report about compliance with a different regulatory reporting requirement to the Ministry of Environmental Protection (not the CBS survey this site is based on), describing a situation from roughly 18 years ago. Both figures are correct in their own context, but they are not directly comparable. Full detail in <code>data/CONFLICTS.md</code> in the source repository.</div>

<h3>Known limitations</h3>
<div class="caveat"><strong>National total.</strong> Summing the data of all individual authorities comes out about 7&ndash;8% lower than CBS's own official total line, because CBS's national total includes an estimate for authorities that don't report separately. That's why the "National Overview" page uses CBS's official total line, not a sum of the authority-level data.</div>
<div class="caveat"><strong>District.</strong> We haven't yet found a data source mapping authority&rarr;district. This field is currently missing from the site (no filtering by district in v1).</div>
<div class="caveat"><strong>Socioeconomic cluster.</strong> The only data source we found covers localities within regional councils only (995 localities, 54 councils) &mdash; with no coverage for cities and local councils, which make up most of the authorities shown on this site. So this field isn't shown at all in v1, to avoid presenting a partial and misleading figure.</div>
<div class="caveat"><strong>Two authorities without population data</strong>: Sdot Dan and Sha'ar Shomron &mdash; not found in any of the population sources checked.</div>
<div class="caveat"><strong>Recycling vs. other recovery</strong>: The CBS table combines "recycling" and "other recovery" (such as energy recovery) into a single figure. These cannot be separated with the current source.</div>

<h3>Data updates</h3>
<p>Last updated: {generated_at}. The data does not update automatically &mdash; a future update will require re-running the processing pipeline once CBS publishes new data.</p>
"""
    else:
        body = f"""
<h2>מקורות ומתודולוגיה</h2>
<p class="lede">כל מספר באתר הזה מקושר למקור הרשמי שלו. עודכן לאחרונה: {generated_at}.</p>

<h3>מקורות נתונים</h3>
<dl class="methodology-source">
  <dt>פסולת לפי רשות מקומית (<bdi dir="ltr">2014&ndash;2024</bdi>)</dt>
  <dd>הלשכה המרכזית לסטטיסטיקה (למ"ס), "פסולת ביתית ומסחרית שנאספה, לפי אופן טיפול ורשות מקומית". פורסם: 4.11.2025.</dd>
  <dd><a href="https://www.cbs.gov.il/he/publications/Pages/2019/פסולת-שנאספה-ברשויות-המקומיות-2014-2017.aspx" target="_blank" rel="noopener">cbs.gov.il</a></dd>

  <dt>אוכלוסייה לפי יישוב</dt>
  <dd>למ"ס, מפקד האוכלוסין והדיור 2022, "אוכלוסייה ומשקי בית לפי יישוב".</dd>
  <dd><a href="https://data.gov.il" target="_blank" rel="noopener">data.gov.il</a> (dataset 3bd97fde-6cc3-456d-ab63-1caad16b2b6a)</dd>

  <dt>פתרונות קצה לפסולת עירונית בישראל &mdash; רקע ושאלות לדיון</dt>
  <dd>מרכז המחקר והמידע של הכנסת, ינואר 2026. מקור לרקע הכלכלי-מדיניותי על היטל ההטמנה.</dd>
  <dd><a href="https://fs.knesset.gov.il/25/Committees/25_cs_mmm_11061789.pdf" target="_blank" rel="noopener">fs.knesset.gov.il (PDF)</a></dd>

  <dt>פסולת ביתית בישראל</dt>
  <dd>מרכז המחקר והמידע של הכנסת, יוני 2008. מקור נתון הדיווח ההיסטורי (ראו "שיעור הדיווח" למטה).</dd>
  <dd><a href="https://fs.knesset.gov.il/globaldocs/MMM/034c6b58-e9f7-e411-80c8-00155d010977/2_034c6b58-e9f7-e411-80c8-00155d010977_11_6689.pdf" target="_blank" rel="noopener">fs.knesset.gov.il (PDF)</a></dd>
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
<div class="caveat">ייתכן שנתקלתם בנתון של "כ-120 רשויות בלבד מדווחות", החוזר מדי פעם בשיח הציבורי. מקורו בדוח מרכז המחקר והמידע של הכנסת <strong>מיוני 2008</strong> (<a href="https://fs.knesset.gov.il/globaldocs/MMM/034c6b58-e9f7-e411-80c8-00155d010977/2_034c6b58-e9f7-e411-80c8-00155d010977_11_6689.pdf" target="_blank" rel="noopener">"פסולת ביתית בישראל"</a>) &mdash; דוח העוסק בעמידה בדרישת דיווח רגולטורית שונה למשרד להגנת הסביבה (לא בסקר הלמ"ס שעליו מבוסס אתר זה), ומתאר מצב לפני כ-18 שנה. שני הנתונים נכונים כל אחד להקשרו, אך אינם ניתנים להשוואה ישירה. פירוט מלא ב-<code>data/CONFLICTS.md</code> במאגר הקוד.</div>

<h3>מגבלות ידועות</h3>
<div class="caveat"><strong>סך הפסולת הארצי.</strong> סכימה של נתוני כל הרשויות הבודדות נמוכה בכ-7&ndash;8% מהשורה הרשמית שמפרסמת הלמ"ס עצמה, מכיוון שהלמ"ס כוללת בסך הארצי הערכה לרשויות שאינן מדווחות בנפרד. לכן עמוד "תמונת מצב ארצית" משתמש בשורת הסך הרשמית של הלמ"ס, ולא בסכימה של נתוני הרשויות.</div>
<div class="caveat"><strong>מחוז.</strong> טרם נמצא מקור נתונים למיפוי רשות&larr;מחוז. שדה זה חסר כרגע באתר (אין סינון לפי מחוז ב-v1).</div>
<div class="caveat"><strong>אשכול חברתי-כלכלי.</strong> מקור הנתונים היחיד שנמצא מכסה רק יישובים בתוך מועצות אזוריות (995 יישובים, 54 מועצות) &mdash; ללא כיסוי לערים ומועצות מקומיות, שהן רוב הרשויות המוצגות באתר. לכן שדה זה אינו מוצג כלל ב-v1, כדי לא להציג נתון חלקי ומטעה.</div>
<div class="caveat"><strong>שתי רשויות ללא נתוני אוכלוסייה</strong>: שדות דן ושער שומרון &mdash; לא נמצאו באף אחד ממקורות האוכלוסייה שנבדקו.</div>
<div class="caveat"><strong>מיחזור מול השבה אחרת</strong>: טבלת הלמ"ס משלבת "מיחזור" ו"השבה אחרת" (כגון השבת אנרגיה) למדד אחד. לא ניתן להפריד ביניהם עם המקור הנוכחי.</div>

<h3>עדכון הנתונים</h3>
<p>עודכן לאחרונה: {generated_at}. הנתונים אינם מתעדכנים אוטומטית &mdash; עדכון עתידי ידרוש הרצה חוזרת של תהליך העיבוד כאשר הלמ"ס מפרסמת נתונים חדשים.</p>
"""
    title = "מתודולוגיה — מדד הפסולת" if lang == "he" else "Methodology — Israel Waste Index"
    lang_toggle_href = "en/methodology.html" if lang == "he" else "../methodology.html"
    return shell(title, "methodology.html", body, root_prefix=root_prefix, nav_prefix="", lang=lang, lang_toggle_href=lang_toggle_href)


def main():
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs(f"{OUT_DIR}/authority", exist_ok=True)
    os.makedirs(f"{OUT_DIR}/en", exist_ok=True)

    with open(f"{OUT_DIR}/index.html", "w", encoding="utf-8") as f:
        f.write(build_home_page(data))
    with open(f"{OUT_DIR}/ranking.html", "w", encoding="utf-8") as f:
        f.write(build_ranking_page(data))
    with open(f"{OUT_DIR}/national.html", "w", encoding="utf-8") as f:
        f.write(build_national_page(data))
    with open(f"{OUT_DIR}/wall-of-silence.html", "w", encoding="utf-8") as f:
        f.write(build_wall_of_silence_page(data))
    with open(f"{OUT_DIR}/glossary.html", "w", encoding="utf-8") as f:
        f.write(build_glossary_page(data))
    with open(f"{OUT_DIR}/methodology.html", "w", encoding="utf-8") as f:
        f.write(build_methodology_page(data))

    with open(f"{OUT_DIR}/en/index.html", "w", encoding="utf-8") as f:
        f.write(build_home_page(data, lang="en"))
    with open(f"{OUT_DIR}/en/ranking.html", "w", encoding="utf-8") as f:
        f.write(build_ranking_page(data, lang="en"))
    with open(f"{OUT_DIR}/en/national.html", "w", encoding="utf-8") as f:
        f.write(build_national_page(data, lang="en"))
    with open(f"{OUT_DIR}/en/wall-of-silence.html", "w", encoding="utf-8") as f:
        f.write(build_wall_of_silence_page(data, lang="en"))
    with open(f"{OUT_DIR}/en/glossary.html", "w", encoding="utf-8") as f:
        f.write(build_glossary_page(data, lang="en"))
    with open(f"{OUT_DIR}/en/methodology.html", "w", encoding="utf-8") as f:
        f.write(build_methodology_page(data, lang="en"))

    for authority in data["authorities"]:
        path = f"{OUT_DIR}/authority/{authority['slug']}.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(build_authority_page(authority, data["years"]))

    print(f"generated index/ranking/national/wall-of-silence/glossary/methodology + en/{{index,ranking,national,wall-of-silence,glossary,methodology}} + {len(data['authorities'])} authority pages")


if __name__ == "__main__":
    main()
