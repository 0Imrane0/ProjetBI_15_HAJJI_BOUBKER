#!/bin/bash
# setup_from_docker.sh
# Script à exécuter DANS le container Python (via docker-compose exec)
# Crée les rapports et génère les données depuis DANS Docker

set -e

echo ""
echo "============================================================================"
echo "🚀 DATA SETUP FROM DOCKER - Reports + User Interactions"
echo "============================================================================"
echo ""

# Étape 1: Créer les rapports
echo "📋 Step 1: Creating Metabase reports..."
export DOCKER_ENV=true
python create_metabase_reports.py
if [ $? -eq 0 ]; then
    echo "✅ Reports created successfully"
else
    echo "❌ Failed to create reports"
    exit 1
fi

echo ""

# Étape 2: Générer les données
echo "👥 Step 2: Generating user interactions..."
python generate_data.py
if [ $? -eq 0 ]; then
    echo "✅ User data generated successfully"
else
    echo "❌ Failed to generate user data"
    exit 1
fi

echo ""
echo "============================================================================"
echo "✅ DATA SETUP COMPLETE!"
echo "============================================================================"
echo ""
