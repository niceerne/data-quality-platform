# Plateforme de collecte et de qualité des données

Projet académique / personnel — Python, Pandas, SQL, PostgreSQL, dbt, Airflow, Docker.

## Objectifs

1. **Ingestion** de données depuis des fichiers CSV/Excel, des APIs REST et des bases de données vers PostgreSQL (schéma `raw`).
2. **Contrôles qualité** : valeurs manquantes, doublons, données invalides, incohérences de schéma.
3. **Automatisation** avec Airflow et **suivi de la qualité** dans des tables dédiées (schéma `dq`) + modèles dbt.

## Architecture

```
Sources (CSV/Excel, API, DB)
        │  Python / Pandas (src/dqp/ingestion)
        ▼
  PostgreSQL  raw.*  ──►  contrôles qualité (src/dqp/quality)  ──►  dq.check_results / dq.run_log
        │
        ▼  dbt
  staging.*  (nettoyage, typage, dédoublonnage)  ──►  marts.* (dq_summary)
        ▲
        └── orchestré par Airflow (dags/ingestion_quality_dag.py)
```

## Structure du projet

```
├── docker-compose.yml        # PostgreSQL + Airflow
├── Dockerfile                # image Airflow + dépendances
├── Makefile
├── requirements.txt
├── .env.example
├── sql/init.sql              # schémas raw / staging / dq / marts
├── config/sources.yml        # déclaration des sources et règles qualité
├── data/sample/              # jeux de données d'exemple (avec erreurs volontaires)
├── src/dqp/                  # package Python
│   ├── config.py, db.py
│   ├── ingestion/            # files.py, api.py, database.py
│   └── quality/              # checks.py, runner.py
├── dags/ingestion_quality_dag.py
├── dbt/                      # projet dbt (staging + marts + tests)
└── tests/                    # tests pytest des contrôles qualité
```

## Démarrage rapide

```bash
cp .env.example .env
docker compose up -d --build
# Airflow : http://localhost:8080  (admin / admin)
# Déclencher le DAG "ingestion_quality_pipeline"
```

Sans Docker (mode local, avec un PostgreSQL disponible) :

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make test                 # tests unitaires
python -m dqp.run_all     # ingestion + contrôles (PYTHONPATH=src)
```

## Contrôles qualité implémentés

| Contrôle | Fonction | Exemple |
|---|---|---|
| Valeurs manquantes | `check_missing` | taux de NULL > seuil sur `email` |
| Doublons | `check_duplicates` | clé `customer_id` dupliquée |
| Données invalides | `check_invalid` | email mal formé, montant négatif, date future |
| Schéma | `check_schema` | colonnes manquantes/en trop, types inattendus |

Chaque contrôle écrit une ligne dans `dq.check_results` (run_id, table, contrôle, statut, nb de lignes en échec, taux). Le modèle dbt `dq_summary` agrège le suivi par jour.

## Pistes d'amélioration

- Alertes (email/Slack) en cas d'échec de contrôle critique.
- Dashboard (Metabase / Superset) branché sur `marts.dq_summary`.
- Great Expectations ou Soda en complément.
- Ingestion incrémentale (watermark) pour les sources base de données.
