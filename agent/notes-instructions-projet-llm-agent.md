## Notes à retenir pour l'Atelier ML - LLM Agentique

#### TÂCHE GLOBALE : Reprise du code du TP C++ et le transfo en UI

1. Ouvrir le repo agent dans notre container
1. Installer ollama dans le container
1. Mettre en plein écran la fenêtre open code dans le terminal
1. NB : On ne reste pas longtemps dans, le build, les épisodes plan vont être plus longues (on va alterner ainsi : _plan-build-plan-build-plan-..._)
1. Tu peux suivre les modifs de l'agent dans l'onglet git à gauche dans VS code
1. Quand il crée un fichier, **exec ton code avant de le commit** pour voir si ça fonctionne
1. faire un 'bel' historique git, cela veut dire que quand notre llm veut nous créer trop chose en mm temps, on le corrige et **on y va _1 étape à la fois avec l'agent_**
1. créer un modèle de UI avec Figma pour l'agent
1. `pybind` (=fichier d'interface c++) sera utilisé pour lié notre code c++ en python
1. Le fichier agent.md doit être versionné
1. agent.md =/= historique/log des chats

---

#### Commmandes intéressantes

- `go`
- `compact`
- `export`

## Étapes

1. `cd agent`
1. `ctrl` + `shift` + `p` > "_Dec Containers: Open Folder in Container_" > open < show logs
1. Dans un autre terminal, toujours dans le repertoire `agent` :

```bash
mkdir build
cd build/
cmake ..
make
```

```bash
./bibliotheque -d ../data/ # tester le fonctionnement de l'application
```

1. Aller sur [ollama.com/download](https://ollama.com/download), copier la commande pour installer ollama dans le devcontainer
1. dans le terminal, copier la commande
1. Puis...

```bash
ollama signin 6:05
```
