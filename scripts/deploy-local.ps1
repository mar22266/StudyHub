param([switch]$SkipBuild)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $repo '.env'
$compose = Join-Path $repo 'compose.deploy.yml'

if (-not (Test-Path -LiteralPath $envFile)) {
    $dbPassword = [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(24))
    $jwtSecret = [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
    @(
        'POSTGRES_DB=studyhub'
        'POSTGRES_USER=studyhub_user'
        "POSTGRES_PASSWORD=$dbPassword"
        "DATABASE_URL=postgresql+psycopg://studyhub_user:$dbPassword@db:5432/studyhub"
        "JWT_SECRET=$jwtSecret"
        'FRONTEND_URL=http://localhost:8080'
    ) | Set-Content -LiteralPath $envFile -Encoding utf8
    Write-Host 'Se creó .env local con secretos aleatorios. El archivo está ignorado por Git.'
}

$settings = Get-Content -LiteralPath $envFile -Raw
if ($settings -match 'replace-with|change-me|studyhub_local_development_secret') {
    throw 'Reemplaza los secretos de ejemplo en .env antes del despliegue.'
}

& docker compose --env-file $envFile -f $compose config --quiet
if ($LASTEXITCODE -ne 0) { throw 'La configuración de Docker Compose no es válida.' }

$upArgs = @('compose', '--env-file', $envFile, '-f', $compose, 'up', '-d', '--wait')
if (-not $SkipBuild) { $upArgs += '--build' }
& docker @upArgs
if ($LASTEXITCODE -ne 0) { throw 'El despliegue local falló.' }

$health = Invoke-RestMethod -Uri 'http://127.0.0.1:8080/api/health' -TimeoutSec 10
if ($health.status -ne 'ok') { throw 'La API no respondió correctamente.' }
$page = Invoke-WebRequest -Uri 'http://127.0.0.1:8080/' -TimeoutSec 10
if ($page.StatusCode -ne 200 -or $page.Content -notmatch '<div id="root"') {
    throw 'El frontend no respondió correctamente.'
}
Write-Host 'StudyHub local operativo: http://127.0.0.1:8080/'
