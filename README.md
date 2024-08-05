# Créez une API sécurisée RESTful en utilisant Django REST

## Français

### Introducion

Une API Django REST qui permet aux utilisateurs connectés de gérer des projets, problèmes et commentaires.

# Installation

Pré-requis:

- Python >= 3.12
- Git 2.x (uniquement pour cloner le repo)
- pipenv

```sh
git clone https://github.com/GromPras/oc-projet_10.git
```

`Ou téléchargez le fichier ZIP depuis https://github.com/GromPras/oc-projet_10/archive/refs/heads/main.zip`

Créez un environement virtuel à l'intérieur du dossier cloné:

```sh
cd oc-projet_10
python3 -m venv {/path/to/virtual/environment}
```

Sur Windows, appelez la commande venv comme suit :

```sh
c:\>c:\Python3\python -m venv c:\path\to\myenv
```

Activer l'environement virtuel :

```sh
source {/path/to/virtual/environment}/bin/activate
```

Sur Windows, appelez la commande venv comme suit :

```sh
C:\> <venv>\Scripts\activate.bat
```

Installez pipenv si besoin:

```sh
pip install pipenv
```

Ou sur Windows :

```sh
py -m pip install pipenv
```

Installez les dépendances:

```sh
pipenv sync
```

Si vous avez un problème avec la création de l'environnement consultez la documentation : `https://docs.python.org/fr/3/library/venv.html#creating-virtual-environments`

### Post Installation

#### Pour lancer le programme, exécutez les commandes suivantes :

```sh
python3 manage.py migrate
python3 manage.py runserver
```