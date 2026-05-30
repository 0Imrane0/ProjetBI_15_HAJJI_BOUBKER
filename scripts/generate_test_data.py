#!/usr/bin/env python3
"""
Generate Test Data: Simulate user interactions
This script creates realistic test data for the recommendation system
"""

import psycopg2
from psycopg2.extras import execute_values
import random
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_NAME = os.getenv("DB_NAME", "bi_recommendation")

class TestDataGenerator:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to PostgreSQL"""
        print("🔗 Connecting to PostgreSQL...")
        try:
            self.conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            self.cursor = self.conn.cursor()
            print("✅ Connected!")
            return True
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    def create_test_users(self, count=10):
        """Create test users"""
        print(f"\n👥 Creating {count} test users...")
        
        users = []
        for i in range(1, count + 1):
            users.append((
                i,  # metabase_user_id
                f"user{i}@example.com",
                f"User {i}",
                random.choice(["analyst", "manager", "executive", "viewer"])
            ))

        try:
            execute_values(
                self.cursor,
                """
                INSERT INTO users (metabase_user_id, email, name, role)
                VALUES %s
                ON CONFLICT (metabase_user_id) DO NOTHING
                """,
                users
            )
            self.conn.commit()
            print(f"✅ Created {count} users")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            self.conn.rollback()
            return False

    def create_test_reports(self, count=15):
        """Create test reports"""
        print(f"\n📊 Creating {count} test reports...")
        
        categories = ["Sales", "Finance", "HR", "Marketing", "Operations", "Analytics"]
        reports = []
        
        for i in range(1, count + 1):
            reports.append((
                i,  # metabase_report_id
                f"Report {i}: {random.choice(categories)} Dashboard",
                f"Description for report {i}",
                ",".join(random.sample(categories, 2)),
                random.choice(categories)
            ))

        try:
            execute_values(
                self.cursor,
                """
                INSERT INTO reports (metabase_report_id, title, description, tags, category)
                VALUES %s
                ON CONFLICT (metabase_report_id) DO NOTHING
                """,
                reports
            )
            self.conn.commit()
            print(f"✅ Created {count} reports")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            self.conn.rollback()
            return False

    def generate_interactions(self, num_interactions=200):
        """Generate realistic user-report interactions"""
        print(f"\n🖱️  Generating {num_interactions} user interactions...")
        
        # Get existing users and reports
        self.cursor.execute("SELECT id FROM users LIMIT 10")
        user_ids = [row[0] for row in self.cursor.fetchall()]
        
        self.cursor.execute("SELECT id FROM reports LIMIT 15")
        report_ids = [row[0] for row in self.cursor.fetchall()]

        if not user_ids or not report_ids:
            print("❌ No users or reports found. Create them first!")
            return False

        interactions = []
        now = datetime.now()

        for _ in range(num_interactions):
            user_id = random.choice(user_ids)
            report_id = random.choice(report_ids)
            action = random.choice(["view", "click", "export", "share"])
            duration = random.randint(10, 600)  # 10 seconds to 10 minutes
            timestamp = now - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            interactions.append((
                user_id,
                report_id,
                action,
                duration,
                timestamp
            ))

        try:
            execute_values(
                self.cursor,
                """
                INSERT INTO navigation_logs (user_id, report_id, action, duration, timestamp)
                VALUES %s
                """,
                interactions
            )
            self.conn.commit()
            print(f"✅ Created {num_interactions} interactions")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            self.conn.rollback()
            return False

    def verify_data(self):
        """Verify the generated data"""
        print("\n📋 Verifying data...")
        
        try:
            self.cursor.execute("SELECT COUNT(*) FROM users")
            user_count = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM reports")
            report_count = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM navigation_logs")
            interaction_count = self.cursor.fetchone()[0]

            print(f"\n✅ Data Summary:")
            print(f"   • Users: {user_count}")
            print(f"   • Reports: {report_count}")
            print(f"   • Interactions: {interaction_count}")

            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

def main():
    print("\n" + "="*60)
    print("🚀 TEST DATA GENERATOR - Create Realistic Data")
    print("="*60)

    generator = TestDataGenerator()

    # Connect
    if not generator.connect():
        return

    # Generate data
    generator.create_test_users(count=10)
    generator.create_test_reports(count=15)
    generator.generate_interactions(num_interactions=300)

    # Verify
    generator.verify_data()

    # Close
    generator.close()

    print("\n" + "="*60)
    print("✅ TEST DATA GENERATION COMPLETE!")
    print("="*60)
    print("\n💡 Next steps:")
    print("   1. Check PostgreSQL: SELECT COUNT(*) FROM navigation_logs;")
    print("   2. Run the Publisher to sync with Metabase")
    print("   3. Check RabbitMQ for messages")
    print("   4. Verify Consumer processed the data\n")

if __name__ == "__main__":
    main()
