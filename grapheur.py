import pathlib as pl
import toml
import tkinter as tk
from sys import argv
import tkinter.font as tkfont
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox
from ctypes import windll
import subprocess
import concurrent.futures as cf
import pdf2image
import os
import tempfile
import sys

# https://www.tutorialfor.com/questions-291237.htm
_original_constructor = subprocess.Popen.__init__
def _patched_constructor (*args, **kwargs):
    kwargs['stdin'] = subprocess.PIPE
    return _original_constructor(*args, **kwargs)
subprocess.Popen.__init__ = _patched_constructor

from validateur import *
from tkplus import *
from graphique import *
from latex import *
from enregistrementtoml import *


if getattr(sys, 'frozen', False):
    CHEMIN_XELATEX = os.path.dirname(os.path.realpath(sys.executable)) + '/TinyTeX/bin/win32/xelatex'
    CHEMIN_POPPLER = os.path.dirname(os.path.realpath(sys.executable)) + os.sep + 'poppler'
elif __file__:
    CHEMIN_XELATEX = os.path.dirname(os.path.realpath(__file__)) + '/TinyTeX/bin/win32/xelatex'
    CHEMIN_POPPLER = os.path.dirname(os.path.realpath(__file__)) + os.sep + 'poppler'


def main():
    if False:
        if len(argv) == 2:
            try:
                with open(argv[1], encoding = 'utf-8') as f:
                    configuration_source = f.read()
            except OSError:
                print(f'Le fichier {argv[1]} n\'existe pas.', file = stderr)
                exit(1)
        else:
            configuration_source = '''
                [plan]
                minx = -10
                miny = -10
                maxx = 10
                maxy = 10

                [axes]
                lignes = 'centre' # boîte, gauche, centre, droite, aucun

                [étiquettes]
                pos = '+' # '+', AXE_LIGNE (sur le côté positif ou négatif de l'axe)
                rel = '+' # '+', '0', AXE_LIGNE (au dessus ou au dessous de l'axe ou sur la pointe)

                [grillage]
                bordure = 'ouverte' # ouverte, fermée (pas de lignes de grillage autour)
                '''

        try:
            configuration = toml.loads(configuration_source)
        except toml.TomlDecodeError:
            #print(f'Le fichier {argv[1]} n\'est pas un fichier TOML valide.', file = stderr)
            exit(2)

    # https://stackoverflow.com/questions/56418948/converting-pdf-to-image-without-non-python-dependencies
    # https://stackoverflow.com/a/404750
    os.environ['PATH'] = os.sep.join([os.path.dirname(os.path.realpath(sys.executable)), 'poppler']) + os.pathsep + os.environ['PATH']

    grapheur = Grapheur(tk.Tk())
    grapheur.lancer_menu_principal()
    grapheur.ctx.mainloop()


def num_à_str(x):
    return str(int(x) if float(x).is_integer() else x)


class Grapheur:
    def __init__(self, ctx):
        self.exécuteur = cf.ThreadPoolExecutor()

        self.ctx = ctx
        self.ctx.bind('<Control-s>', lambda _: self._enregistrer())
        self.ctx.bind('<Control-r>', lambda _: self._rendre())
        self.ctx.bind('<Control-q>', lambda _: self._quitter())

        self.ctx.protocol('WM_DELETE_WINDOW', self._quitter)

        # Gérer pour les écrans à haut DPI.
        windll.shcore.SetProcessDpiAwareness(1)

        # Définir les polices.
        police_défaut = tkfont.nametofont('TkDefaultFont')
        police_défaut.configure(family = 'Palatino Linotype', size = 14)
        self.ctx.option_add('*Font', police_défaut)
        self.police_gras = tkfont.Font(family = 'Palatino Linotype', size = 14, weight = 'bold')
        self.police_petit = tkfont.Font(family = 'Palatino Linotype', size = 12)

        self.graphique = None
        self.dernier_enregistrement = None
        self.copie_source = True
        self._défini_nom_fichier()
        self.rends = False

        self.page_plan = None
        self.page_objets = None

        self.métas = None
        self.métasobj = None
        self.défilables = None
        self.informations_visibles = None
        self.composants_rendre = None


    def _défini_nom_fichier(self, fichier = None):
        if fichier is None:
            self.ctx.title('Grapheur')
        else:
            nom = fichier.rsplit('/', 1)[1] if '/' in fichier else fichier
            self.ctx.title(f'{nom} — Grapheur')

        self.fichier_enregistrement = fichier


    def lancer_menu_principal(self):
        for composant in self.ctx.winfo_children():
            composant.destroy()
        self.page_plan = None
        self.page_objets = None
        self.métas = None
        self.métasobj = None
        self.défilables = None
        self.informations_visibles = None

        _, x, y = self.ctx.geometry().split('+')
        self.ctx.geometry(f'300x200+{x}+{y}')
        self.ctx.resizable(0, 0)

        menu = tk.Frame(self.ctx, padx = 3, pady = 3)
        menu.rowconfigure((1, 3, 5), minsize = 3, weight = 0)
        menu.rowconfigure((0, 2, 4), weight = 1)
        menu.columnconfigure(0, weight = 1)
        menu.pack(side = tk.TOP, fill = tk.BOTH, expand = 1)

        nouveau = tk.Button(menu, text = 'Nouveau', padx = 10, pady = 10, command = self._créer_graphique)
        nouveau.grid(row = 0, column = 0, sticky = tk.EW)

        ouvrir = tk.Button(menu, text = 'Ouvrir', padx = 10, pady = 10, command = self._ouvrir_graphique)
        ouvrir.grid(row = 2, column = 0, sticky = tk.EW)

        quitter = tk.Button(menu, text = 'Quitter', padx = 10, pady = 10, command = lambda: self.ctx.quit())
        quitter.grid(row = 4, column = 0, sticky = tk.EW)

        tk.Label(menu, text = 'Grapheur par Jeffrey René Ouimet', font = self.police_petit).grid(row = 6, column = 0, sticky = tk.EW)


    def _créer_graphique(self):
        self.graphique = Graphique()
        self.dernier_enregistrement = hash(str(self.graphique))

        self._lancer_éditeur()


    def _ouvrir_graphique(self):
        while True:
            fichier = tkfiledialog.askopenfilename(defaultextension = '.graph', filetypes = [('Grapheur', '*.graph'), ('Tout fichiers', '*')], parent = self.ctx, title = 'Ouvrir')
            if fichier == '':
                return
            if fichier.lower().endswith('.graph'):
                break

        graphique = EnregistrementToml.lire(fichier)
        if isinstance(graphique, Erreur):
            tkmessagebox.showinfo('Erreur', str(graphique))
            return

        self._défini_nom_fichier(fichier)
        self.graphique = graphique
        self.dernier_enregistrement = hash(str(self.graphique))

        self._lancer_éditeur()


    def _lancer_éditeur(self):
        if self.graphique is None:
            raise ValueError('Le graphique est indéfini.')

        self.métas = []
        self.métasobj = []
        self.défilables = []
        self.informations_visibles = False

        for composant in self.ctx.winfo_children():
            composant.destroy()

        _, x, y = self.ctx.geometry().split('+')
        self.ctx.geometry(f'480x640+{x}+{y}')
        self.ctx.resizable(True, True)

        menu2 = tk.Frame(self.ctx, padx = 3, pady = 0)
        menu2.pack(side = tk.TOP, anchor = tk.CENTER, fill = tk.X, pady = (3, 0))
        menu2.columnconfigure((0, 2, 4), uniform = 'equal', weight = 1)
        menu2.columnconfigure((1, 3), minsize = 3)
        enregistrer = tk.Button(menu2, text = 'Enregistrer', padx = 0, pady = 0, command = self._enregistrer)
        enregistrer.grid(column = 0, row = 0, sticky = tk.EW)
        tk.Button(menu2, text = 'Aide', padx = 0, pady = 0, command = self._basculer_informations).grid(column = 2, row = 0, sticky = tk.EW)
        fermer = tk.Button(menu2, text = 'Fermer', padx = 0, pady = 0, command = self._fermer)
        fermer.grid(column = 4, row = 0, sticky = tk.EW)

        menu = tk.Frame(self.ctx, padx = 3, pady = 0)
        menu.pack(side = tk.TOP, anchor = tk.CENTER, fill = tk.X, pady = 3)
        menu.columnconfigure((0, 2, 4), uniform = 'equal', weight = 1)
        menu.columnconfigure((1, 3), minsize = 3)
        tk.Button(menu, text = 'Objets', padx = 0, pady = 0, command = self._lancer_page_objets).grid(column = 0, row = 0, sticky = tk.EW)
        tk.Button(menu, text = 'Plan', padx = 0, pady = 0, command = self._lancer_page_plan).grid(column = 2, row = 0, sticky = tk.EW)
        rendre = tk.Button(menu, text = 'Rendre', padx = 0, pady = 0, command = self._rendre)
        rendre.grid(column = 4, row = 0, sticky = tk.EW)

        self.composants_rendre = [rendre, enregistrer, fermer]

        self._prépare_page_plan()
        self._prépare_page_objets()
        self.page_plan.pack(fill = tk.BOTH, expand = True)
        #self.page_objets.pack(fill = tk.BOTH, expand = True)


    def _basculer_informations(self):
        self.informations_visibles = not self.informations_visibles
        for méta in self.métas:
            méta.affiche_info(self.informations_visibles)
        for métasobj in self.métasobj:
            for méta in métasobj:
                méta.affiche_info(self.informations_visibles)

        for défilable in self.défilables:
            défilable.haut()


    # Source: https://www.w3resource.com/python-exercises/class-exercises/python-class-exercise-1.php
    def _entier_à_romain(x):
        valeur = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4,
            1
            ]
        symbole = [
            'm', 'cm', 'd', 'cd',
            'c', 'xc', 'l', 'xl',
            'x', 'ix', 'v', 'iv',
            'i'
            ]

        x = int(x)
        romain = ''
        i = 0
        while x > 0:
            for _ in range(x // valeur[i]):
                romain += symbole[i]
                x -= valeur[i]
            i += 1

        return romain


    def _préparer_fichier_latex(self):
        graphique = self.graphique

        commandes = {
            'largeur': f'{graphique.dimensions[0]}cm',
            'hauteur': f'{graphique.dimensions[1]}cm',
            'grillageouvert': 'true' if graphique.grillage_ouvert else 'false',
            'angles': 'rad' if graphique.angles == ANGLE_RADIANS else 'deg',
            'xmin': min(graphique.axes[0].bornes),
            'xmax': max(graphique.axes[0].bornes),
            'xdir': 'normal' if graphique.axes[0].bornes[0] < graphique.axes[0].bornes[1] else 'reverse',
            'ymin': min(graphique.axes[1].bornes),
            'ymax': max(graphique.axes[1].bornes),
            'ydir': 'normal' if graphique.axes[1].bornes[0] < graphique.axes[1].bornes[1] else 'reverse',
            'axexetiquette': graphique.axes[0].étiquette,
            'axeyetiquette': graphique.axes[1].étiquette,
            'axex': 'false' if graphique.axes[0].droite == AXE_CACHÉ else 'true',
            'axey': 'false' if graphique.axes[1].droite == AXE_CACHÉ else 'true',
            'axexstyle': 'avec flèche' if graphique.axes[0].droite == AXE_FLÈCHE else 'sans flèche',
            'axeystyle': 'avec flèche' if graphique.axes[1].droite == AXE_FLÈCHE else 'sans flèche',
            'valeursxdistance': graphique.axes[0].pas,
            'valeursydistance': graphique.axes[1].pas,
            'valeursxmineur': graphique.axes[0].interpas,
            'valeursymineur': graphique.axes[1].interpas,
            'grillagexmajeur': 'true' if graphique.axes[0].grillage_majeur else 'false',
            'grillageymajeur': 'true' if graphique.axes[1].grillage_majeur else 'false',
            'grillagexmineur': 'true' if graphique.axes[0].grillage_mineur else 'false',
            'grillageymineur': 'true' if graphique.axes[1].grillage_mineur else 'false'
        }

        couleurs = {
            'plancouleur': ','.join(map(str, graphique.couleur)),
            'axexcouleur': ','.join(map(str, graphique.axes[0].couleur)),
            'axeycouleur': ','.join(map(str, graphique.axes[1].couleur)),
            'grillagexmajeurcouleur': ','.join(map(str, graphique.axes[0].grillage_majeur_couleur)),
            'grillageymajeurcouleur': ','.join(map(str, graphique.axes[1].grillage_majeur_couleur)),
            'grillagexmineurcouleur': ','.join(map(str, graphique.axes[0].grillage_mineur_couleur)),
            'grillageymineurcouleur': ','.join(map(str, graphique.axes[1].grillage_mineur_couleur))
        }

        for idx, objet in enumerate(graphique.objets):
            r = Grapheur._entier_à_romain(idx + 1)
            commandes.update({
                f'objet{r}type': objet.type,
                f'objet{r}etiquette': objet.étiquette,
                f'objet{r}etiquettepos': objet.position,
                f'objet{r}etiquetterel': 'center' if objet.ancre is None else objet.ancre,
                f'objet{r}style': objet.style,
                f'objet{r}equation': f'{{{objet.équation[0]}}}, {{{objet.équation[1]}}}' if objet.type == RELATION_XY_T else objet.équation,
                f'objet{r}cerclesouverts': ','.join(map(str, objet.points_ouverts)),
                f'objet{r}cerclesfermes': ','.join(map(str, objet.points_fermés)),
                f'objet{r}domainemin': '' if objet.bornes[0] == float('-inf') else objet.bornes[0],
                f'objet{r}domainemax': '' if objet.bornes[1] == float('inf') else objet.bornes[1]
            })

            couleurs.update({
                f'objet{r}couleur': ','.join(map(str, objet.couleur))
            })

        commandes = [f'\\newcommand\\{clé}{{{val}}}' for clé, val in commandes.items()]
        couleurs = [f'\\definecolor{{{clé}}}{{RGB}}{{{val}}}' for clé, val in couleurs.items()]

        return LATEX.replace('___VARIABLES___', '\n'.join(commandes + couleurs))


    def _rendre(self):
        if self.graphique is None or not self._enregistrer() or self.rends:
            return

        self.rends = True

        for c in self.composants_rendre:
            c.configure(state = tk.DISABLED)

        fichier = self.fichier_enregistrement[:-len('.graph')]
        fichier_court = fichier.rsplit('/', 1)[1] if '/' in fichier else fichier

        # TODO: supprime toujours le répertoire, même en cas d'erreur
        répertoire_latex = f'{tempfile.gettempdir()}/grapheur'
        os.makedirs(répertoire_latex, exist_ok = True)

        latex = self._préparer_fichier_latex()

        with open(f'{répertoire_latex}/{fichier_court}.tex', 'w', encoding = 'utf-8') as f:
            f.write(latex)

        #processus = None
        # TODO: pdflatex -output-directory=target <file>
        # https://stackoverflow.com/questions/984941/python-subprocess-popen-from-a-thread
        def travail():
            résultat = ''
            try:
                résultat = subprocess.run([CHEMIN_XELATEX, '-halt-on-error', f'{fichier_court}.tex'], text = True, shell = True, stdin = subprocess.DEVNULL, stderr = subprocess.STDOUT, stdout = subprocess.PIPE, cwd = répertoire_latex).stdout
            except subprocess.TimeoutExpired:
                # TODO: Erreur de temps épuisé
                tkmessagebox.showerror('Erreur', 'Une erreur XeLaTeX s\'est produite. (1)')
            except subprocess.SubprocessError:
                # TODO: Erreur inattendue
                tkmessagebox.showerror('Erreur', 'Une erreur XeLaTeX s\'est produite. (2)')

            return résultat

        def _post_rendu(travailleur):
            sortie = travailleur.result()
            if self.copie_source:
                os.replace(f'{répertoire_latex}/{fichier_court}.tex', f'{fichier}.tex')

            if sortie != '':
                if f'Output written on {fichier_court}.pdf' in sortie:
                    os.replace(f'{répertoire_latex}/{fichier_court}.pdf', f'{fichier}.pdf')

                    try :
                        pages = pdf2image.convert_from_path(f'{fichier}.pdf' , poppler_path = CHEMIN_POPPLER)
                        pages[0].save(f'{fichier}.png', 'PNG')
                        subprocess.run(['start', f'{fichier}.png'], shell = True, stdin = subprocess.DEVNULL, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
                    except Exception as e:
                        tkmessagebox.showerror('Erreur', e)
                else:
                    os.replace(f'{répertoire_latex}/{fichier_court}.log', f'{fichier}.log')
                    tkmessagebox.showerror('Erreur', f'Une erreur XeLaTeX s\'est produite.\n\nVoir le fichier « {fichier_court}.log » pour les détails de l\'erreur.')

            try:
                with os.scandir(répertoire_latex) as répertoire:
                    for f in répertoire:
                        if f.is_file() or f.is_symlink():
                            os.remove(f.path)
                os.rmdir(répertoire_latex)
            except:
                pass

            for c in self.composants_rendre:
                c.configure(state = tk.ACTIVE)

            self.rends = False

        travailleur = self.exécuteur.submit(travail)
        travailleur.add_done_callback(_post_rendu)


    def _enregistrer(self):
        if self.graphique is None or self.rends:
            return False

        if self.fichier_enregistrement is None:
            fichier = tkfiledialog.asksaveasfilename(defaultextension = '.graph', filetypes = [('Grapheur', '*.graph'), ('Tout fichiers', '*')], parent = self.ctx, title = 'Enregistrer')
            if fichier == '':
                return False
            fichier = fichier if fichier.lower().endswith('.graph') else fichier + '.graph'
        else:
            fichier = self.fichier_enregistrement

        erreur = EnregistrementToml.enregistrer(fichier, self.graphique)
        if erreur is not None:
            tkmessagebox.showerror('Erreur', str(erreur))
            return False

        self._défini_nom_fichier(fichier)
        self.dernier_enregistrement = hash(str(self.graphique))

        return True


    def _quitter(self):
        if self.graphique:
            self._fermer()
            if self.graphique:
                return

        self.ctx.destroy()


    def _fermer(self):
        if self.rends:
            return

        enregistrement_actuel = hash(str(self.graphique))
        if enregistrement_actuel != self.dernier_enregistrement:
            class DialogueEnregistrement(tk.Toplevel):
                def __init__(self, parent):
                    tk.Toplevel.__init__(self, parent, padx = 5, pady = 5)
                    self.geometry(f'+{parent.winfo_rootx() + 50}+{parent.winfo_rooty() + 50}')

                    self.parent = parent
                    self.transient(parent)

                    self.à_annuler = False
                    self.à_enregistrer = False

                    tk.Label(self, text = 'Voulez-vous enregistrer le fichier avant de fermer?').pack(pady = 3)

                    choix = tk.Frame(self)

                    enregister = tk.Button(choix, text = 'Enregistrer', command = self.enregister, default = tk.ACTIVE)
                    enregister.pack(side = tk.LEFT)
                    tk.Button(choix, text = 'Ne pas enregister', command = self.ignorer).pack(side = tk.LEFT, padx = 5)
                    tk.Button(choix, text = 'Annuler', command = self.annuler).pack(side = tk.LEFT)
                    self.bind('<Return>', self.enregister)
                    self.bind('<Escape>', self.annuler)
                    self.protocol('WM_DELETE_WINDOW', self.annuler)

                    choix.pack()

                    self.grab_set()
                    enregister.focus_set()
                    self.wait_window(self)

                def enregister(self, *args):
                    self.à_enregistrer = True
                    self.parent.focus_set()
                    self.destroy()

                def annuler(self, *args):
                    self.à_annuler = True
                    self.parent.focus_set()
                    self.destroy()

                def ignorer(self):
                    self.parent.focus_set()
                    self.destroy()

            question = DialogueEnregistrement(self.ctx)

            if question.à_annuler:
                return
            if question.à_enregistrer and not self._enregistrer():
                return

        self._défini_nom_fichier()
        self.graphique = None
        self.dernier_enregistrement = None
        self.lancer_menu_principal()
        self.composants_rendre = None


    def _lancer_page_objets(self):
        self.page_plan.pack_forget()
        self.page_objets.pack(fill = tk.BOTH, expand = True)


    def _lancer_page_plan(self):
        self.page_objets.pack_forget()
        self.page_plan.pack(fill = tk.BOTH, expand = True)


    def _prépare_page_objets(self):
        self.page_objets = tk.Frame(self.ctx)

        def _créer_fonction(type):
            def _créateur():
                self.graphique.objets.append(Fonction(type))
                self.métasobj.append([])
                self._préparer_objet(len(self.graphique.objets) - 1)
            return _créateur
        création = tk.Frame(self.page_objets)
        création.pack(fill = tk.X, padx = 3, pady = 3)
        création.columnconfigure((0, 2, 4), weight = 1)
        création.columnconfigure((1, 3), minsize = 3)
        tk.Button(création, text = '+𝑓(𝑥)', command = _créer_fonction(RELATION_F_X)).grid(row = 0, column = 0, padx = 0, sticky = tk.EW)
        tk.Button(création, text = '+𝑓(𝑦)', command = _créer_fonction(RELATION_F_Y)).grid(row = 0, column = 2, padx = 0, sticky = tk.EW)
        tk.Button(création, text = '+(𝑥(𝑡); 𝑦(𝑡))', command = _créer_fonction(RELATION_XY_T)).grid(row = 0, column = 4, padx = 0, sticky = tk.EW)

        liste_défilable = ScrollableFrame(self.page_objets)
        self.défilables.append(liste_défilable)
        liste_défilable.pack(fill = tk.BOTH, expand = True)
        self.composant_liste = liste = liste_défilable.intérieur

        # Configuration de la mise en page des éléments
        liste.columnconfigure(0, weight = 0)
        liste.columnconfigure(1, weight = 1)

        for i, objet in enumerate(self.graphique.objets):
            self.métasobj.append([])
            self._préparer_objet(i)


    def _préparer_objet(self, idx):
        objet = self.graphique.objets[idx]
        liste = self.composant_liste

        cadre = tk.Frame(liste)
        cadre.pack(fill = tk.X, expand = True, pady = (16, 0) if idx else 0)
        cadre.columnconfigure(1, weight = 1)

        fn_type = {
            RELATION_F_X: '𝑓(𝑥)',
            RELATION_F_Y: '𝑓(𝑦)',
            RELATION_XY_T: '(𝑥(𝑡); 𝑦(𝑡))'
        }
        indépendante_types = {
            RELATION_F_X: '𝑥',
            RELATION_F_Y: '𝑦',
            RELATION_XY_T: '𝑡'
        }
        équation_côté_gauche = {
            RELATION_F_X: '𝑦 = ',
            RELATION_F_Y: '𝑥 = ',
            RELATION_XY_T: '(𝑥; 𝑦) = '
        }
        bornes_types = {
            RELATION_F_X: 'Domaine',
            RELATION_F_Y: 'Image',
            RELATION_XY_T: 'Bornes'
        }

        titre = tk.Frame(cadre)
        titre.grid(row = 0, column = 0, pady = 1, columnspan = 2, sticky = tk.EW)
        def _traite_suppression():
            parent = self.ctx.nametowidget(cadre.winfo_parent())
            cadre.destroy()

            idx = self.graphique.objets.index(objet)
            del self.graphique.objets[idx]
            del self.métasobj[idx]

            i = 0
            for o in parent.winfo_children():
                objet_no = recherche_enfants(o, 'no')
                if objet_no is not None:
                    o.pack_configure(pady = (16, 0) if i else 0)
                    objet_no.configure(text = f'#{i + 1}')
                    i += 1
        tk.Button(titre, text = '⤬', padx = 0, pady = 0, command = _traite_suppression).pack(side = tk.LEFT, padx = (0, 3))
        tk.Label(titre, text = f'#{idx + 1}', name = 'no', font = self.police_gras, anchor = tk.W).pack(side = tk.LEFT)
        tk.Label(titre, text = f'{fn_type[objet.type]}', font = self.police_gras, anchor = tk.W).pack(side = tk.LEFT)
        RELATION_var = tk.StringVar(value = objet.type)

        équation, r = self._prépare_champ(cadre, 1, 'Équation')
        équation_méta = CadreMéta(équation)
        équation_méta.définir_info(f'L\'équation de la relation. La variable indépendante est « {indépendante_types[objet.type]} ».')
        équation_méta.grid(row = 1, column = 0, columnspan = 5, pady = 1, sticky = tk.N + tk.EW)
        self.métasobj[idx].append(équation_méta)
        if objet.type != RELATION_XY_T:
            équation.columnconfigure(1, weight = 1)
            équation_var = tk.StringVar(value = objet.équation)
            tk.Label(équation, text = équation_côté_gauche[objet.type]).grid(row = 0, column = 0)
            équation_champ = tk.Entry(équation, textvariable = équation_var)
            équation_champ.grid(row = 0, column = 1, columnspan = 4, sticky = tk.EW)
            self._valide_champ(
                validateur = Validateur.objet_équation,
                méta = équation_méta,
                variables = (RELATION_var, équation_var, ),
                champs = (équation_champ, ),
                cible = (objet, 'équation')
            )
        else:
            équation.columnconfigure((1, 3), weight = 1)
            équation_x_var = tk.StringVar(value = objet.équation[0])
            équation_y_var = tk.StringVar(value = objet.équation[1])
            tk.Label(équation, text = f'{équation_côté_gauche[objet.type]}(').grid(row = 0, column = 0)
            équation_x_champ = tk.Entry(équation, textvariable = équation_x_var)
            équation_x_champ.grid(row = 0, column = 1, sticky = tk.EW)
            tk.Label(équation, text = '; ').grid(row = 0, column = 2)
            équation_y_champ = tk.Entry(équation, textvariable = équation_y_var)
            équation_y_champ.grid(row = 0, column = 3, sticky = tk.EW)
            tk.Label(équation, text = ')').grid(row = 0, column = 4)
            self._valide_champ(
                validateur = Validateur.objet_équation,
                méta = équation_méta,
                variables = (RELATION_var, équation_x_var, équation_y_var),
                champs = (équation_x_champ, équation_y_champ),
                cible = (objet, 'équation')
            )

        bornes, r = self._prépare_champ(cadre, r, bornes_types[objet.type])
        bornes.columnconfigure((0, 2), weight = 1)
        bornes_min_var = tk.StringVar(value = '' if objet.bornes[0] == float('-inf') else num_à_str(objet.bornes[0]))
        bornes_min_champ = tk.Entry(bornes, textvariable = bornes_min_var)
        bornes_min_champ.grid(row = 0, column = 0, sticky = tk.EW)
        tk.Label(bornes, text = ' à ').grid(row = 0, column = 1)
        bornes_max_var = tk.StringVar(value = '' if objet.bornes[1] == float('inf') else num_à_str(objet.bornes[1]))
        bornes_max_champ = tk.Entry(bornes, textvariable = bornes_max_var)
        bornes_max_champ.grid(row = 0, column = 2, sticky = tk.EW)
        bornes_méta = CadreMéta(bornes)
        bornes_méta.définir_info('Les limites inférieure et supérieure de la fonction. Le domaine est ouvert du côté d\'une valeur vide.')
        bornes_méta.grid(row = 1, column = 0, columnspan = 3, pady = 1, sticky = tk.N + tk.EW)
        self.métasobj[idx].append(bornes_méta)
        self._valide_champ(
            validateur = Validateur.objet_bornes,
            méta = bornes_méta,
            variables = (RELATION_var, bornes_min_var, bornes_max_var),
            champs = (bornes_min_champ, bornes_max_champ),
            cible = (objet, 'bornes')
        )

        pouverts, r = self._prépare_champ(cadre, r, 'Points ouverts')
        pouverts_var = tk.StringVar(value = '; '.join(map(num_à_str, objet.points_ouverts)))
        pouverts.columnconfigure(1, weight = 1)
        tk.Label(pouverts, text = f'{indépendante_types[objet.type]} = {{').grid(row = 0, column = 0)
        pouverts_champ = tk.Entry(pouverts, textvariable = pouverts_var)
        pouverts_champ.grid(row = 0, column = 1, sticky = tk.EW)
        tk.Label(pouverts, text = '}').grid(row = 0, column = 2)
        pouverts_méta = CadreMéta(pouverts)
        pouverts_méta.définir_info('Une liste de points ouverts (cercles vides) sur la courbe de l\'équation, séparés par des points-virgules (;).')
        pouverts_méta.grid(row = 1, column = 0, columnspan = 3, pady = 1, sticky = tk.N + tk.EW)
        self.métasobj[idx].append(pouverts_méta)
        self._valide_champ(
            validateur = Validateur.objet_points_ouverts,
            méta = pouverts_méta,
            variables = (pouverts_var, ),
            champs = (pouverts_champ, ),
            cible = (objet, 'points_ouverts')
        )

        pfermés, r = self._prépare_champ(cadre, r, 'Points fermés')
        pfermés_var = tk.StringVar(value = '; '.join(map(num_à_str, objet.points_fermés)))
        pfermés.columnconfigure(1, weight = 1)
        tk.Label(pfermés, text = f'{indépendante_types[objet.type]} = {{').grid(row = 0, column = 0)
        pfermés_champ = tk.Entry(pfermés, textvariable = pfermés_var)
        pfermés_champ.grid(row = 0, column = 1, sticky = tk.EW)
        tk.Label(pfermés, text = '}').grid(row = 0, column = 2)
        pfermés_méta = CadreMéta(pfermés)
        pfermés_méta.définir_info('Une liste de points fermés (cercles pleins) sur la courbe de l\'équation, séparés par des points-virgules (;).')
        pfermés_méta.grid(row = 1, column = 0, columnspan = 3, pady = 1, sticky = tk.N + tk.EW)
        self.métasobj[idx].append(pfermés_méta)
        self._valide_champ(
            validateur = Validateur.objet_points_fermés,
            méta = pfermés_méta,
            variables = (pfermés_var, ),
            champs = (pfermés_champ, ),
            cible = (objet, 'points_fermés')
        )

        style_options = {
            'solid': 'Solide',
            'dotted': 'Point',
            'densely dotted': 'Point dense',
            'loosely dotted': 'Point espacé',
            'dashed': 'Trait',
            'densely dashed': 'Trait dense',
            'loosely dashed': 'Trait espacé',
            'dashdotted': 'Point-trait',
            'densely dashdotted': 'Point-trait dense',
            'loosely dashdotted': 'Point-trait espacé',
            'dashdotdotted': 'Point-point-trait',
            'densely dashdotdotted': 'Point-point-trait dense',
            'loosely dashdotdotted': 'Point-point-trait espacé',
        }
        style, r = self._prépare_champ(cadre, r, 'Style')
        style_var = tk.StringVar(value = objet.style)
        style_champ = OptionMenu(style, style_var, style_options)
        style_champ.configure(anchor = tk.W, pady = 1, highlightthickness = 0)
        style_champ.pack(fill = tk.X)
        style_méta = CadreMéta(style)
        style_méta.définir_info('Le style de la courbe qui représente la fonction.')
        style_méta.pack(fill = tk.X)
        self.métasobj[idx].append(style_méta)
        self._valide_champ(
            validateur = Validateur.objet_style,
            méta = style_méta,
            variables = (style_var, ),
            champs = (style_champ, ),
            cible = (objet, 'style')
        )

        couleur, r = self._prépare_champ(cadre, r, 'Couleur')
        couleur_var = ColorVar(value = objet.couleur)
        couleur_champ = ColorButton(couleur, variable = couleur_var, text = 'objet', padx = 0, pady = 0)
        couleur_champ.pack(fill = tk.X)
        couleur_méta = CadreMéta(couleur)
        couleur_méta.définir_info('La couleur de la fonction.')
        couleur_méta.pack(fill = tk.X)
        self.métasobj[idx].append(couleur_méta)
        self._valide_champ(
            validateur = Validateur.objet_couleur,
            méta = couleur_méta,
            variables = (couleur_var, ),
            champs = (couleur_champ, ),
            cible = (objet, 'couleur')
        )

        étiquette, r = self._prépare_champ(cadre, r, 'Étiquette')
        étiquette.columnconfigure(1, weight = 1)
        étiquette_var = tk.StringVar(value = objet.étiquette)
        étiquette_champ = tk.Entry(étiquette, textvariable = étiquette_var)
        étiquette_champ.grid(row = 0, column = 0, columnspan = 2, pady = 1, sticky = tk.N + tk.EW)
        étiquette_méta = CadreMéta(étiquette)
        étiquette_méta.définir_info('L\'étiquette de la fonction. Le texte « mathématique » peut être entouré de $, tel que $f(x)$. Une étiquette ne sera pas affichée si la valeur est vide.')
        étiquette_méta.grid(row = 1, column = 0, columnspan = 2, pady = 1, sticky = tk.N + tk.EW)
        self.métasobj[idx].append(étiquette_méta)
        self._valide_champ(
            validateur = Validateur.objet_étiquette,
            méta = étiquette_méta,
            variables = (étiquette_var, ),
            champs = (étiquette_champ, ),
            cible = (objet, 'étiquette')
        )

        étiquette_position, _ = self._prépare_champ(étiquette, 2, 'Position')
        étiquette_position_var = tk.StringVar(value = num_à_str(objet.position))
        étiquette_position_champ = tk.Entry(étiquette_position, textvariable = étiquette_position_var)
        étiquette_position_champ.pack(fill = tk.X)
        étiquette_position_méta = CadreMéta(étiquette)
        étiquette_position_méta.définir_info('La position de l\'étiquette de la fonction de 0 (le début de la fonction) à 1 (la fin de la fonction).')
        étiquette_position_méta.grid(row = 3, column = 0, columnspan = 2, pady = 1, sticky = tk.N + tk.EW)
        self.métasobj[idx].append(étiquette_position_méta)
        self._valide_champ(
            validateur = Validateur.objet_position,
            méta = étiquette_position_méta,
            variables = (étiquette_position_var, ),
            champs = (étiquette_position_champ, ),
            cible = (objet, 'position')
        )

        étiquette_ancre, _ = self._prépare_champ(étiquette, 4, 'Ancre')
        étiquette_ancre.columnconfigure(0, weight = 1)
        étiquette_ancre_var = tk.StringVar(value = '' if objet.ancre is None else num_à_str(objet.ancre))
        étiquette_ancre_champ = tk.Entry(étiquette_ancre, textvariable = étiquette_ancre_var)
        étiquette_ancre_champ.grid(row = 0, column = 0, sticky = tk.EW)
        tk.Label(étiquette_ancre, text = '°').grid(row = 0, column = 1)
        étiquette_ancre_méta = CadreMéta(étiquette)
        étiquette_ancre_méta.définir_info('La position de l\'étiquette de la fonction en degrés, entre -360 à 360. « 0 » place l\'étiquette à la droite du point. L\'étiquette sera centrée si aucun angle est fourni.')
        étiquette_ancre_méta.grid(row = 5, column = 0, columnspan = 2, pady = 1, sticky = tk.N + tk.EW)
        self.métasobj[idx].append(étiquette_ancre_méta)
        self._valide_champ(
            validateur = Validateur.objet_ancre,
            méta = étiquette_ancre_méta,
            variables = (étiquette_ancre_var, ),
            champs = (étiquette_ancre_champ, ),
            cible = (objet, 'ancre')
        )

        for méta in self.métasobj[idx]:
            méta.affiche_info(self.informations_visibles)


    def _prépare_section(self, parent, rangée, nom):
        tk.Label(
            parent,
            text = nom,
            font = self.police_gras,
            anchor = tk.W
        ).grid(
            row = rangée,
            column = 0,
            pady = 1 if rangée == 0 else (17, 1),
            columnspan = 2,
            sticky = tk.N + tk.EW
        )

        return rangée + 1


    def _prépare_champ(self, parent, rangée, nom):
        tk.Label(
            parent,
            text = f'{nom}: ',
            padx = 0
        ).grid(
            row = rangée,
            column = 0,
            sticky = tk.NE
        )

        données = tk.Frame(parent)
        données.grid(
            row = rangée,
            column = 1,
            sticky = tk.N + tk.EW
        )

        return données, rangée + 1


    def _valide_champ(self,
        validateur,
        méta,
        variables,
        champs,
        cible
    ):
        def v():
            résultat = validateur(*[v.get() for v in variables])

            if méta is not None:
                méta.définir_erreur('\n'.join([str(e) for e in résultat.erreurs]) if résultat.erreurs else None)

            #if résultat.erreurs:
            #    for champ in champs:
            #        champ.configure(bg = '#FFCCCC')
            #else:
            #    for champ in champs:
            #        champ.configure(bg = 'transparent')

            if not résultat.erreurs:
                setattr(cible[0], cible[1], résultat.résultat)

            return True

        for champ in champs:
            if isinstance(champ, tk.Entry):
                champ.configure(validate = 'focusout', validatecommand = v)
            elif isinstance(champ, tk.OptionMenu):
                champ.textvariable.trace('w', lambda *_: v())
            else:
                champ.configure(command = v)


    def _prépare_page_plan(self):
        self.page_plan = ScrollableFrame(self.ctx)
        self.défilables.append(self.page_plan)
        params = self.page_plan.intérieur

        # Configuration de la mise en page des éléments
        params.columnconfigure(0, weight = 0)
        params.columnconfigure(1, weight = 1)

        r = self._prépare_section(params, 0, 'Plan')

        plan_dimensions, r = self._prépare_champ(params, r, 'Dimensions')
        plan_dimensions.columnconfigure((0, 2), weight = 1)
        dimensions_0_var = tk.StringVar(value = num_à_str(self.graphique.dimensions[0]))
        dimensions_0_champ = tk.Entry(plan_dimensions, textvariable = dimensions_0_var)
        dimensions_0_champ.grid(row = 0, column = 0, sticky = tk.N + tk.EW)
        tk.Label(plan_dimensions, text = ' cm × ').grid(row = 0, column = 1, sticky = tk.N + tk.EW)
        dimensions_1_var = tk.StringVar(value = num_à_str(self.graphique.dimensions[1]))
        dimensions_1_champ = tk.Entry(plan_dimensions, textvariable = dimensions_1_var)
        dimensions_1_champ.grid(row = 0, column = 2, sticky = tk.N + tk.EW)
        tk.Label(plan_dimensions, text = ' cm').grid(row = 0, column = 3, sticky = tk.N + tk.EW)
        dimensions_méta = CadreMéta(plan_dimensions)
        dimensions_méta.définir_info('La largeur et la hauteur du plan cartésien final. Les étiquettes à l\'extérieur du plan cartésien sont exemptées de cette limite.')
        dimensions_méta.grid(row = 1, column = 0, columnspan = 4, pady = 1, sticky = tk.N + tk.EW)
        self.métas.append(dimensions_méta)
        self._valide_champ(
            validateur = Validateur.dimensions,
            méta = dimensions_méta,
            variables = (dimensions_0_var, dimensions_1_var),
            champs = (dimensions_0_champ, dimensions_1_champ),
            cible = (self.graphique, 'dimensions')
        )

        plan_bornes, r = self._prépare_champ(params, r, 'Bornes')
        plan_bornes.columnconfigure((1, 3), weight = 1)
        tk.Label(plan_bornes, text = 'abscisses:', anchor = tk.E).grid(row = 0, column = 0, pady = 1, sticky = tk.N + tk.EW)
        axe_0_bornes_0_var = tk.StringVar(value = num_à_str(self.graphique.axes[0].bornes[0]))
        axe_0_bornes_0_champ = tk.Entry(plan_bornes, textvariable = axe_0_bornes_0_var)
        axe_0_bornes_0_champ.grid(row = 0, column = 1, pady = 1, sticky = tk.N + tk.EW)
        tk.Label(plan_bornes, text = ' à ', anchor = tk.E).grid(row = 0, column = 2, pady = 1, sticky = tk.N + tk.EW)
        axe_0_bornes_1_var = tk.StringVar(value = num_à_str(self.graphique.axes[0].bornes[1]))
        axe_0_bornes_1_champ = tk.Entry(plan_bornes, textvariable = axe_0_bornes_1_var)
        axe_0_bornes_1_champ.grid(row = 0, column = 3, pady = 1, sticky = tk.N + tk.EW)
        axe_0_bornes_méta = CadreMéta(plan_bornes)
        axe_0_bornes_méta.définir_info('Les limites inférieure et supérieure de l\'axe des abscisses.')
        axe_0_bornes_méta.grid(row = 1, column = 0, columnspan = 4, pady = 1, sticky = tk.N + tk.EW)
        self.métas.append(axe_0_bornes_méta)
        self._valide_champ(
            validateur = Validateur.axe_bornes,
            méta = axe_0_bornes_méta,
            variables = (axe_0_bornes_0_var, axe_0_bornes_1_var),
            champs = (axe_0_bornes_0_champ, axe_0_bornes_1_champ),
            cible = (self.graphique.axes[0], 'bornes')
        )
        tk.Label(plan_bornes, text = 'ordonnées:', anchor = tk.E).grid(row = 2, column = 0, pady = 1, sticky = tk.N + tk.EW)
        axe_1_bornes_0_var = tk.StringVar(value = num_à_str(self.graphique.axes[1].bornes[0]))
        axe_1_bornes_0_champ = tk.Entry(plan_bornes, textvariable = axe_1_bornes_0_var)
        axe_1_bornes_0_champ.grid(row = 2, column = 1, pady = 1, sticky = tk.N + tk.EW)
        tk.Label(plan_bornes, text = ' à ', anchor = tk.E).grid(row = 2, column = 2, pady = 1, sticky = tk.N + tk.EW)
        axe_1_bornes_1_var = tk.StringVar(value = num_à_str(self.graphique.axes[1].bornes[1]))
        axe_1_bornes_1_champ = tk.Entry(plan_bornes, textvariable = axe_1_bornes_1_var)
        axe_1_bornes_1_champ.grid(row = 2, column = 3, pady = 1, sticky = tk.N + tk.EW)
        axe_1_bornes_méta = CadreMéta(plan_bornes)
        axe_1_bornes_méta.définir_info('Les limites inférieur et supérieure de l\'axe des ordonnées.')
        axe_1_bornes_méta.grid(row = 3, column = 0, columnspan = 4, pady = 1, sticky = tk.N + tk.EW)
        self.métas.append(axe_1_bornes_méta)
        self._valide_champ(
            validateur = Validateur.axe_bornes,
            méta = axe_1_bornes_méta,
            variables = (axe_1_bornes_0_var, axe_1_bornes_1_var),
            champs = (axe_1_bornes_0_champ, axe_1_bornes_1_champ),
            cible = (self.graphique.axes[1], 'bornes')
        )

        for i, nom in enumerate(['abscisses', 'ordonnées']):
            r = self._prépare_section(params, r, f'Axe des {nom}')

            axe_étiquette, r = self._prépare_champ(params, r, 'Étiquette')
            axe_étiquette_var = tk.StringVar(value = self.graphique.axes[i].étiquette)
            axe_étiquette_champ = tk.Entry(axe_étiquette, textvariable = axe_étiquette_var)
            axe_étiquette_champ.pack(pady = 1, fill = tk.X)
            axe_étiquette_méta = CadreMéta(axe_étiquette)
            axe_étiquette_méta.définir_info(f'L\'étiquette qui sera affichée pour l\'axe des {nom}. Le texte « mathématique » peut être entouré de $, tel que $f(x)$. Une étiquette ne sera pas affichée si cette valeur est vide.')
            axe_étiquette_méta.pack(fill = tk.X)
            self.métas.append(axe_étiquette_méta)
            self._valide_champ(
                validateur = Validateur.axe_étiquette,
                méta = axe_étiquette_méta,
                variables = (axe_étiquette_var, ),
                champs = (axe_étiquette_champ, ),
                cible = (self.graphique.axes[i], 'étiquette')
            )

            axe_droite, r = self._prépare_champ(params, r, 'Droite')
            axe_droite_choix = tk.Frame(axe_droite)
            axe_droite_choix.pack(fill = tk.X)
            axe_droite_var = tk.StringVar(value = self.graphique.axes[i].droite)
            axe_droite_aucun_champ = tk.Radiobutton(axe_droite_choix, text = 'aucune', variable = axe_droite_var, value = AXE_CACHÉ)
            axe_droite_aucun_champ.pack(side = tk.LEFT)
            axe_droite_ligne_champ = tk.Radiobutton(axe_droite_choix, text = 'ligne', variable = axe_droite_var, value = AXE_LIGNE)
            axe_droite_ligne_champ.pack(side = tk.LEFT)
            axe_droite_flèche_champ = tk.Radiobutton(axe_droite_choix, text = 'flèche', variable = axe_droite_var, value = AXE_FLÈCHE)
            axe_droite_flèche_champ.pack(side = tk.LEFT)
            axe_droite_méta = CadreMéta(axe_droite)
            axe_droite_méta.définir_info(f'Le style de l\'axe des {nom}.')
            axe_droite_méta.pack(fill = tk.X)
            self.métas.append(axe_droite_méta)
            self._valide_champ(
                validateur = Validateur.axe_droite,
                méta = axe_droite_méta,
                variables = (axe_droite_var, ),
                champs = (axe_droite_aucun_champ, axe_droite_ligne_champ, axe_droite_flèche_champ),
                cible = (self.graphique.axes[i], 'droite')
            )

            axe_pas, r = self._prépare_champ(params, r, 'Pas')
            axe_pas_var = tk.StringVar(value = num_à_str(self.graphique.axes[i].pas))
            axe_pas_champ = tk.Entry(axe_pas, textvariable = axe_pas_var)
            axe_pas_champ.pack(fill = tk.X)
            axe_pas_méta = CadreMéta(axe_pas)
            axe_pas_méta.définir_info(f'La distance, en unités, entre les valeurs de l\'échelle de l\'axe des {nom}.')
            axe_pas_méta.pack(fill = tk.X)
            self.métas.append(axe_pas_méta)
            self._valide_champ(
                validateur = Validateur.axe_pas,
                méta = axe_pas_méta,
                variables = (axe_pas_var, ),
                champs = (axe_pas_champ, ),
                cible = (self.graphique.axes[i], 'pas')
            )

            axe_interpas, r = self._prépare_champ(params, r, 'Interpas')
            axe_interpas_var = tk.StringVar(value = num_à_str(self.graphique.axes[i].interpas))
            axe_interpas_champ = tk.Entry(axe_interpas, textvariable = axe_interpas_var)
            axe_interpas_champ.pack(fill = tk.X)
            axe_interpas_méta = CadreMéta(axe_interpas)
            axe_interpas_méta.définir_info(f'Le nombre de lignes entre chaque valeur de l\'échelle de l\'axe des {nom}. Aucune ligne intermédiaire sera affichée si cette valeur est vide.')
            axe_interpas_méta.pack(fill = tk.X)
            self.métas.append(axe_interpas_méta)
            self._valide_champ(
                validateur = Validateur.axe_interpas,
                méta = axe_interpas_méta,
                variables = (axe_interpas_var, ),
                champs = (axe_interpas_champ, ),
                cible = (self.graphique.axes[i], 'interpas')
            )

        r = self._prépare_section(params, r, 'Grillage')

        grillage_ouvert, r = self._prépare_champ(params, r, 'Bordure')
        grillage_ouvert_choix = tk.Frame(grillage_ouvert)
        grillage_ouvert_choix.pack(fill = tk.X)
        grillage_ouvert_var = tk.BooleanVar(value = self.graphique.grillage_ouvert)
        grillage_ouvert_vrai_champ = tk.Radiobutton(grillage_ouvert_choix, text = 'ouverte', variable = grillage_ouvert_var, value = True)
        grillage_ouvert_vrai_champ.pack(side = tk.LEFT)
        grillage_ouvert_faux_champ = tk.Radiobutton(grillage_ouvert_choix, text = 'fermée', variable = grillage_ouvert_var, value = False)
        grillage_ouvert_faux_champ.pack(side = tk.LEFT)
        grillage_ouvert_méta = CadreMéta(grillage_ouvert)
        grillage_ouvert_méta.définir_info('« Ouverte » réduit légèrement les bornes du graphique pour empêcher le dessinage du dernier grillage. « Fermée » ne réduit pas les bornes.')
        grillage_ouvert_méta.pack(fill = tk.X)
        self.métas.append(grillage_ouvert_méta)
        self._valide_champ(
            validateur = Validateur.grillage_ouvert,
            méta = grillage_ouvert_méta,
            variables = (grillage_ouvert_var, ),
            champs = (grillage_ouvert_vrai_champ, grillage_ouvert_faux_champ),
            cible = (self.graphique, 'grillage_ouvert')
        )

        for i, nom in enumerate(['Abscisses', 'Ordonnées']):
            axe_grillage, r = self._prépare_champ(params, r, nom)
            axe_grillage_items = tk.Frame(axe_grillage)
            axe_grillage_items.pack(fill = tk.X)
            axe_grillage_majeur_var = tk.BooleanVar(value = self.graphique.axes[i].grillage_majeur)
            axe_grillage_majeur_champ = tk.Checkbutton(axe_grillage_items, text = 'majeur', variable = axe_grillage_majeur_var)
            axe_grillage_majeur_champ.pack(side = tk.LEFT)
            axe_grillage_mineur_var = tk.BooleanVar(value = self.graphique.axes[i].grillage_mineur)
            axe_grillage_mineur_champ = tk.Checkbutton(axe_grillage_items, text = 'mineur', variable = axe_grillage_mineur_var)
            axe_grillage_mineur_champ.pack(side = tk.LEFT)
            axe_grillage_méta = CadreMéta(axe_grillage)
            axe_grillage_méta.définir_info(f'L\'affichage des lignes perpendiculaires à l\'axe des {nom.lower()}. « Majeur » est en lien avec « Pas » et « Mineur » avec « Interpas ».')
            axe_grillage_méta.pack(fill = tk.X)
            self.métas.append(axe_grillage_méta)
            self._valide_champ(
                validateur = Validateur.axe_grillage_majeur,
                méta = axe_grillage_méta,
                variables = (axe_grillage_majeur_var, ),
                champs = (axe_grillage_majeur_champ, ),
                cible = (self.graphique.axes[i], 'grillage_majeur')
            )
            self._valide_champ(
                validateur = Validateur.axe_grillage_mineur,
                méta = axe_grillage_méta,
                variables = (axe_grillage_mineur_var, ),
                champs = (axe_grillage_mineur_champ, ),
                cible = (self.graphique.axes[i], 'grillage_mineur')
            )

        r = self._prépare_section(params, r, 'Couleurs')

        couleur, r = self._prépare_champ(params, r, 'Plan')
        couleur_var = ColorVar(value = self.graphique.couleur)
        couleur_champ = ColorButton(couleur, variable = couleur_var, text = 'arrière plan', padx = 0, pady = 0)
        couleur_champ.pack(fill = tk.X)
        couleur_méta = CadreMéta(couleur)
        couleur_méta.définir_info(f'La couleur de l\'arrière plan du plan cartésien.')
        couleur_méta.pack(fill = tk.X)
        self.métas.append(couleur_méta)
        self._valide_champ(
            validateur = Validateur.couleur,
            méta = couleur_méta,
            variables = (couleur_var, ),
            champs = (couleur_champ, ),
            cible = (self.graphique, 'couleur')
        )

        for i, nom in enumerate(['Abscisses', 'Ordonnées']):
            axe_couleurs, r = self._prépare_champ(params, r, nom)
            axe_couleurs.columnconfigure((0, 2, 4), weight = 1)
            axe_couleurs.columnconfigure((1, 3), minsize = 2)

            axe_couleur_var = ColorVar(value = self.graphique.axes[i].couleur)
            axe_couleur_champ = ColorButton(axe_couleurs, variable = axe_couleur_var, text = 'axe', padx = 0, pady = 0)
            axe_couleur_champ.grid(row = 0, column = 0, sticky = tk.EW)
            axe_majeur_couleur_var = ColorVar(value = self.graphique.axes[i].grillage_majeur_couleur)
            axe_majeur_couleur_champ = ColorButton(axe_couleurs, variable = axe_majeur_couleur_var, text = 'majeur', padx = 0, pady = 0)
            axe_majeur_couleur_champ.grid(row = 0, column = 2, sticky = tk.EW)
            axe_mineur_couleur_var = ColorVar(value = self.graphique.axes[i].grillage_mineur_couleur)
            axe_mineur_couleur_champ = ColorButton(axe_couleurs, variable = axe_mineur_couleur_var, text = 'mineur', padx = 0, pady = 0)
            axe_mineur_couleur_champ.grid(row = 0, column = 4, sticky = tk.EW)
            axe_couleurs_méta = CadreMéta(axe_couleurs)
            axe_couleurs_méta.définir_info(f'La couleur de l\'axe des {nom.lower()} et des lignes perpendiculaires à l\'axe.')
            axe_couleurs_méta.grid(row = 1, column = 0, columnspan = 5, sticky = tk.EW)
            self.métas.append(axe_couleurs_méta)
            self._valide_champ(
                validateur = Validateur.axe_couleur,
                méta = axe_couleurs_méta,
                variables = (axe_couleur_var, ),
                champs = (axe_couleur_champ, ),
                cible = (self.graphique.axes[i], 'couleur')
            )
            self._valide_champ(
                validateur = Validateur.axe_grillage_majeur_couleur,
                méta = axe_couleurs_méta,
                variables = (axe_majeur_couleur_var, ),
                champs = (axe_majeur_couleur_champ, ),
                cible = (self.graphique.axes[i], 'grillage_majeur_couleur')
            )
            self._valide_champ(
                validateur = Validateur.axe_grillage_mineur_couleur,
                méta = axe_couleurs_méta,
                variables = (axe_mineur_couleur_var, ),
                champs = (axe_mineur_couleur_champ, ),
                cible = (self.graphique.axes[i], 'grillage_mineur_couleur')
            )

        r = self._prépare_section(params, r, 'Unités')

        angles, r = self._prépare_champ(params, r, 'Angles')
        angles_choix = tk.Frame(angles)
        angles_choix.pack(fill = tk.X)
        angles_var = tk.StringVar(value = self.graphique.angles)
        angles_rads_champ = tk.Radiobutton(angles_choix, text = 'radians', variable = angles_var, value = ANGLE_RADIANS)
        angles_rads_champ.pack(side = tk.LEFT)
        angles_degs_champ = tk.Radiobutton(angles_choix, text = 'degrés', variable = angles_var, value = ANGLE_DEGRÉS)
        angles_degs_champ.pack(side = tk.LEFT)
        angles_méta = CadreMéta(angles)
        angles_méta.définir_info('La mesure angulaire utilisée pour les fonctions trigonométriques.')
        angles_méta.pack(fill = tk.X)
        self.métas.append(angles_méta)
        self._valide_champ(
            validateur = Validateur.angles,
            méta = angles_méta,
            variables = (angles_var, ),
            champs = (angles_degs_champ, angles_rads_champ),
            cible = (self.graphique, 'angles')
        )


main()
