#!/usr/bin/env python3
"""
EdoTec Kit Navigatie Generator
================================
Genereaza toate combinatiile cod produs + titlu pentru kituri de navigatie.

UTILIZARE:
  python3 edotec_kit_generator.py

LOGICA:
  - Fiecare KIT = o rama cu cablaje pentru o masina specifica
  - Fiecare tableta = o platforma de navigatie cu o litera unica in titlu
  - Titlu generat: "{Masina} {Litera_Platforma}-{Nr_Kit} {Descriere_Tableta}"
  - Rame 9": combinate doar cu tablete 9"
  - Rame 10": combinate cu tablete 10" (native) + tablete 9" cu +KIT-10-9 (adaptor)

ACTUALIZARE PENTRU KITURI NOI:
  1. Adauga kitul nou in FRAMES_9 sau FRAMES_10
  2. Adauga masina in KIT_CAR
  3. Ruleaza scriptul

ACTUALIZARE PENTRU TABLETE NOI:
  1. Adauga tableta in TABLETS_9 sau TABLETS_10
  2. Adauga prefix + text in TABLET_FMT
  3. Ruleaza scriptul
"""

import re
import csv
import json
import sys
from pathlib import Path

# ══════════════════════════════════════════════════════════
# CONFIGURARE RAME (KITURI)
# ══════════════════════════════════════════════════════════

# Rame cu ecran de 9" - combinate DOAR cu tablete 9"
FRAMES_9 = [
    'KIT-044',   # Honda Civic 2005-2011
    'KIT-124',   # Suzuki SX4 2006-2013
    'KIT-173',   # Volvo XC90
    'KIT-179',   # Suzuki Swift 2010-2017
    'KIT-212',   # Mazda CX-5 2012- Manual
    'KIT-219',   # BMW X1 E84
    'KIT-223',   # Mazda 6 2013-2017
    'KIT-469',   # Honda CRV 2012-2016
    'KIT-500NEW',# Fiat 500 2015-2021
    'KIT-517',   # Hyundai i20 2015-2018
    'KIT-1058',  # Hyundai Kona
    'KIT-1135',  # Hyundai Tucson 2019-
    'KIT-1142',  # VW Touareg 2012-2019
]

# Rame cu ecran de 10" - combinate cu tablete 10" + tablete 9" cu adaptor KIT-10-9
FRAMES_10 = [
    'KIT-026',   # Mitsubishi ASX 2013-2017
    'KIT-338',   # Opel Insignia 2014-2016
    'KIT-361',   # Hyundai IX35
    'KIT-381',   # Toyota Land Cruiser L200
]

# Masina per kit (folosita in titlu)
KIT_CAR = {
    'KIT-026':    'Navigatie MITSUBISHI ASX 2013-2017',
    'KIT-044':    'Navigatie Honda Civic 2005-2011',
    'KIT-124':    'Navigatie Suzuki SX4 2006-2013',
    'KIT-173':    'Navigatie Volvo XC90',
    'KIT-179':    'Navigatie Suzuki Swift 2010-2017',
    'KIT-212':    'Navigatie MAZDA CX-5 2012- Manual',
    'KIT-219':    'Navigatie BMW X1 E84',
    'KIT-223':    'Navigatie Mazda 6 2013-2017',
    'KIT-338':    'Navigatie Opel Insignia 2014-2016',
    'KIT-361':    'Navigatie Hyundai IX35',
    'KIT-381':    'Navigatie TOYOTA Land Cruiser L200',
    'KIT-469':    'Navigatie Honda CRV 2012-2016',
    'KIT-500NEW': 'Navigatie Fiat 500 2015-2021',
    'KIT-517':    'Navigatie Hyundai i20 2015-2018',
    'KIT-1058':   'Navigatie Hyundai Kona',
    'KIT-1135':   'Navigatie Hyundai Tucson 2019-',
    'KIT-1142':   'Navigatie VW Touareg 2012-2019',
}

# ══════════════════════════════════════════════════════════
# CONFIGURARE TABLETE / PLATFORME
# ══════════════════════════════════════════════════════════
# Format: 'COD_TABLETA': ('LITERA_PLATFORMA', 'TEXT_DUPA_LITERA-NR')
# LITERA_PLATFORMA = litera unica (A-Z) SAU prefix special (Kit, Pro, 5960Pro)
# Regula: aceeasi litera apare consistent pe TOATE kiturile cu aceasta tableta

TABLET_FMT = {
    # ── 9 INCH ──
    'EDT-E211-RK':    ('Kit', 'Edotec  4+64 10.5 inch Incell 1K android Wifi 5Ghz gps internet'),
    'EDT-E212-RK':    ('K',   'Edotec 4+64 12.3 inch Incell 1K android Wifi 5Ghz gps internet'),
    'EDT-E309V3':     ('B',   'Android Ecran QLED octa core 4+64 carplay android auto'),
    'EDT-E413V3':     ('N',   'Edonav ecran 13" 1K 4+64 Android Waze USB Navigatie 4G 360 Toslink'),
    'EDT-E424':       ('Kit', 'Edotec 2 ecrane  8 core 4+128 21.6 inch Incell android Wifi 5Ghz gps internet'),
    'EDT-E509-PRO':   ('E',   'Octa Core cu Android Radio Bluetooth Internet GPS WIFI DSP 4+64GB 4G RESIGILAT'),
    'EDT-E609':       ('F',   'Octa Core cu Android Radio Bluetooth Internet GPS WIFI DSP 8+128GB 4G'),
    'EDT-E708':       ('K',   'ecran tip TESLA 9.7" cu Android Radio Bluetooth Internet GPS WIFI 2+32GB DSP 4G'),
    'EDT-E709':       ('G',   'ecran tip TESLA 9.7" cu Android Radio Bluetooth Internet GPS WIFI 4+32GB DSP 4G'),
    'NAM5960Pro-A9Z': ('5960Pro', 'Android Octa Core Qualcomm 2K Qled 8+128 DTS DSP 360 4G Optical'),
    'LITE-D4-9-4+64': ('Kit', '4+64 GB Android Waze USB Navigatie Internet Youtube Radio'),
    'PRO-2K-9-4+64':  ('Kit', '8 core QLED 2K 4+64 360 Android Waze USB Navigatie Internet Youtube Radio'),
    'PRO-2K-9-8+256': ('Kit', '8 core QLED 2K 8+256 360 Android Waze USB Navigatie Internet Youtube Radio'),
    'PRO-2K-9-12+256':('Kit', '8 core QLED 2K 12+256 360 Android Waze USB Navigatie Internet Youtube Radio'),
    'ULTRA-9-4+64':   ('Kit', '8 core QLED Qualcomm 4+64 360 Android Waze USB Navigatie Internet Youtube Radio'),
    'ULTRA-2K-9-8+128':('M',  'Octa Core Android Radio Bluetooth GPS WIFI/4G DSP 2K 8+128GB 360 Toslink'),

    # ── 10 INCH ──
    'EDT-E310V3':     ('B',   'Android Ecran QLED octa core 4+64 10" carplay android auto'),
    'EDT-E510-PRO':   ('E',   'Octa Core cu Android Radio Bluetooth Internet GPS WIFI DSP 4+64GB 4G ecran 10"'),
    'EDT-E610':       ('F',   'Octa Core cu Android Radio Bluetooth Internet GPS WIFI DSP 8+128GB 4G ecran 10"'),
    'EDT-E710':       ('H',   'ecran tip TESLA 10" cu Android Radio Bluetooth Internet GPS WIFI 4+32GB DSP 4G'),
    'EDT-E810-2K':    ('Kit', '8 core QLED 2K 16+512GB 360 Android Waze USB Navigatie Internet Youtube Radio'),
    'LITE-10.5-4+64': ('Kit', 'Lenovo  8 core 4+64 10.5 inch Incell 1K android Wifi 5Ghz gps internet'),
    'LITE-10-6+128':  ('Kit', '8 core 6+128 GB Android Waze USB Navigatie Internet Youtube Radio'),
    'LITE-D4-10-4+64':('Kit', '4+64 GB Android Waze USB Navigatie Internet Youtube Radio'),
    'PRO-12.3-4+64':  ('K',   'Lenovo PRO 4+64 12.3 inch qled android 4G DSP gps internet  8Core'),
    'PRO-12.3-8+256': ('K',   'Lenovo PRO 8+256 12.3 inch qled android 4G DSP gps internet  8Core'),
    'PRO-2K-10-4+64': ('Kit', '8 core QLED 2K 4+64 360 Android Waze USB Navigatie Internet Youtube Radio'),
    'PRO-2K-10-8+256':('Kit', '8 core QLED 2K 8+256 360 Android Waze USB Navigatie Internet Youtube Radio'),
    'PRO-2K-10-12+256':('Kit','8 core QLED 2K 12+256 360 Android Waze USB Navigatie Internet Youtube Radio'),
    'PRO-2K-13-4+64': ('K',   'Lenovo PRO 4+64 13 inch 2K android 4G DSP gps internet  8Core'),
    'ULTRA-10-4+64':  ('Kit', '8 core QLED Qualcomm 4+64 360 Android Waze USB Navigatie Internet Youtube Radio'),
    'ULTRA-2K-10-8+128':('M', 'Octa Core Android Radio Bluetooth GPS WIFI/4G DSP 2K 8+128GB 360 Toslink'),
    'ULTRA-2K-13-8+128':('N', 'ecran 13" 2K 8+128 Android Waze USB Navigatie 4G 360 Toslink Youtube Radio'),
}

TABLETS_9  = [t for t in TABLET_FMT if t in [
    'EDT-E211-RK','EDT-E212-RK','EDT-E309V3','EDT-E413V3','EDT-E424',
    'EDT-E509-PRO','EDT-E609','EDT-E708','EDT-E709','NAM5960Pro-A9Z',
    'LITE-D4-9-4+64','PRO-2K-9-4+64','PRO-2K-9-8+256','PRO-2K-9-12+256',
    'ULTRA-9-4+64','ULTRA-2K-9-8+128'
]]

TABLETS_10 = [t for t in TABLET_FMT if t not in TABLETS_9]

# ══════════════════════════════════════════════════════════
# FUNCTII
# ══════════════════════════════════════════════════════════

def get_kit_num(kit):
    """Extrage numarul din codul kitului (ex: KIT-044 -> 044, KIT-500NEW -> 500NEW)"""
    m = re.search(r'KIT-(.+)', kit, re.IGNORECASE)
    return m.group(1) if m else kit

def make_title(kit, tablet):
    """Genereaza titlul produsului dupa logica EdoTec"""
    car = KIT_CAR.get(kit, f'Navigatie {kit}')
    num = get_kit_num(kit)
    letter, text = TABLET_FMT.get(tablet, ('Kit', tablet))
    return f'{car} {letter}-{num} {text}'

def make_code(kit, tablet, adaptor=False):
    """Genereaza codul produsului"""
    code = f'{kit}+{tablet}'
    if adaptor:
        code += '+KIT-10-9'
    return code

def generate_all(price_lookup=None):
    """
    Genereaza toate combinatiile.
    price_lookup: dict optional {(kit.upper(), tablet.upper()): price}
    Returneaza lista de dictionare cu: cod, titlu, pret, kit, tableta, frame
    """
    rows = []
    price_lookup = price_lookup or {}

    # Rame 9" + tablete 9"
    for kit in FRAMES_9:
        for tablet in TABLETS_9:
            code = make_code(kit, tablet)
            title = make_title(kit, tablet)
            price = price_lookup.get((kit.upper(), tablet.upper()), '')
            rows.append({
                'cod': code,
                'titlu': title,
                'pret': price,
                'kit': kit,
                'tableta': tablet,
                'frame': '9"',
                'adaptor': False
            })

    # Rame 10" + tablete 10" (native)
    for kit in FRAMES_10:
        for tablet in TABLETS_10:
            code = make_code(kit, tablet)
            title = make_title(kit, tablet)
            price = price_lookup.get((kit.upper(), tablet.upper()), '')
            rows.append({
                'cod': code,
                'titlu': title,
                'pret': price,
                'kit': kit,
                'tableta': tablet,
                'frame': '10"',
                'adaptor': False
            })

        # Rame 10" + tablete 9" cu adaptor KIT-10-9
        for tablet in TABLETS_9:
            code = make_code(kit, tablet, adaptor=True)
            title = make_title(kit, tablet)
            price = price_lookup.get((kit.upper(), tablet.upper()), '')
            rows.append({
                'cod': code,
                'titlu': title,
                'pret': price,
                'kit': kit,
                'tableta': tablet + '+KIT-10-9',
                'frame': '10"(adaptor)',
                'adaptor': True
            })

    return rows

def export_csv(rows, filepath='kit_navigatie_export.csv'):
    """Exporta in CSV pentru import pe site"""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['cod','titlu','pret','kit','tableta','frame'])
        writer.writeheader()
        writer.writerows(rows)
    print(f'Exportat {len(rows)} produse in {filepath}')

# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
if __name__ == '__main__':
    rows = generate_all()
    total = len(rows)
    frames9_count = sum(1 for r in rows if r['frame'] == '9"')
    frames10_count = sum(1 for r in rows if r['frame'] == '10"')
    adaptor_count = sum(1 for r in rows if r['adaptor'])

    print(f'Total produse: {total}')
    print(f'  Rame 9": {frames9_count}')
    print(f'  Rame 10" native: {frames10_count}')
    print(f'  Rame 10" cu adaptor: {adaptor_count}')
    print()
    print('Exemple titluri generate:')
    for r in rows[:5]:
        print(f'  {r["cod"]}')
        print(f'  -> {r["titlu"]}')
        print()

    export_csv(rows)
