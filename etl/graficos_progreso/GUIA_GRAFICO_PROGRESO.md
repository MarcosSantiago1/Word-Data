# Gráfico de progreso en el tiempo

Una página interactiva para ver cómo cambió un indicador año a año y comparar lugares entre sí, en tres niveles:

| Nivel | Lugares | Origen de los datos |
|---|---|---|
| Países | 217 países | `datos_procesados/paises_anual.csv` (pasos 1 y 2) |
| Provincias argentinas | 24 jurisdicciones + "Argentina (total país)" | `argentina_provincias/*.csv` |
| Subdivisiones de Latinoamérica | 339 estados, provincias, departamentos y regiones | `latam_subnacional/*.csv` |

## Cómo se regenera

```bash
cd etl
python graficos_progreso/preparar_datos_progreso.py
```

El script no descarga nada: lee las tablas que ya generaron los otros pasos. Conviene correrlo después de la actualización mensual. Produce dos archivos:

- `datos_progreso.json`: las series, una por nivel, indicador y lugar.
- `progreso_en_el_tiempo.html`: la página lista para abrir en el navegador. Es `plantilla_progreso.html` con el JSON pegado adentro, así funciona sin servidor.

Para cambiar el diseño se edita la plantilla; para sumar un indicador se agrega una línea en `IND_PAISES`, `IND_PROVINCIAS` o `IND_LATAM` del script y, si viene de una tabla nueva, su entrada en el diccionario `T` de esa función.

## Las tres vistas

**Valores.** El dato tal cual, en su unidad (por ejemplo, pesos de 2004 o años de vida).

**Índice (base = 100).** Cada serie se divide por su propio valor en el primer año del período y se multiplica por 100. Si Chile pasa de 100 a 172, su PIB per cápita creció 72 %. Sirve para comparar lugares de tamaños muy distintos: la Ciudad de Buenos Aires y Salta empiezan en 100 aunque una tenga cinco veces el ingreso de la otra.

**Ranking.** Para cada año se ordenan todos los lugares del nivel con dato y se cuenta el puesto. El 1.° es el mejor: el valor más alto, salvo en indicadores donde menos es mejor (mortalidad, pobreza, homicidios, Gini), donde el 1.° es el más bajo. El total país no compite en el ranking.

## Cómo se mide el progreso

La tabla "Cómo cambió cada uno" y el gráfico de barras "Quién avanzó más" comparan el primer y el último año del período. Si falta justo ese año, se usa el más cercano dentro de 3 años (el Gini, por ejemplo, sale de encuestas que no se hacen todos los años).

Cada indicador tiene dos reglas fijas en el script:

- `mejor`: `"alto"`, `"bajo"` o `None`. Decide si un aumento es una mejora (▲ Mejoró) o un empeoramiento. En población, temperatura, producción o gasto no hay juicio: solo se dice si subió o bajó.
- `cambio`: `"pct"` para cambio relativo en % (PIB, salario, producción) o `"pts"` para la diferencia en la unidad (porcentajes, años de vida, °C). Pasar de 30 % a 25 % de pobreza es "−5 puntos", no "−17 %".

Para los indicadores en % la tabla suma el **crecimiento anual promedio**:

```
anual = (valor_final / valor_inicial) ^ (1 / años) − 1
```

Ejemplo, Argentina 2000-2024, PIB per cápita PPA: (26.772 / 22.281) ^ (1/24) − 1 = 0,8 % por año.

## El total país en provincias

"Argentina (total país)" se calcula solo donde tiene sentido sumar:

- Sumas: población, petróleo, gas, soja, maíz, trigo, stock bovino, pernoctes.
- Cocientes de sumas: PBG per cápita (VAB total / población), médicos cada 10.000 hab., empresas cada 1.000 hab., hogares con agua, cloaca y NBI (ponderados por hogares).
- Promedio ponderado: salario, por puestos de trabajo.
- Sin total: pobreza, indigencia y Gini de la EPH (la encuesta no cubre toda la provincia), vacunación, presión tributaria, temperatura.

Los cocientes solo se calculan en años con las 24 provincias.

## Decisiones y cuidados

- **Años incompletos afuera.** Petróleo, gas y pernoctes descartan el año en curso y cualquier año con menos de 12 meses. Pobreza descarta años con menos de 3 trimestres (2026 tiene uno solo).
- **Población provincial hasta el año próximo.** La tabla de INDEC llega a 2040 porque son proyecciones; el gráfico corta en el año siguiente al actual.
- **Sin duplicar Argentina.** Las tablas de Latinoamérica (temperatura, agro, ganadería, petróleo) ya traen las provincias argentinas. En el nivel Latinoamérica se usan tal cual y no se les suma `argentina_provincias/`.
- **El PIB por subdivisión de la OCDE** cubre Brasil, Chile, Colombia, México y Perú. Argentina no tiene PIB regional en la OCDE: para eso está el nivel de provincias.
- **Colores.** Hasta 8 lugares a la vez, con la paleta categórica validada para daltonismo. El color sigue al lugar: si se quita uno, los demás no cambian de color.
- **Qué recuerda la página.** El nivel, el indicador y los lugares elegidos se guardan solo en el navegador de quien la abre.
