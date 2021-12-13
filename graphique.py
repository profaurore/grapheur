RELATION_F_X = 'x'
RELATION_F_Y = 'y'
RELATION_XY_T = 't'

ANGLE_DEGRÉS = 'degrés'
ANGLE_RADIANS = 'radians'

AXE_FLÈCHE = '->'
AXE_LIGNE = '-'
AXE_CACHÉ = 'x'


class Graphique:
    def __init__(self):
        self.dimensions = (5, 5)
        self.grillage_ouvert = True
        self.angles = ANGLE_RADIANS
        self.couleur = (255, 255, 255)
        self.axes = (Axe('$x$'), Axe('$y$'))
        self.objets = []


    def __str__(self):
        champs = [
            f'{a}: {str(getattr(self, a))}'
            for a in dir(self)
            if not a.startswith('_') and not callable(getattr(self, a))
        ]
        return 'Graphique(' + ', '.join(champs) + ')'


    def __repr__(self):
        return self.__str__()


class Axe:
    def __init__(self, étiquette = ''):
        self.bornes = [-5, 5]
        self.étiquette = étiquette
        self.droite = AXE_FLÈCHE
        self.pas = 2
        self.interpas = 1
        self.grillage_majeur = True
        self.grillage_mineur = True
        self.couleur = (0, 0, 0)
        self.grillage_majeur_couleur = (191, 191, 191)
        self.grillage_mineur_couleur = (191, 191, 191)


    def __str__(self):
        return 'Axe(' + ', '.join([f'{a}: {str(getattr(self, a))}' for a in dir(self) if not a.startswith('_') and not callable(getattr(self, a))]) + ')'


    def __repr__(self):
        return self.__str__()


class Fonction:
    def __init__(self, type):
        self.type = type
        self.équation = [type, type] if type == RELATION_XY_T else type
        self.bornes = [0, 1] if type == RELATION_XY_T else [float('-inf'), float('inf')]
        self.points_ouverts = []
        self.points_fermés = []
        self.style = 'solid'
        self.couleur = (0, 0, 0)
        self.étiquette = ''
        self.position = 0.5
        self.ancre = None


    def __str__(self):
        return 'Fonction(' + ', '.join([f'{a}: {str(getattr(self, a))}' for a in dir(self) if not a.startswith('_') and not callable(getattr(self, a))]) + ')'


    def __repr__(self):
        return self.__str__()
