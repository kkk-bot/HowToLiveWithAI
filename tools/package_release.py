#!/usr/bin/env python3
"""Package the current reading editions and their public sources for offline use."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import argparse, json

ROOT = Path(__file__).resolve().parents[1]


def public_files():
    names = [
        'README.md', 'CONTRIBUTING.md', 'CHANGELOG.md', 'LICENSE',
        'requirements.txt', 'project.json', '.nojekyll', '.gitignore',
        '.gitattributes', 'index.html', '阅读全文.html', '完整指南.md',
        'downloads/普通人的AI学习指南.pdf', 'downloads/build-manifest.json',
    ]
    files = {ROOT / name for name in names}
    for pattern in ('book/*.md', 'docs/**/*.md', 'assets/*.png', 'assets/*.jpg',
                    'assets/*.md', 'tools/*.py', 'tools/*.cjs', '.github/**/*.yml'):
        files.update(ROOT.glob(pattern))
    return sorted(files)


def check_archive(archive, files):
    with ZipFile(archive) as bundle:
        if bundle.testzip() is not None:
            raise ValueError('Corrupt archive')
        expected = {'HowToLiveWithAI/' + p.relative_to(ROOT).as_posix(): p for p in files}
        if set(bundle.namelist()) != set(expected) or len(bundle.namelist()) != len(expected):
            raise ValueError('Offline archive file list differs')
        for name, path in expected.items():
            if bundle.read(name) != path.read_bytes():
                raise ValueError('Offline archive is stale: ' + name)
    print(json.dumps({'archive': archive.name, 'files': len(files), 'contents': 'passed'}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    meta = json.loads((ROOT / 'project.json').read_text())
    archive = ROOT / 'downloads' / f'HowToLiveWithAI-v{meta["version"]}.zip'
    files = public_files()
    if not args.check:
        with ZipFile(archive, 'w', ZIP_DEFLATED) as bundle:
            for path in files:
                bundle.write(path, 'HowToLiveWithAI/' + path.relative_to(ROOT).as_posix())
    check_archive(archive, files)


if __name__ == '__main__':
    main()
