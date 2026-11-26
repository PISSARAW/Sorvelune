# Règles de contribution

Appliquer KISS et SOLID. Garder une responsabilité explicite, limiter les dépendances et justifier les abstractions par leurs usages. Examiner les alternatives plus simples lors de la revue.

Limiter chaque fonction ou méthode à trois paramètres explicites, chaque fichier de code à 500 lignes physiques et l’imbrication des contrôles à trois niveaux. Réduire le nombre de chemins possibles. Le seuil bloquant de complexité par fonction est 10.

Activer les hooks avec `make setup`. Qualifier chaque commit de code et attester la revue de conception dans son message. Mettre à jour un guide ou le README lors d’un changement important. Consigner chaque décision majeure dans un nouvel ADR. La convention, les exemples de messages et l’arbre documentaire figurent dans [le guide de contribution](docs/guides/contribuer.md).
