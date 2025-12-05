from dotenv import find_dotenv
from pathlib import Path
import sys

def main():
    p = find_dotenv()
    print('FOUND_DOTENV_PATH:', repr(p))
    if not p:
        print('No .env found')
        return
    path = Path(p)
    try:
        b = path.read_bytes()
    except Exception as e:
        print('Could not read bytes:', e)
        return
    print('BYTES_START:', ' '.join(['%02X' % x for x in b[:32]]))
    try:
        print('DECODED (utf-8):')
        print(b.decode('utf-8'))
    except Exception as e:
        print('DECODE error:', e)

if __name__ == '__main__':
    main()
