import pyodbc
import pandas as pd
import os

SERVER = 'localhost'
DATABASE = 'scout_DW'

def probe():
    available = [d for d in pyodbc.drivers() if 'SQL Server' in d]
    driver = next((d for d in available if '18' in d), None) or \
             next((d for d in available if '17' in d), None) or available[0]
    
    conn_str = f'DRIVER={{{driver}}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;TrustServerCertificate=yes;Encrypt=yes'
    print(f"Connecting with: {conn_str}")
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print("\n--- Tables and Columns in scout_DW ---")
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = [t[0] for t in cursor.fetchall()]
        
        for table in tables:
            print(f"\n[{table}] columns:")
            cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}'")
            for col in cursor.fetchall():
                print(f"  - {col[0]}")
            
        if not tables:
            print("NO TABLES FOUND!")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    probe()
