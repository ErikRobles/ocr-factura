' Launcher that runs OCRFactura.exe without showing the console window.
' Use this as the shortcut target so users get a clean "click icon -> browser opens" experience.
' Double-clicking OCRFactura.exe directly still shows the console (for status and to close the app).
Set fso = CreateObject("Scripting.FileSystemObject")
ScriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
ExePath = fso.BuildPath(ScriptDir, "OCRFactura.exe")
CreateObject("WScript.Shell").Run """" & ExePath & """", 0, False
