import tkinter as tk
import re

from erreur import *
from graphique import *


class RésultatValidateur:
    def __init__(self, défaut = None):
        self.erreurs = []
        self.résultat = défaut


class Validateur:
    def _réel(x):
        if not isinstance(x, float) and not isinstance(x, int):
            x = x.get() if isinstance(x, tk.StringVar) else str(x)
            x = x.strip()

            if re.fullmatch(r'-?[0-9]+(?:\.[0-9]+)?', x):
                try:
                    x = float(x)
                except Exception:
                    x = None
            else:
                x = None

        return x


    def _entier(x):
        if isinstance(x, float):
            x = int(x)
        elif not isinstance(x, int):
            x = variable.get() if isinstance(x, tk.StringVar) else str(x)
            x = x.strip()

            if re.fullmatch(r'-?[0-9]+', x):
                try:
                    x = int(x)
                except Exception:
                    x = None
            else:
                x = None

        return x


    def _couleur(c):
        if not (isinstance(c, tuple) or isinstance(c, list)) or len(c) != 3:
            c = None
        else:
            c = tuple(map(lambda ci: int(ci) if isinstance(ci, float) else ci, c))

            if not all(isinstance(ci, int) and 0 <= ci <= 255 for ci in c):
                c = None

        return c


    def dimensions(largeur, hauteur):
        r = RésultatValidateur()

        largeur = Validateur._réel(largeur)
        if largeur is None:
            r.erreurs.append(Erreur(Erreur.DIMENSIONS_LARGEUR_FORMAT))
        elif largeur <= 0:
            r.erreurs.append(Erreur(Erreur.DIMENSIONS_LARGEUR_NONPOSITIF))

        hauteur = Validateur._réel(hauteur)
        if hauteur is None:
            r.erreurs.append(Erreur(Erreur.DIMENSIONS_HAUTEUR_FORMAT))
        elif hauteur <= 0:
            r.erreurs.append(Erreur(Erreur.DIMENSIONS_HAUTEUR_NONPOSITIF))

        if not r.erreurs:
            r.résultat = (largeur, hauteur)

        return r


    def axe_bornes(min, max):
        r = RésultatValidateur()

        min = Validateur._réel(min)
        if min is None:
            r.erreurs.append(Erreur(Erreur.AXE_BORNES_MIN_FORMAT))

        max = Validateur._réel(max)
        if max is None:
            r.erreurs.append(Erreur(Erreur.AXE_BORNES_MAX_FORMAT))
        
        if not r.erreurs:
            if min == max:
                r.erreurs.append(Erreur(Erreur.AXE_BORNES_VIDE))
            else:
                r.résultat = (min, max)

        return r


    def axe_étiquette(étiquette):
        return RésultatValidateur(str(étiquette))


    def axe_droite(droite):
        r = RésultatValidateur()

        if droite not in [AXE_FLÈCHE, AXE_LIGNE, AXE_CACHÉ]:
            r.erreurs.append(Erreur(Erreur.AXE_DROITE_TYPE))
        else:
            r.résultat = droite

        return r


    def axe_pas(pas):
        r = RésultatValidateur()

        pas = Validateur._réel(pas)
        if pas is None:
            r.erreurs.append(Erreur(Erreur.AXE_PAS_FORMAT))
        elif pas <= 0:
            r.erreurs.append(Erreur(Erreur.AXE_PAS_NONPOSITIF))
        else:
            r.résultat = pas

        return r


    def axe_interpas(interpas):
        r = RésultatValidateur(0)

        if not isinstance(interpas, int):
            interpas = str(interpas)
            if interpas.strip() != '':
                interpas = Validateur._entier(interpas)
                if interpas is None:
                    r.erreurs.append(Erreur(Erreur.AXE_INTERPAS_FORMAT))

        if not r.erreurs:
            if interpas < 0:
                r.erreurs.append(Erreur(Erreur.AXE_INTERPAS_NÉGATIF))
            else:
                r.résultat = interpas

        return r


    def grillage_ouvert(grillage_ouvert):
        return RésultatValidateur(bool(grillage_ouvert))


    def axe_grillage_majeur(grillage_majeur):
        return RésultatValidateur(bool(grillage_majeur))


    def axe_grillage_mineur(grillage_mineur):
        return RésultatValidateur(bool(grillage_mineur))


    def couleur(couleur):
        r = RésultatValidateur()

        couleur = Validateur._couleur(couleur)
        if couleur is None:
            r.erreurs.append(Erreur(Erreur.COULEUR_FORMAT))
        else:
            r.résultat = couleur

        return r


    def axe_couleur(couleur):
        r = RésultatValidateur()

        couleur = Validateur._couleur(couleur)
        if couleur is None:
            r.erreurs.append(Erreur(Erreur.AXE_COULEUR_FORMAT))
        else:
            r.résultat = couleur

        return r


    def axe_grillage_majeur_couleur(couleur):
        r = RésultatValidateur()

        couleur = Validateur._couleur(couleur)
        if couleur is None:
            r.erreurs.append(Erreur(Erreur.AXE_GMAJEUR_COULEUR_FORMAT))
        else:
            r.résultat = couleur

        return r


    def axe_grillage_mineur_couleur(couleur):
        r = RésultatValidateur()

        couleur = Validateur._couleur(couleur)
        if couleur is None:
            r.erreurs.append(Erreur(Erreur.AXE_GMINEUR_COULEUR_FORMAT))
        else:
            r.résultat = couleur

        return r


    def angles(angles):
        r = RésultatValidateur()

        if angles not in [ANGLE_DEGRÉS, ANGLE_RADIANS]:
            r.erreurs.append(Erreur(Erreur.ANGLES_TYPE))
        else:
            r.résultat = angles

        return r


    def objet_type(type):
        r = RésultatValidateur()

        if type not in [RELATION_F_X, RELATION_F_Y, RELATION_XY_T]:
            r.erreurs.append(Erreur(Erreur.OBJET_TYPE))
        else:
            r.résultat = type

        return r


    def objet_équation(type, *équation):
        return RésultatValidateur(str(équation[0]) if type != RELATION_XY_T else tuple(map(str, équation)))


    def objet_bornes(type, min, max):
        r = RésultatValidateur()

        if type != RELATION_XY_T and isinstance(min, str) and min.strip() == '':
            min = float('-inf')
        else:
            min = Validateur._réel(min)
            if min is None:
                r.erreurs.append(Erreur(Erreur.OBJET_BORNES_MIN_FORMAT))

        if type != RELATION_XY_T and isinstance(max, str) and max.strip() == '':
            max = float('inf')
        else:
            max = Validateur._réel(max)
            if max is None:
                r.erreurs.append(Erreur(Erreur.OBJET_BORNES_MAX_FORMAT))
        
        if not r.erreurs:
            if min >= max:
                r.erreurs.append(Erreur(Erreur.OBJET_BORNES_VIDE))
            else:
                r.résultat = (min, max)

        return r


    def objet_points_ouverts(points):
        r = RésultatValidateur()

        if isinstance(points, str):
            points = points.split(';')

        if not isinstance(points, list):
            r.erreurs.append(Erreur(Erreur.OBJET_POUVERTS_FORMAT))
        else:
            points = list(map(lambda xi: str(xi).strip(), points))

            for i, p in enumerate(points):
                if not p:
                    continue

                p = Validateur._réel(p)
                if p is None:
                    r.erreurs.append(Erreur(Erreur.OBJET_POUVERTS_ITEM_FORMAT, item = i + 1))
                points[i] = p

            if r.erreurs:
                r.erreurs.insert(0, Erreur(Erreur.OBJET_POUVERTS_FORMAT))
            else:
                r.résultat = list(filter(None, points))

        return r


    def objet_points_fermés(points):
        r = RésultatValidateur()

        if isinstance(points, str):
            points = points.split(';')

        if not isinstance(points, list):
            r.erreurs.append(Erreur(Erreur.OBJET_PFERMÉS_FORMAT))
        else:
            points = list(map(lambda xi: str(xi).strip(), points))

            for i, p in enumerate(points):
                if not p:
                    continue

                p = Validateur._réel(p)
                if p is None:
                    r.erreurs.append(Erreur(Erreur.OBJET_PFERMÉS_ITEM_FORMAT, item = i + 1))
                points[i] = p

            if r.erreurs:
                r.erreurs.insert(0, Erreur(Erreur.OBJET_PFERMÉS_FORMAT))
            else:
                r.résultat = list(filter(None, points))

        return r


    def objet_style(style):
        r = RésultatValidateur()

        if style not in [
            'solid',
            'dotted',
            'densely dotted',
            'loosely dotted',
            'dashed',
            'densely dashed',
            'loosely dashed',
            'dashdotted',
            'densely dashdotted',
            'loosely dashdotted',
            'dashdotdotted',
            'densely dashdotdotted',
            'loosely dashdotdotted'
        ]:
            r.erreurs.append(Erreur(Erreur.OBJET_STYLE_TYPE))
        else:
            r.résultat = style

        return r


    def objet_couleur(couleur):
        r = RésultatValidateur()

        couleur = Validateur._couleur(couleur)
        if couleur is None:
            r.erreurs.append(Erreur(Erreur.OBJET_COULEUR_FORMAT))
        else:
            r.résultat = couleur

        return r


    def objet_étiquette(étiquette):
        return RésultatValidateur(str(étiquette))


    def objet_position(position):
        r = RésultatValidateur()

        position = Validateur._réel(position)
        if position is None:
            r.erreurs.append(Erreur(Erreur.OBJET_ÉTIQUETTE_POS_FORMAT))
        elif position < 0 or position > 1:
            r.erreurs.append(Erreur(Erreur.OBJET_ÉTIQUETTE_POS_ÉTENDU))
        else:
            r.résultat = position

        return r


    def objet_ancre(ancre):
        r = RésultatValidateur()

        if ancre is not None and not (isinstance(ancre, str) and ancre.strip() == ''):
            ancre = Validateur._réel(ancre)
            if ancre is None:
                r.erreurs.append(Erreur(Erreur.OBJET_ANCRE_FORMAT))
            elif ancre < -360 or ancre > 360:
                r.erreurs.append(Erreur(Erreur.OBJET_ANCRE_ÉTENDU))
            else:
                r.résultat = ancre

        return r
