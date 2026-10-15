"""
CHEQUEO DE FUENTES: prueba si cada fuente que se renueva todos los meses sigue respondiendo.

No necesita a Claude: es Python puro. Lo llama actualizar_mensual.py y también se puede correr solo:
    python chequear_fuentes.py

Para cada fuente hace un pedido corto (solo lee el comienzo de la respuesta) y la clasifica:
  - ok                      respondió bien
  - bloqueada_por_la_red    el proxy del entorno no deja salir (hay que habilitar el dominio);
                            no es culpa de la fuente
  - no_existe_mas           la dirección da 404 o 410, o una página web en vez de datos: el archivo
                            o la API se movió o se dio de baja
  - no_responde             error 5xx, rechazo (403) o sin respuesta: puede ser temporal

Una fuente se marca como POSIBLEMENTE DISCONTINUADA si da "no_existe_mas", o si da "no_responde"
dos meses seguidos. El historial queda en actualizaciones/estado_fuentes.csv.

Las fuentes fijas (censos, COW/DESTA/ATOP, electorAr, CEP, MiPyME 2024, Factbook, BM Subnational
Population) no se chequean:
ya están bajadas y no cambian.
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

ETL = Path(__file__).resolve().parent
for carpeta in ("", "argentina_provincias", "latam_subnacional", "maestros", "modelo_unificado"):
    sys.path.insert(0, str(ETL / carpeta))

import construir_master as mu  # noqa: E402
import crear_maestros as ma  # noqa: E402
import extraer_argentina_provincias as ar  # noqa: E402
import extraer_latam_subnacional as la  # noqa: E402
import paso2_distribucion_precios_bienestar as p2  # noqa: E402
from paso1_extraer_banco_mundial import URL_BASE  # noqa: E402

HISTORIAL = ETL / "actualizaciones" / "estado_fuentes.csv"
CA_SALUD = ETL / "argentina_provincias" / "crudos" / "certificados_salud.pem"


def fuentes():
    """(nombre, script, urls candidatas, opciones). Las URLs salen de los mismos scripts."""
    salud = {"verify": str(CA_SALUD)} if CA_SALUD.exists() else {}
    eph = [ar.URL_EPH.rsplit("/", 1)[0] + "/" + v.format(t=t, o=ar.ORDINAL[t], anio=a)
           for a in (datetime.now().year, datetime.now().year - 1) for t in (1, 2, 3, 4)
           for v in ar.URL_EPH_VARIANTES]
    cckp = ar.URL_CCKP.format(codigos=f"ARG.{next(iter(ar.CODIGO_CCKP.values()))}")
    return [
        ("Banco Mundial API (indicadores)", "paso1", [f"{URL_BASE}/country/ARG/indicator/SP.POP.TOTL?format=json"], {}),
        ("Banco Mundial Food Prices for Nutrition", "paso2", [f"{URL_BASE}/sources/88?format=json"], {}),
        ("ILOSTAT salario promedio", "paso2", [p2.URL_ILOSTAT], {"headers": p2.CABECERAS}),
        ("World Happiness Report", "paso2", [p2.URL_FELICIDAD], {}),
        ("Wikidata SPARQL", "maestros", [ma.WIKIDATA + "?query=ASK%7B%7D&format=json"], {"headers": ma.CABECERA}),
        ("Banco Mundial países (es/en)", "maestros/modelo", [mu.URL_BM_PAISES], {}),
        ("Regiones M49 (lukes)", "modelo", [mu.URL_M49], {}),
        ("CEPAL VAB por provincia", "argentina", [ar.URL_CEPAL], {}),
        ("Energía petróleo por provincia", "argentina", [ar.URL_PETROLEO], {}),
        ("Energía gas por provincia", "argentina", [ar.URL_GAS], {}),
        ("MAGyP estimaciones agrícolas", "argentina", [ar.URL_MAGYP], {"method": "post", "data": {"Dataset": "Dataset"}}),
        ("MAGyP stock bovino", "argentina", [ar.URL_BOVINOS], {}),
        ("Argendata PBG per cápita", "argentina", [ar.URL_PBG_PC], {}),
        ("EOH pernoctes (turismo)", "argentina", [ar.URL_PERNOCTES], {}),
        ("EOH viajeros (turismo)", "argentina", [ar.URL_VIAJEROS], {}),
        ("CCKP temperatura", "argentina", [cckp], {}),
        ("INDEC proyecciones de población", "argentina", [ar.URL_PROYECCIONES], {}),
        ("HCDN diputados", "argentina", [ar.URL_DIPUTADOS], {}),
        ("Senado senadores", "argentina", [ar.URL_SENADORES], {}),
        ("Salud médicos (API)", "argentina",
         [ar.URL_SALUD_API.format(id="serie-de-profesionales-de-medicina")], salud),
        ("Salud vacuna triple viral", "argentina", [ar.URL_SRP], salud),
        ("OEDE empresas por rama", "argentina", [ar.URL_OEDE_RAMAS], {}),
        ("OEDE empresas por tamaño", "argentina", [ar.URL_OEDE_CUADROS], {}),
        ("OEDE remuneraciones", "argentina", [ar.URL_OEDE_SALARIOS], {}),
        ("OEDE empleo", "argentina", [ar.URL_OEDE_EMPLEO], {}),
        ("DNAP recaudación provincial", "argentina", [ar.URL_TOP], {}),
        ("DNAP alícuotas IIBB", "argentina", [ar.URL_ALICUOTAS_IIBB.format(anio=2025)], {}),
        ("INDEC canasta básica (CBA/CBT)", "argentina", [ar.URL_CBA_CBT], {}),
        ("Canastas regionales (holatam)", "argentina", [ar.URL_CANASTAS_REGIONALES], {}),
        ("INDEC EPH microdatos", "argentina", eph, {}),
        ("OCDE estadísticas regionales (SDMX)", "latam",
         [la.URL_OCDE.format(flujo="DSD_REG_DEMO@DF_POP_BROAD", clave="A.TL2.._Z.POP._T._T.PS", desde=2023)], {}),
        ("IBGE SIDRA (Brasil)", "latam",
         [la.URL_SIDRA.format(tabla=6579, variables="9324", periodos="last", clasif="")], {}),
        ("ANP petróleo por estado (Brasil)", "latam", [la.URL_ANP + "producao-petroleo-m3.csv"], {}),
        ("ANP gas por estado (Brasil)", "latam", [la.URL_ANP + "producao-gas-natural-1000m3.csv"], {}),
        *[(f"datos.gov.co {nombre} (Colombia)", "latam", [la.URL_DATOS_GOV_CO.format(id=i) + "?$limit=1"],
           {"headers": la.NAVEGADOR})
          for nombre, i in (("EVA agrícola 2006-2018", "2pnw-mmge"), ("EVA agrícola 2019+", "uejq-wxrr"),
                            ("ICA inventario bovino", "cea5-4ctf"), ("ANH crudo", "fdvb-hsrf"),
                            ("ANH gas", "5dux-bfvx"))],
    ]


def probar(urls, opciones):
    """Devuelve (estado, detalle). Con varias URLs alcanza con que una responda."""
    opciones = dict(opciones)
    metodo = opciones.pop("method", "get")
    peor = ("no_responde", "sin URL")
    for url in urls:
        try:
            with requests.request(metodo, url, stream=True, timeout=60, **opciones) as r:
                inicio = next(r.iter_content(512), b"").lstrip().lower()
                es_pagina = "text/html" in r.headers.get("content-type", "") or inicio.startswith((b"<!doctype", b"<html"))
                if r.status_code < 400 and not es_pagina:
                    return "ok", str(r.status_code)
                if r.status_code < 400:  # muchos sitios responden 200 con una página de "no encontrado"
                    peor = ("no_existe_mas", f"{r.status_code} pero devuelve una página web en vez de datos")
                    continue
                estado = "no_existe_mas" if r.status_code in (404, 410) else "no_responde"
                peor = (estado, str(r.status_code))
        except requests.exceptions.ProxyError as error:
            peor = ("bloqueada_por_la_red", type(error).__name__)
        except requests.RequestException as error:
            peor = ("no_responde", type(error).__name__)
    return peor


def chequear(guardar=True):
    """Prueba todas las fuentes y devuelve (tabla de hoy, líneas de texto para el resumen)."""
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    filas = []
    for nombre, script, urls, opciones in fuentes():
        estado, detalle = probar(urls, opciones)
        filas.append({"fecha": ahora, "fuente": nombre, "script": script, "estado": estado,
                      "detalle": detalle, "url": urls[0]})
    hoy = pd.DataFrame(filas)

    # ¿Venía fallando la vez anterior?
    anterior = pd.read_csv(HISTORIAL) if HISTORIAL.exists() else pd.DataFrame(columns=hoy.columns)
    previo = anterior[anterior.fecha.str[:7] < ahora[:7]]  # última corrida de un mes anterior
    previo = previo[previo.fecha == previo.fecha.max()].set_index("fuente").estado if len(previo) else {}
    hoy["posible_discontinuada"] = [
        int(e == "no_existe_mas" or (e == "no_responde" and previo.get(f) in ("no_responde", "no_existe_mas")))
        for f, e in zip(hoy.fuente, hoy.estado)]
    if guardar:
        hoy.to_csv(HISTORIAL, mode="a", header=not HISTORIAL.exists(), index=False)

    total = len(hoy)
    disc = hoy[hoy.posible_discontinuada == 1]
    lineas = ["## Estado de las fuentes",
              f"- Respondieron {int((hoy.estado == 'ok').sum())} de {total} fuentes que se renuevan.",
              f"- **Posiblemente discontinuadas: {len(disc)} de {total} ({100 * len(disc) / total:.0f} %).**"]
    for etiqueta, estado in (("Posiblemente discontinuadas", None),
                             ("Bloqueadas por la red del entorno (habilitar el dominio)", "bloqueada_por_la_red"),
                             ("Sin respuesta este mes (puede ser temporal)", "no_responde")):
        sub = disc if estado is None else hoy[(hoy.estado == estado) & (hoy.posible_discontinuada == 0)]
        if len(sub):
            lineas.append(f"- {etiqueta}:")
            lineas += [f"  - {r.fuente} ({r.script}): {r.estado} {r.detalle}, {r.url}" for r in sub.itertuples()]
    return hoy, lineas


if __name__ == "__main__":
    _, texto = chequear(guardar="--sin-guardar" not in sys.argv)
    print("\n".join(texto))
