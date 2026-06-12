# build.ps1
$ErrorActionPreference = "Stop"

Write-Host "[INFO] Deleting old dist files..." -ForegroundColor Cyan
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue dist/bundle.js, dist/typings/

Write-Host "[INFO] Running Rollup..." -ForegroundColor Cyan
npx rollup -c rollup.config.js
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Rollup failed" -ForegroundColor Red
    exit 1
}

# Copy LWC standalone
$LWC = "node_modules/lightweight-charts/dist/lightweight-charts.standalone.production.js"
if (Test-Path $LWC) {
    Copy-Item $LWC "lightweight_charts_csava/js/lightweight-charts.js"
    Write-Host "[INFO] Copied lightweight-charts v5 standalone" -ForegroundColor Cyan
} else {
    Write-Host "[WARNING] Could not find LWC standalone" -ForegroundColor Yellow
}

# Copy bundle and styles
Copy-Item dist/bundle.js, src/general/styles.css -Destination lightweight_charts_csava/js
Write-Host "`n[BUILD SUCCESS]" -ForegroundColor Green