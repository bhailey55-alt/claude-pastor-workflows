# claude-pastor-workflows / session-agenda
# Minimal .docx writer (no template) so the file stays small enough to upload as base64.
# Input: JSON list of [text, level, bold, highlight]  (level 0 = title/flush left, 1..4 = indent)
import zipfile, json, sys, html
def run(t, b, hl):
    rpr = '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/>' + ('<w:b/>' if b else '') \
        + ('<w:highlight w:val="yellow"/>' if hl else '') + '<w:sz w:val="26"/></w:rPr>'   # 13 pt
    return f'<w:r>{rpr}<w:t xml:space="preserve">{html.escape(t)}</w:t></w:r>'
def para(t, lvl=0, b=False, hl=False):
    ind = f'<w:ind w:left="{360*lvl+ (360 if lvl else 0)}" w:hanging="{360 if lvl else 0}"/>'
    return f'<w:p><w:pPr><w:spacing w:after="40"/>{ind}</w:pPr>{run(t, b, hl)}</w:p>'
W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
def build(items, out):
    body = ''.join(para(*i) for i in items)
    doc = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document {W}><w:body>{body}<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1080" w:right="1080" w:bottom="1080" w:left="1080"/></w:sectPr></w:body></w:document>'
    ct = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'
    rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr('[Content_Types].xml', ct); z.writestr('_rels/.rels', rels); z.writestr('word/document.xml', doc)
if __name__ == '__main__':
    build(json.load(open(sys.argv[1])), sys.argv[2])
