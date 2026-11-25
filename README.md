# Sorvelune
Un détecteur attribue un score à 10 000 dossiers. Les analystes examinent surtout les 100 premiers et découvrent de nombreuses fraudes. Cela renseigne sur le haut du classement. Que sait-on des 9 900 autres, et peut-on réellement affirmer que le nouveau modèle fait mieux ?

Le simulateur Python compare les stratégies de revue par score, aléatoire et mixte. Il attribue le même budget à chacune et enregistre la probabilité d’inclusion de chaque dossier examiné dans le calcul.

## Démarrage

Depuis la racine du dépôt avec Python 3.10 ou ultérieur et Make :

```sh
make demo
make test
```

Commande directe :

```sh
python3 -m sorvelune examples/simulation.json
```

Le rapport donne les fraudes trouvées en moyenne et l’erreur absolue moyenne sur le total simulé. Pour la politique par score, une partie de la population a une probabilité nulle d’être revue. L’estimation du total est alors `null`.

Codes de sortie : 0 simulation terminée, 2 configuration invalide.

## Organisation

- `sorvelune.py` contient le moteur et son interface en ligne de commande.
- `examples/` contient les entrées fictives et reproductibles.
- `tests/` couvre le comportement nominal et les cas limites.

## Périmètre du socle

Le jeu est synthétique, les réponses sont immédiates et la graine figure dans la configuration. L’estimateur pondère les observations par l’inverse de leur probabilité d’inclusion. L’erreur est calculée contre la vérité cachée du simulateur. Les résultats ne mesurent pas la performance d’un système antifraude réel.

## Premier chantier à reprendre

Conserver les décisions, probabilités de sélection et dates d’observation dans SQLite ou PostgreSQL. Ajouter des étiquettes retardées et mesurer la couverture d’un intervalle sur une série de simulations indépendantes.
