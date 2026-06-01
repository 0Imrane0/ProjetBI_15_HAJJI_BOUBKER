#!/bin/bash
# setup_data.sh - Complete data setup script
# Crée les rapports et génère les données en une seule commande

set -e

echo ""
echo "============================================================================"
echo "🚀 COMPLETE DATA SETUP - Reports + User Interactions"
echo "============================================================================"
echo ""

# Étape 1: Créer les rapports
echo "📋 Step 1: Creating Metabase reports..."
python create_metabase_reports.py
if [ $? -eq 0 ]; then
    echo "✅ Reports created successfully"
else
    echo "❌ Failed to create reports"
    exit 1
fi

echo ""

# Étape 2: Générer les données utilisateur
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
echo "✅ ALL DATA SETUP COMPLETE!"
echo "============================================================================"
echo ""
echo "📊 NEXT STEPS (copy/paste this sequence):"
echo ""
echo "   docker-compose up -d"
echo "   sleep 10"
echo "   docker-compose ps"
echo "   docker-compose logs --tail=80 publisher"
echo "   docker-compose logs --tail=80 consumer"
echo "   docker exec bi_postgres psql -U admin -d bi_recommendation -c \"SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM reports; SELECT COUNT(*) FROM navigation_logs;\""
echo "   curl -X POST http://localhost:8000/train"
echo "   curl \"http://localhost:8000/recommendations/1?n=5\""
echo ""
echo "📘 Full tutorial:"
echo "   docs/final_report/TUTORIAL_TESTER_UTILISER_SOLUTION.md"
echo ""
