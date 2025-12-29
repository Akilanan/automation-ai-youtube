$ShortcutName = "Auto_AI_Agent"
$TargetFile = "n8n.cmd" # Assuming n8n is in path, or we use the npm path
$Arguments = "start --tunnel"
$StartupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$ShortcutPath = "$StartupPath\$ShortcutName.lnk"

# Find n8n executable path
$n8nPath = (Get-Command n8n).Source

if (-not $n8nPath) {
    Write-Host "Error: n8n not found in PATH. Please run 'npm install n8n -g' first."
    exit
}

$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $n8nPath
$Shortcut.Arguments = "start --tunnel"
$Shortcut.WindowStyle = 7 # Minimized
$Shortcut.Description = "Starts AI Automation Agent on Boot"
$Shortcut.Save()

Write-Host "Success! AI Agent will now auto-start when you log in."
Write-Host "Shortcut created at: $ShortcutPath"
