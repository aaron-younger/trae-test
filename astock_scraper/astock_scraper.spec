# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['start_app.py'],
    pathex=['/workspace/astock_scraper'],
    binaries=[],
    datas=[
        ('web/templates/index.html', 'web/templates'),
        ('data/stocks.db', 'data'),
        ('core/__init__.py', 'core'),
        ('core/database.py', 'core'),
        ('core/scraper.py', 'core'),
        ('core/analyzer.py', 'core'),
        ('core/cleaner.py', 'core'),
        ('models/__init__.py', 'models'),
        ('models/stock.py', 'models'),
        ('visualization/__init__.py', 'visualization'),
        ('visualization/charts.py', 'visualization'),
        ('web/__init__.py', 'web'),
        ('web/app.py', 'web'),
    ],
    hiddenimports=[
        'core',
        'core.database',
        'core.scraper', 
        'core.analyzer',
        'core.cleaner',
        'models',
        'models.stock',
        'visualization',
        'visualization.charts',
        'web',
        'web.app',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='astock_scraper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
