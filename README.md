# Scout Intelligence Hub (ML & Analytics)

📋 **Description**  
Ce volet du projet transforme le scoutisme traditionnel en un modèle de **Scoutisme Digital** grâce à l'intelligence artificielle et l'analyse prédictive. Il est alimenté par un **Data Warehouse (DW)** localisé en langue arabe.

🚀 **Fonctionnalités Clés**
Le dashboard comprend **13 objectifs ML** avancés :
- **Prédictions**: Forecasting des effectifs et prédiction du taux de participation.
- **Classification & Risque**: Détection d'anomalies financières et identification des unités à risque.
- **Segmentation**: Clustering comportemental et scoring d'engagement des membres.
- **Adaptation**: Modélisation météo et simulateur d'adaptation des activités.
- **Alertes**: Système d'alerte précoce (Early Warning) dynamique.

🏗️ **Architecture Technique**
- **Backend**: Flask (Python)
- **ML Engine**: Scikit-learn (Random Forest, KMeans, Isolation Forest)
- **Database**: SQL Server (scout_DW) avec `pyodbc`
- **Frontend**: Dashboard professionnel avec **Chart.js** pour les visualisations.

🚀 **Démarrage**
1. **Lancer le serveur Flask**
   ```bash
   cd ml_app
   python app.py
   ```
2. **Accéder au Hub**
   - **URL**: http://localhost:5000
3. **Visualisation**
   - Naviguez entre les 13 objectifs via le menu latéral.
   - Les graphiques Chart.js s'activent automatiquement pour les visualisations d'engagement.

📊 **Données & Localisation**
Le système est entièrement intégré avec le **Data Warehouse Arabe** (`scout_DW`). Les données incluent des noms, grades et unités localisés pour une fidélité maximale aux opérations réelles.

✅ **Checklist de Stabilisation**
- [x] Connexion DW temps réel
- [x] Nettoyage des doublons (Unique Rows)
- [x] Correction des erreurs NaN
- [x] Optimisation des temps de chargement
- [x] Visualisations professionnelles intégrées

🔧 **Structure du dossier ml_app/**
```
ml_app/
├── app.py             # Cœur de l'application & endpoints
├── export_dw.py       # Outil d'exportation vers Excel
├── populate_dw.py     # Script de localisation Arabe
└── templates/
    └── index.html     # Dashboard interactif
```

📞 **Support**
Pour toute question sur les modèles ML ou les seuils de classification, contactez l'équipe analytique.
