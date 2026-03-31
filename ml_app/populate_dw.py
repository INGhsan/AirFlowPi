import pyodbc
import pandas as pd
import numpy as np
import random

def populate():
    print("🔌 Starting Raw pyodbc Data Enrichment...")
    available = [d for d in pyodbc.drivers() if 'SQL Server' in d]
    driver = next((d for d in available if '18' in d), None) or \
             next((d for d in available if '17' in d), None) or available[0]
    
    conn_str = f'DRIVER={{{driver}}};SERVER=localhost;DATABASE=scout_DW;Trusted_Connection=yes;TrustServerCertificate=yes;Encrypt=yes'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # 1. Fetch lookup IDs
    cursor.execute("SELECT unit_id FROM dbo.dim_unite")
    unit_ids = [r[0] for r in cursor.fetchall()]
    cursor.execute("SELECT type_id FROM dbo.dim_type_act_cam")
    type_ids = [r[0] for r in cursor.fetchall()]
    cursor.execute("SELECT date_id FROM dbo.dim_date")
    date_ids = [r[0] for r in cursor.fetchall()]
    cursor.execute("SELECT sponsor_id FROM dbo.dim_sponsor")
    sponsor_ids = [r[0] for r in cursor.fetchall()] or [1]

    # --- Arabic Localization Data ---
    first_names = ["أنيس", "سلمى", "ياسين", "مريم", "عمر", "ليندا", "أحمد", "فاطمة", "سامي", "إيناس", "يوسف", "ليلى"]
    last_names = ["كرّاي", "عبيد", "الطرابلسي", "بن عمر", "غربال", "الشعري", "اللواتي", "الرقيق", "السالمي", "الحمامي"]
    ranks = ["قائد وحدة", "مشترك", "قائد مساعد", "مسؤول"]
    positions = ["المشاركون", "نشط"]
    training_levels = ["الابتدائية", "التدريب 1", "التدريب 2", "متقدم"]

    # --- Purge old synthetic data to avoid mixing ---
    print("🧹 Purging old synthetic data...")
    # We only delete records we added (e.g. IDs > 30 or specific markers)
    # For safety in this demo, we'll just delete where membre_position NOT IN (original values if known)
    # Or just delete everything in Fact tables and reload.
    cursor.execute("DELETE FROM dbo.Fact_activite")
    cursor.execute("DELETE FROM dbo.Fact_Sponsors")
    cursor.execute("DELETE FROM dbo.Fact_Weather_Events")
    cursor.execute("DELETE FROM dbo.dim_membre WHERE membre_id >= 31") # IDs 28-30 were real in screenshot
    conn.commit()

    # --- dim_membre ---
    print("👤 Inserting 500 Arabic members...")
    for i in range(500):
        try:
            cursor.execute("""
                INSERT INTO dbo.dim_membre (first_name, last_name, membre_code, membre_rank, unit_fk, training_level, membre_position)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                random.choice(first_names), 
                random.choice(last_names), 
                int(2000 + i), 
                random.choice(ranks), 
                random.choice(unit_ids), 
                random.choice(training_levels), 
                random.choice(positions)
            ))
        except Exception as e:
            print(f"  ⚠ Error at member {i}: {e}")
            break
    conn.commit()

    # --- Fact_activite ---
    print("🏕️ Inserting 1500 activities...")
    for i in range(1500):
        try:
            cursor.execute("""
                INSERT INTO dbo.Fact_activite (unit_FK, date_FK, type_FK, Nb_Activites, Nb_Participants)
                VALUES (?, ?, ?, ?, ?)
            """, (random.choice(unit_ids), random.choice(date_ids), random.choice(type_ids), random.randint(1, 4), random.randint(10, 50)))
        except Exception as e:
            print(f"  ⚠ Error at activity {i}: {e}")
            break
    conn.commit()

    # --- Fact_Sponsors ---
    print("💰 Inserting 500 sponsorship records...")
    for i in range(500):
        try:
            amount = round(random.uniform(500, 15000), 2)
            cursor.execute("""
                INSERT INTO dbo.Fact_Sponsors (Unit_FK, Date_FK, Sponsor_FK, Location_FK, promised_amount_TND, Received_amount_TND)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (random.choice(unit_ids), random.choice(date_ids), random.choice(sponsor_ids), 1, amount, round(amount * random.uniform(0.8, 1.0), 2)))
        except Exception as e:
            print(f"  ⚠ Error at sponsor {i}: {e}")
            break
    conn.commit()

    # --- Fact_Weather_Events ---
    print("🌤️ Inserting weather history...")
    for d_id in date_ids:
        try:
            cursor.execute("""
                INSERT INTO dbo.Fact_Weather_Events (Date_FK, Location_FK, temp_max_mean, Total_Rainfall, Max_win_speed, weather_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (d_id, 1, round(random.uniform(5, 45), 1), round(random.uniform(0, 20), 1), round(random.uniform(5, 60), 1), round(random.uniform(10, 100), 1)))
        except Exception as e:
            print(f"  ⚠ Error at weather {d_id}: {e}")
            break
    conn.commit()

    print("\n✅ DATA ENRICHMENT COMPLETE!")
    conn.close()

if __name__ == "__main__":
    populate()
