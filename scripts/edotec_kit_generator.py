#!/usr/bin/env python3
"""
EdoTec Kit Navigatie Generator
================================
Genereaza toate combinatiile cod produs + titlu pentru kituri de navigatie.

LOGICA:
  - Rame 9" → combinate DOAR cu tablete 9"
  - Rame 9" EXCLUSIVE (marcate cu *) → idem, DOAR 9" (rama fizica permite max 9")
  - Rame 10" → combinate cu tablete 10" (native) + tablete 9" cu adaptor KIT-10-9
  - Rame marcate DOAR9 (de ex. cele cu 9 incercuit pe lista fizica) → merg DOAR cu tablete 9"

ACTUALIZARE PENTRU KITURI NOI:
  1. Adauga kitul nou in FRAMES_9 sau FRAMES_10
  2. Adauga masina in KIT_CAR
  3. Ruleaza scriptul
"""

import re
import csv
import json
import sys
from pathlib import Path

# ══════════════════════════════════════════════════════════
# CONFIGURARE RAME (KITURI)
# Conventie: toate codurile sunt string-uri cu prefix KIT-
# Kiturile cu 9 incercuit pe lista fizica → doar in FRAMES_9 (nu se combina cu 10/13")
# ══════════════════════════════════════════════════════════

# ── RAME 9" (inclusiv toate cele cu 9 incercuit / DOAR9) ──
FRAMES_9 = [
    # ─── EXISTENTE ───
    'KIT-044',      # Honda Civic 2005-2011
    'KIT-124',      # Suzuki SX4 2006-2013
    'KIT-173',      # Volvo XC90 (173 pe lista - confirmat 9")
    'KIT-179',      # Suzuki Swift 2010-2017
    'KIT-212',      # Mazda CX-5 2012- Manual  [CERC - DOAR9]
    'KIT-219',      # BMW X1 E84
    'KIT-223',      # Mazda 6 2013-2017  [CERC - DOAR9]
    'KIT-469',      # Honda CRV 2012-2016
    'KIT-500NEW',   # Fiat 500 2015-2021
    'KIT-517',      # Hyundai i20 2015-2018
    'KIT-1058',     # Hyundai Kona
    'KIT-1135',     # Hyundai Tucson 2019-
    'KIT-1142',     # VW Touareg 2012-2019

    # ─── NOI DIN LISTA - HYUNDAI / KIA ───
    'KIT-BONO15',       # Iveco Daily 15
    'KIT-DUCATO',       # Fiat Ducato
    'KIT-STILO',        # Fiat Stilo
    'KIT-FREMONT',      # Fiat Fremont
    'KIT-DUCATO-HIGH',  # Fiat Ducato High
    'KIT-DAILY',        # Iveco Daily
    'KIT-DAILY20',      # Iveco Daily 2020
    'KIT-H1',           # Hyundai H1
    'KIT-H20-MAN',      # Hyundai H20 Manual
    'KIT-IX20-AUF',     # Hyundai IX20 AUF
    'KIT-IONIA',        # Hyundai Ioniq
    'KIT-IX55',         # Hyundai IX55
    'KIT-I30-AUTO',     # Hyundai I30 Auto
    'KIT-I30-MAN',      # Hyundai I30 Manual
    'KIT-H350',         # Hyundai H350
    'KIT-IAO2007',      # Hyundai IAO 2007
    'KIT-VELOSTER',     # Hyundai Veloster
    'KIT-ACCENT',       # Hyundai Accent
    'KIT-GETZ',         # Hyundai Getz
    'KIT-I20-2012',     # Hyundai i20 2012
    'KIT-I40',          # Hyundai i40
    'KIT-GENESIS',      # Hyundai Genesis

    # ─── TOYOTA ───
    'KIT-P30-2011',     # Toyota P30 2011
    'KIT-SANTAFE-OLA',  # Hyundai Santa Fe OLA
    'KIT-4RUNNER',      # Toyota 4Runner
    'KIT-RAW4-OCA',     # Toyota RAW4 OCA
    'KIT-YARIS09',      # Toyota Yaris 09
    'KIT-YARIS10',      # Toyota Yaris 10
    'KIT-YARIS2020',    # Toyota Yaris 2020  [CERC - DOAR9]
    'KIT-TOYOTA-UNIV',  # Toyota Universal
    'KIT-AURIS15',      # Toyota Auris 15
    'KIT-AURIS13',      # Toyota Auris 13
    'KIT-AURIS2017',    # Toyota Auris 2017
    'KIT-AVENSIS03',    # Toyota Avensis 03
    'KIT-CHA-A',        # Toyota C-HR A
    'KIT-MY2AIN',       # Toyota MY2AIN
    'KIT-TY12',         # Toyota TY12
    'KIT-TY50',         # Toyota TY50
    'KIT-J120',         # Toyota J120
    'KIT-APIUS5PLUS',   # Toyota Alphard 5 Plus  [CERC - DOAR9]
    'KIT-PRIUS',        # Toyota Prius  [CERC - DOAR9]
    'KIT-TY39',         # Toyota TY39  [CERC - DOAR9]

    # ─── SEAT / MERCEDES ───
    'KIT-TENIOS',       # Tenios
    'KIT-ALTER',        # Alter
    'KIT-LEON5',        # Seat Leon 5
    'KIT-NAZ',          # Seat NAZ  [CERC - DOAR9]
    'KIT-ATECA',        # Seat Ateca
    'KIT-ANOMA',        # Seat Anoma  [CERC - DOAR9]
    'KIT-A-CLASSE-OLA', # Mercedes A Classe OLA  [CERC - DOAR9]
    'KIT-SLK',          # Mercedes SLK
    'KIT-W163',         # Mercedes W163
    'KIT-W200',         # Mercedes W200
    'KIT-W22N3',        # Mercedes W22N3
    'KIT-CCKL',         # Mercedes CCKL
    'KIT-W204',         # Mercedes W204
    'KIT-GLK',          # Mercedes GLK
    'KIT-W20Y-N45',     # Mercedes W20Y N45
    'KIT-MORRA2',       # Mercedes Sprinter MORRA
    'KIT-MORITA1',      # Mercedes MORITA
    'KIT-ASTRAAK',      # Opel Astra AK
    'KIT-ASTRAH',       # Opel Astra H
    'KIT-MANUA',        # MANUA
    'KIT-PAGNAC',       # PAGNAC  [CERC - DOAR9]
    'KIT-PAGNIA19',     # PAGNIA 19
    'KIT-NARL',         # NARL

    # ─── MAZDA / CITROEN / HONDA / MITSUBISHI ───
    'KIT-MAZDA2',       # Mazda 2
    'KIT-CX3',          # Mazda CX-3
    'KIT-MZ22',         # Mazda MZ-22
    'KIT-CX5',          # Mazda CX-5
    'KIT-MAZDA6-18',    # Mazda 6 2018
    'KIT-MZA6',         # Mazda 6
    'KIT-CX-HIGH',      # Mazda CX High
    'KIT-JUMPY16',      # Citroen Jumpy 16
    'KIT-CZ-LOW',       # Citroen CZ Low
    'KIT-AIRCROSS',     # Citroen Aircross
    'KIT-C3-09',        # Citroen C3 09
    'KIT-BERLINGO',     # Citroen Berlingo
    'KIT-HATCHMACK',    # Hatchback
    'KIT-CIVIC',        # Honda Civic
    'KIT-INSIGHT',      # Honda Insight
    'KIT-CRV19',        # Honda CRV 19
    'KIT-CRZ',          # Honda CR-Z
    'KIT-JAZZ',         # Honda Jazz
    'KIT-MARZOSTAN',    # Marzostan
    'KIT-LANCER07',     # Mitsubishi Lancer 07
    'KIT-RIO2020',      # Kia Rio 2020
    'KIT-COBRAS2006',   # Cobras 2006

    # ─── KIA / NISSAN ───
    'KIT-CARNIVAL2006', # Kia Carnival 2006
    'KIT-MOMENTO12',    # Kia Momento 12
    'KIT-SOUL2014',     # Kia Soul 2014
    'KIT-STONIC',       # Kia Stonic
    'KIT-RIO11',        # Kia Rio 11
    'KIT-SORENTO2020',  # Kia Sorento 2020
    'KIT-KING',         # Kia King
    'KIT-SOUL',         # Kia Soul
    'KIT-CEED18',       # Kia Ceed 18
    'KIT-CEED10',       # Kia Ceed 10
    'KIT-SPONTAGE19',   # Kia Sportage 19
    'KIT-SORENTO-NAV',  # Kia Sorento NAV
    'KIT-CEEN7',        # Kia Ceed 7
    'KIT-PATROL',       # Nissan Patrol
    'KIT-NAV5',         # Nissan Navara 5
    'KIT-NAV-OEM',      # Nissan Navara OEM
    'KIT-NAVANA',       # Nissan Navana
    'KIT-MURANO2010',   # Nissan Murano 2010
    'KIT-MICRA2003',    # Nissan Micra 2003  [CERC - DOAR9]
    'KIT-LEAF',         # Nissan Leaf
    'KIT-MACNA',        # Nissan Macna
    'KIT-MURANO',       # Nissan Murano
    'KIT-MICRA2010',    # Nissan Micra 2010
    'KIT-JUKE',         # Nissan Juke
    'KIT-NAVANA17',     # Nissan Navana 17
    'KIT-PATNOLOLA',    # Nissan Pathfinder OLA

    # ─── KIT CODURI OVALE (DOAR9) ───
    'KIT-R62',          # R62  [CERC]
    'KIT-3702',         # 3702  [CERC]
    'KIT-359',          # 359  [CERC]
    'KIT-574',          # 574  [CERC]
    'KIT-SMART05',      # Smart 05  [CERC]
    'KIT-TIVOLI2015',   # Tivoli 2015  [CERC]
    'KIT-RETON',        # Reton  [CERC]
    'KIT-012',          # 012  [CERC]
    'KIT-042',          # 042  [CERC]
    'KIT-068',          # 068  [CERC]
    'KIT-145',          # 145  [CERC]
    'KIT-038',          # 038  [CERC]
    'KIT-097',          # 097  [CERC]
    'KIT-092',          # 092  [CERC]
    'KIT-093',          # 093  [CERC]
    'KIT-083',          # 083  [CERC]
    'KIT-R70',          # R70  [CERC]
    'KIT-CT',           # CT  [CERC]
    'KIT-LS2006',       # LS2006  [CERC]
    'KIT-CT-HIGH',      # CT High  [CERC]
    'KIT-2023',         # 2023  [CERC]
    'KIT-939',          # 939  [CERC]
    'KIT-325',          # 325  [CERC]
    'KIT-256',          # 256  [CERC]
    'KIT-232',          # 232  [CERC]
    'KIT-463',          # 463  [CERC]
    'KIT-456',          # 456  [CERC]
    'KIT-DISCOVERY3',   # Land Rover Discovery 3  [CERC]
    'KIT-MINI01',       # Mini 01  [CERC]
    'KIT-MINI02',       # Mini 02  [CERC]
    'KIT-MINI03',       # Mini 03  [CERC]
    'KIT-MINI04',       # Mini 04  [CERC]
    'KIT-215',          # 215  [CERC]
    'KIT-209',          # 209  [CERC]
    'KIT-173LOW',       # 173 Low  [CERC]
    'KIT-368LEVIN',     # 368 Levin  [CERC]
    'KIT-377',          # 377  [CERC]
    'KIT-377SINC',      # 377 SINC  [CERC]

    # ─── ALFA ROMEO / AUDI / BMW [CERC - DOAR9] ───
    'KIT-068-BUTONS',   # 068 Butons  [CERC - DOAR9]
    'KIT-9030',         # Alfa 9030  [CERC - DOAR9]
    'KIT-9030-FACELIFT',# Alfa 9030 Facelift
    'KIT-GIULIETTA',    # Alfa Giulietta
    'KIT-ALFA159',      # Alfa Romeo 159
    'KIT-A6-C6',        # Audi A6 C6  [CERC - DOAR9]
    'KIT-Q7',           # Audi Q7  [CERC - DOAR9]
    'KIT-Q5',           # Audi Q5  [CERC - DOAR9]
    'KIT-Q5-HIGH',      # Audi Q5 High  [CERC - DOAR9]
    'KIT-F30-NBT',      # BMW F30 NBT  [CERC - DOAR9]
    'KIT-BMW117',       # BMW 117  [CERC - DOAR9]
    'KIT-BMW117-MAN',   # BMW 117 Manual  [CERC - DOAR9]
    'KIT-E90',          # BMW E90  [CERC - DOAR9]
    'KIT-XS-CIC',       # XS CIC  [CERC - DOAR9]
    'KIT-XS-CCC',       # XS CCC  [CERC - DOAR9]

    # ─── VW [unele CERC - DOAR9] ───
    'KIT-CADDY2022',    # VW Caddy 2022
    'KIT-POLO',         # VW Polo
    'KIT-TOUAREG-OLA',  # VW Touareg OLA
    'KIT-AMAROK',       # VW Amarok
    'KIT-SHARAN',       # VW Sharan
    'KIT-CARAVELLE',    # VW Caravelle
    'KIT-GOLF6',        # VW Golf 6  [CERC - DOAR9]
    'KIT-B5-V2',        # VW B5 V2
    'KIT-CNTUR',        # Cntur

    # ─── RENAULT / DACIA / SKODA ───
    'KIT-KOLEOS',       # Renault Koleos
    'KIT-RANGOO',       # Renault Kangoo
    'KIT-RTO9',         # Renault RTO9
    'KIT-CCIO5',        # CCIO5
    'KIT-RAPIA',        # Dacia Rapia
    'KIT-KONLAQ2022',   # Skoda Kodiaq 2022
    'KIT-LOGAN',        # Dacia Logan
    'KIT-AUSTEN2023',   # Dacia Duster 2023
    'KIT-DOTKEN',       # Dotken
    'KIT-DACIA',        # Dacia
    'KIT-SANDERO15',    # Dacia Sandero 15
    'KIT-SANDENO',      # Dacia Sandero
    'KIT-8951',         # 8951
    'KIT-8951HIGH',     # 8951 High
    'KIT-2265',         # 2265

    # ─── FORD ───
    'KIT-MONDEO2004',   # Ford Mondeo 2004
    'KIT-MONDEO2009VZ', # Ford Mondeo 2009 VZ
    'KIT-FOCUS4',       # Ford Focus 4
    'KIT-TOURNEO',      # Ford Tourneo
    'KIT-FORD-OVAL',    # Ford Oval
    'KIT-SMAX-NAUI',    # Ford S-Max NAUI
    'KIT-MONDEO2001',   # Ford Mondeo 2001
    'KIT-TOURNEO-CUST', # Ford Tourneo Custom
    'KIT-F150',         # Ford F150
    'KIT-KA',           # Ford Ka  [CERC - DOAR9]
    'KIT-KUGA',         # Ford Kuga  [CERC - DOAR9]
    'KIT-MUSTANG6',     # Ford Mustang 6
    'KIT-MONDEO-NAVIO', # Ford Mondeo Navio
    'KIT-RANGER',       # Ford Ranger
    'KIT-ECO-SPORT2018',# Ford Eco Sport 2018
    'KIT-EDGE-MIA',     # Ford Edge MIA
    'KIT-EDGE-HIGH',    # Ford Edge High  [CERC - DOAR9]
    'KIT-FIESTA-MH5',   # Ford Fiesta MH5
]

# ── RAME 10" ──
FRAMES_10 = [
    # ─── EXISTENTE ───
    'KIT-026',          # Mitsubishi ASX 2013-2017
    'KIT-338',          # Opel Insignia 2014-2016
    'KIT-361',          # Hyundai IX35
    'KIT-381',          # Toyota Land Cruiser L200

    # ─── NOI ───
    'KIT-BONO10',       # Iveco Daily 10
    'KIT-FIAT500-10',   # Fiat 500 (10")
    'KIT-TY59',         # Toyota TY59
    'KIT-W447',         # Mercedes W447
    'KIT-SPRINTER',     # Mercedes Sprinter
    'KIT-GLKN45',       # Mercedes GLK N45
    'KIT-TOVANO',       # Mercedes Tovano/Vito
    'KIT-VIANDOL9',     # Viandol 10
    'KIT-TUCSON2021',   # Hyundai Tucson 2021
    'KIT-HY38',         # Hyundai 38
    'KIT-L100',         # Toyota L100
    'KIT-IANV1',        # IANV1
    'KIT-ESTIMA',       # Toyota Estima
    'KIT-AURIS2015',    # Toyota Auris 2015
    'KIT-HIGHLANDER',   # Toyota Highlander
    'KIT-HIGHLANDER2015',# Toyota Highlander 2015
    'KIT-AVENSIS15',    # Toyota Avensis 15
    'KIT-TUNARA07',     # Toyota Tunara 07
    'KIT-SEQOIA',       # Toyota Sequoia
    'KIT-CAMRY2015',    # Toyota Camry 2015
    'KIT-CAMRY2021',    # Toyota Camry 2021
    'KIT-CAMRY2018PLUS',# Toyota Camry 2018+
    'KIT-CAMRY12',      # Toyota Camry 12
    'KIT-CX4',          # Mazda CX-4
    'KIT-CX5-10',       # Mazda CX-5 10"
    'KIT-BERLINGO2021', # Citroen Berlingo 2021
    'KIT-C1-10',        # Citroen C1 10"
    'KIT-ACCNA-10',     # ACCNA 10
    'KIT-ACCBA2020',    # Accba 2020
    'KIT-FN-V',         # Honda FN-V
    'KIT-CIVIC2022',    # Honda Civic 2022
    'KIT-HRV2022',      # Honda HRV 2022
    'KIT-PILOT08',      # Honda Pilot 08
    'KIT-ECLIPSE',      # Mitsubishi Eclipse
    'KIT-OUTLANDER23',  # Mitsubishi Outlander 23
    'KIT-RX5-2020',     # Mitsubishi RX5 2020
    'KIT-CEED20',       # Kia Ceed 20
    'KIT-NOTE2012',     # Nissan Note 2012
    'KIT-PULSAR',       # Nissan Pulsar
    'KIT-IXTRAIL-OLA',  # Nissan X-Trail OLA
    'KIT-GIULIETTA-FL', # Alfa Giulietta Facelift
    'KIT-VW-CRAFTER',   # VW Crafter
    'KIT-TOURAN3',      # VW Touran 3
    'KIT-TOURAN1',      # VW Touran 1
    'KIT-TOURAN2',      # VW Touran 2
    'KIT-GOLF5-HAN',    # VW Golf 5 HAN
    'KIT-GOLF5-AUTO',   # VW Golf 5 Auto
    'KIT-JETTA15',      # VW Jetta 15
    'KIT-SPORTIVAN',    # Sportivan
    'KIT-TRAFIC2009',   # Renault Trafic 2009
    'KIT-LAGUNA',       # Renault Laguna
    'KIT-MASTER',       # Renault Master
    'KIT-EXPRESS2025',  # Renault Express 2025
    'KIT-OCTAVIA',      # Skoda Octavia
    'KIT-SUPERB2',      # Skoda Superb 2
    'KIT-NETI',         # NETI
    'KIT-PABIA2',       # Skoda Fabia 2
    'KIT-FAMIA',        # Skoda Fabia
    'KIT-KAMIQ',        # Skoda Kamiq
    'KIT-6928',         # 6928
    'KIT-HONEOCCIHA',   # Honda Occiha
    'KIT-FIESTA2020',   # Ford Fiesta 2020
    'KIT-MUSTANG-OLD',  # Ford Mustang OLD
    'KIT-MONDEO-NAVIO10',# Ford Mondeo Navio 10
    'KIT-TRANSIT2019B', # Ford Transit 2019B
    'KIT-TRANSIT2019A', # Ford Transit 2019A
]

# ══════════════════════════════════════════════════════════
# MASINA PER KIT
# ══════════════════════════════════════════════════════════
KIT_CAR = {
    # ─── EXISTENTE ───
    'KIT-026':    'Navigatie MITSUBISHI ASX 2013-2017',
    'KIT-044':    'Navigatie Honda Civic 2005-2011',
    'KIT-124':    'Navigatie Suzuki SX4 2006-2013',
    'KIT-173':    'Navigatie Volvo XC90',
    'KIT-179':    'Navigatie Suzuki Swift 2010-2017',
    'KIT-212':    'Navigatie MAZDA CX-5 2012 Manual',
    'KIT-219':    'Navigatie BMW X1 E84',
    'KIT-223':    'Navigatie Mazda 6 2013-2017',
    'KIT-338':    'Navigatie Opel Insignia 2014-2016',
    'KIT-361':    'Navigatie Hyundai IX35',
    'KIT-381':    'Navigatie TOYOTA Land Cruiser L200',
    'KIT-469':    'Navigatie Honda CRV 2012-2016',
    'KIT-500NEW': 'Navigatie Fiat 500 2015-2021',
    'KIT-517':    'Navigatie Hyundai i20 2015-2018',
    'KIT-1058':   'Navigatie Hyundai Kona',
    'KIT-1135':   'Navigatie Hyundai Tucson 2019',
    'KIT-1142':   'Navigatie VW Touareg 2012-2019',
    # ─── HYUNDAI / FIAT / IVECO ───
    'KIT-BONO10':       'Navigatie Iveco Daily 10',
    'KIT-BONO15':       'Navigatie Iveco Daily 15',
    'KIT-DUCATO':       'Navigatie Fiat Ducato',
    'KIT-STILO':        'Navigatie Fiat Stilo',
    'KIT-FREMONT':      'Navigatie Fiat Fremont',
    'KIT-FIAT500-10':   'Navigatie Fiat 500',
    'KIT-DUCATO-HIGH':  'Navigatie Fiat Ducato High',
    'KIT-DAILY':        'Navigatie Iveco Daily',
    'KIT-DAILY20':      'Navigatie Iveco Daily 2020',
    'KIT-H1':           'Navigatie Hyundai H1',
    'KIT-H20-MAN':      'Navigatie Hyundai H1 Manual',
    'KIT-IX20-AUF':     'Navigatie Hyundai IX20',
    'KIT-IONIA':        'Navigatie Hyundai Ioniq',
    'KIT-IX55':         'Navigatie Hyundai IX55',
    'KIT-I30-AUTO':     'Navigatie Hyundai i30 Auto',
    'KIT-I30-MAN':      'Navigatie Hyundai i30 Manual',
    'KIT-H350':         'Navigatie Hyundai H350',
    'KIT-IAO2007':      'Navigatie Hyundai IAO 2007',
    'KIT-VELOSTER':     'Navigatie Hyundai Veloster',
    'KIT-ACCENT':       'Navigatie Hyundai Accent',
    'KIT-GETZ':         'Navigatie Hyundai Getz',
    'KIT-HY38':         'Navigatie Hyundai 38',
    'KIT-I20-2012':     'Navigatie Hyundai i20 2012',
    'KIT-I40':          'Navigatie Hyundai i40',
    'KIT-GENESIS':      'Navigatie Hyundai Genesis',
    'KIT-TUCSON2021':   'Navigatie Hyundai Tucson 2021',
    # ─── TOYOTA ───
    'KIT-P30-2011':     'Navigatie Toyota P30 2011',
    'KIT-SANTAFE-OLA':  'Navigatie Hyundai Santa Fe OLA',
    'KIT-4RUNNER':      'Navigatie Toyota 4Runner',
    'KIT-RAW4-OCA':     'Navigatie Toyota RAV4 OCA',
    'KIT-YARIS09':      'Navigatie Toyota Yaris 09',
    'KIT-YARIS10':      'Navigatie Toyota Yaris 10',
    'KIT-YARIS2020':    'Navigatie Toyota Yaris 2020',
    'KIT-TOYOTA-UNIV':  'Navigatie Toyota Universal',
    'KIT-AURIS15':      'Navigatie Toyota Auris 15',
    'KIT-AURIS13':      'Navigatie Toyota Auris 13',
    'KIT-ESTIMA':       'Navigatie Toyota Estima',
    'KIT-AURIS2017':    'Navigatie Toyota Auris 2017',
    'KIT-AURIS2015':    'Navigatie Toyota Auris 2015',
    'KIT-HIGHLANDER':   'Navigatie Toyota Highlander',
    'KIT-HIGHLANDER2015':'Navigatie Toyota Highlander 2015',
    'KIT-AVENSIS03':    'Navigatie Toyota Avensis 03',
    'KIT-AVENSIS15':    'Navigatie Toyota Avensis 15',
    'KIT-CHA-A':        'Navigatie Toyota C-HR',
    'KIT-TUNARA07':     'Navigatie Toyota Tunara 07',
    'KIT-SEQOIA':       'Navigatie Toyota Sequoia',
    'KIT-CAMRY2015':    'Navigatie Toyota Camry 2015',
    'KIT-CAMRY2021':    'Navigatie Toyota Camry 2021',
    'KIT-CAMRY2018PLUS':'Navigatie Toyota Camry 2018+',
    'KIT-CAMRY12':      'Navigatie Toyota Camry 12',
    'KIT-APIUS5PLUS':   'Navigatie Toyota Alphard 5 Plus',
    'KIT-MY2AIN':       'Navigatie Toyota MY2AIN',
    'KIT-TY12':         'Navigatie Toyota TY12',
    'KIT-TY50':         'Navigatie Toyota TY50',
    'KIT-TY59':         'Navigatie Toyota TY59',
    'KIT-J120':         'Navigatie Toyota J120',
    'KIT-L100':         'Navigatie Toyota L100',
    'KIT-IANV1':        'Navigatie IANV1',
    'KIT-PRIUS':        'Navigatie Toyota Prius',
    'KIT-TY39':         'Navigatie Toyota TY39',
    # ─── SEAT / MERCEDES ───
    'KIT-TENIOS':       'Navigatie TENIOS',
    'KIT-ALTER':        'Navigatie ALTER',
    'KIT-LEON5':        'Navigatie Seat Leon 5',
    'KIT-NAZ':          'Navigatie Seat NAZ',
    'KIT-ATECA':        'Navigatie Seat Ateca',
    'KIT-ANOMA':        'Navigatie Seat ANOMA',
    'KIT-A-CLASSE-OLA': 'Navigatie Mercedes A Classe OLA',
    'KIT-SLK':          'Navigatie Mercedes SLK',
    'KIT-W163':         'Navigatie Mercedes ML W163',
    'KIT-W200':         'Navigatie Mercedes W200',
    'KIT-W22N3':        'Navigatie Mercedes W22N3',
    'KIT-W447':         'Navigatie Mercedes V-Clase W447',
    'KIT-SPRINTER':     'Navigatie Mercedes Sprinter',
    'KIT-CCKL':         'Navigatie Mercedes CCKL',
    'KIT-W204':         'Navigatie Mercedes C-Clase W204',
    'KIT-GLK':          'Navigatie Mercedes GLK',
    'KIT-W20Y-N45':     'Navigatie Mercedes W20Y N45',
    'KIT-GLKN45':       'Navigatie Mercedes GLK N45',
    'KIT-TOVANO':       'Navigatie Mercedes Vito/Viano',
    'KIT-VIANDOL9':     'Navigatie Viano OLA',
    'KIT-MORRA2':       'Navigatie Mercedes MORRA 2',
    'KIT-MORITA1':      'Navigatie Mercedes MORITA 1',
    'KIT-ASTRAAK':      'Navigatie Opel Astra AK',
    'KIT-ASTRAH':       'Navigatie Opel Astra H',
    'KIT-MANUA':        'Navigatie MANUA',
    'KIT-PAGNAC':       'Navigatie PAGNAC',
    'KIT-PAGNIA19':     'Navigatie PAGNIA 19',
    'KIT-NARL':         'Navigatie NARL',
    # ─── MAZDA / CITROEN / HONDA ───
    'KIT-MAZDA2':       'Navigatie Mazda 2',
    'KIT-CX3':          'Navigatie Mazda CX-3',
    'KIT-CX4':          'Navigatie Mazda CX-4',
    'KIT-MZ22':         'Navigatie Mazda MZ-22',
    'KIT-CX5':          'Navigatie Mazda CX-5',
    'KIT-CX5-10':       'Navigatie Mazda CX-5',
    'KIT-MAZDA6-18':    'Navigatie Mazda 6 2018',
    'KIT-MZA6':         'Navigatie Mazda 6',
    'KIT-CX-HIGH':      'Navigatie Mazda CX High',
    'KIT-JUMPY16':      'Navigatie Citroen Jumpy 16',
    'KIT-CZ-LOW':       'Navigatie Citroen CZ Low',
    'KIT-AIRCROSS':     'Navigatie Citroen C5 Aircross',
    'KIT-BERLINGO2021': 'Navigatie Citroen Berlingo 2021',
    'KIT-C3-09':        'Navigatie Citroen C3 09',
    'KIT-C1-10':        'Navigatie Citroen C1',
    'KIT-BERLINGO':     'Navigatie Citroen Berlingo',
    'KIT-ACCNA-10':     'Navigatie ACCNA',
    'KIT-HATCHMACK':    'Navigatie Hatchback',
    'KIT-ACCBA2020':    'Navigatie ACCBA 2020',
    'KIT-CIVIC':        'Navigatie Honda Civic',
    'KIT-INSIGHT':      'Navigatie Honda Insight',
    'KIT-CRV19':        'Navigatie Honda CRV 19',
    'KIT-CRZ':          'Navigatie Honda CR-Z',
    'KIT-FN-V':         'Navigatie Honda FN-V',
    'KIT-CIVIC2022':    'Navigatie Honda Civic 2022',
    'KIT-HRV2022':      'Navigatie Honda HRV 2022',
    'KIT-JAZZ':         'Navigatie Honda Jazz',
    'KIT-PILOT08':      'Navigatie Honda Pilot 08',
    'KIT-MARZOSTAN':    'Navigatie MARZOSTAN',
    'KIT-ECLIPSE':      'Navigatie Mitsubishi Eclipse',
    'KIT-OUTLANDER23':  'Navigatie Mitsubishi Outlander 23',
    'KIT-LANCER07':     'Navigatie Mitsubishi Lancer 07',
    'KIT-RX5-2020':     'Navigatie Mitsubishi RX5 2020',
    'KIT-RIO2020':      'Navigatie Kia Rio 2020',
    'KIT-COBRAS2006':   'Navigatie Cobras 2006',
    # ─── KIA / NISSAN ───
    'KIT-CARNIVAL2006': 'Navigatie Kia Carnival 2006',
    'KIT-MOMENTO12':    'Navigatie Kia Momento 12',
    'KIT-SOUL2014':     'Navigatie Kia Soul 2014',
    'KIT-STONIC':       'Navigatie Kia Stonic',
    'KIT-RIO11':        'Navigatie Kia Rio 11',
    'KIT-SORENTO2020':  'Navigatie Kia Sorento 2020',
    'KIT-KING':         'Navigatie Kia King',
    'KIT-SOUL':         'Navigatie Kia Soul',
    'KIT-CEED18':       'Navigatie Kia Ceed 18',
    'KIT-CEED20':       'Navigatie Kia Ceed 20',
    'KIT-CEED10':       'Navigatie Kia Ceed 10',
    'KIT-SPONTAGE19':   'Navigatie Kia Sportage 19',
    'KIT-SORENTO-NAV':  'Navigatie Kia Sorento NAV',
    'KIT-CEEN7':        'Navigatie Kia Ceed 7',
    'KIT-PATROL':       'Navigatie Nissan Patrol',
    'KIT-NAV5':         'Navigatie Nissan Navara 5',
    'KIT-NAV-OEM':      'Navigatie Nissan Navara OEM',
    'KIT-NAVANA':       'Navigatie Nissan Navara',
    'KIT-MURANO2010':   'Navigatie Nissan Murano 2010',
    'KIT-NOTE2012':     'Navigatie Nissan Note 2012',
    'KIT-MICRA2003':    'Navigatie Nissan Micra 2003',
    'KIT-LEAF':         'Navigatie Nissan Leaf',
    'KIT-MACNA':        'Navigatie Nissan Macna',
    'KIT-MURANO':       'Navigatie Nissan Murano',
    'KIT-MICRA2010':    'Navigatie Nissan Micra 2010',
    'KIT-JUKE':         'Navigatie Nissan Juke',
    'KIT-NAVANA17':     'Navigatie Nissan Navara 17',
    'KIT-PULSAR':       'Navigatie Nissan Pulsar',
    'KIT-IXTRAIL-OLA':  'Navigatie Nissan X-Trail OLA',
    'KIT-PATNOLOLA':    'Navigatie Nissan Pathfinder OLA',
    # ─── OVALE (kit coduri scurte) ───
    'KIT-R62':          'Navigatie KIT-R62',
    'KIT-3702':         'Navigatie KIT-3702',
    'KIT-359':          'Navigatie KIT-359',
    'KIT-574':          'Navigatie KIT-574',
    'KIT-SMART05':      'Navigatie Smart 05',
    'KIT-TIVOLI2015':   'Navigatie Ssangyong Tivoli 2015',
    'KIT-RETON':        'Navigatie Ssangyong Rexton',
    'KIT-012':          'Navigatie KIT-012',
    'KIT-042':          'Navigatie KIT-042',
    'KIT-068':          'Navigatie KIT-068',
    'KIT-145':          'Navigatie KIT-145',
    'KIT-038':          'Navigatie KIT-038',
    'KIT-097':          'Navigatie KIT-097',
    'KIT-092':          'Navigatie KIT-092',
    'KIT-093':          'Navigatie KIT-093',
    'KIT-083':          'Navigatie KIT-083',
    'KIT-R70':          'Navigatie KIT-R70',
    'KIT-CT':           'Navigatie KIT-CT',
    'KIT-LS2006':       'Navigatie Lexus LS 2006',
    'KIT-CT-HIGH':      'Navigatie Lexus CT High',
    'KIT-2023':         'Navigatie KIT-2023',
    'KIT-939':          'Navigatie KIT-939',
    'KIT-325':          'Navigatie BMW Seria 3 325',
    'KIT-256':          'Navigatie KIT-256',
    'KIT-232':          'Navigatie KIT-232',
    'KIT-463':          'Navigatie KIT-463',
    'KIT-456':          'Navigatie KIT-456',
    'KIT-DISCOVERY3':   'Navigatie Land Rover Discovery 3',
    'KIT-MINI01':       'Navigatie Mini 01',
    'KIT-MINI02':       'Navigatie Mini 02',
    'KIT-MINI03':       'Navigatie Mini 03',
    'KIT-MINI04':       'Navigatie Mini 04',
    'KIT-215':          'Navigatie KIT-215',
    'KIT-209':          'Navigatie KIT-209',
    'KIT-173LOW':       'Navigatie Volvo XC90 Low',
    'KIT-368LEVIN':     'Navigatie Toyota 368 Levin',
    'KIT-377':          'Navigatie KIT-377',
    'KIT-377SINC':      'Navigatie KIT-377 SINC',
    # ─── ALFA / AUDI / BMW ───
    'KIT-068-BUTONS':   'Navigatie 068 Butons',
    'KIT-9030':         'Navigatie Alfa Romeo 9030',
    'KIT-9030-FACELIFT':'Navigatie Alfa Romeo 9030 Facelift',
    'KIT-GIULIETTA':    'Navigatie Alfa Giulietta',
    'KIT-GIULIETTA-FL': 'Navigatie Alfa Giulietta Facelift',
    'KIT-ALFA159':      'Navigatie Alfa Romeo 159',
    'KIT-A6-C6':        'Navigatie Audi A6 C6',
    'KIT-Q7':           'Navigatie Audi Q7',
    'KIT-Q5':           'Navigatie Audi Q5',
    'KIT-Q5-HIGH':      'Navigatie Audi Q5 High',
    'KIT-F30-NBT':      'Navigatie BMW F30 NBT',
    'KIT-BMW117':       'Navigatie BMW 117',
    'KIT-BMW117-MAN':   'Navigatie BMW 117 Manual',
    'KIT-E90':          'Navigatie BMW E90',
    'KIT-XS-CIC':       'Navigatie XS CIC',
    'KIT-XS-CCC':       'Navigatie XS CCC',
    # ─── VW ───
    'KIT-VW-CRAFTER':   'Navigatie VW Crafter',
    'KIT-CADDY2022':    'Navigatie VW Caddy 2022',
    'KIT-TOURAN3':      'Navigatie VW Touran 3',
    'KIT-TOURAN1':      'Navigatie VW Touran 1',
    'KIT-TOURAN2':      'Navigatie VW Touran 2',
    'KIT-POLO':         'Navigatie VW Polo',
    'KIT-TOUAREG-OLA':  'Navigatie VW Touareg OLA',
    'KIT-GOLF5-HAN':    'Navigatie VW Golf 5',
    'KIT-GOLF5-AUTO':   'Navigatie VW Golf 5 Auto',
    'KIT-AMAROK':       'Navigatie VW Amarok',
    'KIT-SHARAN':       'Navigatie VW Sharan',
    'KIT-CARAVELLE':    'Navigatie VW Caravelle',
    'KIT-GOLF6':        'Navigatie VW Golf 6',
    'KIT-JETTA15':      'Navigatie VW Jetta 15',
    'KIT-B5-V2':        'Navigatie VW B5 V2',
    'KIT-SPORTIVAN':    'Navigatie Sportivan',
    'KIT-CNTUR':        'Navigatie Cntur',
    'KIT-TRAFIC2009':   'Navigatie Renault Trafic 2009',
    # ─── RENAULT / DACIA / SKODA ───
    'KIT-KOLEOS':       'Navigatie Renault Koleos',
    'KIT-RANGOO':       'Navigatie Renault Kangoo',
    'KIT-LAGUNA':       'Navigatie Renault Laguna',
    'KIT-MASTER':       'Navigatie Renault Master',
    'KIT-EXPRESS2025':  'Navigatie Renault Express 2025',
    'KIT-RTO9':         'Navigatie Renault RTO9',
    'KIT-CCIO5':        'Navigatie CCIO5',
    'KIT-RAPIA':        'Navigatie Dacia RAPIA',
    'KIT-OCTAVIA':      'Navigatie Skoda Octavia',
    'KIT-SUPERB2':      'Navigatie Skoda Superb 2',
    'KIT-NETI':         'Navigatie NETI',
    'KIT-PABIA2':       'Navigatie Skoda Fabia 2',
    'KIT-FAMIA':        'Navigatie Skoda Fabia',
    'KIT-KAMIQ':        'Navigatie Skoda Kamiq',
    'KIT-KONLAQ2022':   'Navigatie Skoda Kodiaq 2022',
    'KIT-LOGAN':        'Navigatie Dacia Logan',
    'KIT-AUSTEN2023':   'Navigatie Dacia Duster 2023',
    'KIT-DOTKEN':       'Navigatie Dotken',
    'KIT-DACIA':        'Navigatie Dacia',
    'KIT-SANDERO15':    'Navigatie Dacia Sandero 15',
    'KIT-SANDENO':      'Navigatie Dacia Sandero',
    'KIT-8951':         'Navigatie 8951',
    'KIT-8951HIGH':     'Navigatie 8951 High',
    'KIT-6928':         'Navigatie 6928',
    'KIT-2265':         'Navigatie 2265',
    # ─── FORD ───
    'KIT-HONEOCCIHA':   'Navigatie Honda/Ford HONEOCCIHA',
    'KIT-FIESTA2020':   'Navigatie Ford Fiesta 2020',
    'KIT-MONDEO2004':   'Navigatie Ford Mondeo 2004',
    'KIT-MONDEO2009VZ': 'Navigatie Ford Mondeo 2009 VZ',
    'KIT-MUSTANG-OLD':  'Navigatie Ford Mustang OLD',
    'KIT-FOCUS4':       'Navigatie Ford Focus 4',
    'KIT-TOURNEO':      'Navigatie Ford Tourneo',
    'KIT-FORD-OVAL':    'Navigatie Ford OVAL',
    'KIT-SMAX-NAUI':    'Navigatie Ford S-Max NAUI',
    'KIT-MONDEO2001':   'Navigatie Ford Mondeo 2001',
    'KIT-TOURNEO-CUST': 'Navigatie Ford Tourneo Custom',
    'KIT-F150':         'Navigatie Ford F150',
    'KIT-KA':           'Navigatie Ford Ka',
    'KIT-KUGA':         'Navigatie Ford Kuga',
    'KIT-MUSTANG6':     'Navigatie Ford Mustang 6',
    'KIT-MONDEO-NAVIO': 'Navigatie Ford Mondeo NAVIO',
    'KIT-MONDEO-NAVIO10':'Navigatie Ford Mondeo NAVIO 10',
    'KIT-RANGER':       'Navigatie Ford Ranger',
    'KIT-ECO-SPORT2018':'Navigatie Ford Eco Sport 2018',
    'KIT-EDGE-MIA':     'Navigatie Ford Edge MIA',
    'KIT-EDGE-HIGH':    'Navigatie Ford Edge High',
    'KIT-FIESTA-MH5':   'Navigatie Ford Fiesta MH5',
    'KIT-TRANSIT2019B': 'Navigatie Ford Transit 2019B',
    'KIT-TRANSIT2019A': 'Navigatie Ford Transit 2019A',
}

# ══════════════════════════════════════════════════════════
# CONFIGURARE TABLETE / PLATFORME (neschimbat)
# ══════════════════════════════════════════════════════════
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
    m = re.search(r'KIT-(.+)', kit, re.IGNORECASE)
    return m.group(1) if m else kit

def make_title(kit, tablet):
    car = KIT_CAR.get(kit, f'Navigatie {kit}')
    num = get_kit_num(kit)
    letter, text = TABLET_FMT.get(tablet, ('Kit', tablet))
    return f'{car} {letter}-{num} {text}'

def make_code(kit, tablet, adaptor=False):
    code = f'{kit}+{tablet}'
    if adaptor:
        code += '+KIT-10-9'
    return code

def generate_all(price_lookup=None):
    rows = []
    price_lookup = price_lookup or {}
    for kit in FRAMES_9:
        for tablet in TABLETS_9:
            code = make_code(kit, tablet)
            title = make_title(kit, tablet)
            price = price_lookup.get((kit.upper(), tablet.upper()), '')
            rows.append({'cod': code, 'titlu': title, 'pret': price,
                         'kit': kit, 'tableta': tablet, 'frame': '9"', 'adaptor': False})
    for kit in FRAMES_10:
        for tablet in TABLETS_10:
            code = make_code(kit, tablet)
            title = make_title(kit, tablet)
            price = price_lookup.get((kit.upper(), tablet.upper()), '')
            rows.append({'cod': code, 'titlu': title, 'pret': price,
                         'kit': kit, 'tableta': tablet, 'frame': '10"', 'adaptor': False})
        for tablet in TABLETS_9:
            code = make_code(kit, tablet, adaptor=True)
            title = make_title(kit, tablet)
            price = price_lookup.get((kit.upper(), tablet.upper()), '')
            rows.append({'cod': code, 'titlu': title, 'pret': price,
                         'kit': kit, 'tableta': tablet + '+KIT-10-9', 'frame': '10"(adaptor)', 'adaptor': True})
    return rows

def export_csv(rows, filepath='kit_navigatie_export.csv'):
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['cod','titlu','pret','kit','tableta','frame'],
                                extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    print(f'Exportat {len(rows)} produse in {filepath}')

def export_removal_list(filepath='kit_navigatie_removal.csv'):
    """
    Genereaza lista de coduri de produs INVALIDE:
    kiturile din FRAMES_9 combinate cu tablete 10/13" (care NU ar trebui sa existe pe site).
    Foloseste aceasta lista ca sa stergi produsele de pe site.
    """
    rows = []
    for kit in FRAMES_9:
        # Combinatii invalide: kit 9" + tableta 10" (native, fara adaptor)
        for tablet in TABLETS_10:
            code = make_code(kit, tablet)
            title = make_title(kit, tablet)
            rows.append({'cod': code, 'titlu': title, 'kit': kit, 'tableta': tablet,
                         'motiv': 'Rama 9" incompatibila cu tableta 10/13"'})
        # Combinatii invalide: kit 9" + tableta 9" cu adaptor KIT-10-9
        for tablet in TABLETS_9:
            code = make_code(kit, tablet, adaptor=True)
            title = make_title(kit, tablet)
            rows.append({'cod': code, 'titlu': title, 'kit': kit,
                         'tableta': tablet + '+KIT-10-9',
                         'motiv': 'Rama 9" - adaptor KIT-10-9 invalid'})
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['cod','titlu','kit','tableta','motiv'])
        writer.writeheader()
        writer.writerows(rows)
    print(f'Lista removal: {len(rows)} produse invalide in {filepath}')
    return rows

if __name__ == '__main__':
    rows = generate_all()
    total = len(rows)
    frames9_count = sum(1 for r in rows if r['frame'] == '9"')
    frames10_count = sum(1 for r in rows if r['frame'] == '10"')
    adaptor_count = sum(1 for r in rows if r['adaptor'])

    print(f'Total produse VALIDE: {total}')
    print(f'  Rame 9": {frames9_count}')
    print(f'  Rame 10" native: {frames10_count}')
    print(f'  Rame 10" cu adaptor: {adaptor_count}')
    print()

    script_dir = Path(__file__).parent
    export_path = script_dir.parent / 'deploy-netlify' / 'kit_navigatie_export.csv'
    removal_path = script_dir.parent / 'deploy-netlify' / 'kit_navigatie_removal.csv'

    export_csv(rows, str(export_path))
    removal = export_removal_list(str(removal_path))
    print(f'\nProduse de STERS de pe site: {len(removal)}')
    print(f'CSV export:   {export_path}')
    print(f'CSV removal:  {removal_path}')
