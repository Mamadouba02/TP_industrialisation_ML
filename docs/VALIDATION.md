# Validation locale — 12 octobre 2026

## Exécuté

- Windows, Python 3.12.7, Git 2.54.0, Docker 29.4.3, Compose 5.1.3, Java 17.
- Environnement `.venv` créé, pip mis à jour en 26.2.1 ; dépendances exactes dans `requirements.txt` ; `pip check` réussi.
- Dataset : 2 000 lignes ; 1 139 non-churn, 861 churn, aucune valeur manquante.
- Trois modèles entraînés ; modèle, partitions, métadonnées et graphiques sauvegardés. Notebook livré.
- Pytest : 13 réussis, 1 Selenium ignoré dans la suite standard. Starlette émet un avertissement de dépréciation TestClient/httpx sans échec.
- API réellement démarrée sur le port temporaire 18000 : `/health` UP ; exemple `/predict` CHURN, probabilité 0,67. Le serveur temporaire est arrêté après validation.
- Syntaxe Python, JSON notebook/dashboard, XML JMeter et configuration Compose complète validés.
- Selenium exécuté avec Chrome headless : 1 réussi sur l'API conteneurisée après optimisation, Swagger affiche `/predict`.
- Prometheus démarré et prêt ; Grafana démarré, dashboard `churn-api` provisionné avec cinq panneaux et source Prometheus configurée.
- Image `ml-churn-api:1.0` construite ; API déployée avec Compose, healthcheck healthy, exemple CHURN/0,67.
- ELK démarré ; Kibana disponible, logs réellement indexés dans `churn-logs-*`. Elasticsearch est yellow sur ce nœud unique en raison d'une réplique non affectée ; les shards primaires sont actifs.
- Métriques de l'API effectivement collectées par Prometheus, cible up après optimisation et pendant la charge.
- Projet publié sur `https://github.com/Mamadouba02/TP_industrialisation_ML` : main, develop et feature/model.

| Modèle | Accuracy | Précision | Rappel | F1 |
|---|---:|---:|---:|---:|
| Régression logistique | 0,6250 | 0,5821 | 0,4535 | 0,5098 |
| Arbre de décision | 0,6325 | 0,5828 | 0,5116 | 0,5449 |
| Random Forest | 0,6050 | 0,5515 | 0,4360 | 0,4870 |

La forêt est conservée selon la consigne ; elle est moins performante que l'arbre sur cette partition. La référence majoritaire du jeu de test vaut 57 %. Ces scores modestes doivent être discutés en soutenance.

## Charge JMeter exécutée

Matériel : Intel Core i7-10510U, 8 processeurs logiques, environ 16 Go de RAM. Générateur et pile Docker partagent la machine. Ramp-up 10 s, 10 boucles par utilisateur, timeout de réponse 30 s. Mesures indicatives locales, sans engagement de performance en production.

| Utilisateurs | Requêtes | Moyenne (ms) | Médiane (ms) | p90 (ms) | p95 (ms) | Requêtes/s | Erreurs |
|---|---:|---:|---:|---:|---:|---:|---:|
| 100 | 1 000 | 1 413,89 | 1 598,00 | 2 062 | 2 105 | 40,77 | 0 % |
| 500 | 5 000 | 16 890,07 | 14 622,50 | 30 004 | 30 010 | 24,40 | 12,80 % |
| 1 000 | 10 000 | 29 687,32 | 30 006,00 | 30 015 | 30 017 | 32,29 | 96,17 % |

Le débit inclut les requêtes en erreur : sa hausse à 1 000 utilisateurs n'indique pas davantage de prédictions réussies. Le p95 à 500/1 000 utilisateurs atteint le timeout client ; ce n'est pas un p95 fiable des seules inférences réussies. L'instance unique sature à forte charge et ne satisfait pas une charge de 1 000 utilisateurs. Prévoir contrôle d'admission, limites d'attente et plusieurs réplicas/processus, puis refaire des mesures isolées et définir une cible métier avant une exploitation réelle.

L'optimisation évite le double parcours de la forêt et limite l'inférence à un travailleur par processus. Sur le scénario Docker à 100 utilisateurs, le p95 mesuré passe de 13 441 à 2 105 ms, le débit de 8,48 à 40,77 requêtes/s, avec 0 % d'erreurs dans les deux essais. La classe prédite reste identique à `model.predict`, vérifiée par Pytest.

Les essais Windows initiaux ont été perturbés par une interruption/instabilité de l'environnement : durées de plusieurs dizaines de minutes malgré le timeout de 30 s. Ils ne servent pas de référence. Résultats retenus : `reports/runtime.json`, section `load`, sources `*-optimized.jtl`. Les essais antérieurs sont conservés séparément. Les fichiers JTL et rapports HTML restent disponibles localement dans `reports/load` et sont exclus de Git. Le marqueur `valid_measurement` détecte uniquement les durées anormales dépassant 60 s ; il ne constitue pas une validation de SLA.

## CI GitHub

Le workflow est reconnu et actif ; Actions est activé dans le dépôt. Aucun run n'a été enregistré après le premier push. Le déclenchement manuel `workflow_dispatch` a exécuté [la CI finale avec succès](https://github.com/Mamadouba02/TP_industrialisation_ML/actions/runs/38288623027) : provenance des artefacts versionnés, installation, génération, entraînement, exploration, Pytest, Compose, build Docker, intégration HTTP et Selenium. Le compte rendu de cette exécution et le commit testé sont conservés dans `reports/github-ci.json`.

La vérification Git a détecté une différence d'empreinte due à CRLF/LF. Les générateurs et `.gitattributes` imposent maintenant LF. `scripts/check_artifacts.py` vérifie le dataset et le modèle publiés avant tout réentraînement dans la CI, afin de détecter ce défaut plutôt que de le masquer en régénérant les fichiers.

## Infrastructure externe nécessaire

Déploiement VM/cloud : aucun serveur cible n'a été fourni. Le déploiement local Docker est réalisé ; la procédure distante est documentée, mais son exécution n'est pas déclarée réalisée.
