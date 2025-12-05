from pathlib import Path

content = 'GEMINI_API_KEY="AIzaSyA_s72LQxuajfXNRRxf3akZUK8DXDgWZlY"\r\n'

Path('.env').write_text(content, encoding='utf-8')
print('Wrote .env as UTF-8 (no BOM)')
