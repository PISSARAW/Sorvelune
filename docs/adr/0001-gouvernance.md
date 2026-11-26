# 0001 — Gouvernance commune

## Contexte

Les cinq outils évoluent indépendamment et échangent des dossiers versionnés. Une modification difficile à relire dans un seul dépôt peut modifier l’interprétation du résultat final.

## Options

Une charte seule laisse les dépassements à la charge du relecteur. Une plateforme centrale ajouterait une dépendance au réseau au moment de chaque commit. Des contrôles locaux versionnés peuvent relire l’index et être rejoués sur chaque commit en CI.

## Décision

Les cinq dépôts adoptent les mêmes seuils, la même arborescence et les mêmes déclarations d’impact. Le contrôle lit l’instantané Git et les arbres syntaxiques des langages des applications. L’auteur atteste la revue KISS et SOLID. La CI vérifie les mêmes règles que les hooks locaux.

## Conséquences

Chaque nouveau clone doit activer les hooks. La revue humaine apprécie la simplicité, la pertinence de l’ADR et l’exactitude du niveau d’impact. Une évolution des règles communes doit être propagée aux cinq dépôts. Les commandes des outils et leurs formats d’échange restent couverts par les tests métier.
