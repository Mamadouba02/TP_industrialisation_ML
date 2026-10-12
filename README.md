# Industrialisation ML — prédiction du churn

Implémentation du TP `industr_ML.txt`. Données synthétiques pédagogiques, classification binaire, Random Forest exposé par FastAPI.

## Installation Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/generate_data.py
python src/train.py
python notebooks/exploration.py
pytest
uvicorn api.main:app --reload
```

Linux : `python3 -m venv .venv`, puis `source .venv/bin/activate` ; les autres commandes sont identiques. Python 3.12 est utilisé ici et en CI/Docker.

API : http://localhost:8000 ; Swagger : http://localhost:8000/docs ; disponibilité : `/health` ; métadonnées : `/model/info` ; métriques : `/metrics`.

```powershell
$payload = @{age=35;anciennete=5;revenu=450000;nb_reclamations=2;montant_mensuel=25000;retards_paiement=2} | ConvertTo-Json
Invoke-RestMethod http://localhost:8000/predict -Method Post -ContentType 'application/json' -Body $payload
```

## Docker et observabilité

```sh
docker compose build
docker compose up -d
docker compose --profile monitoring --profile elk up -d
docker compose ps
docker compose logs api
docker compose down
```

Prometheus : http://localhost:9090 ; Grafana : http://localhost:3000 (admin / churn-local-demo, modifier `GRAFANA_ADMIN_PASSWORD`) ; Kibana : http://localhost:5601. Grafana reçoit automatiquement sa source et son dashboard. Kibana : créer une vue de données `churn-logs-*` avec `@timestamp`, puis filtrer `operation:prediction`, `level:ERROR`, `model_version` et `response_time_ms`. ELK est une configuration locale pédagogique sans authentification ; les ports publiés sont limités à localhost. Prévoir plusieurs Go de mémoire pour l'ensemble.

## Tests navigateur et charge

API démarrée, Chrome installé : sous PowerShell, `$env:RUN_E2E='1'; pytest tests/test_selenium.py`. Le test vérifie le chargement de Swagger et la présence de `/predict`. Sans activation explicite il est ignoré par pytest. La CI l'exécute sur le conteneur.

Plan JMeter : [tests/load/churn.jmx](tests/load/churn.jmx). Java est requis. Une installation portable de JMeter 5.6.3 est disponible localement dans `tools/apache-jmeter-5.6.3` ; elle est exclue du dépôt. Sous Windows, remplacer `jmeter` par `.\tools\apache-jmeter-5.6.3\bin\jmeter.bat`. Exécuter depuis la racine, API démarrée :

```sh
jmeter -n -t tests/load/churn.jmx -Jusers=100 -Jramp=10 -Jloops=10 -l reports/load/100.jtl -e -o reports/load/100
jmeter -n -t tests/load/churn.jmx -Jusers=500 -Jramp=10 -Jloops=10 -l reports/load/500.jtl -e -o reports/load/500
jmeter -n -t tests/load/churn.jmx -Jusers=1000 -Jramp=10 -Jloops=10 -l reports/load/1000.jtl -e -o reports/load/1000
```

Créer `reports/load` au préalable ; chaque répertoire de sortie HTML doit être vide ou inexistant. Relever moyenne, médiane, p90, p95, débit et pourcentage d'erreurs. Ces mesures doivent être faites sur une machine identifiée ; aucune valeur de charge n'est inventée.

## GitHub et déploiement

Le workflow `.github/workflows/ci.yml` génère les données, entraîne, teste, construit l'image, vérifie le conteneur et lance Selenium. Il ne publie ni ne déploie automatiquement.

Le projet est publié sur [GitHub](https://github.com/Mamadouba02/TP_industrialisation_ML) avec `main`, `develop` et `feature/model`. Pour les nouvelles fonctionnalités, créer une branche et ouvrir une PR vers `develop`. Pour rattacher un nouveau dossier local au dépôt :

```sh
git remote add origin https://github.com/Mamadouba02/TP_industrialisation_ML.git
git push -u origin main
git push -u origin develop
```

Sur une VM Linux : installer Docker et Compose, cloner avec `git clone https://github.com/Mamadouba02/TP_industrialisation_ML.git`, puis `docker compose up -d --build` depuis le dépôt. Les ports sont locaux par défaut : accès via tunnel SSH (`ssh -L 8000:localhost:8000 utilisateur@serveur`) ou reverse proxy TLS authentifié. Vérifier `/health` et une prédiction avant mise en service. Pour revenir à une version antérieure, récupérer le commit et le modèle associés, reconstruire puis relancer ; conserver les métriques d'évaluation et les dépendances de chaque version.

Documentation : [architecture](docs/TECHNIQUE.md), [rapport](docs/RAPPORT.md), [présentation et soutenance](docs/PRESENTATION.md), [validation locale](docs/VALIDATION.md).
