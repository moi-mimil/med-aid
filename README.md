# MED AID

Projet présenté aux **Trophées NSI**.

MED AID est une application de bureau qui aide à explorer quelles affections courantes sont compatibles avec un ensemble de symptômes. L'utilisateur sélectionne ses symptômes, et l'application compare cette sélection aux symptômes de chaque affection de sa base de connaissances.

L'interface est en français et réalisée avec [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).

> ⚠️ **Avertissement.** MED AID est un projet éducatif. Ce n'est **pas** un dispositif médical et il **ne fournit pas de diagnostic**. Les données sont simplifiées et n'ont pas été validées médicalement. En cas de malaise, consultez un professionnel de santé. En cas d'urgence, appelez le **15** (SAMU) ou le **112** (numéro d'urgences européen).

## Fonctionnalités

- **Recherche de symptômes en direct**, insensible aux accents et à la casse : taper `etourdissement` retrouve *Étourdissements*.
- **Tri des résultats** : les symptômes qui *commencent par* la saisie apparaissent en premier.
- **Sélection en deux panneaux** : à gauche les symptômes non sélectionnés, à droite ceux déjà choisis (en vert). Un clic sur un symptôme le fait passer d'un panneau à l'autre.
- **Correspondance avec les affections** : les symptômes sélectionnés sont comparés à ceux de chaque affection, avec détection des correspondances parfaites et partielles.
- **Base de connaissances modifiable** : affections, symptômes, conseils de traitement et liens Wikipédia sont regroupés dans un seul fichier qui sert de base de données.

## Contenu de l'archive

```
MED_AID/
├── file.py            # Interface graphique et logique de correspondance (fichier à lancer)
├── data.py            # Affections, symptômes, traitements, liens Wikipédia
├── requirements.txt   # Dépendances Python
└── README.md          # Ce fichier
```

⚠️ Les fichiers `file.py` et `data.py` doivent rester **dans le même dossier**, car `file.py` importe `data.py`.

## Installation

### Prérequis

- Python 3.9 ou plus récent, avec Tkinter (inclus dans la plupart des installateurs Python)
- Les bibliothèques `customtkinter` et `unidecode`

### Étapes

1. Extraire l'archive `.zip` dans un dossier.
2. Ouvrir un terminal dans ce dossier.
3. Installer les dépendances :

```bash
pip install -r requirements.txt
```

4. Lancer l'application :

```bash
python file.py
```

> Sous Linux ou macOS, la commande peut être `python3`.

## Utilisation

1. Taper un symptôme dans la barre de recherche (par exemple `toux` ou `fièvre`).
2. Cliquer sur un résultat pour le sélectionner : il passe dans la liste verte à droite.
3. Cliquer sur un symptôme sélectionné pour le retirer.
4. Cliquer sur **Valider les symptômes** pour lancer la correspondance.

## Fonctionnement de la correspondance

Pour chaque affection, le programme compare les symptômes sélectionnés à la liste de symptômes de l'affection :

- **Correspondance parfaite** : les symptômes sélectionnés sont exactement ceux de l'affection.
- **Correspondance proche** : au moins un symptôme en commun ; le nombre de symptômes partagés est enregistré.

## Format des données

Chaque affection de `data.py` a cette forme :

```python
"Grippe": {
    "symptoms": ["Fièvre", "Frissons", "Fatigue", "Toux"],
    "wikipedia": "https://fr.wikipedia.org/wiki/Grippe",
    "treatment": "Repos et hydratation. ..."
}
```

Pour ajouter une affection :

1. Ajouter une entrée au dictionnaire `conditions`.
2. Vérifier que chaque symptôme utilisé existe aussi dans `symptom_list`, sinon l'utilisateur ne pourra pas le sélectionner.

## Limites connues et pistes d'amélioration

- Les résultats de la correspondance s'affichent pour l'instant dans la console, pas dans l'interface.
- Le score repose sur le nombre de symptômes en commun, ce qui avantage les affections ayant de longues listes de symptômes.
- Certaines affections ont des listes de symptômes identiques et ne peuvent pas être distinguées, et certains symptômes de la liste ne sont rattachés à aucune affection.
- Les signes de gravité (par exemple douleur thoracique avec essoufflement) ne déclenchent pas encore d'alerte.
- Les conseils de traitement et les liens Wikipédia ne sont pas encore affichés dans l'interface.
- Les panneaux de symptômes ne sont pas défilants.
