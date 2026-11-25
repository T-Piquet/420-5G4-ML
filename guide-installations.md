# Atelier ML - Mon guide

## 1. Extensions

- Juppyter (fourni par Microsoft)
- Python (fourni par Microsoft)
- Rainbow CSV
- markdownlint
- Markdown Preview Enhanced

## Installations (cmd)

```bash
$ apt install python3.12-venv
$ sudo apt install python3-pip
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install requests matplotlib # un exemple d'une installation qui fait que la ligne suivante ne retourne rien de vide
$ pip freeze > requirements.txt
$ pip install pandas
$ pip freeze > requirements.txt
```

## Sur une autre machine, il suffira de réinstaller le tout avec

```bash
$ pip install -r requirements.txt
```

## Quitter l’environnement : Dès que tu as fini de travailler sur le projet

```bash
$ pip freeze > requirements.txt
$ deactivate
```
