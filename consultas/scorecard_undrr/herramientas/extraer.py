import re, json, sys, html, openpyxl, os
src_dir, xlsm, out = sys.argv[1], sys.argv[2], sys.argv[3]
wb = openpyxl.load_workbook(xlsm)
wbxml = open(f'{src_dir}/xl/workbook.xml', encoding='utf8').read()
rels = open(f'{src_dir}/xl/_rels/workbook.xml.rels', encoding='utf8').read()
relmap = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', rels)) | {a: b for b, a in re.findall(r'Target="([^"]+)"[^>]*Id="(rId\d+)"', rels)}
sheets = re.findall(r'<sheet name="([^"]+)" sheetId="\d+" r:id="(rId\d+)"', wbxml)
def clean(t):
    t = re.sub(r'<[^>]+>', '', t); t = html.unescape(t)
    return re.sub(r'\s+', ' ', t).strip()
res = []
for name, rid in sheets:
    if not re.match(r'E\d\d$', name): continue
    sheetfile = relmap[rid].split('/')[-1]
    srels = open(f'{src_dir}/xl/worksheets/_rels/{sheetfile}.rels', encoding='utf8').read()
    vml = re.search(r'Target="\.\./drawings/(vmlDrawing\d+\.vml)"', srels).group(1)
    drw = re.search(r'Target="\.\./drawings/(drawing\d+\.xml)"', srels).group(1)
    ws = wb[name]
    refs = []
    for r in range(1, ws.max_row + 1):
        g = ws.cell(r, 7).value
        if g and str(g).strip():
            refs.append((r, str(g).strip(), str(ws.cell(r, 2).value or '').strip()))
    # textboxes
    d = open(f'{src_dir}/xl/drawings/{drw}', encoding='utf8').read()
    tbs = []
    for a in re.findall(r'<xdr:twoCellAnchor.*?</xdr:twoCellAnchor>', d, re.S):
        m = re.search(r'<xdr:from><xdr:col>(\d+)</xdr:col>.*?<xdr:row>(\d+)</xdr:row>', a, re.S)
        nm = re.search(r'name="([^"]*)"', a).group(1)
        if not nm.startswith('TextBox'): continue
        paras = re.findall(r'<a:p>(.*?)</a:p>', a, re.S)
        t = '\n'.join(clean(''.join(re.findall(r'<a:t>(.*?)</a:t>', p, re.S))) for p in paras).strip()
        if t: tbs.append((int(m.group(2)) + 1, int(m.group(1)), t))
    # radios
    v = open(f'{src_dir}/xl/drawings/{vml}', encoding='utf8', errors='replace').read()
    radios = []
    for shp in re.findall(r'<v:shape .*?</v:shape>', v, re.S):
        if 'ObjectType="Radio"' not in shp: continue
        txt = clean(re.search(r'<v:textbox.*?</v:textbox>', shp, re.S).group(0))
        link = re.search(r'<x:FmlaLink>([^<]+)</x:FmlaLink>', shp)
        sid = re.search(r'id="(_x0000_s\d+)"', shp).group(1)
        anc = [int(x) for x in re.search(r'<x:Anchor>([^<]+)</x:Anchor>', shp).group(1).split(',')]
        radios.append({'shape': sid, 'text': txt, 'link': link.group(1) if link else None, 'row': anc[2] + 1})
    groups = []
    for r in radios:
        if r['link']:
            groups.append({'link': r['link'], 'lrow': int(re.search(r'(\d+)$', r['link']).group(1)), 'opts': []})
    for r in radios:
        cand = [g for g in groups if g['lrow'] - 1 <= r['row'] <= g['lrow'] + 6]
        if len(cand) != 1: print('WARN', name, r, [g['link'] for g in cand]); continue
        cand[0]['opts'].append(r)
    for g in groups:
        if not g['link']: continue
        row = g['lrow']
        # ref = last ref row <= row-4
        ref = [x for x in refs if x[0] <= row][-1]
        q = [t for t in tbs if ref[0] <= t[0] <= row and t[1] == 0]
        gd = [t for t in tbs if ref[0] <= t[0] <= row and t[1] >= 2]
        res.append({'sheet': name, 'ref': ref[1], 'title': ref[2], 'ref_row': ref[0], 'resp_cell': f'E{row}', 'comment_cell': f'C{row}',
                    'question': ' '.join(t[2] for t in q), 'guidance': ' '.join(t[2] for t in gd)[:1500],
                    'options': [o['text'] for o in g['opts']], 'shapes': [o['shape'] for o in g['opts']]})
json.dump(res, open(out, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print(len(res))
for r in res[:3]: print(json.dumps(r, ensure_ascii=False)[:900])
