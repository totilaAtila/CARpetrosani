# CARpetrosani.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],  # Sau calea către proiect
    binaries=[],
    datas=[
        ('fonts', 'fonts'),
        ('Icons', 'Icons'),
        ('ui', 'ui'),
        ('Arial.ttf', '.'),
        ('DejaVuBoldSans.ttf', '.'),
        ('DejaVuSans.ttf', '.'),
        ('DejaVuSans-Bold.ttf', '.')
    ],
    hiddenimports=[
        'openpyxl',
        'xlsxwriter', 
        'et_xmlfile',
        'reportlab',
        'reportlab.lib',
        'reportlab.pdfgen',
        'reportlab.pdfbase',
        'ssl',
        'cryptography',
        'AppKit',
        'Foundation'
    ],
    hookspath=[],
    hooksconfig={},
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
    name='CARpetrosani',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='universal2',
    codesign_identity=None,
    entitlements_file=None,
    icon='pol.icns',
)