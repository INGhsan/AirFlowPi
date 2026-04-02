# Airflow + Talend ETL Pipeline

📋 **Description**  
Ce projet configure Apache Airflow pour exécuter automatiquement les jobs Talend ETL dans un environnement Docker.

🏗️ **Architecture**  
- **Postgres**: Base de données pour Airflow
- **Airflow Webserver**: Interface web (port 8080)
- **Airflow Scheduler**: Ordonnanceur des tâches
- **Jobs Talend**:
  - **SA** (Staging Area / Analytics)
  - **DIM** (Dimensions)
  - **FACT** (Tables de faits)

🚀 **Démarrage**
1. **Lancer l'environnement Docker**
   ```bash
   docker-compose up -d
   ```
2. **Accéder à l'interface Airflow**
   - **URL**: http://localhost:8080
   - **Username**: `admin`
   - **Password**: `admin`
3. **Exécuter le pipeline Talend**
   - Trouvez le DAG `01_talend_etl_pipeline`
   - Activez-le (toggle à droite)
   - Cliquez sur le bouton "Play" pour lancer manuellement

📊 **DAGs disponibles**
- **00_smoke_test**: Test simple pour vérifier qu'Airflow fonctionne.
- **01_talend_etl_pipeline**: Pipeline ETL complet (SA → DIM → FACT).
- **01_talend_etl_pipeline_2150**: Pipeline planifié quotidiennement à 21:50.

✅ **État de votre checklist**
- Connections & Configuration: OK
- DAGs & Dependencies: OK
- Automated Jobs: OK
- Monitoring & Logs: OK
- Scheduler integration: ✅ complété
- Talend routines / custom Java code: OK

🔧 **Structure des dossiers**
```
airflow-docker/
├── docker-compose.yaml    # Configuration Docker
├── Dockerfile             # Image Airflow avec Java
├── dags/                  # DAGs Airflow
├── logs/                  # Logs d'exécution
├── plugins/               # Plugins Airflow
└── talend/               # Jobs Talend
```

🛠️ **Commandes utiles**
- **Démarrer**: `docker-compose up -d`
- **Arrêter**: `docker-compose down`
- **Logs**: `docker-compose logs -f`

📞 **Support**
Pour modifier le pipeline ou ajouter de nouveaux jobs Talend, contactez l'équipe technique.
