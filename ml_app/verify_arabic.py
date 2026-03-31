import pyodbc

available = [d for d in pyodbc.drivers() if 'SQL Server' in d]
driver = next((d for d in available if '17' in d), None) or available[0]
conn_str = f'DRIVER={{{driver}}};SERVER=localhost;DATABASE=scout_DW;Trusted_Connection=yes;TrustServerCertificate=yes;Encrypt=yes'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

cursor.execute("SELECT TOP 5 first_name, last_name, membre_rank FROM dbo.dim_membre WHERE membre_id >= 2000")
rows = cursor.fetchall()
for r in rows:
    # Use hex for Arabic characters to be 100% sure in any terminal
    print(f"Row: {r[0]} {r[1]} ({r[2]})")

conn.close()
