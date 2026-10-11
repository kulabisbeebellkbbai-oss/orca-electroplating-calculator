from pathlib import Path
import tomllib
from zipfile import ZipFile


def test_wheel_is_complete_and_portable():
    project = tomllib.loads(Path('pyproject.toml').read_text(encoding='utf-8'))['project']
    version = project['version']
    wheels=list(Path('dist').glob(f'electroplating_calculator-{version}-py3-none-any.whl'))
    assert len(wheels)==1, 'Build the release wheel first'
    with ZipFile(wheels[0]) as archive:
        names=set(archive.namelist())
        metadata=f'electroplating_calculator-{version}.dist-info/'
        for suffix in ('METADATA','WHEEL','RECORD','top_level.txt','licenses/LICENSE'):
            assert metadata+suffix in names
        assert archive.read(metadata+'top_level.txt').decode().strip()=='electroplating_calculator'
        assert b'Requires-Dist: numpy<3,>=2' in archive.read(metadata+'METADATA')
        assert f'License-Expression: {project["license"]}'.encode() in archive.read(metadata+'METADATA')
        assert b'Description-Content-Type: text/markdown' in archive.read(metadata+'METADATA')
        assert archive.read(metadata+'licenses/LICENSE') == Path('LICENSE').read_bytes()
        for module in ('__init__.py','geometry.py','calculation.py','settings.py','profiles.py','orca_adapter.py','dialog.py','plugin.py','resources/calculator.html','resources/calculator.js'):
            assert 'electroplating_calculator/'+module in names
        assert all(not any(marker in name for marker in ('tests/','.kimetsu','__pycache__','.venv','C:')) for name in names)
        assert b'Tag: py3-none-any' in archive.read(metadata+'WHEEL')
