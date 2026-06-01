# setup_data.ps1 - Complete data setup script for Windows
# Crée les rapports et génère les données en une seule commande

$ErrorActionPreference = "Stop"

Write-Host "`n" -ForegroundColor White
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "🚀 COMPLETE DATA SETUP - Reports + User Interactions" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Étape 1: Créer les rapports
Write-Host "📋 Step 1: Creating Metabase reports..." -ForegroundColor Yellow
try {
    python create_metabase_reports.py
    Write-Host "✅ Reports created successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create reports" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Étape 2: Générer les données utilisateur
Write-Host "👥 Step 2: Generating user interactions..." -ForegroundColor Yellow
try {
    python generate_data.py
    Write-Host "✅ User data generated successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to generate user data" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Green
Write-Host "✅ ALL DATA SETUP COMPLETE!" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 NEXT STEPS (copy/paste this sequence):" -ForegroundColor Yellow
Write-Host ""
Write-Host "   docker-compose up -d" -ForegroundColor White
Write-Host "   Start-Sleep -Seconds 10" -ForegroundColor White
Write-Host "   docker-compose ps" -ForegroundColor White
Write-Host "   docker-compose logs --tail=80 publisher" -ForegroundColor White
Write-Host "   docker-compose logs --tail=80 consumer" -ForegroundColor White
Write-Host "   docker exec bi_postgres psql -U admin -d bi_recommendation -c ""SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM reports; SELECT COUNT(*) FROM navigation_logs;""" -ForegroundColor White
Write-Host "   Invoke-RestMethod -Method Post ""http://localhost:8000/train"" | ConvertTo-Json -Depth 10" -ForegroundColor White
Write-Host "   Invoke-RestMethod ""http://localhost:8000/recommendations/1?n=5"" | ConvertTo-Json -Depth 10" -ForegroundColor White
Write-Host ""
Write-Host "📘 Full tutorial:" -ForegroundColor Yellow
Write-Host "   docs/final_report/TUTORIAL_TESTER_UTILISER_SOLUTION.md" -ForegroundColor Cyan
Write-Host ""
