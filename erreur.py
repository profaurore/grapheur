class Erreur:
    DIMENSIONS_LARGEUR_FORMAT = 'DIMENSIONS_LARGEUR_FORMAT'
    DIMENSIONS_LARGEUR_NONPOSITIF = 'DIMENSIONS_LARGEUR_NONPOSITIF'
    DIMENSIONS_HAUTEUR_FORMAT = 'DIMENSIONS_HAUTEUR_FORMAT'
    DIMENSIONS_HAUTEUR_NONPOSITIF = 'DIMENSIONS_HAUTEUR_NONPOSITIF'
    AXE_BORNES_MIN_FORMAT = 'AXE_BORNES_MIN_FORMAT'
    AXE_BORNES_MAX_FORMAT = 'AXE_BORNES_MAX_FORMAT'
    AXE_BORNES_VIDE = 'AXE_BORNES_VIDE'
    AXE_DROITE_TYPE = 'AXE_DROITE_TYPE'
    AXE_PAS_FORMAT = 'AXE_PAS_FORMAT'
    AXE_PAS_NONPOSITIF = 'AXE_PAS_NONPOSITIF'
    AXE_INTERPAS_FORMAT = 'AXE_INTERPAS_FORMAT'
    AXE_INTERPAS_NÉGATIF = 'AXE_INTERPAS_NÉGATIF'
    COULEUR_FORMAT = 'COULEUR_FORMAT'
    AXE_COULEUR_FORMAT = 'AXE_COULEUR_FORMAT'
    AXE_GMAJEUR_COULEUR_FORMAT = 'AXE_GMAJEUR_COULEUR_FORMAT'
    AXE_GMINEUR_COULEUR_FORMAT = 'AXE_GMINEUR_COULEUR_FORMAT'
    ANGLES_TYPE = 'ANGLES_TYPE'
    OBJET_TYPE = 'OBJET_TYPE'
    OBJET_BORNES_MIN_FORMAT = 'OBJET_BORNES_MIN_FORMAT'
    OBJET_BORNES_MAX_FORMAT = 'OBJET_BORNES_MAX_FORMAT'
    OBJET_BORNES_VIDE = 'OBJET_BORNES_VIDE'
    OBJET_POUVERTS_FORMAT = 'OBJET_POUVERTS_FORMAT'
    OBJET_POUVERTS_ITEM_FORMAT = 'OBJET_POUVERTS_ITEM_FORMAT'
    OBJET_PFERMÉS_FORMAT = 'OBJET_PFERMÉS_FORMAT'
    OBJET_PFERMÉS_ITEM_FORMAT = 'OBJET_PFERMÉS_ITEM_FORMAT'
    OBJET_STYLE_TYPE = 'OBJET_STYLE_TYPE'
    OBJET_COULEUR_FORMAT = 'OBJET_COULEUR_FORMAT'
    OBJET_ÉTIQUETTE_POS_FORMAT = 'OBJET_ÉTIQUETTE_POS_FORMAT'
    OBJET_ÉTIQUETTE_POS_ÉTENDU = 'OBJET_ÉTIQUETTE_POS_ÉTENDU'
    OBJET_ANCRE_FORMAT = 'OBJET_ANCRE_FORMAT'
    OBJET_ANCRE_ÉTENDU = 'OBJET_ANCRE_ÉTENDU'
    TOML_ENREGISTREMENT = 'TOML_ENREGISTREMENT'
    TOML_FORMAT = 'TOML_FORMAT'
    TOML_INACCESSIBLE = 'TOML_INACCESSIBLE'
    TOML_INVALIDE = 'TOML_INVALIDE'
    TOML_DONNÉES = 'TOML_DONNÉES'


    MESSAGES = {
        DIMENSIONS_LARGEUR_FORMAT: 'La largeur doit être un nombre réel positif.',
        DIMENSIONS_LARGEUR_NONPOSITIF: 'La largeur doit être un nombre réel positif.',
        DIMENSIONS_HAUTEUR_FORMAT: 'La hauteur doit être un nombre réel positif.',
        DIMENSIONS_HAUTEUR_NONPOSITIF: 'La hauteur doit être un nombre réel positif.',
        AXE_BORNES_MIN_FORMAT: 'La valeur minimale de la borne doit être un nombre réel.',
        AXE_BORNES_MAX_FORMAT: 'La valeur minimale de la borne doit être un nombre réel.',
        AXE_BORNES_VIDE: 'Les bornes inférieur et supérieur doivent être inégales.',
        AXE_DROITE_TYPE: 'Le type de droite est invalide.',
        AXE_PAS_FORMAT: 'Le pas doit être un nombre réel positif.',
        AXE_PAS_NONPOSITIF: 'Le pas doit être un nombre réel positif.',
        AXE_INTERPAS_FORMAT: 'L\'interpas doit être vide ou un nombre entier non-négatif.',
        AXE_INTERPAS_NÉGATIF: 'L\'interpas doit être vide ou un nombre entier non-négatif.',
        COULEUR_FORMAT: 'La couleur de l\'arrière plan est invalide.',
        AXE_COULEUR_FORMAT: 'La couleur de l\'axe est invalide.',
        AXE_GMAJEUR_COULEUR_FORMAT: 'La couleur de l\'axe majeur est invalide.',
        AXE_GMINEUR_COULEUR_FORMAT: 'La couleur de l\'axe mineur est invalide.',
        ANGLES_TYPE: 'Le type d\'angle est invalide.',
        OBJET_TYPE: 'Le type d\'objet est invalide.',
        OBJET_BORNES_MIN_FORMAT: 'La borne inférieure doit être vide ou un nombre réel.',
        OBJET_BORNES_MAX_FORMAT: 'La borne supérieure doit être vide ou un nombre réel.',
        OBJET_BORNES_VIDE: 'La borne supérieure doit être supérieure à la borne inférieure.',
        OBJET_POUVERTS_FORMAT: 'Les points ouverts doivent être une liste de nombres réels séparés par des points-virgules (;).',
        OBJET_POUVERTS_ITEM_FORMAT: 'Le point {item} doit être un nombre réel.',
        OBJET_PFERMÉS_FORMAT: 'Les points fermés doivent être une liste de nombres réels séparés par des points-virgules (;).',
        OBJET_PFERMÉS_ITEM_FORMAT: 'Le point {item} doit être un nombre réel.',
        OBJET_STYLE_TYPE: 'Le style est invalide.',
        OBJET_COULEUR_FORMAT: 'Le couleur est invalide.',
        OBJET_ÉTIQUETTE_POS_FORMAT: 'La position de l\'étiquette doit être un nombre réel entre 0 et 1, inclusivement.',
        OBJET_ÉTIQUETTE_POS_ÉTENDU: 'La position de l\'étiquette doit être un nombre réel entre 0 et 1, inclusivement.',
        OBJET_ANCRE_FORMAT: 'L\'ancre doit être vide ou un nombre réel entre -360 et 360, inclusivement.',
        OBJET_ANCRE_ÉTENDU: 'L\'ancre doit être vide ou un nombre réel entre -360 et 360, inclusivement.',
        TOML_ENREGISTREMENT: 'Une erreur s\'est produite.\n\n{erreur}',
        TOML_FORMAT: 'Le fichier « {fichier} » n\'est pas dans le bon format.\n\n{erreur}',
        TOML_INACCESSIBLE: 'Le fichier « {fichier} » est inaccessible.\n\n{erreur}',
        TOML_INVALIDE: 'Le fichier « {fichier} » est invalide.\n\n{erreur}',
        TOML_DONNÉES: 'Le fichier « {fichier} » contient des données invalides pour le champ « {champ} ».'
    }


    def __init__(self, id, **args):
        self.id = id
        self.args = args


    def __str__(self):
        return Erreur.MESSAGES[self.id].format(**self.args)


    def __repr__(self):
        return self.id
