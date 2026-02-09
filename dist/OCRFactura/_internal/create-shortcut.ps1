# Creates a desktop shortcut that runs OCRFactura without showing the console (uses RunOCRFactura.vbs).
# Run from the OCRFactura folder (the one that contains OCRFactura.exe).
# Usage: powershell -ExecutionPolicy Bypass -File create-shortcut.ps1

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VbsPath = Join-Path $ScriptDir "RunOCRFactura.vbs"
$ExePath = Join-Path $ScriptDir "OCRFactura.exe"

if (-not (Test-Path $ExePath)) {
    Write-Error "OCRFactura.exe not found at: $ExePath"
    exit 1
}
if (-not (Test-Path $VbsPath)) {
    Write-Error "RunOCRFactura.vbs not found at: $VbsPath"
    exit 1
}

$WshShell = New-Object -ComObject WScript.Shell
$ShortcutPath = Join-Path $WshShell.SpecialFolders.Item("Desktop") "OCRFactura.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $VbsPath
$Shortcut.WorkingDirectory = $ScriptDir
$Shortcut.Description = "OCRFactura — ChatGPT receipt batch to Excel"
$Shortcut.Save()
Write-Host "Shortcut created: $ShortcutPath (opens app without console window)"
