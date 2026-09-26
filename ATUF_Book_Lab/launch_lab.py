"""Mac launcher support. Standard library only; no source-file patching."""
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent


def project_name(root=ROOT):
    marker = root / '.lab-project'
    if marker.exists():
        name = marker.read_text().strip()
        if not re.fullmatch(r'atuf-reader-[a-f0-9]{12}', name):
            raise RuntimeError('Invalid saved lab project. Preserve this folder and use a fresh extraction.')
        return name
    name = 'atuf-reader-' + secrets.token_hex(6)
    marker.write_text(name + '\n')
    return name


def main():
    os.chdir(ROOT)
    if sys.version_info < (3, 11):
        raise RuntimeError('Install Python 3.11 or later from python.org, then reopen this launcher.')
    # Finder terminals may not initially include Docker Desktop's CLI paths.
    os.environ['PATH'] = os.pathsep.join([
        os.environ.get('PATH', ''), '/usr/local/bin', '/opt/homebrew/bin',
        '/Applications/Docker.app/Contents/Resources/bin'])
    if not shutil.which('docker'):
        raise RuntimeError('Install and start Docker Desktop, then reopen this launcher.')
    os.environ['COMPOSE_PROJECT_NAME'] = project_name()
    print('Lab folder:', ROOT, flush=True)
    print('Docker project:', os.environ['COMPOSE_PROJECT_NAME'], flush=True)
    if sys.argv[1:] == ['stop']:
        return subprocess.call(['docker', 'compose', 'stop'])
    if sys.argv[1:]:
        raise RuntimeError('Only the optional stop argument is supported.')
    report = ROOT / 'test-results' / 'report.json'
    if report.exists():
        status = json.loads(report.read_text()).get('status', 'UNKNOWN')
        print(f'Existing run: {status}. Evidence is preserved at {report}')
        print('This launcher does not overwrite an existing run. For a fresh run,')
        print('stop this lab with Stop_Lab.command and extract the ZIP into a new folder.')
        return 0 if status == 'PASS' else 1
    executable = ROOT / '.venv' / 'bin' / 'python'
    if not executable.exists():
        print('Creating the local Python virtual environment...', flush=True)
        venv.EnvBuilder(with_pip=False).create(ROOT / '.venv')
    os.environ['PATH'] = str(executable.parent) + os.pathsep + os.environ['PATH']
    os.environ['VIRTUAL_ENV'] = str(ROOT / '.venv')
    return subprocess.call([str(executable), str(ROOT / 'test_all.py')])


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as exc:
        print(f'Cannot start the lab: {exc}', file=sys.stderr)
        raise SystemExit(1)
