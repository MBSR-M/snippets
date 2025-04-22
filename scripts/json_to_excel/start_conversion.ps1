Write-Host "Installing required Python libraries..."

pip install requests pandas openpyxl

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error installing required libraries. Please check pip configuration or try running as administrator."
    exit 1
}

$json_file_path = Read-Host "Enter Json File Path"

Write-Host "Converting JSON to Excel..."
$pythonResult = python .\main.py --json_file_path $json_file_path

# Check if main.py executed successfully
if ($LASTEXITCODE -ne 0) {
    Write-Host "main.py encountered an error during execution."
    exit 1
}

Write-Host $pythonResult
Write-Host "Script completed successfully."
Pause
