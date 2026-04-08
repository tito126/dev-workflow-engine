import os, zipfile, xml.etree.ElementTree as ET
ppt = r'D:\飞书\download\异常信息提示培训.pptx'
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
with zipfile.ZipFile(ppt,'r') as z:
    for i in range(1,12):
        path=f'ppt/slides/slide{i}.xml'
        root=ET.fromstring(z.read(path))
        texts=[]
        for sp in root.findall('.//p:sp',ns):
            t=''.join((node.text or '') for node in sp.findall('.//a:t',ns)).strip()
            if t:
                texts.append(t)
        print('--- slide', i, '---')
        for t in texts:
            print(t)
