import copy
import toml

from erreur import *
from graphique import *
from validateur import *

VERSION_ENREGISTREMENT = 1

class EnregistrementToml:
    def lire(fichier):
        try:
            données = toml.load(fichier)
        except toml.TomlDecodeError as e:
            return Erreur(Erreur.TOML_FORMAT, fichier = fichier, erreur = e)
        except OSError as e:
            return Erreur(Erreur.TOML_INACCESSIBLE, fichier = fichier, erreur = e)
        except Exception as e:
            return Erreur(Erreur.TOML_INVALIDE, fichier = fichier, erreur = e)

        def _vérifie_champ(objet, données, champ, sous_champ = ''):
            valeur = None if champ not in données else données[champ]

            if sous_champ == 'objet_' and champ in ['équation', 'bornes']:
                params = (objet.type, *valeur)
            elif not isinstance(valeur, list) or 'couleur' in champ or 'points' in champ:
                params = (valeur, )
            else:
                params = valeur

            résultat = getattr(Validateur, f'{sous_champ}{champ}')(*params)
            if résultat.erreurs:
                return Erreur(Erreur.TOML_DONNÉES, fichier = fichier, champ = champ)

            setattr(objet, champ, résultat.résultat)

        graphique = Graphique()
        champs = [champ for champ in dir(graphique) if not champ.startswith('_') and champ not in ['axes', 'objets']]
        for champ in champs:
            erreur = _vérifie_champ(graphique, données, champ)
            if erreur:
                return erreur

        if 'axes' not in données or not isinstance(données['axes'], list) or len(données['axes']) != 2:
            return Erreur(Erreur.TOML_DONNÉES, fichier = fichier, champ = 'axes')

        axes = []
        for données_axe in données['axes']:
            axe = Axe()
            champs = [champ for champ in dir(axe) if not champ.startswith('_')]
            for champ in champs:
                erreur = _vérifie_champ(axe, données_axe, champ, 'axe_')
                if erreur:
                    return erreur

            axes.append(axe)
        graphique.axes = tuple(axes)

        if 'objets' not in données or not isinstance(données['objets'], list):
            return Erreur(Erreur.TOML_DONNÉES, fichier = fichier, champ = 'objets')

        for données_objet in données['objets']:
            if 'type' not in données_objet or Validateur.objet_type(données_objet['type']).erreurs:
                return Erreur(Erreur.TOML_DONNÉES, fichier = fichier, champ = 'type')

            objet = Fonction(données_objet['type'])
            champs = [champ for champ in dir(objet) if not champ.startswith('_') and champ != 'type']
            for champ in champs:
                erreur = _vérifie_champ(objet, données_objet, champ, 'objet_')
                if erreur:
                    return erreur

            graphique.objets.append(objet)

        return graphique


    def enregistrement(nom_fichier, graphique):
        try:
            with open(nom_fichier, mode = 'w', encoding = 'utf-8') as f:
                données = copy.deepcopy(vars(graphique))
                données['version'] = VERSION_ENREGISTREMENT
                données['axes'] = [vars(axe) for axe in données['axes']]
                données['objets'] = [vars(objet) for objet in données['objets']]

                toml.dump(données, f)
        except BaseException as e:
            return Erreur(Erreur.TOML_ENREGISTREMENT, erreur = str(e))

        return None
