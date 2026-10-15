"""
Alianzas económicas e internacionales por país (tabla aparte del panel).

Arma cuatro tablas en etl/alianzas/, todas con iso3 para unir con
datos_procesados/paises_anual.csv (clave iso3 + anio):

1. membresias_organizaciones.csv  -> una fila por episodio país-organización
   (año de ingreso, año de salida, estado). Bloques comerciales, OTAN, OPEP,
   BRICS, G20, OMC, OCDE, Mercosur, UE, etc.
2. alianzas_pais_anual.csv         -> panel país-año 2000-2025 con una columna
   0/1 por organización y conteos (acuerdos comerciales, pactos militares).
3. tratados_comerciales_pais.csv   -> una fila por país y acuerdo comercial
   (DESTA: TLC, uniones aduaneras, acuerdos de alcance parcial).
4. alianzas_militares_diadas.csv   -> pares de países con un pacto militar
   vigente cada año (ATOP: defensa, ofensiva, neutralidad, no agresión,
   consulta).

Fuentes (todas abiertas, descargadas de copias en GitHub con commit fijo):
- Correlates of War, Intergovernmental Organizations v3 (Pevehouse et al.
  2020): membresía anual 1816-2014 en ~530 organizaciones.
- DESTA 2.0 (Dür, Baccini y Elsig 2014; versión oct. 2020): acuerdos
  comerciales firmados 1948-2020 y sus miembros.
- ATOP 5.1 (Leeds et al. 2002), formato díada-año, 1815-2018, vía el paquete
  peacesciencer.
- Carga manual: cambios 2015-2025 de las organizaciones que COW cubre hasta
  2014 y organizaciones que COW no tiene (UE completa, eurozona, G7, G20,
  BRICS, OPEP+, T-MEC, CPTPP, RCEP, Alianza del Pacífico, ALBA, Unión
  Económica Euroasiática, AES, Quad, AUKUS, aliados extra-OTAN de EE. UU.).

Convención de años: un país cuenta como miembro en un año si lo era al 31 de
diciembre. El año de ingreso cuenta; el año de salida no (anio_salida es el
primer año en que ya no es miembro). anio_salida vacío = sigue siendo miembro.

Uso:  python extraer_alianzas_internacionales.py
Requiere: requests, pandas, pyreadr, pycountry
"""

import pathlib
import re
import unicodedata

import pandas as pd
import pycountry
import pyreadr
import requests

BASE = pathlib.Path(__file__).resolve().parent
CRUDOS = BASE / "crudos"
PANEL = BASE.parent / "datos_procesados" / "paises_anual.csv"
ANIOS_PANEL = range(2000, 2026)

RAW = "https://raw.githubusercontent.com"
DESCARGAS = {
    "cow_igo_year_formatv3.csv": f"{RAW}/globalgov/manyigos/49a498e0278e3dd9e2f10caf9a1a9c8b7249b8e1/data-raw/memberships/COW_MEM/igo_year_formatv3.csv",
    "desta_2_0.csv": f"{RAW}/globalgov/manytreaties/4bf79f94c78a9f9016bd55b99135b45208500631/data-raw/parties/DESTA/DESTA.csv",
    "atop_5_1_diada_anio.rda": f"{RAW}/svmiller/peacesciencer/fe150a2648056fbd4fbbbd833f0c9e437b2ed04b/data/atop_alliance.rda",
    "cow_estados.rda": f"{RAW}/svmiller/peacesciencer/fe150a2648056fbd4fbbbd833f0c9e437b2ed04b/data/cow_states.rda",
}

# ---------------------------------------------------------------------------
# Catálogo de organizaciones
# ---------------------------------------------------------------------------
# sigla -> (nombre en español, tipo, código en COW o None si es carga manual)
ORGANIZACIONES = {
    # Comercio e integración económica
    "OMC": ("Organización Mundial del Comercio", "económica-comercial", "WTO"),
    "OCDE": ("Organización para la Cooperación y el Desarrollo Económicos", "económica-comercial", "OECD"),
    "UE": ("Unión Europea (CEE/CE antes de 1993)", "económica-comercial", None),
    "EUROZONA": ("Zona euro (usa el euro como moneda oficial)", "económica-comercial", None),
    "AELC": ("Asociación Europea de Libre Comercio (EFTA)", "económica-comercial", "EFTA"),
    "UEE": ("Unión Económica Euroasiática", "económica-comercial", None),
    "MERCOSUR": ("Mercado Común del Sur", "económica-comercial", "Mercosur"),
    "CAN": ("Comunidad Andina", "económica-comercial", "Andean"),
    "ALADI": ("Asociación Latinoamericana de Integración", "económica-comercial", "LAIA"),
    "ALIANZA_PACIFICO": ("Alianza del Pacífico", "económica-comercial", None),
    "CARICOM": ("Comunidad del Caribe", "económica-comercial", "CARICOM"),
    "SICA": ("Sistema de la Integración Centroamericana", "económica-comercial", "SICA"),
    "TLCAN": ("Tratado de Libre Comercio de América del Norte (NAFTA)", "económica-comercial", "NAFTA"),
    "TMEC": ("Tratado entre México, Estados Unidos y Canadá (USMCA)", "económica-comercial", None),
    "APEC": ("Foro de Cooperación Económica Asia-Pacífico", "económica-comercial", "APEC"),
    "CPTPP": ("Tratado Integral y Progresista de Asociación Transpacífico", "económica-comercial", None),
    "RCEP": ("Asociación Económica Integral Regional (Asia-Pacífico)", "económica-comercial", None),
    "ASEAN": ("Asociación de Naciones del Sudeste Asiático", "económica-comercial", "ASEAN"),
    "SAARC": ("Asociación del Asia Meridional para la Cooperación Regional", "económica-comercial", "SAARC"),
    "CCG": ("Consejo de Cooperación del Golfo", "económica-comercial", "GCC"),
    "CEDEAO": ("Comunidad Económica de los Estados de África Occidental (ECOWAS)", "económica-comercial", "ECOWAS"),
    "UEMOA": ("Unión Económica y Monetaria de África Occidental", "económica-comercial", "UEMOA"),
    "CEMAC": ("Comunidad Económica y Monetaria de África Central", "económica-comercial", "CEMAC"),
    "SADC": ("Comunidad de Desarrollo de África Austral", "económica-comercial", "SADC"),
    "SACU": ("Unión Aduanera de África Austral", "económica-comercial", "SACU"),
    "COMESA": ("Mercado Común de África Oriental y Austral", "económica-comercial", "COMESA"),
    "EAC": ("Comunidad de África Oriental", "económica-comercial", "EAC"),
    # Energía
    "OPEP": ("Organización de Países Exportadores de Petróleo", "energética", "OPEC"),
    "OPEP_PLUS": ("OPEP+ (países fuera de la OPEP en la Declaración de Cooperación)", "energética", None),
    # Seguridad y defensa
    "OTAN": ("Organización del Tratado del Atlántico Norte", "militar-seguridad", "NATO"),
    "OTSC": ("Organización del Tratado de Seguridad Colectiva", "militar-seguridad", "CSTO"),
    "OCS": ("Organización de Cooperación de Shanghái", "militar-seguridad", "SCO"),
    "AUKUS": ("Pacto de seguridad Australia-Reino Unido-EE. UU.", "militar-seguridad", None),
    "QUAD": ("Diálogo de Seguridad Cuadrilateral", "militar-seguridad", None),
    "AES": ("Alianza de Estados del Sahel", "militar-seguridad", None),
    "MNNA_EEUU": ("Aliado principal extra-OTAN de EE. UU. (designación unilateral)", "militar-seguridad", None),
    # Foros y grupos de países
    "G7": ("Grupo de los Siete", "foro informal", None),
    "G8": ("Grupo de los Ocho (G7 + Rusia)", "foro informal", None),
    "G20": ("Grupo de los Veinte", "foro informal", None),
    "BRICS": ("BRICS (Brasil, Rusia, India, China, Sudáfrica y ampliación)", "foro informal", None),
    # Políticas y diplomáticas
    "UA": ("Unión Africana (OUA antes de 2002)", "política-diplomática", "AU"),
    "OEA": ("Organización de los Estados Americanos", "política-diplomática", "OAS"),
    "ALBA": ("Alianza Bolivariana para los Pueblos de Nuestra América", "política-diplomática", None),
    "LIGA_ARABE": ("Liga de los Estados Árabes", "política-diplomática", "LOAS"),
    "OCI": ("Organización de Cooperación Islámica", "política-diplomática", "OIC"),
    "CONSEJO_EUROPA": ("Consejo de Europa", "política-diplomática", "COE"),
    "COMMONWEALTH": ("Mancomunidad de Naciones (Commonwealth)", "política-diplomática", "ComSec"),
    "CEI": ("Comunidad de Estados Independientes", "política-diplomática", "CIS"),
}

# ---------------------------------------------------------------------------
# Carga manual 1: organizaciones que COW no cubre (o cubre mal)
# (sigla, [iso3...], anio_ingreso, anio_salida, estado, nota)
# ---------------------------------------------------------------------------
UE6 = ["BEL", "FRA", "DEU", "ITA", "LUX", "NLD"]
G7 = ["USA", "JPN", "DEU", "FRA", "GBR", "ITA"]
MANUAL = [
    # Unión Europea: COW empieza en 1993 (Maastricht); acá va desde la CEE
    ("UE", UE6, 1958, None, "pleno", "CEE desde el Tratado de Roma"),
    ("UE", ["DNK", "IRL"], 1973, None, "pleno", ""),
    ("UE", ["GBR"], 1973, 2020, "pleno", "Brexit: sale el 31-01-2020"),
    ("UE", ["GRC"], 1981, None, "pleno", ""),
    ("UE", ["PRT", "ESP"], 1986, None, "pleno", ""),
    ("UE", ["AUT", "FIN", "SWE"], 1995, None, "pleno", ""),
    ("UE", ["CYP", "CZE", "EST", "HUN", "LVA", "LTU", "MLT", "POL", "SVK", "SVN"], 2004, None, "pleno", ""),
    ("UE", ["BGR", "ROU"], 2007, None, "pleno", ""),
    ("UE", ["HRV"], 2013, None, "pleno", ""),
    # Zona euro
    ("EUROZONA", ["AUT", "BEL", "FIN", "FRA", "DEU", "IRL", "ITA", "LUX", "NLD", "PRT", "ESP"], 1999, None, "pleno", "billetes desde 2002"),
    ("EUROZONA", ["GRC"], 2001, None, "pleno", ""),
    ("EUROZONA", ["SVN"], 2007, None, "pleno", ""),
    ("EUROZONA", ["CYP", "MLT"], 2008, None, "pleno", ""),
    ("EUROZONA", ["SVK"], 2009, None, "pleno", ""),
    ("EUROZONA", ["EST"], 2011, None, "pleno", ""),
    ("EUROZONA", ["LVA"], 2014, None, "pleno", ""),
    ("EUROZONA", ["LTU"], 2015, None, "pleno", ""),
    ("EUROZONA", ["HRV"], 2023, None, "pleno", ""),
    ("EUROZONA", ["BGR"], 2026, None, "pleno", "adopta el euro el 01-01-2026"),
    # Grupos informales
    ("G7", G7, 1975, None, "pleno", "cumbre de Rambouillet"),
    ("G7", ["CAN"], 1976, None, "pleno", ""),
    ("G8", G7 + ["CAN"], 1997, 2014, "pleno", "formato G8 hasta la suspensión de Rusia"),
    ("G8", ["RUS"], 1997, 2014, "pleno", "suspendida en 2014 por la anexión de Crimea"),
    ("G20", ["ARG", "AUS", "BRA", "CAN", "CHN", "FRA", "DEU", "IND", "IDN", "ITA", "JPN", "KOR",
             "MEX", "RUS", "SAU", "ZAF", "TUR", "GBR", "USA"], 1999, None, "pleno",
     "además la UE (1999) y la Unión Africana (2023) como bloques"),
    ("BRICS", ["BRA", "RUS", "IND", "CHN"], 2009, None, "pleno", "primera cumbre BRIC en 2009"),
    ("BRICS", ["ZAF"], 2011, None, "pleno", "invitada en dic. 2010, primera cumbre en 2011"),
    ("BRICS", ["EGY", "ETH", "IRN", "ARE"], 2024, None, "pleno", "Arabia Saudita fue invitada y no confirmó"),
    ("BRICS", ["IDN"], 2025, None, "pleno", ""),
    ("OPEP_PLUS", ["AZE", "BHR", "BRN", "KAZ", "MYS", "MEX", "OMN", "RUS", "SDN", "SSD"], 2017, None, "pleno",
     "Declaración de Cooperación firmada el 10-12-2016; los miembros de la OPEP están en la sigla OPEP"),
    # América
    ("ALIANZA_PACIFICO", ["CHL", "COL", "MEX", "PER"], 2011, None, "pleno", "Declaración de Lima 2011; acuerdo marco 2012"),
    ("TMEC", ["USA", "MEX", "CAN"], 2020, None, "pleno", "reemplaza al TLCAN desde el 01-07-2020"),
    ("ALBA", ["VEN", "CUB"], 2004, None, "pleno", ""),
    ("ALBA", ["BOL"], 2006, 2019, "pleno", "sale en nov. 2019"),
    ("ALBA", ["BOL"], 2020, None, "pleno", "vuelve en nov. 2020"),
    ("ALBA", ["NIC"], 2007, None, "pleno", ""),
    ("ALBA", ["DMA"], 2008, None, "pleno", ""),
    ("ALBA", ["HND"], 2008, 2010, "pleno", "sale en ene. 2010"),
    ("ALBA", ["ECU"], 2009, 2018, "pleno", "sale en ago. 2018"),
    ("ALBA", ["VCT", "ATG"], 2009, None, "pleno", ""),
    ("ALBA", ["LCA"], 2013, None, "pleno", ""),
    ("ALBA", ["GRD", "KNA"], 2014, None, "pleno", ""),
    # Asia-Pacífico (años de entrada en vigor para cada país)
    ("CPTPP", ["AUS", "CAN", "JPN", "MEX", "NZL", "SGP"], 2018, None, "pleno", "en vigor el 30-12-2018"),
    ("CPTPP", ["VNM"], 2019, None, "pleno", ""),
    ("CPTPP", ["PER"], 2021, None, "pleno", ""),
    ("CPTPP", ["MYS"], 2022, None, "pleno", ""),
    ("CPTPP", ["CHL", "BRN"], 2023, None, "pleno", ""),
    ("CPTPP", ["GBR"], 2024, None, "pleno", "en vigor el 15-12-2024"),
    ("RCEP", ["AUS", "BRN", "KHM", "CHN", "JPN", "LAO", "NZL", "SGP", "THA", "VNM", "KOR", "MYS"], 2022, None, "pleno",
     "Myanmar ratificó pero su entrada en vigor está en disputa: no se incluye"),
    ("RCEP", ["IDN", "PHL"], 2023, None, "pleno", ""),
    ("QUAD", ["USA", "JPN", "IND", "AUS"], 2017, None, "pleno", "primer diálogo en 2007, inactivo 2008-2016"),
    ("AUKUS", ["AUS", "GBR", "USA"], 2021, None, "pleno", ""),
    # Eurasia y África
    ("UEE", ["RUS", "BLR", "KAZ", "ARM", "KGZ"], 2015, None, "pleno", "sucede a la Comunidad Económica Euroasiática"),
    ("AES", ["MLI", "BFA", "NER"], 2023, None, "pleno", "Carta de Liptako-Gourma; confederación desde 2024"),
    # OPEP completa (COW omite a Angola y fecha mal a Qatar y Gabón)
    ("OPEP", ["IRN", "IRQ", "KWT", "SAU", "VEN"], 1960, None, "pleno", "fundadores, Conferencia de Bagdad"),
    ("OPEP", ["QAT"], 1961, 2019, "pleno", "sale el 01-01-2019"),
    ("OPEP", ["IDN"], 1962, 2009, "pleno", "suspende su membresía en ene. 2009"),
    ("OPEP", ["IDN"], 2016, 2016, "pleno", "vuelve en ene. 2016 y se suspende en nov. 2016 (no cuenta al 31-12)"),
    ("OPEP", ["LBY"], 1962, None, "pleno", ""),
    ("OPEP", ["ARE"], 1967, None, "pleno", "Abu Dabi desde 1967; Emiratos Árabes Unidos desde 1974"),
    ("OPEP", ["DZA"], 1969, None, "pleno", ""),
    ("OPEP", ["NGA"], 1971, None, "pleno", ""),
    ("OPEP", ["ECU"], 1973, 1992, "pleno", "suspende su membresía en dic. 1992"),
    ("OPEP", ["ECU"], 2007, 2020, "pleno", "vuelve en oct. 2007; sale el 01-01-2020"),
    ("OPEP", ["GAB"], 1975, 1995, "pleno", "sale en ene. 1995"),
    ("OPEP", ["GAB"], 2016, None, "pleno", "vuelve en jul. 2016"),
    ("OPEP", ["AGO"], 2007, 2024, "pleno", "sale el 01-01-2024"),
    ("OPEP", ["GNQ"], 2017, None, "pleno", ""),
    ("OPEP", ["COG"], 2018, None, "pleno", ""),
    # Mercosur completo (COW codifica a Bolivia y Chile como plenos cuando eran asociados)
    ("MERCOSUR", ["ARG", "BRA", "URY"], 1991, None, "pleno", "Tratado de Asunción"),
    ("MERCOSUR", ["PRY"], 1991, 2012, "pleno", "Tratado de Asunción"),
    ("MERCOSUR", ["PRY"], 2012, 2013, "suspendido", "suspendido jun. 2012 - ago. 2013"),
    ("MERCOSUR", ["PRY"], 2013, None, "pleno", ""),
    ("MERCOSUR", ["VEN"], 2012, 2016, "pleno", ""),
    ("MERCOSUR", ["VEN"], 2016, None, "suspendido", "suspendida desde dic. 2016"),
    ("MERCOSUR", ["BOL"], 1996, 2024, "asociado", ""),
    ("MERCOSUR", ["BOL"], 2024, None, "pleno", "miembro pleno desde jul. 2024"),
    ("MERCOSUR", ["CHL"], 1996, None, "asociado", ""),
    ("MERCOSUR", ["PER"], 2003, None, "asociado", ""),
    ("MERCOSUR", ["COL", "ECU"], 2004, None, "asociado", ""),
    ("MERCOSUR", ["GUY", "SUR"], 2013, None, "asociado", ""),
    ("MERCOSUR", ["PAN"], 2024, None, "asociado", ""),
    # Comunidad de África Oriental completa (COW mezcla miembros de otros bloques)
    ("EAC", ["KEN", "TZA", "UGA"], 2000, None, "pleno", "tratado en vigor desde jul. 2000"),
    ("EAC", ["BDI", "RWA"], 2007, None, "pleno", ""),
    ("EAC", ["SSD"], 2016, None, "pleno", ""),
    ("EAC", ["COD"], 2022, None, "pleno", ""),
    ("EAC", ["SOM"], 2024, None, "pleno", ""),
    # Unión Africana completa (COW tiene huecos, p. ej. Guinea Ecuatorial sale en 2006)
    ("UA", ["DZA", "AGO", "BEN", "BWA", "BFA", "BDI", "CPV", "CMR", "CAF", "TCD", "COM", "COG", "COD",
            "CIV", "DJI", "EGY", "GNQ", "ERI", "SWZ", "ETH", "GAB", "GMB", "GHA", "GIN", "GNB", "KEN",
            "LSO", "LBR", "LBY", "MDG", "MWI", "MLI", "MRT", "MUS", "MOZ", "NAM", "NER", "NGA", "RWA",
            "STP", "SEN", "SYC", "SLE", "SOM", "ZAF", "SDN", "TZA", "TGO", "TUN", "UGA", "ZMB", "ZWE"],
     2002, None, "pleno", "la UA reemplaza a la OUA (1963) en jul. 2002; no se modelan suspensiones"),
    ("UA", ["SSD"], 2011, None, "pleno", ""),
    ("UA", ["MAR"], 2017, None, "pleno", "había dejado la OUA en 1984"),
    # Correcciones puntuales a COW (el episodio de COW se borra en BORRAR_COW y se carga este)
    ("OMC", ["HKG", "MAC"], 1995, None, "pleno", "territorios aduaneros, no están en COW"),
    ("OMC", ["MKD"], 2003, None, "pleno", "falta en COW"),
    ("APEC", ["HKG"], 1991, None, "pleno", "economía miembro, no está en COW"),
    ("OCDE", ["DEU"], 1961, None, "pleno", "Alemania Occidental hasta 1990"),
    ("OCDE", ["FIN"], 1969, None, "pleno", ""),
    ("CEDEAO", ["MRT"], 1975, 2000, "pleno", "sale en dic. 2000"),
    ("CEDEAO", ["CPV"], 1977, None, "pleno", ""),
    ("SADC", ["ZAF"], 1994, None, "pleno", ""),
    ("SADC", ["MUS"], 1995, None, "pleno", ""),
    ("SADC", ["COD"], 1997, None, "pleno", ""),
    ("SADC", ["SYC"], 1997, 2004, "pleno", "sale en jul. 2004"),
    ("SADC", ["SYC"], 2008, None, "pleno", ""),
    ("SADC", ["MDG"], 2005, 2009, "pleno", ""),
    ("SADC", ["MDG"], 2009, 2014, "suspendido", "suspendida tras el golpe de 2009"),
    ("SADC", ["MDG"], 2014, None, "pleno", ""),
    ("COMESA", ["ERI", "COD"], 1994, None, "pleno", ""),
    ("COMESA", ["SOM"], 2018, None, "pleno", "COW la incluye desde 1994, pero ingresa en 2018"),
    ("CEI", ["GEO"], 1993, 2009, "pleno", "sale en ago. 2009"),
    ("OTSC", ["UZB"], 2006, 2012, "pleno", "vuelve en 2006, suspende su participación en 2012"),
    ("AELC", ["FIN"], 1961, 1986, "asociado", ""),
    ("AELC", ["FIN"], 1986, 1995, "pleno", "pasa a la UE en 1995"),
    ("COMMONWEALTH", ["FJI"], 1970, 1987, "pleno", "sale tras el golpe de 1987"),
    ("COMMONWEALTH", ["FJI"], 1997, 2009, "pleno", "suspensiones parciales en 2000-2001 y 2006-2009"),
    ("COMMONWEALTH", ["FJI"], 2009, 2014, "suspendido", "suspendida por completo sep. 2009 - sep. 2014"),
    ("COMMONWEALTH", ["FJI"], 2014, None, "pleno", ""),
    ("COMMONWEALTH", ["NGA"], 1960, 1995, "pleno", ""),
    ("COMMONWEALTH", ["NGA"], 1995, 1999, "suspendido", "suspendida nov. 1995 - may. 1999"),
    ("COMMONWEALTH", ["NGA"], 1999, None, "pleno", ""),
    # Aliados principales extra-OTAN de EE. UU. (año de designación)
    ("MNNA_EEUU", ["AUS", "EGY", "ISR", "JPN", "KOR"], 1989, None, "pleno", ""),
    ("MNNA_EEUU", ["JOR"], 1996, None, "pleno", ""),
    ("MNNA_EEUU", ["NZL"], 1997, None, "pleno", ""),
    ("MNNA_EEUU", ["ARG"], 1998, None, "pleno", ""),
    ("MNNA_EEUU", ["BHR"], 2002, None, "pleno", ""),
    ("MNNA_EEUU", ["PHL", "THA", "TWN"], 2003, None, "pleno", "Taiwán: tratado como tal por ley, sin designación formal"),
    ("MNNA_EEUU", ["KWT", "MAR", "PAK"], 2004, None, "pleno", ""),
    ("MNNA_EEUU", ["AFG"], 2012, 2022, "pleno", "revocado en 2022"),
    ("MNNA_EEUU", ["TUN"], 2015, None, "pleno", ""),
    ("MNNA_EEUU", ["BRA"], 2019, None, "pleno", ""),
    ("MNNA_EEUU", ["COL", "QAT"], 2022, None, "pleno", ""),
    ("MNNA_EEUU", ["KEN"], 2024, None, "pleno", ""),
]

# Organizaciones de COW que se reemplazan enteras por la carga manual, y
# episodios puntuales de COW que se borran porque están mal (se recargan arriba).
REEMPLAZAR_COW = {"UE", "OPEP", "MERCOSUR", "EAC", "UA"}
BORRAR_COW = [("OMC", "DZA"),  # Argelia no es miembro de la OMC (es observadora)
              ("OCDE", "DEU"), ("OCDE", "FIN"), ("CEDEAO", "MRT"), ("CEDEAO", "CPV"),
              ("SADC", "ZAF"), ("SADC", "MUS"), ("SADC", "COD"), ("SADC", "SYC"), ("SADC", "MDG"),
              ("COMESA", "SOM"), ("COMESA", "ERI"), ("COMESA", "SSD"),  # Sudán del Sur no es miembro
              ("CEI", "GEO"), ("OTSC", "UZB"),
              ("AELC", "FIN"), ("COMMONWEALTH", "FJI"), ("COMMONWEALTH", "NGA")]

# Años de ingreso de COW corregidos tras comparar con Wikidata (P463 con fecha de inicio).
# El Commonwealth en COW arranca en 1965 (año de su Secretaría) y por eso los miembros
# más antiguos figuraban desde 1965; otros casos son errores puntuales.
AJUSTE_INGRESO = {
    ("COMMONWEALTH", "GBR"): 1931, ("COMMONWEALTH", "AUS"): 1931, ("COMMONWEALTH", "CAN"): 1931,
    ("COMMONWEALTH", "NZL"): 1931, ("COMMONWEALTH", "IND"): 1947, ("COMMONWEALTH", "PAK"): 1947,
    ("COMMONWEALTH", "LKA"): 1948, ("COMMONWEALTH", "GHA"): 1957, ("COMMONWEALTH", "MYS"): 1957,
    ("COMMONWEALTH", "CYP"): 1961, ("COMMONWEALTH", "SLE"): 1961, ("COMMONWEALTH", "TZA"): 1961,
    ("COMMONWEALTH", "TTO"): 1962, ("COMMONWEALTH", "UGA"): 1962, ("COMMONWEALTH", "JAM"): 1962,
    ("COMMONWEALTH", "KEN"): 1963, ("COMMONWEALTH", "TON"): 1970, ("COMMONWEALTH", "WSM"): 1970,
    ("COMMONWEALTH", "KIR"): 1979,
    ("CARICOM", "BHS"): 1983, ("CONSEJO_EUROPA", "FIN"): 1989, ("CONSEJO_EUROPA", "DEU"): 1950,
    ("OCI", "CMR"): 1974,
}

# ---------------------------------------------------------------------------
# Carga manual 2: cambios desde 2015 en organizaciones que COW cubre hasta 2014
# (y algunas correcciones de COW). (sigla, iso3, accion, anio, estado, nota)
# "ingreso" cierra cualquier episodio abierto del país en esa organización
# (por ejemplo, observador -> miembro) y abre uno nuevo.
# ---------------------------------------------------------------------------
CAMBIOS = [
    ("OMC", "SYC", "ingreso", 2015, "pleno", ""),
    ("OMC", "KAZ", "ingreso", 2015, "pleno", ""),
    ("OMC", "LBR", "ingreso", 2016, "pleno", ""),
    ("OMC", "AFG", "ingreso", 2016, "pleno", ""),
    ("OMC", "COM", "ingreso", 2024, "pleno", ""),
    ("OMC", "TLS", "ingreso", 2024, "pleno", ""),
    ("OCDE", "LVA", "ingreso", 2016, "pleno", ""),
    ("OCDE", "LTU", "ingreso", 2018, "pleno", ""),
    ("OCDE", "COL", "ingreso", 2020, "pleno", ""),
    ("OCDE", "CRI", "ingreso", 2021, "pleno", ""),
    ("TLCAN", "USA", "salida", 2020, None, "reemplazado por el T-MEC"),
    ("TLCAN", "MEX", "salida", 2020, None, "reemplazado por el T-MEC"),
    ("TLCAN", "CAN", "salida", 2020, None, "reemplazado por el T-MEC"),
    ("ASEAN", "TLS", "ingreso", 2025, "pleno", "admitido en oct. 2025"),
    ("COMESA", "TUN", "ingreso", 2018, "pleno", ""),
    ("SADC", "COM", "ingreso", 2017, "pleno", ""),
    ("CEDEAO", "BFA", "salida", 2025, None, "salida efectiva el 29-01-2025"),
    ("CEDEAO", "MLI", "salida", 2025, None, "salida efectiva el 29-01-2025"),
    ("CEDEAO", "NER", "salida", 2025, None, "salida efectiva el 29-01-2025"),
    ("OTAN", "MNE", "ingreso", 2017, "pleno", ""),
    ("OTAN", "MKD", "ingreso", 2020, "pleno", ""),
    ("OTAN", "FIN", "ingreso", 2023, "pleno", ""),
    ("OTAN", "SWE", "ingreso", 2024, "pleno", ""),
    ("OCS", "IND", "ingreso", 2017, "pleno", ""),
    ("OCS", "PAK", "ingreso", 2017, "pleno", ""),
    ("OCS", "IRN", "ingreso", 2023, "pleno", ""),
    ("OCS", "BLR", "ingreso", 2024, "pleno", ""),
    ("LIGA_ARABE", "SYR", "ingreso", 2011, "suspendido", "suspendida en nov. 2011"),
    ("LIGA_ARABE", "SYR", "ingreso", 2023, "pleno", "readmitida en may. 2023"),
    ("OEA", "VEN", "salida", 2019, None, "denuncia de la Carta efectiva en abr. 2019"),
    ("OEA", "NIC", "salida", 2023, None, "denuncia de la Carta efectiva en nov. 2023"),
    ("CONSEJO_EUROPA", "RUS", "salida", 2022, None, "expulsada en mar. 2022"),
    ("COMMONWEALTH", "MDV", "salida", 2016, None, ""),
    ("COMMONWEALTH", "GMB", "ingreso", 2018, "pleno", "vuelve tras salir en 2013"),
    ("COMMONWEALTH", "MDV", "ingreso", 2020, "pleno", ""),
    ("COMMONWEALTH", "GAB", "ingreso", 2022, "pleno", ""),
    ("COMMONWEALTH", "TGO", "ingreso", 2022, "pleno", ""),
    ("CEI", "UKR", "salida", 2018, None, "COW la codifica como asociada; deja de participar en 2014 y se retira en 2018"),
]

# ---------------------------------------------------------------------------
# Códigos de país
# ---------------------------------------------------------------------------
# Columnas del archivo COW IGO (nombres comprimidos) que no se resuelven solas.
COW_COLUMNA_ISO3 = {
    "antiguabarbuda": "ATG", "bosnia": "BIH", "car": "CAF", "congobrazz": "COG",
    "czechrep": "CZE", "domrepublic": "DOM", "etimor": "TLS", "fyromacedonia": "MKD",
    "ivorycoast": "CIV", "marshallis": "MHL", "micronesiafs": "FSM", "nokorea": "PRK",
    "nyemen": "YEM", "yemen": "YEM", "soafrica": "ZAF", "sokorea": "KOR", "sosudan": "SSD",
    "solomonis": "SLB", "stkitts": "KNA", "stlucia": "LCA", "stvincent": "VCT",
    "trinidad": "TTO", "uae": "ARE", "uk": "GBR", "usa": "USA", "germany": "DEU",
    "wgermany": "DEU", "wsamoa": "WSM", "yugoslaviaserb": "SRB", "zaire": "COD",
    "capeverde": "CPV", "eqguinea": "GNQ", "guineabissau": "GNB", "papuanewguinea": "PNG",
    "saotome": "STP", "sanmarino": "SMR", "saudiarabia": "SAU", "sierraleone": "SLE",
    "srilanka": "LKA", "burkinafaso": "BFA", "newzealand": "NZL", "elsalvador": "SLV",
    "costarica": "CRI", "kosovo": "XKX", "laos": "LAO", "russia": "RUS", "iran": "IRN",
    "syria": "SYR", "vietnam": "VNM", "taiwan": "TWN", "bolivia": "BOL", "venezuela": "VEN",
    "tanzania": "TZA", "moldova": "MDA", "swaziland": "SWZ", "turkey": "TUR",
    "brunei": "BRN", "myanmar": "MMR", "libya": "LBY", "kyrgyzstan": "KGZ",
    "cambodia": "KHM", "comoros": "COM", "gambia": "GMB", "bahamas": "BHS",
    "macedonia": "MKD", "palau": "PLW", "nauru": "NRU", "tonga": "TON", "tuvalu": "TUV",
    "kiribati": "KIR", "vanuatu": "VUT", "dominica": "DMA", "grenada": "GRD",
    # Estados que ya no existen y no se asignan a un iso3 actual
    "austriahungary": None, "baden": None, "bavariaelect": None, "czechoslovakia": None,
    "egermany": None, "hanover": None, "hesseelect": None, "hessegrand": None,
    "korea": None, "mecklenburg": None, "modena": None, "papalstates": None, "parma": None,
    "saxony": None, "svietnam": None, "syemen": None, "tuscany": None, "twosicilies": None,
    "wurtenburg": None, "zanzibar": None,
}
COW_CCODE_ISO3 = {  # códigos numéricos COW (ATOP) con nombre ambiguo
    2: "USA", 20: "CAN", 40: "CUB", 200: "GBR", 255: "DEU", 260: "DEU", 265: None,
    315: None, 316: "CZE", 317: "SVK", 343: "MKD", 345: "SRB", 347: "XKX", 365: "RUS",
    437: "CIV", 484: "COG", 490: "COD", 510: "TZA", 511: None, 572: "SWZ", 630: "IRN",
    652: "SYR", 678: "YEM", 679: "YEM", 680: None, 713: "TWN", 730: None, 731: "PRK",
    732: "KOR", 812: "LAO", 816: "VNM", 817: None, 860: "TLS", 987: "FSM", 359: "MDA",
    640: "TUR", 58: "ATG", 57: "VCT", 60: "KNA", 56: "LCA", 835: "BRN", 775: "MMR",
    620: "LBY", 703: "KGZ", 300: None, 327: None, 329: None, 332: None, 335: None,
    337: None, 240: None, 245: None, 267: None, 269: None, 271: None, 273: None,
    275: None, 280: None, 991: None, 992: None, 402: "CPV",
}


def iso3_por_nombre(nombre):
    try:
        return pycountry.countries.lookup(nombre).alpha_3
    except LookupError:
        try:
            return pycountry.countries.search_fuzzy(nombre)[0].alpha_3
        except LookupError:
            return None


def descargar():
    CRUDOS.mkdir(parents=True, exist_ok=True)
    for nombre, url in DESCARGAS.items():
        destino = CRUDOS / nombre
        if destino.exists():
            continue
        print(f"Descargando {nombre} ...")
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        destino.write_bytes(r.content)


# ---------------------------------------------------------------------------
# 1. Membresías en organizaciones
# ---------------------------------------------------------------------------
ESTADO_COW = {1: "pleno", 2: "asociado", 3: "observador"}


def leer_cow_igo():
    cow = pd.read_csv(CRUDOS / "cow_igo_year_formatv3.csv", sep="\t", encoding="latin-1", low_memory=False)
    columnas_pais = cow.columns[3:cow.columns.get_loc("sdate")]
    largo = cow.melt(id_vars=["ioname", "year"], value_vars=columnas_pais,
                     var_name="pais_cow", value_name="estado_cow")
    mapa = {c: COW_COLUMNA_ISO3[c] if c in COW_COLUMNA_ISO3 else iso3_por_nombre(c) for c in columnas_pais}
    sin_mapa = [c for c, v in mapa.items() if v is None and c not in COW_COLUMNA_ISO3]
    if sin_mapa:
        print("  COW: columnas sin iso3:", sin_mapa)
    largo["iso3"] = largo.pais_cow.map(mapa)
    largo = largo[largo.iso3.notna() & largo.estado_cow.isin([1, 2, 3])]
    # Si dos columnas caen en el mismo iso3 (Alemania Occidental y Alemania), gana el mejor estado
    largo = largo.groupby(["ioname", "iso3", "year"], as_index=False).estado_cow.min()
    return cow, largo


def episodios_desde_cow(cow, largo):
    """Convierte la membresía año a año de COW en episodios (ingreso, salida, estado)."""
    filas = []
    sigla_por_cow = {v[2]: k for k, v in ORGANIZACIONES.items() if v[2]}
    ultimo_anio = int(cow.year.max())  # 2014
    for ioname, sigla in sigla_por_cow.items():
        anios_org = sorted(cow.loc[cow.ioname == ioname, "year"].unique())
        sub = largo[largo.ioname == ioname]
        for iso3, g in sub.groupby("iso3"):
            estados = dict(zip(g.year, g.estado_cow))
            inicio, actual = None, None
            # recorre los años que la organización tiene en el archivo (antes de 1965 COW
            # registra cada 5 años, por eso no se exige que los años sean consecutivos)
            for anio in anios_org:
                e = estados.get(anio)
                if e != actual:
                    if actual is not None:
                        filas.append((iso3, sigla, inicio, anio, ESTADO_COW[actual], "Correlates of War IGO v3", ""))
                    inicio, actual = anio, e
            if actual is not None:
                # sigue en la organización en el último año del archivo: episodio abierto
                salida = None if anios_org[-1] == ultimo_anio else anios_org[-1] + 1
                filas.append((iso3, sigla, inicio, salida, ESTADO_COW[actual], "Correlates of War IGO v3", ""))
    return pd.DataFrame(filas, columns=["iso3", "organizacion", "anio_ingreso", "anio_salida", "estado", "fuente", "nota"])


def aplicar_cambios(ep):
    ep = ep.copy()
    for sigla, iso3, accion, anio, estado, nota in CAMBIOS:
        abiertos = (ep.organizacion == sigla) & (ep.iso3 == iso3) & ep.anio_salida.isna()
        ep.loc[abiertos, "anio_salida"] = anio
        if accion == "ingreso":
            ep.loc[len(ep)] = [iso3, sigla, anio, None, estado, "carga manual (cambios desde 2015)", nota]
        else:
            ep.loc[abiertos, "nota"] = nota
            ep.loc[abiertos, "fuente"] = ep.loc[abiertos, "fuente"] + " + carga manual (salida)"
    return ep


def episodios_manuales():
    filas = []
    for sigla, paises, ingreso, salida, estado, nota in MANUAL:
        for iso3 in paises:
            filas.append((iso3, sigla, ingreso, salida, estado, "carga manual", nota))
    return pd.DataFrame(filas, columns=["iso3", "organizacion", "anio_ingreso", "anio_salida", "estado", "fuente", "nota"])


# ---------------------------------------------------------------------------
# 2. Tratados comerciales (DESTA)
# ---------------------------------------------------------------------------
TIPO_DESTA = {1: "bilateral", 2: "plurilateral", 3: "plurilateral con tercer país",
              4: "región con región", 5: "adhesión", 6: "adhesión vía bloque regional", 7: "retiro"}
ALIAS_DESTA = {"GBR": ["UK"], "USA": ["US"], "KOR": ["Korea"], "COD": ["DRCongo"], "MKD": ["Macedonia"],
               "TWN": ["Taiwan"], "RUS": ["Russia"], "CZE": ["Czech Republic"], "VEN": ["Venezuela"],
               "BOL": ["Bolivia"], "TZA": ["Tanzania"], "IRN": ["Iran"], "SYR": ["Syria"], "MDA": ["Moldova"],
               "LAO": ["Laos", "Lao"], "VNM": ["Vietnam", "Viet Nam"]}


def iso3_desde_numerico(n):
    c = pycountry.countries.get(numeric=f"{int(n):03d}")
    return c.alpha_3 if c else None


def nombres_pais(iso3):
    c = pycountry.countries.get(alpha_3=iso3)
    nombres = set(ALIAS_DESTA.get(iso3, []))
    if c:
        for attr in ("name", "common_name", "official_name"):
            if hasattr(c, attr):
                nombres.add(getattr(c, attr))
    return nombres


def tratados_desde_desta():
    d = pd.read_csv(CRUDOS / "desta_2_0.csv", sep=";")
    d = d[d.entry_type.isin(["base_treaty", "accession", "withdrawal"])].copy()
    cols = [f"c{i}" for i in range(1, 92)]
    d["miembros"] = d[cols].apply(lambda r: [iso3_desde_numerico(x) for x in r.dropna()], axis=1)
    d["miembros"] = d.miembros.apply(lambda l: [x for x in l if x])
    base = d[d.entry_type == "base_treaty"].set_index("base_treaty")
    filas = []
    for bt, g in d.groupby("base_treaty"):
        if bt not in base.index:
            continue
        b = base.loc[bt]
        vigor_base = b.entryforceyear
        info = {}  # iso3 -> dict
        for iso3 in b.miembros:
            info[iso3] = dict(via="fundador", anio_firma=b.year, anio_vigor=vigor_base, anio_salida=None)
        orden = g[g.entry_type != "base_treaty"].sort_values(["year", "number"])
        for r in orden.itertuples():
            if r.entry_type == "accession":
                for iso3 in r.miembros:
                    if iso3 not in info or info[iso3]["anio_salida"] is not None:
                        vigor = r.entryforceyear if pd.notna(r.entryforceyear) else r.year
                        if pd.notna(vigor_base):
                            vigor = max(vigor, vigor_base)
                        else:
                            vigor = float("nan")
                        info[iso3] = dict(via="adhesión", anio_firma=r.year, anio_vigor=vigor, anio_salida=None)
            else:  # withdrawal: la fila lista a los miembros, el nombre dice quién se va
                texto = r.name.split("withdrawal", 1)[1]
                for iso3 in r.miembros:
                    if iso3 in info and info[iso3]["anio_salida"] is None and any(
                            re.search(rf"\b{re.escape(n)}\b", texto) for n in nombres_pais(iso3)):
                        info[iso3]["anio_salida"] = r.year
        for iso3, v in info.items():
            filas.append(dict(iso3=iso3, acuerdo_id=int(bt), acuerdo=b["name"],
                              tipo=TIPO_DESTA.get(b.typememb, ""), region=b.regioncon,
                              via=v["via"], anio_firma=v["anio_firma"], anio_entrada_vigor=v["anio_vigor"],
                              anio_salida=v["anio_salida"], listado_omc=int(b.wto_listed) if pd.notna(b.wto_listed) else None))
    t = pd.DataFrame(filas)
    for c in ["anio_firma", "anio_entrada_vigor", "anio_salida"]:
        t[c] = t[c].astype("Int64")
    return t


# ---------------------------------------------------------------------------
# 3. Pactos militares (ATOP)
# ---------------------------------------------------------------------------
def diadas_atop():
    atop = pyreadr.read_r(CRUDOS / "atop_5_1_diada_anio.rda")["atop_alliance"]
    estados = pyreadr.read_r(CRUDOS / "cow_estados.rda")["cow_states"].drop_duplicates("ccode")
    mapa = {}
    for r in estados.itertuples():
        cc = int(r.ccode)
        mapa[cc] = COW_CCODE_ISO3[cc] if cc in COW_CCODE_ISO3 else iso3_por_nombre(r.statenme)
    atop = atop.astype({"ccode1": int, "ccode2": int, "year": int})
    atop["iso3_a"] = atop.ccode1.map(mapa)
    atop["iso3_b"] = atop.ccode2.map(mapa)
    sin = sorted(set(atop.loc[atop.iso3_a.isna() & (atop.year >= 1945), "ccode1"]))
    if sin:
        print("  ATOP: ccode sin iso3 (desde 1945):", sin)
    atop = atop[atop.iso3_a.notna() & atop.iso3_b.notna() & (atop.iso3_a < atop.iso3_b) & (atop.year >= 1945)]
    atop = atop.rename(columns={"year": "anio", "atop_defense": "defensa", "atop_offense": "ofensiva",
                                "atop_neutral": "neutralidad", "atop_nonagg": "no_agresion",
                                "atop_consul": "consulta"})
    cols = ["defensa", "ofensiva", "neutralidad", "no_agresion", "consulta"]
    atop = atop.groupby(["iso3_a", "iso3_b", "anio"], as_index=False)[cols].max()
    atop[cols] = atop[cols].astype(int)
    return atop


# ---------------------------------------------------------------------------
# Principal
# ---------------------------------------------------------------------------
def main():
    descargar()
    panel = pd.read_csv(PANEL, usecols=["iso3", "pais"]).drop_duplicates("iso3")
    nombre = dict(zip(panel.iso3, panel.pais))

    def pais(iso3):
        if iso3 in nombre:
            return nombre[iso3]
        c = pycountry.countries.get(alpha_3=iso3)
        return c.name if c else iso3

    print("1/4 Membresías en organizaciones (COW + carga manual)")
    cow, cow_largo = leer_cow_igo()
    ep = episodios_desde_cow(cow, cow_largo)
    ep = ep[~ep.organizacion.isin(REEMPLAZAR_COW)]
    borrar = pd.MultiIndex.from_tuples(BORRAR_COW)
    ep = ep[~pd.MultiIndex.from_arrays([ep.organizacion, ep.iso3]).isin(borrar)]
    for (sigla, iso3), anio in AJUSTE_INGRESO.items():
        sel = ep[(ep.organizacion == sigla) & (ep.iso3 == iso3)]
        if len(sel):
            i = sel.anio_ingreso.idxmin()
            ep.loc[i, "nota"] = f"COW dice {int(ep.loc[i, 'anio_ingreso'])}; corregido con Wikidata"
            ep.loc[i, "anio_ingreso"] = anio
    ep = pd.concat([ep, episodios_manuales()], ignore_index=True)
    ep = aplicar_cambios(ep)
    ep["pais"] = ep.iso3.map(pais)
    ep["organizacion_nombre"] = ep.organizacion.map(lambda s: ORGANIZACIONES[s][0])
    ep["tipo"] = ep.organizacion.map(lambda s: ORGANIZACIONES[s][1])
    for c in ["anio_ingreso", "anio_salida"]:
        ep[c] = pd.to_numeric(ep[c]).astype("Int64")
    ep["en_panel"] = ep.iso3.isin(nombre).astype(int)
    ep = ep[["iso3", "pais", "organizacion", "organizacion_nombre", "tipo", "estado",
             "anio_ingreso", "anio_salida", "fuente", "nota", "en_panel"]]
    ep = ep.sort_values(["organizacion", "anio_ingreso", "iso3"]).reset_index(drop=True)
    ep.to_csv(BASE / "membresias_organizaciones.csv", index=False)
    print(f"   {len(ep)} episodios, {ep.organizacion.nunique()} organizaciones, {ep.iso3.nunique()} países")

    print("2/4 Tratados comerciales (DESTA)")
    tr = tratados_desde_desta()
    tr.insert(1, "pais", tr.iso3.map(pais))
    tr = tr.sort_values(["iso3", "anio_firma", "acuerdo_id"]).reset_index(drop=True)
    tr.to_csv(BASE / "tratados_comerciales_pais.csv", index=False)
    print(f"   {len(tr)} filas país-acuerdo, {tr.acuerdo_id.nunique()} acuerdos")

    print("3/4 Pactos militares (ATOP)")
    at = diadas_atop()
    at.insert(1, "pais_a", at.iso3_a.map(pais))
    at.insert(3, "pais_b", at.iso3_b.map(pais))
    at.to_csv(BASE / "alianzas_militares_diadas.csv", index=False)
    print(f"   {len(at)} filas díada-año, {at.anio.min()}-{at.anio.max()}")

    print("4/4 Panel país-año")
    filas = [(i, a) for i in panel.iso3 for a in ANIOS_PANEL]
    pa = pd.DataFrame(filas, columns=["iso3", "anio"])
    pa.insert(1, "pais", pa.iso3.map(nombre))
    plenos = ep[ep.estado == "pleno"]
    for sigla in ORGANIZACIONES:
        e = plenos[plenos.organizacion == sigla]
        m = pa.merge(e[["iso3", "anio_ingreso", "anio_salida"]], on="iso3", how="left")
        dentro = (m.anio >= m.anio_ingreso) & (m.anio_salida.isna() | (m.anio < m.anio_salida))
        miembro = dentro.fillna(False).groupby([m.iso3, m.anio]).any()
        pa[f"miembro_{sigla.lower()}"] = pa.set_index(["iso3", "anio"]).index.map(miembro).astype(int)
    cols_org = [c for c in pa.columns if c.startswith("miembro_")]
    pa["n_organizaciones_clave"] = pa[cols_org].sum(axis=1)
    tipos = {}
    for sigla, (_, tipo, _) in ORGANIZACIONES.items():
        tipos.setdefault(tipo, []).append(f"miembro_{sigla.lower()}")
    for tipo, cs in tipos.items():
        clave = unicodedata.normalize("NFKD", tipo).encode("ascii", "ignore").decode().replace("-", "_").replace(" ", "_")
        pa[f"n_org_{clave}"] = pa[cs].sum(axis=1)

    # Total de organizaciones intergubernamentales COW (miembro pleno), hasta 2014
    n_igos = cow_largo[cow_largo.estado_cow == 1].groupby(["iso3", "year"]).ioname.nunique()
    n_igos.index = n_igos.index.set_names(["iso3", "anio"])
    pa["n_igos_cow_total"] = pa.set_index(["iso3", "anio"]).index.map(n_igos)
    pa.loc[pa.anio > int(cow.year.max()), "n_igos_cow_total"] = pd.NA
    pa.loc[(pa.anio <= int(cow.year.max())) & pa.n_igos_cow_total.isna() & pa.iso3.isin(cow_largo.iso3), "n_igos_cow_total"] = 0

    # Acuerdos comerciales en vigor (DESTA, hasta 2020)
    tv = tr[tr.anio_entrada_vigor.notna()]
    m = pa[["iso3", "anio"]].merge(tv[["iso3", "anio_entrada_vigor", "anio_salida"]], on="iso3")
    m = m[(m.anio >= m.anio_entrada_vigor) & (m.anio_salida.isna() | (m.anio < m.anio_salida))]
    n_acu = m.groupby(["iso3", "anio"]).size()
    pa["n_acuerdos_comerciales_en_vigor"] = pa.set_index(["iso3", "anio"]).index.map(n_acu).fillna(0).astype("Int64")
    pa.loc[pa.anio > 2020, "n_acuerdos_comerciales_en_vigor"] = pd.NA

    # Pactos militares (ATOP, hasta 2018): cantidad de países con los que tiene cada tipo de pacto
    doble = pd.concat([at.rename(columns={"iso3_a": "iso3", "iso3_b": "otro"}),
                       at.rename(columns={"iso3_b": "iso3", "iso3_a": "otro"})])
    for col, nuevo in [("defensa", "n_aliados_defensa"), (None, "n_aliados_cualquier_pacto")]:
        sub = doble if col is None else doble[doble[col] == 1]
        n = sub.groupby(["iso3", "anio"]).otro.nunique()
        pa[nuevo] = pa.set_index(["iso3", "anio"]).index.map(n).fillna(0).astype("Int64")
        pa.loc[pa.anio > int(at.anio.max()), nuevo] = pd.NA

    pa.to_csv(BASE / "alianzas_pais_anual.csv", index=False)
    print(f"   {len(pa)} filas ({pa.iso3.nunique()} países × {len(ANIOS_PANEL)} años), {len(pa.columns)} columnas")


if __name__ == "__main__":
    main()
