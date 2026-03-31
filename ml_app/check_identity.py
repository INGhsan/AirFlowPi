import pyodbc

def check_identity():
    available = [d for d in pyodbc.drivers() if 'SQL Server' in d]
    driver = next((d for d in available if '18' in d), None) or \
             next((d for d in available if '17' in d), None) or available[0]
    
    conn_str = f'DRIVER={{{driver}}};SERVER=localhost\\MSSQLSERVER;DATABASE=scout_DW;Trusted_Connection=yes;TrustServerCertificate=yes;Encrypt=yes'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    tables = ['dim_membre', 'Fact_activite', 'Fact_Sponsors', 'Fact_Weather_Events']
    for table in tables:
        print(f"\nChecking table: {table}")
        cursor.execute(f"""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table}' 
            AND COLUMNPROPERTY(OBJECT_ID(TABLE_SCHEMA + '.' + TABLE_NAME), COLUMN_NAME, 'IsIdentity') = 1
        """)
        row = cursor.fetchone()
        if row:
            print(f"  - Identity Column found: {row[0]}")
        else:
            print("  - No Identity Column.")
    
    conn.close()

if __name__ == "__main__":
    check_identity()
