# Grapheur

Ce logiciel fourni une interface graphique pour créer des plans cartésiens avec des fonctions à l'aide de LaTeX et Poppler.

## Dépendances

Le paquet Python [toml](https://github.com/uiri/toml) est requis pour sauvegarder et charger le fichier des paramètres.

[TinyTeX](https://yihui.org/tinytex/) est requis pour rendre le graphique via XeLaTex.

Le paquet [pdf2image](https://github.com/Belval/pdf2image) est requis pour convertir le document PDF produit par XeLaTeX en fichier image. Par extension, pdf2image dépend sur [Poppler](https://poppler.freedesktop.org/).

Les répertoires de TinyTeX et Poppler doivent être situés dans le répertoire du script Python ou dans le répertoire de l'exécutable produit par PyInstaller.

### toml et pdf2image

```
pip install toml pdf2image
```

### TinyTeX

1. Naviguer au [site de téléchargement pour TinyTeX](https://github.com/yihui/tinytex-releases).
2. Défiler à la section «Releases».
3. Télécharger l'option «TinyTeX-1.zip».
4. Extraire le contenu de l'archive au répertoire `TinyTeX` dans le répertoire du script ou de l'exécutable.

### Poppler

1. Naviguer au [site de téléchargement de binaires de Poppler](https://github.com/oschwartz10612/poppler-windows/releases/) par Owen Schwartz.
2. Télécharger l'option «Release-XX.XX.X-X.zip» la plus récente.
3. Extraire le contenu du répertoire `Library/bin` de l'archive au répertoire `poppler` dans le répertoire du script ou de l'exécutable.

## Exécuter

```
python grapheur.py
```

## Bâtir avec PyInstaller

```
pyinstaller --onefile --noconsole grapheur.py
```