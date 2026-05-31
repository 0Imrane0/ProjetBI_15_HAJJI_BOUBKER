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
Write-Host "📊 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Run: docker-compose up -d" -ForegroundColor White
Write-Host "   2. Check logs: docker-compose logs -f publisher consumer" -ForegroundColor White
Write-Host "   3. Open Metabase: http://localhost:3000" -ForegroundColor White
Write-Host "   4. Verify data in PostgreSQL:" -ForegroundColor White
Write-Host ""
Write-Host "      docker exec -it bi_postgres psql -U admin -d bi_recommendation" -ForegroundColor Gray
Write-Host "      SELECT COUNT(*) FROM navigation_logs;" -ForegroundColor Gray
Write-Host "      SELECT COUNT(*) FROM users;" -ForegroundColor Gray
Write-Host "      SELECT COUNT(*) FROM reports;" -ForegroundColor Gray
Write-Host ""
