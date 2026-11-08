"""Función reutilizable para rellenar scorecards UNDRR editando el XML."""
import json, re, sys, os, shutil, zipfile, html

def rellenar(src, xdir, preg_json, RESP, INFO, prefijo, out):

    work = out + '.dir'
    if os.path.exists(work): shutil.rmtree(work)
    shutil.copytree(xdir, work)

    def rd(p): return open(os.path.join(work, p), encoding='utf8').read()
    def wr(p, s): open(os.path.join(work, p), 'w', encoding='utf8').write(s)

    def col_idx(ref):
        letters = re.match(r'[A-Z]+', ref).group(0)
        n = 0
        for ch in letters: n = n * 26 + ord(ch) - 64
        return n

    def set_cell(xml, ref, value):
        """Pone value (número o texto) en la celda ref conservando su estilo."""
        rown = int(re.search(r'\d+', ref).group(0))
        if isinstance(value, (int, float)):
            body = f'<v>{value}</v>'; tattr = ''
        else:
            txt = html.escape(str(value), quote=False)
            body = f'<is><t xml:space="preserve">{txt}</t></is>'; tattr = ' t="inlineStr"'
        m_row = re.search(rf'<row r="{rown}"[^>]*?(?:/>|>.*?</row>)', xml, re.S)
        if not m_row:
            # insertar fila nueva en orden
            rows = [(int(m.group(1)), m.start()) for m in re.finditer(r'<row r="(\d+)"', xml)]
            after = [pos for r, pos in rows if r > rown]
            newrow = f'<row r="{rown}"><c r="{ref}"{tattr}>{body}</c></row>'
            if after: return xml[:after[0]] + newrow + xml[after[0]:]
            i = xml.index('</sheetData>'); return xml[:i] + newrow + xml[i:]
        row = m_row.group(0)
        if row.endswith('/>'):
            row = row[:-2] + '></row>'
        m_c = re.search(rf'<c r="{ref}"([^>]*?)(/>|>.*?</c>)', row, re.S)
        if m_c:
            attrs = re.sub(r'\s+t="[^"]*"', '', m_c.group(1))
            newc = f'<c r="{ref}"{attrs}{tattr}>{body}</c>'
            row = row[:m_c.start()] + newc + row[m_c.end():]
        else:
            newc = f'<c r="{ref}"{tattr}>{body}</c>'
            cells = [(col_idx(m.group(1)), m.start()) for m in re.finditer(r'<c r="([A-Z]+\d+)"', row)]
            after = [pos for c, pos in cells if c > col_idx(ref)]
            if after: row = row[:after[0]] + newc + row[after[0]:]
            else: row = row[:-len('</row>')] + newc + '</row>'
        return xml[:m_row.start()] + row + xml[m_row.end():]

    # mapa hoja -> archivo
    wbx = rd('xl/workbook.xml'); rels = rd('xl/_rels/workbook.xml.rels')
    relmap = {}
    for m in re.finditer(r'<Relationship [^>]*>', rels):
        t = m.group(0); relmap[re.search(r'Id="([^"]+)"', t).group(1)] = re.search(r'Target="([^"]+)"', t).group(1)
    sheetfile = {n: relmap[r].split('/')[-1] for n, r in re.findall(r'<sheet name="([^"]+)" sheetId="\d+" r:id="(rId\d+)"', wbx)}

    preg = json.load(open(preg_json, encoding='utf8'))
    por_hoja = {}
    for q in preg: por_hoja.setdefault(q['sheet'], []).append(q)

    resumen = []
    for hoja, qs in por_hoja.items():
        sf = sheetfile[hoja]; sp = f'xl/worksheets/{sf}'
        xml = rd(sp)
        srels = rd(f'xl/worksheets/_rels/{sf}.rels')
        vml = 'xl/drawings/' + re.search(r'Target="\.\./drawings/(vmlDrawing\d+\.vml)"', srels).group(1)
        v = rd(vml)
        srelmap = {}
        for m in re.finditer(r'<Relationship [^>]*>', srels):
            t = m.group(0); srelmap[re.search(r'Id="([^"]+)"', t).group(1)] = re.search(r'Target="([^"]+)"', t).group(1)
        shape2ctrl = {sid: srelmap[rid] for sid, rid in re.findall(r'<control shapeId="(\d+)" r:id="(rId\d+)"', xml)}
        for q in qs:
            score, conf, evid, accion, resp, plazo = RESP[q['ref']]
            idx = next(i for i, o in enumerate(q['options']) if o.strip().startswith(str(score)))
            val = idx + 1
            row = int(q['resp_cell'][1:])
            xml = set_cell(xml, q['resp_cell'], val)
            xml = set_cell(xml, q['comment_cell'], f'{prefijo} confianza {conf}] {evid}')
            arow = row + 7
            if accion and accion != 'Sin acción.':
                xml = set_cell(xml, f'B{arow}', accion)
                xml = set_cell(xml, f'C{arow}', resp)
                xml = set_cell(xml, f'D{arow}', plazo)
            # estado visual de los botones: VML y ctrlProp
            for i, shp in enumerate(q['shapes']):
                m = re.search(rf'<v:shape id="{shp}".*?</v:shape>', v, re.S)
                block = re.sub(r'\s*<x:Checked>\d</x:Checked>', '', m.group(0))
                if i == idx:
                    block = block.replace('<x:NoThreeD/>', '<x:Checked>1</x:Checked>\n   <x:NoThreeD/>', 1)
                v = v[:m.start()] + block + v[m.end():]
                sidnum = shp.replace('_x0000_s', '')
                if sidnum in shape2ctrl:
                    cp = 'xl/' + shape2ctrl[sidnum].replace('../', '')
                    c = re.sub(r'\s+checked="[^"]*"', '', rd(cp))
                    if i == idx:
                        c = c.replace('objectType="Radio"', 'objectType="Radio" checked="Checked"', 1)
                    wr(cp, c)
            resumen.append((q['sheet'], q['ref'], score, conf))
        wr(sp, xml); wr(vml, v)

    # hoja Info
    isf = 'xl/worksheets/' + sheetfile['Info']
    ix = rd(isf)
    for ref, val in INFO.items():
        ix = set_cell(ix, ref, val)
    wr(isf, ix)

    # recalcular al abrir
    wbx = re.sub(r'<calcPr([^>]*?)/>', lambda m: '<calcPr' + re.sub(r'\s+fullCalcOnLoad="[^"]*"', '', m.group(1)) + ' fullCalcOnLoad="1"/>', wbx)
    wr('xl/workbook.xml', wbx)

    # re-empaquetar respetando el orden original del zip
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = open(os.path.join(work, item.filename), 'rb').read()
            zout.writestr(item, data, compress_type=zipfile.ZIP_DEFLATED)
    shutil.rmtree(work)

    return resumen

