# build.spec
# ==========
# PyInstaller spec file for Medical Diagnosis System.
#
# Build command:
#   pyinstaller build.spec
#
# All required data files (CSV, PKL, EXE, ICO) are bundled into the
# one-folder distribution so resource_path() resolves them correctly.

import sys
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

block_cipher = None

a = Analysis(
    ['medical_gui.py'],
    pathex=['.'],
    binaries=[
        # Bundle the C++ risk analyser executable
        ('RiskAnalyzer.exe', '.'),
    ],
    datas=[
        # Dataset and model files
        ('Training.csv',        '.'),
        ('Testing.csv',         '.'),
        ('medical_model.pkl',   '.'),
        # Application icon
        ('medical_icon.ico',    '.'),
    ],
    hiddenimports=[
        'sklearn.tree._classes',
        'sklearn.utils._typedefs',
        'sklearn.utils._heap',
        'sklearn.utils._sorting',
        'sklearn.utils._vector_sentinel',
        'joblib',
        'pandas',
        'reportlab',
        'reportlab.platypus',
        'reportlab.lib.styles',
        'reportlab.lib.pagesizes',
        'reportlab.lib.units',
        'reportlab.lib.colors',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'tkinter',
        'notebook',
        'IPython',
        'scipy',
        'numpy.testing',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MedicalDiagnosisSystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,           # compress with UPX if available (reduces size ~30%)
    console=False,      # no console window (GUI app)
    icon='medical_icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MedicalDiagnosisSystem',
)
