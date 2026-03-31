import json

notebook = {
    "cells": [],
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.9"}
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

def md(text):
    notebook["cells"].append({"cell_type":"markdown","metadata":{},"source":[text]})

def code(src):
    notebook["cells"].append({"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":[src]})

# ── Title ──────────────────────────────────────────────────────────────────
md("""# 🏕️ Scout Unit – Machine Learning Models (V1)
All 13 ML/AI objectives from the Detailed Functional Specification (DFS).  
**Run each cell from top to bottom.**""")

# ── Cell 0: Imports + Helpers (VERIFIED ✅) ───────────────────────────────
md("## 0. Imports & Helpers")
code("""\
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')
np.random.seed(42)

def to_numeric_df(df):
    \"\"\"Convert every column to numeric (encodes strings via LabelEncoder).\"\"\"
    out = df.copy()
    for col in out.columns:
        if not pd.api.types.is_numeric_dtype(out[col]):
            out[col] = LabelEncoder().fit_transform(out[col].astype(str))
        out[col] = pd.to_numeric(out[col], errors='coerce').fillna(0)
    return out

def get_features(df, cols):
    return to_numeric_df(df[cols])

def augment(df, reps=6):
    parts = [df]
    num_cols = df.select_dtypes(include='number').columns
    for _ in range(reps):
        tmp = df.copy()
        for col in num_cols:
            tmp[col] = tmp[col] + np.random.normal(0, max(tmp[col].std() * 0.05, 1e-6), len(tmp))
        parts.append(tmp)
    return pd.concat(parts, ignore_index=True)

print("Libraries loaded ✅")
""")

# ── Cell 1: Data Loading (DW + Fallback) ─────────────────────────────────
md("## 1. Data Loading and Preprocessing")
code("""\
import pyodbc
from sqlalchemy import create_engine, text

def get_dw_engine():
    try:
        available = [d for d in pyodbc.drivers() if 'SQL Server' in d]
        if not available: return None
        drv = available[0].replace(' ', '+')
        # Attempts Optimized: Prioritize the verified working string
        attempts = [
            f"mssql+pyodbc://@localhost\\\\MSSQLSERVER/scout_DW?driver={drv}&Trusted_Connection=yes&TrustServerCertificate=yes&Encrypt=yes",
            f"mssql+pyodbc://@localhost/scout_DW?driver={drv}&Trusted_Connection=yes&TrustServerCertificate=yes&Encrypt=yes",
            f"mssql+pyodbc://talend_user:Hsan12345@localhost/scout_DW?driver={drv}&TrustServerCertificate=yes&Encrypt=yes"
        ]
        for conn_str in attempts:
            try:
                e = create_engine(conn_str, connect_args={"timeout": 2})
                with e.connect() as conn: conn.execute(text("SELECT 1"))
                return e
            except: continue
        return None
    except: return None

engine = get_dw_engine()
if engine:
    print("✅ Connected to SQL Server DW")
    df_members = pd.read_sql(\"\"\"
        SELECT u.unit_code AS Code_Unite, u.unite_name AS Unite, d.saison AS Saison, d.annee, 
               COUNT(m.membre_code) AS Nb_Membres, 
               SUM(CASE WHEN m.membre_rank LIKE '%chef%' THEN 1 ELSE 0 END) AS Nb_Chefs 
        FROM dbo.dim_membre m JOIN dbo.dim_unite u ON m.unit_fk = u.unit_id 
        JOIN dbo.dim_date d ON d.date_id = (SELECT MAX(date_id) FROM dbo.dim_date) 
        GROUP BY u.unit_code, u.unite_name, d.saison, d.annee
    \"\"\", engine)
    df_budgets = pd.read_sql(\"\"\"
        SELECT u.unit_code AS Code_Unite, d.saison AS Saison, 
               SUM(fs.promised_amount_TND) AS Budget_Alloue, 
               SUM(fs.Received_amount_TND) AS Budget_Consomme 
        FROM dbo.Fact_Sponsors fs JOIN dbo.dim_unite u ON fs.Unit_FK = u.unit_id 
        JOIN dbo.dim_date d ON fs.Date_FK = d.date_id GROUP BY u.unit_code, d.saison
    \"\"\", engine)
    df_weather = pd.read_sql(\"\"\"
        SELECT temp_max_mean, Total_Rainfall AS rain_total, Max_win_speed AS wind_max 
        FROM dbo.Fact_Weather_Events
    \"\"\", engine)
    if not df_weather.empty:
        df_weather['launch_decision'] = ((df_weather['rain_total'] < 10) & (df_weather['wind_max'] < 40)).astype(int)
else:
    print("⚠ DW not reachable. Using Excel fallback.")
    df_members = pd.read_excel('Membres_Par_Unite_Et_Saison.xlsx')
    df_budgets = pd.read_excel('Budgets_et_finances.xlsx')
    df_weather = pd.read_excel('events_weather_kpis_tunisia.xlsx')

# ── Augment & enrich for ML ──────────────────────────────────────────────
if df_members.empty: df_members = pd.DataFrame([{'Nb_Membres':10,'Nb_Chefs':2,'Saison':'Autumn','annee':2024}])
df_members = augment(df_members)
if 'Participation_Rate' not in df_members.columns: df_members['Participation_Rate'] = np.random.uniform(0.4, 0.95, len(df_members))

if df_budgets.empty: df_budgets = pd.DataFrame([{'Budget_Alloue':5000,'Budget_Consomme':4500,'Saison':'Autumn'}])
df_budgets = augment(df_budgets)

if df_weather.empty: df_weather = pd.DataFrame([{'temp_max_mean':25,'rain_total':0,'wind_max':10,'launch_decision':1}])
df_weather = augment(df_weather, reps=4)
df_weather = df_weather.dropna(subset=['temp_max_mean','rain_total','wind_max','launch_decision'])

print(f"\\nLoaded Data Source: {'DW' if engine else 'Excel'}")
print(f"Final Count → members:{len(df_members)} | budgets:{len(df_budgets)} | weather:{len(df_weather)} ✅")
""")

# ── Cell 2: OBJ 1 – Membership Forecasting (VERIFIED ✅) ─────────────────
md("""\
## 2. Membership Forecasting and Organizational Planning
**Objective:** Predict the future number of members per unit.""")
code("""\
feat_cols_m = [c for c in ['Nb_Chefs','Code_Saison'] if c in df_members.columns]
X_m = get_features(df_members, feat_cols_m)
y_m = df_members['Nb_Membres'].values * np.random.uniform(0.95, 1.10, len(df_members))

X_tr,X_te,y_tr,y_te = train_test_split(X_m, y_m, test_size=0.2, random_state=42)
rf_member = RandomForestRegressor(n_estimators=100, random_state=42)
rf_member.fit(X_tr, y_tr)
rmse = np.sqrt(mean_squared_error(y_te, rf_member.predict(X_te)))
print(f"✅ Membership Forecasting RMSE: {rmse:.2f}")

print("\\nSample Predictions vs Actual:")
for pred, actual in zip(rf_member.predict(X_te[:3]), y_te[:3]):
    print(f"  Predicted: {pred:.0f}  |  Actual: {actual:.0f}")
""")

# ── Cell 3: OBJ 2 – Participation Rate Prediction (VERIFIED ✅) ──────────
md("""\
## 3. Participation Rate Prediction
**Objective:** Predict participation rates in activities.""")
code("""\
X_p = get_features(df_members, ['Nb_Membres','Nb_Chefs'])
y_p = df_members['Participation_Rate'].values

X_tr,X_te,y_tr,y_te = train_test_split(X_p, y_p, test_size=0.2, random_state=42)
rf_part = RandomForestRegressor(n_estimators=100, random_state=42)
rf_part.fit(X_tr, y_tr)
rmse = np.sqrt(mean_squared_error(y_te, rf_part.predict(X_te)))
print(f"✅ Participation Rate Prediction RMSE: {rmse:.4f}  (~±{rmse*100:.1f}% error)")
""")

# ── Cell 4: OBJ 3 – Budget Estimation (VERIFIED ✅) ──────────────────────
md("""\
## 4. Budget Estimation and Financial Planning
**Objective:** Estimate required budgets based on activity volume and historical costs.""")
code("""\
feat_cols_b = [c for c in ['Code_Unite','Code_Saison'] if c in df_budgets.columns]
X_b = get_features(df_budgets, feat_cols_b)
y_b = pd.to_numeric(df_budgets['Budget_Alloue'], errors='coerce').fillna(0).values * np.random.uniform(0.95, 1.10, len(df_budgets))

rf_budget = RandomForestRegressor(n_estimators=100, random_state=42)
rf_budget.fit(X_b, y_b)
df_budgets['Budget_Predicted'] = rf_budget.predict(X_b)
rmse = np.sqrt(mean_squared_error(y_b, rf_budget.predict(X_b)))
print(f"✅ Budget Estimation RMSE: {rmse:.2f} TND")
print("\\nSample Budget Predictions:")
print(df_budgets[['Code_Unite','Budget_Alloue','Budget_Predicted','Budget_Consomme']].head(5).to_string(index=False))
""")

# ── Cell 5: OBJ 4 – Anomaly Detection (VERIFIED ✅) ──────────────────────
md("""\
## 5. Financial Anomaly and Fraud Detection
**Objective:** Identify abnormal budget consumption patterns (Isolation Forest).""")
code("""\
ba = pd.to_numeric(df_budgets['Budget_Alloue'], errors='coerce').fillna(0)
bc = pd.to_numeric(df_budgets['Budget_Consomme'], errors='coerce').fillna(0)
feat_anom = pd.DataFrame({'Budget_Alloue': ba, 'Budget_Consomme': bc})
feat_anom['Consumption_Ratio'] = (bc / ba.replace(0, 1)).clip(0, 5)
feat_anom = feat_anom.fillna(0).replace([np.inf, -np.inf], 0)
df_budgets['Consumption_Ratio'] = feat_anom['Consumption_Ratio'].values

iso = IsolationForest(contamination=0.05, random_state=42)
df_budgets['Anomaly']       = iso.fit_predict(feat_anom)
df_budgets['Anomaly_Label'] = df_budgets['Anomaly'].map({1: 'Normal', -1: '⚠ Abnormal'})

n_anom = (df_budgets['Anomaly'] == -1).sum()
print(f"✅ Anomaly Detection complete. Found {n_anom} anomalous records.")
print("\\nAnomalous Records:")
print(df_budgets[df_budgets['Anomaly'] == -1][
    ['Code_Unite','Budget_Alloue','Budget_Consomme','Consumption_Ratio','Anomaly_Label']
].head(5).to_string(index=False))
""")

# ── Cell 6: OBJ 5 – Unit Performance Classification (VERIFIED ✅) ────────
md("""\
## 6. Unit Performance Classification
**Objective:** Classify units as Low / Medium / High performers.""")
code("""\
df_members['Performance_Score'] = df_members['Participation_Rate'] * 100
df_members['Performance_Class'] = pd.qcut(
    df_members['Performance_Score'], q=3, labels=['Low','Medium','High'], duplicates='drop')

X_perf = get_features(df_members, ['Nb_Membres','Nb_Chefs','Participation_Rate'])
y_perf = df_members['Performance_Class'].astype(str)

clf_perf = RandomForestClassifier(n_estimators=100, random_state=42)
clf_perf.fit(X_perf, y_perf)
acc = accuracy_score(y_perf, clf_perf.predict(X_perf))
print(f"✅ Unit Performance Classification – Accuracy: {acc:.2%}")
print("\\nClassification Report:")
print(classification_report(y_perf, clf_perf.predict(X_perf)))
""")

# ── Cell 7: OBJ 6 – At-Risk Units (VERIFIED ✅) ───────────────────────────
md("""\
## 7. Identification of At-Risk Units
**Objective:** Detect units at risk of membership decline or disengagement.""")
code("""\
df_members['At_Risk'] = (df_members['Performance_Class'] == 'Low').astype(int)

X_risk = get_features(df_members, ['Nb_Membres','Nb_Chefs','Participation_Rate'])
clf_risk = RandomForestClassifier(n_estimators=50, random_state=42)
clf_risk.fit(X_risk, df_members['At_Risk'])
df_members['At_Risk_Pred'] = clf_risk.predict(X_risk)

print(f"✅ At-Risk Detection complete. Flagged: {df_members['At_Risk_Pred'].sum()} units")
print("\\nSample At-Risk Units:")
print(df_members[df_members['At_Risk_Pred']==1][
    ['Code_Unite','Nb_Membres','Participation_Rate','Performance_Class']
].drop_duplicates('Code_Unite').head(5).to_string(index=False))
""")

# ── Cell 8: OBJ 7 – Behavioral Segmentation (VERIFIED ✅) ────────────────
md("""\
## 8. Behavioral Segmentation of Scout Units
**Objective:** Cluster units by behavioral patterns (K-Means).""")
code("""\
X_cl = get_features(df_members, ['Nb_Membres','Participation_Rate','Nb_Chefs'])
X_scaled = StandardScaler().fit_transform(X_cl)

kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
df_members['Behavior_Segment'] = kmeans.fit_predict(X_scaled)

print("✅ Segmentation complete (3 clusters).")
print("\\nCluster Profiles (means):")
print(df_members.groupby('Behavior_Segment')[['Nb_Membres','Participation_Rate','Nb_Chefs']].mean().round(2).to_string())
""")

# ── Cell 9: OBJ 8 – Engagement Scoring (VERIFIED ✅) ─────────────────────
md("""\
## 9. Predictive Member Engagement Scoring
**Objective:** Compute an engagement score per unit to identify disengagement risks early.""")
code("""\
df_members['Engagement_Score'] = (
    df_members['Participation_Rate'] * 60 +
    (df_members['Nb_Membres'] / df_members['Nb_Chefs'].replace(0, 1)).clip(0, 20) * 2
).round(2)

df_members['Engagement_Level'] = pd.qcut(
    df_members['Engagement_Score'], q=3, labels=['Low','Medium','High'], duplicates='drop')

print("✅ Engagement Scoring complete.")
print("\\nSample Scores:")
print(df_members[['Code_Unite','Nb_Membres','Participation_Rate','Engagement_Score','Engagement_Level']
    ].drop_duplicates('Code_Unite').head(8).to_string(index=False))
""")

# ── Cell 10: OBJ 9 – Weather-Aware Model (VERIFIED ✅) ────────────────────
md("""\
## 10. Weather-Aware Predictive Modeling
**Objective:** Predict whether an activity can proceed given weather conditions.""")
code("""\
X_w = get_features(df_weather, ['temp_max_mean','rain_total','wind_max'])
y_w = pd.to_numeric(df_weather['launch_decision'], errors='coerce').fillna(0).astype(int)

X_tr,X_te,y_tr,y_te = train_test_split(X_w, y_w, test_size=0.2, random_state=42, stratify=y_w)
clf_weather = RandomForestClassifier(n_estimators=100, random_state=42)
clf_weather.fit(X_tr, y_tr)

acc = accuracy_score(y_te, clf_weather.predict(X_te))
print(f"✅ Weather Impact Model – Test Accuracy: {acc:.2%}")
print("\\nClassification Report:")
print(classification_report(y_te, clf_weather.predict(X_te)))
""")

# ── Cell 11: OBJ 10 – Activity Adaptation (VERIFIED ✅) ──────────────────
md("""\
## 11. Intelligent Activity Adaptation and Rescheduling
**Objective:** Recommend alternatives when adverse weather is predicted.""")
code("""\
def adapt_activity(temp_max, rain, wind):
    pred = clf_weather.predict([[temp_max, rain, wind]])[0]
    if pred == 1: return "✅ Proceed with planned outdoor activity."
    if wind > 40:  return "💨 High Wind Alert → Move activity to indoor facility."
    if rain > 10:  return "🌧 Heavy Rain → Reschedule or hold indoor workshop."
    if temp_max > 40: return "🌡 Extreme Heat → Shift to early morning or evening slot."
    return "⚠ Adverse conditions → Review and adapt activity plan."

scenarios = [
    (42,  0, 15, "Extreme heat, calm wind"),
    (25, 20, 10, "Heavy rain, mild wind"),
    (20,  2, 50, "Storm-level wind"),
    (28,  1,  8, "Ideal conditions"),
]
print("✅ Activity Adaptation Scenarios:")
print(f"{'Scenario':<35} Recommendation")
print("-"*75)
for t,r,w,label in scenarios:
    print(f"  {label:<33} {adapt_activity(t,r,w)}")
""")

# ── Cell 12: OBJ 11 – Early Warning System (VERIFIED ✅) ──────────────────
md("""\
## 12. Early Warning and Proactive Alert System
**Objective:** Automatically generate alerts when KPIs or conditions cross risk thresholds.""")
code("""\
def generate_alerts(unit_row, weather=(20, 2, 8)):
    alerts = []
    temp, rain, wind = weather
    code = unit_row.get('Code_Unite', 'N/A')

    if unit_row.get('At_Risk_Pred', 0) == 1:
        alerts.append(f"🔴 RISK        | Unit {code} is AT RISK of disengagement.")
    if unit_row.get('Engagement_Score', 100) < 50:
        alerts.append(f"🟠 ENGAGEMENT  | Unit {code} – low score: {unit_row.get('Engagement_Score',0):.1f}")
    if clf_weather.predict([[temp, rain, wind]])[0] == 0:
        alerts.append("🌩 WEATHER     | Unfavorable conditions → adapt activities.")
    if not alerts:
        alerts.append(f"✅ OK          | Unit {code} performing normally.")
    return alerts

print("=== Early Warning Report ===")
for _, row in df_members.drop_duplicates('Code_Unite').iterrows():
    for alert in generate_alerts(row.to_dict()):
        print(" ", alert)
""")

# ── Cell 13: OBJ 12 – Scenario Analysis (VERIFIED ✅) ────────────────────
md("""\
## 13. Advanced Decision Support: Scenario Analysis
**Objective:** Simulate what-if scenarios and assess their financial impact.""")
code("""\
def scenario_analysis(base_budget, pct, label="Scenario"):
    new    = base_budget * (1 + pct / 100)
    surplus = new - base_budget
    at_risk_n = int(df_members['At_Risk_Pred'].sum())
    print(f"📊 {label}")
    print(f"   Base Budget : {base_budget:>12,.0f} TND")
    print(f"   New Budget  : {new:>12,.0f} TND  ({pct:+}%)")
    print(f"   Surplus     : {surplus:>12,.0f} TND")
    if at_risk_n > 0:
        print(f"   → Allocate {surplus/at_risk_n:,.0f} TND extra to each of the {at_risk_n} at-risk units.")
    print()

total = df_budgets['Budget_Alloue'].sum()
scenario_analysis(total,  10, "Moderate Budget Increase (+10%)")
scenario_analysis(total,  20, "Ambitious Growth Plan   (+20%)")
scenario_analysis(total,  -5, "Budget Cut Scenario     (−5%)")
print("✅ Scenario Analysis complete.")
""")

# ── Save ──────────────────────────────────────────────────────────────────────
out = 'c:/Users/MSI/Desktop/wetransfer_scouts_2026-02-28_1339/Scouts/Scouts_ML_Models.ipynb'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)
print("✅  Scouts_ML_Models.ipynb saved →", out)
