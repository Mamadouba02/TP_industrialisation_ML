# Documentation technique

## Flux

`generate_data → churn.csv → split stratifié 80/20 → comparaison de trois modèles → model.pkl + metadata.json → FastAPI → tests → image Docker → CI → déploiement`

Logs : `FastAPI → volume api-logs → Logstash → Elasticsearch → Kibana`.
Métriques : `FastAPI /metrics → Prometheus → Grafana`.

## Données et modèle

2 000 clients synthétiques générés avec la graine 42. Variables : âge, ancienneté, revenu, réclamations, montant mensuel, retards. La cible `churn` est tirée selon la formule de la procédure. Ces données ne démontrent pas une performance sur des clients réels.

La séparation est stratifiée et reproductible. Le scaler de la régression logistique est ajusté uniquement sur le train grâce au Pipeline. Arbre limité à profondeur 5 ; forêt de 200 arbres. Accuracy, précision, rappel et F1 sont enregistrés pour chaque candidat. Random Forest est retenu conformément au TP, même si un autre modèle obtient un meilleur score. `data/processed` conserve les partitions ; `models/metadata.json` conserve leurs tailles, les métriques, les empreintes et la version scikit-learn.

## API et exploitation

Chargement du modèle à l'ouverture de l'application ; échec du démarrage si l'artefact est absent. `MODEL_PATH` permet de changer le modèle et doit pointer vers un artefact accompagné de son `metadata.json`. Charger uniquement des fichiers joblib de confiance. L'ordre et les noms des variables sont partagés entre entraînement et inférence.

Une seule évaluation de `predict_proba` fournit la classe (argmax sur les classes du modèle) et la probabilité du churn, ce qui évite deux parcours de la forêt. L'endpoint est asynchrone ; un sémaphore limite l'inférence à un travailleur par processus, dans le pool de threads, pour éviter la contention CPU et garder les autres routes disponibles. Le test compare la classe retournée à `model.predict`. La durée d'inférence exclut l'attente du sémaphore ; la durée HTTP et son p95 incluent cette attente. Pour augmenter le débit, dimensionner plusieurs processus ou réplicas et vérifier leur consommation mémoire.

`POST /predict` : six variables obligatoires, compteurs entiers non négatifs, âge entre 18 et 120, montants finis non négatifs, champs supplémentaires refusés. Réponse : classe, probabilité du churn, version, durée. Erreur de validation : 422 ; erreur d'inférence : 503 sans détails internes. `/health` vérifie la présence du modèle ; `/model/info` présente sa provenance. Swagger constitue l'interface interactive du TP ; aucun frontend métier distinct n'est livré.

Logs JSON ligne par ligne : timestamp UTC, identifiant de requête, adresse du client sur l'événement HTTP, opération, version, statut, résultat, probabilité et durée. Les variables client ne sont pas journalisées. `LOG_DIR` configure le stockage. Prévoir rétention/rotation et contrôle d'accès pour une exploitation durable.

Compteurs de prédictions par résultat/version, histogramme d'inférence et métriques HTTP. Le dashboard présente requêtes, p95 HTTP, erreurs, taux d'erreur et prédictions. Ces métriques mesurent le service, pas la qualité prédictive : celle-ci nécessite des étiquettes réelles différées, le suivi de dérive et l'évaluation périodique.

## Tests et livraison

Tests unitaires de génération, tests d'intégration API avec le vrai modèle, validation des entrées, panne simulée et métriques. Selenium vérifie Swagger dans un navigateur ; JMeter mesure la charge avec assertion HTTP et résultat. La CI effectue également un test HTTP du conteneur construit.

Déploiement local pédagogique. Avant production : données réelles gouvernées, authentification, TLS, limites de requêtes, sauvegardes, rotation des logs, images évaluées, ressources dimensionnées et seuils d'alerte adaptés. Le retour arrière utilise un ensemble cohérent code/modèle/dépendances ; une nouvelle version doit franchir des critères de validation définis avant promotion.
