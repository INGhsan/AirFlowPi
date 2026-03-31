import pyodbc
import pandas as pd
import numpy as np

def test():
    available = [d for d in pyodbc.drivers() if 'SQL Server' in d]
    driver = next((d for d in available if '18' in d), None) or \
             next((d for d in available if '17' in d), None) or available[0]
    conn_str = f'DRIVER={{{driver}}};SERVER=localhost;DATABASE=scout_DW;Trusted_Connection=yes;TrustServerCertificate=yes;Encrypt=yes'
    conn = pyodbc.connect(conn_str)
    
    queries = {
        "Members": """
                SELECT u.unit_code, u.unite_name, d.saison, d.annee,
                       COUNT(m.membre_id) AS Nb_Membres,
                       SUM(CASE WHEN m.membre_rank LIKE '%chef%' OR m.membre_rank LIKE '%leader%' OR m.membre_rank LIKE N'%قائد%' THEN 1 ELSE 0 END) AS Nb_Chefs
                FROM dbo.dim_membre m
                JOIN dbo.dim_unite u ON m.unit_fk = u.unit_id
                JOIN dbo.dim_date d ON d.date_id = (SELECT MAX(date_id) FROM dbo.dim_date)
                GROUP BY u.unit_code, u.unite_name, d.saison, d.annee
        """,
        "Budgets": """
                SELECT u.unit_code AS Code_Unite, d.saison AS Saison,
                       SUM(fs.promised_amount_TND) AS Budget_Alloue,
                       SUM(fs.Received_amount_TND) AS Budget_Consomme
                FROM dbo.Fact_Sponsors fs
                JOIN dbo.dim_unite u ON fs.Unit_FK = u.unit_id
                JOIN dbo.dim_date d ON fs.Date_FK = d.date_id
                GROUP BY u.unit_code, d.saison
        """,
        "Activities": """
                SELECT u.unit_code, t.type_name, d.saison, SUM(fa.Nb_Activites) AS nb_activities
                FROM dbo.Fact_activite fa
                JOIN dbo.dim_unite u      ON fa.unit_FK = u.unit_id
                JOIN dbo.dim_type_act_cam t ON fa.type_FK = t.type_id
                JOIN dbo.dim_date d       ON fa.date_FK = d.date_id
                GROUP BY u.unit_code, t.type_name, d.saison
        """
    }
    
    for name, q in queries.items():
        print(f"Testing {name}...")
        try:
            df = pd.read_sql(q, conn)
            print(f"  ✅ {name} success: {len(df)} rows")
            print(df.dtypes)
        except Exception as e:
            print(f"  ❌ {name} failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test()
