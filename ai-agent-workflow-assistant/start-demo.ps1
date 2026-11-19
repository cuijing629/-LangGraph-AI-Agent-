$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw 'Install dependencies first. See README.md.' }
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
$rag = $null
$backend = $null
try {
    $rag = Start-Process -FilePath $python -ArgumentList '-m uvicorn demo_rag:app --host 127.0.0.1 --port 8001' -PassThru
    $backend = Start-Process -FilePath $python -ArgumentList '-m uvicorn backend:app --host 127.0.0.1 --port 8000' -PassThru
    & $python -m streamlit run frontend.py --server.address 127.0.0.1
} finally {
    $rag, $backend | Where-Object { $_ -and -not $_.HasExited } | Stop-Process
}
