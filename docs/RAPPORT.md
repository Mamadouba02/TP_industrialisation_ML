# Rapport d'industrialisation

## Objectif et réalisation

Transformer un prototype de classification du churn en service reproductible et vérifiable. Les 28 parties de la procédure sont couvertes par les scripts, configurations, tests et documents ; les étapes nécessitant GitHub, une VM ou des outils absents sont distinguées dans le compte rendu de validation.

Les chemins sont résolus depuis les fichiers plutôt que depuis le dossier courant. L'entraînement conserve les partitions, les métriques et les empreintes ; l'inférence utilise un DataFrame avec les mêmes colonnes. Le modèle est chargé au démarrage, les entrées sont validées et les erreurs ne révèlent pas de détails internes. Les logs structurés sont acheminables vers ELK ; Grafana est provisionné automatiquement. Le build Docker entraîne son propre artefact pour éviter un pickle issu d'une version de bibliothèque incompatible.

## Analyse des résultats

Consulter `models/metadata.json` pour les scores mesurés et `docs/VALIDATION.md` pour les vérifications exécutées. La sélection de Random Forest est une consigne pédagogique, pas une preuve de supériorité. Les performances doivent être comparées au taux de la classe majoritaire et discutées selon le coût des faux négatifs et faux positifs. La probabilité n'a pas été calibrée ; elle ne doit pas être présentée comme une certitude individuelle.

## Limites et suites

Dataset synthétique, absence de validation externe, de test temporel et de labels de production. Un déploiement réel nécessiterait une analyse de dérive, des seuils métier, une calibration et une validation sur données représentatives. Les résultats JMeter et le déploiement distant restent à produire lorsque l'infrastructure est disponible. Les tests de navigateur ne constituent pas un parcours métier complet ; Swagger sert d'interface de démonstration.

## Correspondance des livrables

1. Git local et procédure GitHub : README.
2. Dataset : data/raw/churn.csv.
3. Notebook : notebooks/exploration.ipynb et exploration.py.
4–5. Entraînement et modèle : src/train.py, models/.
6–8. API et tests : api/main.py, tests/.
9. Charge : tests/load/churn.jmx.
10–12. Docker et CI : Dockerfile, docker-compose.yml, .github/workflows/ci.yml.
13–15. Observabilité : monitoring/, docker/logstash/.
16–18. Technique, installation, rapport : docs/TECHNIQUE.md, README.md, ce document.
19. Présentation : docs/PRESENTATION.md.
