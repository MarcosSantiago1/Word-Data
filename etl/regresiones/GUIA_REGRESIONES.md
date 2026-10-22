# Guía: regresión lineal y logística con la base de países

Esta guía explica qué tiene que cumplir la base para que una regresión tenga sentido, qué variables del proyecto sirven y cómo leer los tres ejemplos que corre `regresiones_exploratorias.py`.

```bash
pip install statsmodels scikit-learn
python etl/regresiones/regresiones_exploratorias.py
```

El script lee `etl/datos_procesados/paises_anual.csv` (no lo modifica) y guarda tablas en `etl/regresiones/resultados/`.

---

## 1. ¿Lineal o logística?

| | Regresión lineal (MCO) | Regresión logística |
|---|---|---|
| Variable dependiente (Y) | Número continuo: felicidad 0-10, esperanza de vida, tasa de suicidio | Sí/No (1/0): es democracia, más de la mitad no puede pagar una dieta sana |
| Qué estima | Cuánto cambia Y cuando X sube una unidad, con lo demás constante | Cómo cambia la *chance* (odds) de que Y = 1 |
| Cómo se lee | Coeficiente en unidades de Y | Odds ratio: >1 sube la chance, <1 la baja |
| Qué tan bien ajusta | R² (0 a 1) | Pseudo R², AUC (0,5 = azar, 1 = perfecto), matriz de confusión |

Regla simple: si Y ya es un número con sentido, usá lineal. No conviertas un número en 0/1 solo para usar logística, porque perdés información. La logística es para cuando la pregunta es de verdad "sí o no".

---

## 2. Condiciones que tiene que cumplir la base

### 2.1 Una fila = una unidad, con clave única
En corte transversal, una fila por país (`iso3`) en un año fijo. La base ya cumple esto: 217 países, sin agregados regionales mezclados. Si unís otra tabla (alianzas, master), hacelo por `iso3` + `anio` y verificá que no se dupliquen filas.

### 2.2 Tamaño de muestra suficiente
- **Lineal:** al menos 10 a 20 países por cada variable explicativa. Con ~120 países completos, 5 o 6 explicativas es un techo razonable.
- **Logística:** lo que cuenta es la clase *menos* frecuente. Regla práctica: al menos 10 casos de la clase chica por variable ("eventos por variable"). Ejemplo: derechos indígenas en la constitución tiene solo 21 países con 1, así que alcanza para 1 o 2 explicativas como mucho.
- **Provincias argentinas:** son 24. Con un solo año no se pueden meter más de 2 explicativas. Para más, hay que usar varios años (panel).

### 2.3 Datos faltantes
La regresión usa solo las filas que tienen *todas* las variables. Por eso cada variable que sumás puede achicar la muestra. Ejemplo real: hay 144 países con felicidad en 2021, pero solo 119 tienen además PIB, esperanza de vida, corrupción, gasto en salud y Gini.

Lo importante es **quién** falta. En esta base suelen faltar países pobres, chicos o en conflicto. Si faltan justo esos, los resultados describen a los países con buenas estadísticas, no al mundo.

Qué hacer:
1. Antes de modelar, contá cuántos países quedan y mirá cuáles se caen.
2. Para variables con huecos (Gini, educación), usar el **último dato disponible** de una ventana corta (el script usa Gini 2015-2021). Así el Gini pasa de 81 a 142 países.
3. Evitá variables con menos de ~100 países en 2021 como explicativas: salario (90), Gini directo (81), I+D (88), deuda del gobierno (45).
4. Nivel intermedio: imputación múltiple (`IterativeImputer` de scikit-learn o `mice` de statsmodels).

### 2.4 Multicolinealidad (explicativas que dicen lo mismo)
Si dos explicativas están muy correlacionadas, el modelo no puede separar el efecto de cada una: los coeficientes se vuelven inestables y pierden significancia.

Se mide con el **VIF**: menos de 5 está bien, entre 5 y 10 es para vigilar, y más de 10 es un problema. En esta base, las correlaciones fuertes son:
- Los seis indicadores de gobernanza del Banco Mundial entre sí (corrupción, estado de derecho, efectividad: r = 0,90 a 0,94). Si se ponen los tres juntos, el VIF da 11,7. **Usá uno solo**, o el promedio.
- `voz_rendicion_cuentas` con `indice_democracia_electoral_0_1` (r = 0,95).
- log PIB per cápita con usuarios de internet (0,91), mortalidad infantil (−0,81) y esperanza de vida (0,84).

### 2.5 Supuestos de la regresión lineal
| Supuesto | Cómo se revisa | Si falla |
|---|---|---|
| Relación lineal | Gráfico de Y contra cada X | Transformar: el PIB y la población casi siempre van en logaritmo |
| Varianza constante del error | Test de Breusch-Pagan (p < 0,05 = falla) | Errores robustos (HC3), que el script ya usa |
| Errores independientes | En corte transversal se asume. En panel no: el mismo país se repite | Errores agrupados por país |
| Residuos normales | Jarque-Bera, histograma | Con más de 100 casos importa poco |
| Sin casos que dominen | Distancia de Cook | Correr con y sin esos países y comparar |

### 2.6 Supuestos de la logística
- Y es exactamente 0/1 y el umbral está justificado (por ejemplo, democracia electoral V-Dem ≥ 0,5 es una convención).
- Clases no demasiado desbalanceadas: si 95% son 0, el modelo "acierta" diciendo siempre 0. Por eso conviene mirar el AUC, no solo el porcentaje de acierto.
- Sin **separación perfecta**: si una X divide los 0 y los 1 sin error, los coeficientes se van al infinito y statsmodels avisa.
- Relación lineal entre cada X y el *logit* (de nuevo, logaritmo para PIB).

### 2.7 Corte transversal o panel
- **Corte transversal** (un año, por ejemplo 2021): más simple y es lo recomendable para empezar. 2021 es el año de referencia porque el suicidio llega solo hasta ese año.
- **Panel** (varios años por país): da muchas más observaciones (felicidad: 1.910 país-año) y permite **efectos fijos por país**, que controlan todo lo que no cambia en un país (cultura, geografía, historia). Pero las filas del mismo país no son independientes: hay que usar errores agrupados por país. Ojo: en esta base la felicidad no tiene 2013 ni nada antes de 2011.

### 2.8 Correlación no es causa, y cuidado con variables "mecánicas"
- La regresión muestra asociaciones con otras cosas constantes, no efectos causales. El gasto en salud y la felicidad pueden retroalimentarse, y ambos dependen de la riqueza.
- No expliques una variable con otra que la contiene o la calcula: suicidio total con suicidio de hombres, dieta saludable en moneda local con el tipo de cambio, nivel de ingreso del Banco Mundial con el PIB per cápita (el nivel se define con el ingreso), o un KPI con sus propios componentes.
- No uses `felicidad_ranking` como Y: es el orden de la felicidad, no una medida nueva.

---

## 3. Variables propuestas (cobertura en 2021)

### Regresión lineal
| Y (dependiente) | Países | Explicativas sugeridas | Pregunta |
|---|---|---|---|
| `felicidad` | 144 | log PIB pc PPA, esperanza de vida, un índice de gobernanza, gasto en salud % PIB, Gini (último disponible) | ¿Qué acompaña a la felicidad, más allá de la riqueza? **(ejemplo 1)** |
| `esperanza_vida` | 217 | log PIB pc, gasto en salud % PIB, médicos por mil (123), obesidad, efectividad del gobierno | ¿Rinde el gasto en salud? (es la idea del KPI IESE) |
| log `mortalidad_infantil` | 196 | log PIB pc, gasto en salud, gasto en educación, internet | Igual que la anterior, más sensible en países pobres |
| `suicidio_total_x100k` | 185 | felicidad, log PIB pc, Gini, obesidad, región | Relación débil con la riqueza (r = 0,19): buen caso para ver un R² bajo |
| `pct_no_puede_pagar_dieta_saludable` | 146 | log PIB pc, Gini, remesas % PIB, tipo de cambio sobre PPA | Asequibilidad de la comida |
| log `emisiones_co2_per_capita_tco2e` | 203 | log PIB pc (y su cuadrado), % electricidad renovable | Curva ambiental de Kuznets |

### Regresión logística
| Y (1 si...) | Países con dato | Casos 1 / 0 | Explicativas sugeridas |
|---|---|---|---|
| `indice_democracia_electoral_0_1` ≥ 0,5 | 176 | 92 / 84 | log PIB pc, gasto en educación, región Medio Oriente y Norte de África **(ejemplo 2)** |
| `pct_no_puede_pagar_dieta_saludable` > 50% | 146 | 48 / 98 | log PIB pc, Gini, remesas |
| `suicidio_total_x100k` > 10 (cuartil alto) | 185 | 55 / 130 | felicidad, PIB, región |
| `es_derechos_indigenas_constitucion` = 1 | 185 | 21 / 164 | Pocos casos: 1 o 2 explicativas como máximo (región, fraccionalización étnica de `v_pais_diversidad_cultural` en el master) |
| Miembro de un bloque (por ejemplo `miembro_ocde`, en `etl/alianzas/alianzas_pais_anual.csv`) | todos | depende | log PIB pc, democracia, `n_acuerdos_comerciales_en_vigor` |

---

## 4. Resultados de los ejemplos (corrida del 22-10-2026)

### Ejemplo 1: lineal, felicidad 2021 (n = 119, R² = 0,74)
| Variable | Coeficiente | p | Lectura |
|---|---|---|---|
| log PIB pc PPA | 0,32 | 0,013 | Un PIB per cápita 10% mayor se asocia con +0,03 puntos de felicidad |
| Esperanza de vida | 0,033 | 0,056 | +1 año, +0,03 puntos (en el límite) |
| Control de corrupción | 0,11 | 0,28 | No significativa una vez que está el PIB |
| Gasto en salud % PIB | 0,08 | 0,018 | +1 punto del PIB en salud, +0,08 de felicidad |
| Gini (último 2015-2021) | −0,016 | 0,12 | Más desigualdad, algo menos felicidad (no significativo) |

- VIF máximo 4,95: aceptable.
- Breusch-Pagan p = 0,001: la varianza no es constante, por eso se usan errores robustos.
- Más influyente: Botswana (felicidad 3,5 cuando el modelo predice 5,2). Argentina queda casi justo en lo predicho (6,0 contra 5,9). Brasil y Honduras son más felices de lo que "les toca".
- Archivos: `resultados/lineal_felicidad_2021.csv` y `..._residuos.csv` (real, predicho y residuo por país).

### Ejemplo 2: logística, democracia electoral 2021 (n = 142: 82 democracias, 60 no)
| Variable | Odds ratio | IC 95% | Lectura |
|---|---|---|---|
| log PIB pc PPA | 2,28 | 1,53 – 3,40 | Cada vez que el PIB pc se multiplica por 2,7, la chance de ser democracia se multiplica por 2,3 |
| Gasto en educación % PIB | 1,91 | 1,38 – 2,64 | Cada punto más del PIB en educación casi duplica la chance |
| Medio Oriente y Norte de África | 0,07 | 0,01 – 0,39 | Mucho menor chance, a igual riqueza y educación |

- AUC = 0,85, pseudo R² = 0,30, acierta 75%. Se equivoca más con las no democracias (21 de 60 predichas como democracias, por ejemplo Singapur, con 0,82).
- Eventos por variable = 20, VIF ≈ 1: la base alcanza bien.
- Archivos: `resultados/logistica_democracia_2021.csv` y `..._probabilidades.csv`.

### Ejemplo 3: panel 2011-2024, felicidad ~ log PIB pc (1.910 país-año, 160 países)
- Agrupado (compara países entre sí): coeficiente 0,79 (error 0,04).
- Efectos fijos por país (cada país contra sí mismo): coeficiente 1,39 (error 0,34, nueve veces mayor).
- El efecto fijo usa solo la variación dentro de cada país, que es chica en 14 años. Por eso es mucho más impreciso, aunque controla todo lo fijo del país.

---

## 5. Próximos pasos posibles
1. Graficar real contra predicho y los residuos por región (sirve para el dashboard).
2. Repetir el ejemplo 1 con cada índice de gobernanza por separado y comparar.
3. Panel con efectos fijos para esperanza de vida y gasto en salud 2000-2021.
4. Provincias argentinas: panel de provincias por año (pobreza contra VAB público, presión tributaria), con errores agrupados por provincia.
