$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$evidenceDir = Join-Path $PSScriptRoot "evidence"

New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

$dockerPsFile = Join-Path $evidenceDir "docker_ps_$timestamp.txt"
$monitoringFile = Join-Path $evidenceDir "monitoring_summary_$timestamp.json"
$storedRecoFile = Join-Path $evidenceDir "stored_recommendations_user1_$timestamp.json"
$batchStatusFile = Join-Path $evidenceDir "batch_status_$timestamp.json"
$dbCountsFile = Join-Path $evidenceDir "db_counts_$timestamp.txt"

docker-compose ps | Out-File -FilePath $dockerPsFile -Encoding utf8

Invoke-RestMethod -Uri "http://localhost:8000/monitoring/summary" |
    ConvertTo-Json -Depth 10 |
    Out-File -FilePath $monitoringFile -Encoding utf8

Invoke-RestMethod -Uri "http://localhost:8000/stored-recommendations/1?n=5" |
    ConvertTo-Json -Depth 10 |
    Out-File -FilePath $storedRecoFile -Encoding utf8

Invoke-RestMethod -Uri "http://localhost:8000/batch/status" |
    ConvertTo-Json -Depth 10 |
    Out-File -FilePath $batchStatusFile -Encoding utf8

docker exec bi_postgres psql -U admin -d bi_recommendation -c "SELECT COUNT(*) AS users FROM users; SELECT COUNT(*) AS reports FROM reports; SELECT COUNT(*) AS navigation_logs FROM navigation_logs; SELECT COUNT(*) AS recommendations FROM recommendations;" |
    Out-File -FilePath $dbCountsFile -Encoding utf8

Write-Host "Evidence generated in: $evidenceDir"
Write-Host "Files:"
Write-Host " - $dockerPsFile"
Write-Host " - $monitoringFile"
Write-Host " - $storedRecoFile"
Write-Host " - $batchStatusFile"
Write-Host " - $dbCountsFile"
