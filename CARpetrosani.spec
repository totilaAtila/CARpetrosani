# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Lista completă a modulelor din directorul ui care trebuie incluse explicit
ui_modules = [
    'ui.optimizare_index',
    'ui.salvari',
    'ui.statistici',
    'ui.stergere_membru',
    'ui.sume_lunare',
    'ui.validari',
    'ui.verificareIndex',
    'ui.verificare_fise',
    'ui.versiune',
    'ui.vizualizare_anuala',
    'ui.vizualizare_lunara',
    'ui.vizualizare_trimestriala',
    'ui.vizualizari',
    'ui.actualizare_membru',
    'ui.adauga_membru',
    'ui.adaugare_membru',
    'ui.afisare_membri_lichidati',
    'ui.calculator',
    'ui.despre',
    'ui.dividende',
    'ui.generare_luna',
    'ui.imprumuturi_noi',
    'ui.lichidare_membru',
    'ui.listari',
    'ui.listariEUR',
    'ui.modificare_membru',
]

# Module din rădăcină care trebuie incluse explicit
root_modules = [
    'conversie_widget',
    'currency_logic',
    'dialog_styles',
    'utils',
    'car_dbf_converter_widget',
    'main_ui',
]

# Combinăm toate modulele pentru hidden-imports
hidden_imports = ui_modules + root_modules + [
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
]

# Configurăm datele (resurse non-Python) care trebuie incluse
datas = [
    ('fonts', 'fonts'),
    ('icons', 'icons'),
    ('dual_currency.json', '.'),
    ('imprumuturi_noi_config.json', '.'),
    ('imprumuturi_noi_prima_rata.json', '.'),
    ('theme_settings.json', '.'),
    ('car_settings.json', '.'),
    ('config_dobanda.json', '.'),
    ('conversie_config.json', '.'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
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
    [],
    exclude_binaries=True,
    name='CARpetrosani',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='pol.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CARpetrosani',
)

app = BUNDLE(
    coll,
    name='CARpetrosani.app',
    icon='money.ico',
    bundle_identifier='com.carpetrosani.app',
    info_plist={
        'CFBundleName': 'CARpetrosani',
        'CFBundleDisplayName': 'C.A.R. Petroșani',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': 'True',
        'LSMinimumSystemVersion': '10.13.0',
        'NSAppleEventsUsageDescription': 'Aplicația necesită acces pentru funcționarea corectă.',
    },
)
