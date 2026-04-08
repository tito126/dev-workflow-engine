import zipfile, xml.etree.ElementTree as ET
ppt = r"E:\winning-code\ai\WiN学院-病区护士站_v1.pptx"
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
with zipfile.ZipFile(ppt,'r') as z:
    slides=[n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml') and '/_rels/' not in n]
    print('SLIDE_COUNT', len(slides))
    for i in range(1, min(len(slides), 12)+1):
        path=f'ppt/slides/slide{i}.xml'
        root=ET.fromstring(z.read(path))
        texts=[]
        for sp in root.findall('.//p:sp',ns):
            t=''.join((node.text or '') for node in sp.findall('.//a:t',ns)).strip()
            if t:
                texts.append(t)
        print('--- slide', i, '---')
        for t in texts[:12]:
            print(t)
