# PyInstaller spec for OCRFactura (one-folder Windows build).
# Build from project root: pyinstaller OCRFactura.spec
# Output: dist/OCRFactura/OCRFactura.exe (+ dependencies). Copy the whole folder to the user's machine.

block_cipher = None

a = Analysis(
    ['run_ocrfactura.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('core/retailers.json', 'core'),
        ('create-shortcut.ps1', '.'),
        ('RunOCRFactura.vbs', '.'),
        ('GUIA-USUARIO.md', '.'),
    ],
    hiddenimports=[
        'flask',
        'werkzeug',
        'werkzeug.routing',
        'werkzeug.serving',
        'jinja2',
        'openpyxl',
        'openpyxl.cell._writer',
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
    [],
    exclude_binaries=True,
    name='OCRFactura',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Keep console so user sees "Starting OCRFactura..." and any errors
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OCRFactura',
)
