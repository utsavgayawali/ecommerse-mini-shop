with open('data.json', 'rb') as f:
    content = f.read()

# UTF-8 BOM is b'\xef\xbb\xbf'
if content.startswith(b'\xef\xbb\xbf'):
    content = content[3:]

with open('data_no_bom.json', 'wb') as f:
    f.write(content)
