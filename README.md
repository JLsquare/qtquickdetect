# QtQuickDetect
Une application pour réaliser des détections d'objets sur différents type de support image.

## Fonctionnalités
### Détection sur image :
- Détecter des objets

### Détection sur vidéo :
- Détecter et tracker des objets 

### Détection sur livestream (exemple : caméra) :
- Détecter des objets


## Installation et lancement
Pour pouvoir exécuter l'application, une version de [Python](https://www.python.org/downloads/) 3.10 ou plus doit être installée sur votre machine. 
### Linux :
- Clonez le dépot sur votre machine
- Créez un environnement python avec la commande :
```bash
python3 -m venv venv
```
- Activez l'environnement :
```bash
source venv/bin/activate
```
- Dans le terminal de l'environnement, exécutez la commande : 
```bash
pip install -r requirements.txt
```
- Exécutez l'application :
```bash
python3 qtquickdetect.py
```
### Windows :
- Clonez le dépot sur votre machine
- Dans l'environnement du dépot, exécutez le fichier run.bat ( ou run_cuda.bat pour les machine avec un gpu NVIDIA)

## 
