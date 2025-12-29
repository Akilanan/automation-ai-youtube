# AI Video Agency - Daily Automation Script
# This script is designed to be run by Windows Task Scheduler

$ScriptPath = "C:\Users\12aki\Downloads\automation ai\automation_ai\main.py"
$PythonPath = "python" # Assumes python is in PATH
$LogPath = "C:\Users\12aki\Downloads\automation ai\automation_ai\automation_log.txt"

echo "--- Starting Daily AI Video Automation: $(Get-Date) ---" >> $LogPath

# Run the AI core
& $PythonPath "$ScriptPath" --topic "Auto" >> $LogPath 2>&1

echo "--- Automation Cycle Finished: $(Get-Date) ---" >> $LogPath
