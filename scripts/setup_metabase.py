#!/usr/bin/env python3
"""
Setup Metabase: Create test reports via API
This script creates sample reports in Metabase for testing the recommendation system
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
METABASE_URL = "http://localhost:3000"
METABASE_USER = os.getenv("METABASE_ADMIN_USER", "admin@bi.local")
METABASE_PASS = os.getenv("METABASE_ADMIN_PASS", "metabase123")
DB_ID = 2  # PostgreSQL database ID in Metabase (usually 2 after setup)

class MetabaseSetup:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.db_id = DB_ID

    def login(self):
        """Authenticate with Metabase"""
        print("🔐 Logging into Metabase...")
        try:
            response = self.session.post(
                f"{METABASE_URL}/api/session",
                json={"username": METABASE_USER, "password": METABASE_PASS}
            )
            if response.status_code == 200:
                self.token = response.json()["id"]
                self.session.headers.update({"X-Metabase-Session": self.token})
                print("✅ Login successful!")
                return True
            else:
                print(f"❌ Login failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def get_database_id(self):
        """Get the PostgreSQL database ID"""
        print("🔍 Finding PostgreSQL database...")
        try:
            response = self.session.get(f"{METABASE_URL}/api/database")
            if response.status_code == 200:
                databases = response.json()
                for db in databases:
                    if db.get("engine") == "postgres":
                        self.db_id = db["id"]
                        print(f"✅ Found PostgreSQL database (ID: {self.db_id})")
                        return self.db_id
                print("⚠️  No PostgreSQL database found, using default ID: 2")
                return 2
            else:
                print(f"❌ Error: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def create_report(self, name, description, table_name, columns):
        """Create a simple report (card) in Metabase"""
        print(f"📊 Creating report: {name}...")
        
        # Build the query
        query = {
            "database": self.db_id,
            "type": "query",
            "query": {
                "source-table": self._get_table_id(table_name),
                "filter": None
            }
        }

        payload = {
            "name": name,
            "description": description,
            "display": "table",
            "dataset_query": query,
            "visualization_settings": {}
        }

        try:
            response = self.session.post(
                f"{METABASE_URL}/api/card",
                json=payload
            )
            if response.status_code == 200:
                card_id = response.json()["id"]
                print(f"✅ Report created! (ID: {card_id})")
                return card_id
            else:
                print(f"❌ Error creating report: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def _get_table_id(self, table_name):
        """Get table ID from table name"""
        # This is a simplified version - in production you'd query the API
        table_map = {
            "users": 1,
            "reports": 2,
            "navigation_logs": 3,
            "recommendations": 4
        }
        return table_map.get(table_name, 1)

    def create_all_reports(self):
        """Create all test reports"""
        reports = [
            {
                "name": "📊 Utilisateurs Actifs",
                "description": "Liste de tous les utilisateurs du système",
                "table": "users",
                "columns": ["name", "email", "role"]
            },
            {
                "name": "📈 Rapports Disponibles",
                "description": "Catalogue de tous les rapports",
                "table": "reports",
                "columns": ["title", "category", "description"]
            },
            {
                "name": "👁️ Historique Navigation",
                "description": "Toutes les interactions utilisateur",
                "table": "navigation_logs",
                "columns": ["user_id", "report_id", "action", "duration"]
            },
            {
                "name": "⭐ Rapports Populaires",
                "description": "Rapports les plus consultés",
                "table": "reports",
                "columns": ["title", "category"]
            },
            {
                "name": "🎯 Recommandations",
                "description": "Recommandations générées par le ML",
                "table": "recommendations",
                "columns": ["user_id", "recommended_report_id", "score"]
            }
        ]

        created_reports = {}
        for report in reports:
            report_id = self.create_report(
                report["name"],
                report["description"],
                report["table"],
                report["columns"]
            )
            if report_id:
                created_reports[report["name"]] = report_id
            time.sleep(1)  # Rate limiting

        return created_reports

def main():
    print("\n" + "="*60)
    print("🚀 METABASE SETUP - Create Test Reports")
    print("="*60 + "\n")

    setup = MetabaseSetup()

    # Step 1: Login
    if not setup.login():
        print("❌ Cannot proceed without login")
        return

    # Step 2: Find database
    setup.get_database_id()

    # Step 3: Create reports
    print("\n📋 Creating test reports...\n")
    reports = setup.create_all_reports()

    # Summary
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    print(f"\n📊 Created {len(reports)} reports:")
    for name, report_id in reports.items():
        print(f"  • {name} (ID: {report_id})")
    print("\n💡 Next step: Run generate_test_data.py to create interactions\n")

if __name__ == "__main__":
    main()
