# Script Oral Pret A Dire (7 minutes)

## Minute 0-1: Introduction

"Notre projet s'appelle BI Adaptative. Le probleme cible est la surcharge
d'information dans Metabase: l'utilisateur voit beaucoup de rapports et ne sait
pas rapidement lesquels sont les plus pertinents pour son besoin."

## Minute 1-2: Objectif

"L'objectif est de construire un moteur de recommandation personnalisee qui
apprend les habitudes de navigation et propose automatiquement les rapports les
plus utiles."

## Minute 2-3: Architecture

"Le flux complet est:
Metabase -> RabbitMQ -> Consumer Python -> PostgreSQL -> Feature Engineering ->
Modeles ML -> API FastAPI -> Recommandations stockees en batch."

"RabbitMQ assure le decouplage et la resilience du pipeline."

## Minute 3-4: Partie IA

"Nous avons compare trois approches:
Collaborative Filtering, Content-Based, et Hybride."

"Le modele retenu est hybride KNN + contenu, avec poids 0.6/0.4, car il donne
le meilleur compromis top-5 selon Precision@5 et NDCG@5."

## Minute 4-5: Demonstration technique

"Nous allons lancer le scenario de demo:
1) injection d'evenements synthetiques,
2) persistance en base,
3) generation batch des recommandations,
4) verification via monitoring et endpoint de recommandations stockees."

## Minute 5-6: Qualite et tests

"La validation est faite par:
- tests unitaires,
- tests integration,
- test E2E RabbitMQ->DB->API,
- stress test."

"Un bug reel a ete trouve puis corrige:
reconnexion automatique du consumer PostgreSQL quand la connexion stale."

## Minute 6-7: Conclusion

"Le projet est operationnel localement, mesurable, et demotrable.
La prochaine etape vers production est d'instrumenter une duree reelle
client-side et d'ajouter un A/B test reel."
