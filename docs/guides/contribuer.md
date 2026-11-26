# Contribuer

Dans un nouveau clone, lancer `make setup`. Cette commande configure `core.hooksPath` dans ce dépôt. Si le clone utilise déjà des hooks personnalisés, vérifier cette configuration avant de l'activer. `make quality` analyse l’index préparé par `git add`. Le hook pre-commit analyse les sources et les documents indexés. Le hook commit-msg contrôle aussi la déclaration d’impact. La CI rejoue ces contrôles sur les commits d’un push ou d’une PR. Une copie de travail non indexée ne peut pas corriger un échec de l’index.

## Seuils

| Mesure | Limite et convention |
|---|---|
| Paramètres | 3 paramètres déclarés. Les paramètres nommés, positionnels et variadiques comptent. Le récepteur de méthode est implicite en Go et exclu pour self/cls dans une méthode Python. |
| Longueur | 500 lignes physiques, commentaires et lignes vides compris, pour les sources, tests, scripts, hooks, Makefile et workflows suivis. |
| Profondeur | 3 niveaux de structures de contrôle. La déclaration de fonction est le niveau zéro. Les branches alternatives au même niveau et les fonctions locales sont évaluées séparément. |
| Complexité | 10 par fonction ou lambda. Le compteur commence à 1 et ajoute les décisions, boucles, alternatives de sélection et opérateurs logiques court-circuités. Python compte aussi les expressions conditionnelles et les générateurs de compréhension. |
| Conception | Relire responsabilité, couplage, lisibilité et besoin réel de chaque abstraction. Pour SOLID, examiner aussi les contrats des interfaces, la substituabilité et les dépendances aux implémentations. |

Les contrôles structurels utilisent les arbres syntaxiques de Python et de Go. Les scripts d’accompagnement et les workflows sont soumis au plafond de taille. Les exemples JSON métier sont des données. Les contrôles locaux utilisent Git et Python 3.10+. Les sources Go nécessitent aussi la chaîne Go.

## Messages et documentation

Pour un commit de code, ajouter en fin de message un bloc de deux lignes, séparé du titre ou du corps par une ligne vide. Exemple de commit important :

```text
Décrire les refus dans le dossier de revue

Impact: important
Design-Review: KISS, SOLID
```

- **Mineur** convient par exemple à une correction typographique ou à un test supplémentaire. Écrire `Impact: mineur`.
- **Important** couvre un changement de comportement, d’usage, d’exploitation ou de fonctionnalité. Créer ou modifier un document pertinent dans `docs/` ou le README dans le même commit. L’ajout ou la suppression d’un fichier d’exécution déclenche aussi cette exigence. Pour une modification interne mineure d’un fichier existant, le niveau déclaré s’applique.
- **Majeur** couvre une décision structurante concernant une API publique, un schéma échangé, le stockage, une frontière de confiance ou les règles communes. Écrire `Impact: majeur`, documenter le changement et ajouter un ADR numéroté. Les chemins d’architecture, de schéma et de migration, les manifestes de dépendances reconnus et la politique de contrôle déclenchent automatiquement l’exigence d’ADR.

Une déclaration atteste une revue effectuée. Le relecteur vérifie la pertinence du document et l’impact réel. En cas de squash, conserver les déclarations dans le message définitif. Git autorise le contournement local des hooks avec `--no-verify`. Sur GitHub, le contrôle à rendre obligatoire dans les règles de branche s’appelle `Gouvernance`.

Le fichier `.github/gouvernance-main.json` contient la règle de branche prête à importer. Un administrateur peut l’importer dans **Settings → Rules → Rulesets → New ruleset → Import a ruleset**. Pour une première activation via GitHub CLI depuis le clone, utiliser `gh api --method POST 'repos/{owner}/{repo}/rulesets' --input .github/gouvernance-main.json`.
