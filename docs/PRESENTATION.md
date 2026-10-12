# Présentation finale et préparation à la soutenance

## 1. Problème métier
Anticiper le départ des clients pour orienter les actions de fidélisation. La cible binaire churn définit une classification supervisée. Les données sont synthétiques pour rendre le TP autonome.

## 2. Data Science
Six variables, 2 000 observations, séparation stratifiée 80/20 avec graine 42. Comparaison logistique, arbre et forêt. Random Forest imposé pour la suite ; afficher les scores réels de metadata.json. Discuter précision/rappel selon les coûts métier.

## 3. Service
FastAPI rend le modèle accessible par contrat HTTP indépendant des clients. Validation Pydantic et documentation Swagger. `/health` indique la disponibilité ; `/predict` effectue une inférence. Démontrer une requête valide et une entrée rejetée.

## 4. Qualité
Pytest automatise les contrôles de données et d'API ; unitaire = composant isolé, intégration = coopération API/modèle, E2E = parcours navigateur. Selenium contrôle Swagger. JMeter mesure une charge concurrente : charge = volume attendu, stress = recherche des limites, endurance = durée prolongée. Le p95 est le temps sous lequel 95 % des réponses se situent.

## 5. DevOps
Git conserve l'historique ; branches et PR organisent les changements et la revue. Docker rassemble l'exécution dans une image reproductible. CI vérifie automatiquement tests et build ; la livraison et le déploiement nécessitent un environnement et des autorisations configurés.

## 6. Observabilité
Logs = événements contextualisés ; métriques = agrégats mesurables. ELK permet la recherche d'événements ; Prometheus collecte les séries temporelles ; Grafana les visualise. Démontrer taux de requêtes, erreurs, p95 et nombre de prédictions.

## 7. MLOps
Versionner code, données, environnement et artefact avec leurs empreintes. Comparer le candidat à une référence avant promotion ; conserver l'ancien modèle si le nouveau ne satisfait pas les critères. Surveiller dérive des entrées, disponibilité, latence et qualité avec les vrais labels. Plusieurs versions nécessitent des artefacts et routes ou déploiements identifiables. Retour arrière : redéployer l'ensemble cohérent précédent.

## 8. Démonstration et limites
Génération → entraînement → pytest → Swagger → Compose → métriques/logs. Présenter uniquement les mesures effectivement réalisées. Distinguer la démonstration locale d'un déploiement cloud et d'une validation sur données réelles.
