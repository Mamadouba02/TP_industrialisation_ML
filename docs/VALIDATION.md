# Validation locale — 12 octobre 2026

## Exécuté

- Windows, Python 3.12.7, Git 2.54.0, Docker 29.4.3, Compose 5.1.3, Java 17.
- Environnement `.venv` créé ; dépendances exactes dans `requirements.txt` ; `pip check` réussi.
- Dataset : 2 000 lignes ; 1 139 non-churn, 861 churn, aucune valeur manquante.
- Trois modèles entraînés ; modèle, partitions, métadonnées et graphiques sauvegardés. Notebook livré.
- Pytest : 13 réussis, 1 Selenium ignoré dans la suite standard. Starlette émet un avertissement de dépréciation TestClient/httpx sans échec.
- API réellement démarrée sur le port temporaire 18000 : `/health` UP ; exemple `/predict` CHURN, probabilité 0,67. Le serveur temporaire est arrêté après validation.
- Syntaxe Python, JSON notebook/dashboard, XML JMeter et configuration Compose complète validés.
- Selenium exécuté avec Chrome headless : 1 réussi (5,09 s), Swagger affiche `/predict`.
- Prometheus démarré et prêt ; Grafana démarré, dashboard `churn-api` provisionné avec cinq panneaux et source Prometheus configurée.

| Modèle | Accuracy | Précision | Rappel | F1 |
|---|---:|---:|---:|---:|
| Régression logistique | 0,6250 | 0,5821 | 0,4535 | 0,5098 |
| Arbre de décision | 0,6325 | 0,5828 | 0,5116 | 0,5449 |
| Random Forest | 0,6050 | 0,5515 | 0,4360 | 0,4870 |

La forêt est conservée selon la consigne ; elle est moins performante que l'arbre sur cette partition. La référence majoritaire du jeu de test vaut 57 %. Ces scores modestes doivent être discutés en soutenance.

## Vérifications en cours

Build Docker, observabilité et JMeter. Les résultats détaillés du navigateur et de la charge sont consignés dans `reports/runtime.json` après exécution. Matériel : Intel Core i7-10510U, 8 processeurs logiques, environ 16 Go de RAM. Les téléchargements et builds concurrents peuvent influencer les mesures locales.

## Infrastructure externe nécessaire

Dépôt GitHub distant, exécution réelle de GitHub Actions et déploiement VM/cloud : aucun compte cible, URL de dépôt ou serveur fourni. Les configurations et le guide sont livrés ; ces étapes ne sont pas déclarées réalisées.
