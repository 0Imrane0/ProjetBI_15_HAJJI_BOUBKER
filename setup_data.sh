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
echo "📊 Next steps:"
echo "   1. Run: docker-compose up -d"
echo "   2. Check Publisher/Consumer logs: docker-compose logs -f publisher consumer"
echo "   3. Open Metabase: http://localhost:3000"
echo "   4. Verify data in PostgreSQL:"
echo ""
echo "      docker exec -it bi_postgres psql -U admin -d bi_recommendation"
echo "      SELECT COUNT(*) FROM navigation_logs;"
echo "      SELECT COUNT(*) FROM users;"
echo "      SELECT COUNT(*) FROM reports;"
echo ""
