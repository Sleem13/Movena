param(
    [string]$HostAddress = "127.0.0.1",
    [int]$Port = 8000,
    [switch]$Reload
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$backendDir = Join-Path $repoRoot "backend"
$envFile = Join-Path $repoRoot ".env"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Project virtual environment not found at $python. Create it with: py -3.12 -m venv .venv"
}

$versionOutput = & $python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}'); print(sys.executable)"
$pythonVersion = $versionOutput[0]
$pythonPath = $versionOutput[1]
if ($pythonVersion -ne "3.12") {
    throw "Backend requires Python 3.12, but $pythonPath reports Python $pythonVersion. Recreate .venv with: py -3.12 -m venv .venv"
}

$portUsers = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
    Where-Object { $_.State -in @("Listen", "Bound") } |
    Select-Object -ExpandProperty OwningProcess -Unique

if ($portUsers) {
    $details = foreach ($processId in $portUsers) {
        $process = Get-CimInstance Win32_Process -Filter "ProcessId = $processId" -ErrorAction SilentlyContinue
        if ($process) {
            "PID $processId $($process.Name): $($process.CommandLine)"
        } else {
            "PID $processId"
        }
    }
    throw "Port $Port is already in use.`n$($details -join "`n")`nStop the process or run this script with -Port 8001."
}

if (-not (Test-Path -LiteralPath $envFile)) {
    Write-Warning ".env not found at $envFile. Using application defaults. Copy .env.example to .env for local configuration."
}

$uvicornArgs = @("app.main:app", "--host", $HostAddress, "--port", "$Port")
if (Test-Path -LiteralPath $envFile) {
    $uvicornArgs += @("--env-file", $envFile)
}
if ($Reload) {
    $uvicornArgs += "--reload"
}

Push-Location $backendDir
try {
    & $python -m uvicorn @uvicornArgs
} finally {
    Pop-Location
}
