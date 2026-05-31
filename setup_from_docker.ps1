# setup_from_docker.ps1
# Lance le setup des données DEPUIS DANS Docker (correct way)
# Cela résout le problème de "postgres" vs "localhost"

$ErrorActionPreference = "Stop"

Write-Host "`n" -ForegroundColor White
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "🚀 DATA SETUP FROM DOCKER - Correct Method" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Étape 1 : Vérifier que Docker tourne
Write-Host "🔍 Step 0: Checking Docker status..." -ForegroundColor Yellow
try {
    $status = docker-compose ps
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Start it first!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Étape 2 : Lancer le setup DANS le container PostgreSQL
Write-Host "📋 Step 1: Creating Metabase reports (via docker-compose exec)..." -ForegroundColor Yellow
try {
    docker-compose exec -T postgres python -c "
import os
os.environ['DOCKER_ENV'] = 'true'
os.environ['DB_HOST'] = 'postgres'
exec(open('create_metabase_reports.py').read())
"
    Write-Host "✅ Reports created successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Reports creation had issues, continuing..." -ForegroundColor Yellow
}

Write-Host ""

# Étape 3 : Générer les données DANS le container PostgreSQL
Write-Host "👥 Step 2: Generating user interactions (via docker-compose exec)..." -ForegroundColor Yellow
try {
    docker-compose exec -T postgres python -c "
import os
os.environ['DOCKER_ENV'] = 'true'
os.environ['DB_HOST'] = 'postgres'
exec(open('generate_data.py').read())
"
    Write-Host "✅ User data generated successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠️  User data generation had issues, continuing..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Green
Write-Host "✅ DATA SETUP INITIATED!" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Verification commands:" -ForegroundColor Yellow
Write-Host "   docker exec -it bi_postgres psql -U admin -d bi_recommendation" -ForegroundColor Gray
Write-Host "   SELECT COUNT(*) FROM report_card;" -ForegroundColor Gray
Write-Host "   SELECT COUNT(*) FROM core_user;" -ForegroundColor Gray
Write-Host "   SELECT COUNT(*) FROM recent_views;" -ForegroundColor Gray
Write-Host "   \q" -ForegroundColor Gray
Write-Host ""
