import pyodbc
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error

def to_num(df):
    out = df.copy()
    for col in out.columns:
        if not pd.api.types.is_numeric_dtype(out[col]):
            out[col] = LabelEncoder().fit_transform(out[col].astype(str))
        out[col] = pd.to_numeric(out[col], errors='coerce').fillna(0)
    return out

def feat(df, cols):
    return to_num(df[[c for c in cols if c in df.columns]])

def augment(df, reps=1):
    parts = [df]
    for _ in range(reps):
        tmp = df.copy()
        for col in df.select_dtypes(include='number').columns:
            std = tmp[col].std()
            std = std if not pd.isna(std) else 0.1
            tmp[col] += np.random.normal(0, max(std * 0.05, 1e-6), len(tmp))
        parts.append(tmp)
    return pd.concat(parts, ignore_index=True)

def test_training():
    available = [d for d in pyodbc.drivers() if 'SQL Server' in d]
    driver = next((d for d in available if '18' in d), None) or \
             next((d for d in available if '17' in d), None) or available[0]
    conn_str = f'DRIVER={{{driver}}};SERVER=localhost;DATABASE=scout_DW;Trusted_Connection=yes;TrustServerCertificate=yes;Encrypt=yes'
    conn = pyodbc.connect(conn_str)
    
    print("Loading data...")
    members_raw = pd.read_sql("""
                SELECT u.unit_code, u.unite_name, d.saison, d.annee,
                       COUNT(m.membre_id) AS Nb_Membres,
                       SUM(CASE WHEN m.membre_rank LIKE '%chef%' OR m.membre_rank LIKE '%leader%' OR m.membre_rank LIKE N'%قائد%' THEN 1 ELSE 0 END) AS Nb_Chefs
                FROM dbo.dim_membre m
                JOIN dbo.dim_unite u ON m.unit_fk = u.unit_id
                JOIN dbo.dim_date d ON d.date_id = (SELECT MAX(date_id) FROM dbo.dim_date)
                GROUP BY u.unit_code, u.unite_name, d.saison, d.annee
    """, conn)
    
    print(f"Loaded {len(members_raw)} members. Dtypes:\n{members_raw.dtypes}")
    
    print("Augmenting...")
    members = augment(members_raw, reps=1)
    print("Augmented success.")
    
    print("Training Obj 1...")
    X = feat(members, ['Nb_Chefs', 'Saison', 'annee'])
    print("Feat success.")
    y = members['Nb_Membres'].values * 1.1
    rf = RandomForestRegressor().fit(X, y)
    print("✅ Training success!")

if __name__ == "__main__":
    test_training()
