import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

def to_num(df):
    out = df.copy()
    for col in out.columns:
        if out[col].dtype == object or str(out[col].dtype) == 'category':
            out[col] = LabelEncoder().fit_transform(out[col].astype(str))
        out[col] = pd.to_numeric(out[col], errors='coerce').fillna(0)
    return out

# Simulate data
np.random.seed(42)
units = ['CHBL', 'CHFA', 'RCHT', 'ZHRT', 'JWLA', 'ASFR']
budgets = pd.DataFrame({
    'Code_Unite': units,
    'Saison': ['Automne']*6,
    'Budget_Alloue': [123024, 726264, 151558, 248952, 82632, 152944]
})

# Augment
parts = [budgets]
for _ in range(6):
    tmp = budgets.copy()
    for col in budgets.select_dtypes(include='number').columns:
        tmp[col] += np.random.normal(0, max(tmp[col].std() * 0.05, 1e-6), len(tmp))
    parts.append(tmp)
budgets = pd.concat(parts, ignore_index=True)

# Train
X3 = to_num(budgets[['Code_Unite', 'Saison']])
y3 = pd.to_numeric(budgets['Budget_Alloue'], errors='coerce').fillna(0).values * np.random.uniform(0.95, 1.1, len(budgets))

print("X3:")
print(X3.head(10))
print("\\ny3:")
print(y3[:10])

rf_b = RandomForestRegressor(n_estimators=100, random_state=42).fit(X3, y3)
preds = rf_b.predict(X3)

res = pd.DataFrame({'Code_Unite': budgets['Code_Unite'], 'Allocated': budgets['Budget_Alloue'], 'Predicted': preds})
print("\\nPredictions:")
print(res.drop_duplicates('Code_Unite'))
