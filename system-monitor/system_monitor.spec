# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Collect all Flask and its dependencies
flask_imports = collect_submodules('flask')
werkzeug_imports = collect_submodules('werkzeug')
jinja2_imports = collect_submodules('jinja2')
click_imports = collect_submodules('click')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
    ],
    hiddenimports=[
        # Flask and dependencies
        'flask',
        'flask.json',
        'flask.helpers',
        'werkzeug',
        'werkzeug.serving',
        'werkzeug.routing',
        'werkzeug.security',
        'werkzeug.utils',
        'jinja2',
        'jinja2.ext',
        'click',
        'itsdangerous',
        'markupsafe',
        # System monitoring
        'psutil',
        'psutil._common',
        'psutil._psutil_windows',
        'GPUtil',
        # Plotting
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.figure',
        'matplotlib.backends',
        'matplotlib.backends.backend_agg',
        'matplotlib.backends.backend_pdf',
        # PDF generation
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.pdfgen.canvas',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
        'reportlab.lib.units',
        'reportlab.platypus',
        # Utilities
        'numpy',
        'PIL',
        'PIL.Image',
        'datetime',
        'json',
        'threading',
        'time',
        'os',
    ] + flask_imports + werkzeug_imports + jinja2_imports + click_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'test', 'unittest'],
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
    name='SystemMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SystemMonitor',
)
