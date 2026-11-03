# Atelier ML

## Première partie

Dans le répertoire `apprentissage/`

## Deuxième Partie

Dans le répertoire `analyse_image/`

## Troisième partie

Le repertoire `agent/` contient le code C++ du projet et le devcontainer pour avoir la redirection du server graphique.

## Pour Shawn-Matthew Heng
Si l'environnement virtuel n'est pas créé, écris dans le teminal: py -m venv .venv

Pour activer l'environnement, va au 'Agent host (Local)'<br>
Sinon, écrit ".\.venv\Scripts\Activate.ps1 dans PowerShell" et .venv\Scripts\activate.bat dans cmd

Après dans les fichiers .ipynb, appuyez sur 'Select Kernel' et selectionner .venv

Pour réinstaller les dépendances, écris pip install -r requirements.txt<br>
Sinon, écris pip install requests matplotlib<br>
Si pandas, ou un dépendance spécifique, n'est pas inclus, écris python -m pip install pandas, <nom du dépendance> ou dans une cellule %pip install pandas, <nom du dépendance><br>
Écrivez pip freeze > requirements.txt pour mettre les nouveaux dépendances