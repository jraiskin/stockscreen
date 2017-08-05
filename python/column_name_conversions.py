heb_names = (
    "שווי שוק",
    "EPS-רווח למניה",
    "רווח גולמי למכירות",
    "רווח תפעולי למכירות",
    "רווח לפני מס למכירות",
    "רווח נקי למכירות",
    "תשואה על ההון העצמי",
    "תשואה על ההשקעה",
    "תשואה על הנכסים",
    "דיבידנט למניה",
    "תשואות דיבידנט",
    "מרחק מגבוה 52 שבועות %",
    "% מרחק מנמוך 52 שבועות",
    "בטא",
    "סטיית תקן",
    "% תשואה מתחילת החודש",
    "% תשואה 3 חודשים אחרונים",
    "% תשואה מתחילת השנה",
    "% תשואה 12 חודשים אחרונים",
    "מכפיל תזרים",
    "מכפיל הון",
    "מכפיל מכירות",
    "הון עצמי למאזן",
    "יחס שוטף",
    "מנוף פיננסי",
    "מכפיל רווח")

eng_names = (
    'market_cap',
    'EPS',
    'gross_margin',
    'operating_margin',
    'pre-tax_profit_margin',
    'net_profit_margin',
    'ROE',
    'ROI',
    'ROA',
    'dividend_per_share',
    'dividend_yield',
    '%_from_52_week_high',
    '%_from_52_week_low',
    'beta',
    'standard_dev',
    'return_this_month',
    'trailing_3_month_return',
    'return_this_year',
    'trailing_12_month_return',
    'price_to_cashflow',
    'price_to_book',
    'price_to_revenues',
    'bv_to_assets',
    'cur_assets_to_cur_liab',
    'liab_to_bv',
    'PE'
)

heb_to_eng_names = dict(zip(heb_names, eng_names))
eng_to_heb_names = dict(zip(eng_names, heb_names))