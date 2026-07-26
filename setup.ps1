<#
.SYNOPSIS
    One-shot setup for the GXW4224 Dashboard.
    Installs Python (if missing), downloads the project, installs Python
    dependencies, sets up devices.yaml, and launches the dashboard.

.USAGE
    Right-click this file -> "Run with PowerShell"

    If Windows blocks it with an execution-policy error, instead open
    PowerShell and run:
        powershell -ExecutionPolicy Bypass -File setup.ps1
#>

$ErrorActionPreference = "Stop"

$RepoUrl    = "https://github.com/posi211/GXW4224_Dashboard"
$ZipUrl     = "$RepoUrl/archive/refs/heads/main.zip"
$InstallDir = "$env:USERPROFILE\GXW4224_Dashboard"

function Write-Step($msg) {
    Write-Host ""
    Write-Host "==> $msg" -ForegroundColor Cyan
}

# ---------------------------------------------------------------
# 1. Check for Python, install if missing
# ---------------------------------------------------------------
Write-Step "Checking for Python..."
$python = Get-Command python -ErrorAction SilentlyContinue

if (-not $python) {
    Write-Step "Python not found. Installing..."
    $winget = Get-Command winget -ErrorAction SilentlyContinue

    if ($winget) {
        winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
    } else {
        Write-Step "winget not available — downloading the Python installer directly..."
        $pyInstaller = "$env:TEMP\python-installer.exe"
        Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe" -OutFile $pyInstaller
        Start-Process -FilePath $pyInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0" -Wait
        Remove-Item $pyInstaller
    }

    # Refresh PATH in this session so we can find the newly-installed python.exe
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path", "User")
    $python = Get-Command python -ErrorAction SilentlyContinue

    if (-not $python) {
        Write-Host ""
        Write-Host "Python was installed, but this window doesn't see it on PATH yet." -ForegroundColor Yellow
        Write-Host "Close this window, open a NEW PowerShell window, and run this script again." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "Python installed: $($python.Source)"
} else {
    Write-Host "Found Python: $($python.Source)"
}

# ---------------------------------------------------------------
# 2. Download the project
# ---------------------------------------------------------------
Write-Step "Getting GXW4224_Dashboard..."

if (Test-Path $InstallDir) {
    Write-Host "Found existing folder at $InstallDir — skipping download."
    Write-Host "(Delete that folder first if you want a completely fresh copy.)"
} else {
    $zipPath   = "$env:TEMP\gxw4224_dashboard.zip"
    $extractTo = "$env:TEMP\gxw4224_extract"

    Invoke-WebRequest -Uri $ZipUrl -OutFile $zipPath
    Expand-Archive -Path $zipPath -DestinationPath $extractTo -Force

    $extractedFolder = Get-ChildItem $extractTo | Select-Object -First 1
    Move-Item $extractedFolder.FullName $InstallDir

    Remove-Item $zipPath
    Remove-Item $extractTo -Recurse -Force
    Write-Host "Downloaded to $InstallDir"
}

Set-Location $InstallDir

# ---------------------------------------------------------------
# 3. Install Python dependencies
# ---------------------------------------------------------------
Write-Step "Installing Python dependencies (flask, pysnmp, pyyaml, streamlit)..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# ---------------------------------------------------------------
# 4. Set up devices.yaml from the template, if it doesn't exist
# ---------------------------------------------------------------
if (-not (Test-Path "devices.yaml")) {
    Copy-Item "devices.yaml.example" "devices.yaml"
    Write-Host ""
    Write-Host "devices.yaml created from the template." -ForegroundColor Yellow
    Write-Host "Notepad will open it now — fill in your gateway's real IP, port, and SNMP community string, save, and close it." -ForegroundColor Yellow
    Start-Process -FilePath "notepad.exe" -ArgumentList "devices.yaml" -Wait
}

# ---------------------------------------------------------------
# 5. Launch
# ---------------------------------------------------------------
Write-Step "Starting the dashboard..."
Start-Process -FilePath "start_snmp.bat"

Write-Host ""
Write-Host "Done. The collector is running in the background and the Streamlit dashboard should open in your browser shortly." -ForegroundColor Green
