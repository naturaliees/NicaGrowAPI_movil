"""Build a source ZIP using an explicit allowlist; never include credentials."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent.parent
FILES = ['manage.py', 'requirements.txt', 'requirements.lock.txt', 'requirements.azure.txt',
         'gunicorn.conf.py', 'startup.sh']

def build():
    destination = ROOT / 'dist' / 'NicaGrow_Azure.zip'
    destination.parent.mkdir(exist_ok=True)
    sources = [ROOT / name for name in FILES]
    for directory in ('api', 'config'):
        sources.extend(sorted((ROOT / directory).glob('*.py')))
    with ZipFile(destination, 'w', compression=ZIP_DEFLATED) as archive:
        for file in sources:
            archive.write(file, file.relative_to(ROOT).as_posix())
    print(destination)
    return destination

if __name__ == '__main__':
    build()
