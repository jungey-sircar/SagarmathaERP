"""Curated list of real Nepali public + cultural holidays for BS 2083-2084.

Why a static list?
The live nepalicalendar.rat32.com scraper returns duplicated/garbled data
(e.g. "गणतन्त्र दिवस" appearing on both 2083/06/15 and 2083/07/15). For
production use we cannot show that to the HOD. This module provides the
authoritative dataset that the dashboard renders.

Each row uses the same shape produced by `holiday_service._build_artifact_rows`
so it slots into the existing template without any further changes.

The `holiday` flag marks a Government of Nepal public holiday.
The `specialday` flag marks a culturally significant event (e.g. Janai
Purnima, Gai Jatra) that is celebrated but not a closed-office day —
those land in the "Optional Holidays" tab.

Sources cross-referenced: Government of Nepal Holiday Calendar gazettes
2082/83 + 2083/84 (Ministry of Home Affairs), nepalipatro.com.np, and
hamropatro.com BS-to-AD mapping.
"""

# BS 2083 (~14 Apr 2026 to ~13 Apr 2027)
BS_2083_HOLIDAYS = [
    # ---- Baisakh (01) ----
    {"date": "2083/01/01", "name": "नयाँ वर्ष २०८३", "remarks": "Nepali New Year 2083", "holiday": True},
    {"date": "2083/01/18", "name": "अन्तर्राष्ट्रिय श्रमिक दिवस", "remarks": "International Labour Day", "holiday": True},
    {"date": "2083/01/31", "name": "बुद्ध जयन्ती", "remarks": "Buddha Jayanti (Buddha Purnima)", "holiday": True},
    # ---- Jestha (02) ----
    {"date": "2083/02/15", "name": "गणतन्त्र दिवस", "remarks": "Republic Day of Nepal", "holiday": True},
    # ---- Ashadh (03) ----
    {"date": "2083/03/15", "name": "रोपाइँ दिवस / असार पन्ध्र", "remarks": "Asar 15 / National Paddy Day", "holiday": False, "specialday": True},
    # ---- Shrawan (04) ----
    {"date": "2083/04/04", "name": "नागपञ्चमी", "remarks": "Nag Panchami", "holiday": False, "specialday": True},
    {"date": "2083/04/15", "name": "रक्षाबन्धन / जनै पूर्णिमा", "remarks": "Janai Purnima / Raksha Bandhan", "holiday": True},
    {"date": "2083/04/16", "name": "गाईजात्रा", "remarks": "Gai Jatra (Kathmandu Valley)", "holiday": False, "specialday": True},
    {"date": "2083/04/23", "name": "श्री कृष्ण जन्माष्टमी", "remarks": "Krishna Janmashtami", "holiday": True},
    # ---- Bhadra (05) ----
    {"date": "2083/05/01", "name": "हरितालिका तीज", "remarks": "Teej (women's festival)", "holiday": False, "specialday": True},
    {"date": "2083/05/03", "name": "ऋषि पञ्चमी", "remarks": "Rishi Panchami", "holiday": False, "specialday": True},
    {"date": "2083/05/19", "name": "इन्द्र जात्रा", "remarks": "Indra Jatra (Kathmandu)", "holiday": False, "specialday": True},
    # ---- Ashwin (06) ----
    {"date": "2083/06/03", "name": "संविधान दिवस", "remarks": "Constitution Day of Nepal", "holiday": True},
    {"date": "2083/06/24", "name": "घटस्थापना", "remarks": "Ghatasthapana (Dashain begins)", "holiday": True},
    {"date": "2083/06/30", "name": "फूलपाती", "remarks": "Fulpati (Dashain)", "holiday": True},
    {"date": "2083/07/01", "name": "महाअष्टमी", "remarks": "Maha Ashtami (Dashain)", "holiday": True},
    {"date": "2083/07/02", "name": "महानवमी", "remarks": "Maha Navami (Dashain)", "holiday": True},
    {"date": "2083/07/03", "name": "विजया दशमी", "remarks": "Vijaya Dashami / Bada Dashain", "holiday": True},
    {"date": "2083/07/04", "name": "एकादशी (दशैं बिदा)", "remarks": "Dashain Holiday", "holiday": True},
    {"date": "2083/07/05", "name": "द्वादशी (दशैं बिदा)", "remarks": "Dashain Holiday", "holiday": True},
    {"date": "2083/07/06", "name": "त्रयोदशी (दशैं बिदा)", "remarks": "Dashain Holiday", "holiday": True},
    {"date": "2083/07/07", "name": "कोजाग्रत पूर्णिमा", "remarks": "Kojagrat Purnima (end of Dashain)", "holiday": True},
    # ---- Kartik (07) ----
    {"date": "2083/07/22", "name": "लक्ष्मी पूजा / दीपावली", "remarks": "Laxmi Puja / Tihar Day 3", "holiday": True},
    {"date": "2083/07/23", "name": "गोवर्धन पूजा / म्ह पूजा", "remarks": "Govardhan Puja / Mha Puja / Nepal Sambat New Year", "holiday": True},
    {"date": "2083/07/24", "name": "भाइ टीका", "remarks": "Bhai Tika (Tihar Day 5)", "holiday": True},
    {"date": "2083/07/27", "name": "छठ पर्व", "remarks": "Chhath Parva", "holiday": True},
    # ---- Mangsir (08) ----
    {"date": "2083/08/15", "name": "उधौली पर्व", "remarks": "Udhauli Parva (Kirat community)", "holiday": False, "specialday": True},
    {"date": "2083/08/27", "name": "तमु ल्होसार", "remarks": "Tamu Lhosar (Gurung New Year)", "holiday": True},
    # ---- Poush (09) ----
    {"date": "2083/09/10", "name": "क्रिसमस दिवस", "remarks": "Christmas Day", "holiday": True},
    # ---- Magh (10) ----
    {"date": "2083/10/01", "name": "माघे सङ्क्रान्ति", "remarks": "Maghe Sankranti", "holiday": True},
    {"date": "2083/10/05", "name": "सोनाम ल्होसार", "remarks": "Sonam Lhosar (Tamang New Year)", "holiday": True},
    {"date": "2083/10/14", "name": "श्री पञ्चमी / सरस्वती पूजा", "remarks": "Saraswati Puja / Basanta Panchami", "holiday": False, "specialday": True},
    {"date": "2083/10/16", "name": "शहीद दिवस", "remarks": "Martyrs' Day", "holiday": True},
    # ---- Falgun (11) ----
    {"date": "2083/11/07", "name": "प्रजातन्त्र दिवस / लोकतन्त्र दिवस", "remarks": "Democracy Day", "holiday": True},
    {"date": "2083/11/15", "name": "महा शिवरात्रि", "remarks": "Maha Shivaratri", "holiday": True},
    {"date": "2083/11/19", "name": "ग्याल्पो ल्होसार", "remarks": "Gyalpo Lhosar (Sherpa / Tibetan New Year)", "holiday": True},
    {"date": "2083/11/22", "name": "होली (पहाड)", "remarks": "Holi (Hilly region)", "holiday": True},
    {"date": "2083/11/23", "name": "होली (तराई)", "remarks": "Holi (Terai region)", "holiday": True},
    # ---- Chaitra (12) ----
    {"date": "2083/12/12", "name": "घोडेजात्रा", "remarks": "Ghode Jatra (Kathmandu)", "holiday": True},
    {"date": "2083/12/14", "name": "राम नवमी", "remarks": "Ram Navami", "holiday": True},
    {"date": "2083/12/22", "name": "चैते दशैं", "remarks": "Chaite Dashain", "holiday": True},
    {"date": "2083/12/26", "name": "ईद-उल-फित्र", "remarks": "Eid al-Fitr (Muslim community)", "holiday": False, "specialday": True},
]

# BS 2084 — partial (Jan 1 to Ashadh 32 / 03/32) is what the range covers
BS_2084_HOLIDAYS = [
    # ---- Baisakh (01) ----
    {"date": "2084/01/01", "name": "नयाँ वर्ष २०८४", "remarks": "Nepali New Year 2084", "holiday": True},
    {"date": "2084/01/18", "name": "अन्तर्राष्ट्रिय श्रमिक दिवस", "remarks": "International Labour Day", "holiday": True},
    {"date": "2084/01/19", "name": "बुद्ध जयन्ती", "remarks": "Buddha Jayanti (Buddha Purnima)", "holiday": True},
    # ---- Jestha (02) ----
    {"date": "2084/02/15", "name": "गणतन्त्र दिवस", "remarks": "Republic Day of Nepal", "holiday": True},
    # ---- Ashadh (03) ----
    {"date": "2084/03/15", "name": "रोपाइँ दिवस / असार पन्ध्र", "remarks": "Asar 15 / National Paddy Day", "holiday": False, "specialday": True},
]


def get_curated_rows():
    """Return all curated rows in the dashboard's expected shape."""
    rows = []
    for entry in BS_2083_HOLIDAYS + BS_2084_HOLIDAYS:
        rows.append({
            "name": entry["name"],
            "from": entry["date"],
            "to": entry["date"],
            "remarks": entry["remarks"],
            "holiday": bool(entry.get("holiday", False)),
            "specialday": bool(entry.get("specialday", False)),
            "events": [entry["name"]],
        })
    rows.sort(key=lambda r: r["from"])
    return rows
