# Actualización mensual 2026-10-16 10:17 (PRUEBA: no se publicó nada)

Todos los pasos se actualizaron. 149 archivos cambiaron.

| Paso | Estado | Minutos |
|---|---|---|
| Panel de países (Banco Mundial, OMS, ILOSTAT, WHR) | actualizado | 0.4 |
| Maestros de países y subdivisiones | actualizado | 0.6 |
| Alianzas y tratados internacionales | actualizado | 0.3 |
| Argentina por provincia | actualizado | 4.4 |
| Latinoamérica por subdivisión | actualizado | 6.4 |
| Migración, clima, capital social, gobernanza, deuda y federalismo fiscal | actualizado | 1.9 |
| Dimensiones nuevas sumadas al panel de países | actualizado | 0.0 |
| Educación, redes, videojuegos, construcción, cultura, apuestas y medallero | actualizado | 5.5 |
| Modelo unificado (SQLite) | actualizado | 0.1 |
| Bases Argentina, Latinoamérica y mundial (SQLite) | actualizado | 0.2 |

## Estado de las fuentes
- Respondieron 39 de 39 fuentes que se renuevan.
- **Posiblemente discontinuadas: 0 de 39 (0 %).**

## Qué cambió
- **maestros/paises_maestro.csv**: filas 251 → 251; 1 filas nuevas o con algún valor distinto
- **maestros/subdivisiones_maestro.csv**: filas 3,590 → 3,590; 1 filas nuevas o con algún valor distinto
- **argentina_provincias/agricultura_provincia_anual.csv**: filas 13,059 → 13,060; 2 filas nuevas o con algún valor distinto; celdas con dato +9; (más cambio: provincia_iso +1, provincia +1, campania +1, anio_cosecha +1)
- **argentina_provincias/petroleo_gas_provincia_anual.csv**: filas 222 → 222; 11 filas nuevas o con algún valor distinto
- **latam_subnacional/agricultura_subdivision_anual.csv**: filas 127,148 → 127,149; 2 filas nuevas o con algún valor distinto; celdas con dato +11; (más cambio: iso3 +1, subdivision_iso +1, subdivision +1, anio +1)
- **latam_subnacional/ocde_regional_largo.csv.gz**: filas 721,316 → 721,316; 0 filas nuevas o con algún valor distinto
- **latam_subnacional/petroleo_gas_subdivision_anual.csv**: filas 809 → 809; 10 filas nuevas o con algún valor distinto
- **modelo_unificado/master_paises_provincias.sqlite**: 1 tablas cambiaron de tamaño: hecho_subdivision_agricultura 13,059 → 13,060
- **modelo_unificado/tablas/dim_pais.csv**: filas 251 → 251; 1 filas nuevas o con algún valor distinto
- **modelo_unificado/tablas/dim_subdivision.csv**: filas 3,591 → 3,591; 1 filas nuevas o con algún valor distinto
- **modelo_unificado/tablas/pais_equivalencia.csv**: filas 2,306 → 2,306; 1 filas nuevas o con algún valor distinto
- **modelo_unificado/tablas/ref_catalogo_tabla.csv**: filas 60 → 60; 1 filas nuevas o con algún valor distinto
- **modelo_unificado/tablas/v_pais.csv**: filas 251 → 251; 1 filas nuevas o con algún valor distinto
- **bases_regionales/base_argentina.sqlite**: 1 tablas cambiaron de tamaño: hecho_subdivision_agricultura 13,059 → 13,060
- **bases_regionales/base_latam.sqlite**: 2 tablas cambiaron de tamaño: hecho_subdivision_agricultura 13,059 → 13,060, hecho_subdivision_latam_agricultura 127,148 → 127,149
- **bases_regionales/base_mundial.sqlite**: 2 tablas cambiaron de tamaño: hecho_subdivision_agricultura 13,059 → 13,060, hecho_subdivision_latam_agricultura 127,148 → 127,149
- **bases_regionales/resumen_bases.csv**: filas 77 → 77; 2 filas nuevas o con algún valor distinto
- Además cambiaron 132 archivos crudos o auxiliares.
