import pyodbc

def check_schema():
    available = [d for d in pyodbc.drivers() if 'SQL Server' in d]
    driver = next((d for d in available if '18' in d), None) or \
             next((d for d in available if '17' in d), None) or available[0]
    
    conn_str = f'DRIVER={{{driver}}};SERVER=localhost;DATABASE=scout_DW;Trusted_Connection=yes;TrustServerCertificate=yes;Encrypt=yes'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'dim_membre'")
    for row in cursor.fetchall():
        print(f"{row[0]} -> {row[1]}")
    conn.close()

if __name__ == "__main__":
    check_schema()
