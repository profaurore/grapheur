import tkinter as tk
import tkinter.ttk as ttk
import tkinter.colorchooser as tkcolorchooser


def recherche_enfants(noeud, nom):
    liste = noeud.winfo_children()

    for item in liste:
        if item.winfo_name() == nom:
            return item

        enfants = item.winfo_children()
        if enfants:
            liste.extend(enfants)


class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        self.container = container

        # Objet de la toile et de la barre de défilement
        barre = ttk.Scrollbar(self, orient = 'vertical')
        barre.pack(side = 'right', fill = tk.Y, expand = False)
        self.toile = toile = tk.Canvas(self, bd = 0, highlightthickness = 0, yscrollcommand = barre.set)
        toile.pack(side = 'left', fill = tk.BOTH, expand = True)
        barre.configure(command = toile.yview)

        # Réinitialiser la vue
        toile.xview_moveto(0)
        toile.yview_moveto(0)

        # Créer le cadre qui contiendra le contenu à défiler
        self.intérieur = tk.Frame(toile, padx = 5, pady = 5)
        toile.create_window((0, 0), window = self.intérieur, tag = 'w', anchor = 'nw')

        # Gérer le redimensionnement
        self.redim = container.bind('<Configure>', lambda e: toile.itemconfig(toile.find_withtag('w')[0], width = container.winfo_width() - barre.winfo_reqwidth()))
        self.intérieur.bind('<Configure>', lambda _: toile.configure(scrollregion = toile.bbox(tk.ALL)))

        self.bind('<Enter>', lambda _: toile.bind_all('<MouseWheel>', lambda e: toile.yview_scroll(int(-1 * e.delta / 120), 'units')))
        self.bind('<Leave>', lambda _: toile.unbind_all('<MouseWheel>'))


    def haut(self):
        self.toile.yview_moveto(0)


    def destroy(self):
        self.container.unbind('<Configure>', self.redim)
        tk.Frame.destroy(self)


class ColorVar(tk.Variable):
    _default = (0, 0, 0)

    def __init__(self, master = None, value = None, name = None):
        if not isinstance(value, tuple) or len(value) != 3:
            raise ValueError('ColorVar value must be 3-item tuple')
        tk.Variable.__init__(self, master, ';'.join([str(x) for x in value]), name)

    def set(self, value):
        if not isinstance(value, tuple) or len(value) != 3:
            raise ValueError('ColorVar value must be 3-item tuple')
        tk.Variable.set(self, ';'.join([str(x) for x in value]))

    def get(self):
        value = self._tk.globalgetvar(self._name)
        if not isinstance(value, str):
            return self._default
        return tuple([int(x) for x in value.split(';')])


class ColorButton(tk.Button):
    def __init__(self, parent, *args, **kwargs):
        if 'command' in kwargs:
            self._command = kwargs['command']
            del kwargs['command']
        else:
            self._command = None

        if 'variable' in kwargs:
            if not isinstance(kwargs['variable'], ColorVar):
                raise ValueError('ColorButton error: -variables requires ColorVar.')
            self._variable = kwargs['variable']
            del kwargs['variable']
        else:
            self._variable = ColorVar()

        tk.Button.__init__(self, parent, *args, **kwargs)
        tk.Button.configure(self,
            command = self._choisi_couleur,
            background = ColorButton._couleur_hex(self._variable.get()),
            foreground = ColorButton._couleur_contraste(self._variable.get())
        )


    def config(self, **kw):
        self.configure(**kw)


    def configure(self, **kw):
        if 'command' in kw:
            self._command = kw['command']
            del kw['command']

        if 'variable' in kw:
            if not isinstance(kw['variable'], ColorVar):
                raise ValueError('ColorButton error: -variables requires ColorVar.')
            self._variable = kw['variable']
            del kw['variable']

        tk.Button.configure(self, **kw)


    def _choisi_couleur(self):
        c, _ = tkcolorchooser.askcolor(self._variable.get())
        if c is not None:
            c = tuple(int(x) for x in c)
            self._variable.set(c)
            self.configure(
                background = ColorButton._couleur_hex(c),
                foreground = ColorButton._couleur_contraste(c)
            )

            if self._command is not None:
                self._command()


    def _couleur_hex(rvb):
        return f'#{rvb[0]:02x}{rvb[1]:02x}{rvb[2]:02x}'


    def _couleur_contraste(rvb):
        if sum(rvb) < 3 * 255 / 2:
            return '#FFFFFF'
        else:
            return '#000000'


class OptionMenu(tk.OptionMenu):
    def __init__(self, master, variable, values, **kwargs):
        self.textvariable = variable

        values_inv = {v: k for k, v in values.items()}

        value = values[variable.get()]
        variable_false = tk.StringVar(value = value)
        variable_false.trace('w', lambda *_: self.textvariable.set(values_inv[variable_false.get()]))

        tk.OptionMenu.__init__(self, master, variable_false, value, *values.values(), **kwargs)


class CadreMéta(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.columnconfigure(0, weight = 1)
        self._erreur = tk.Label(self, pady = 1, justify = tk.LEFT, fg = '#dd0000')
        self._info = tk.Label(self, pady = 1, justify = tk.LEFT, fg = '#0000dd')
        self.bind('<Configure>', self.actualiser_retour)

        # Ceci est requis pour que le cadre se redimensionne s'il n'y a pas de messages.
        ttk.Separator(self).grid(column = 0, row = 2)


    def actualiser_retour(self, év):
        self._erreur.configure(wraplength = év.width)
        self._info.configure(wraplength = év.width)


    def définir_erreur(self, erreur = None):
        if erreur is None:
            self._erreur.configure(text = None)
            self._erreur.grid_forget()
        else:
            self._erreur.configure(text = erreur)
            self._erreur.grid(column = 0, row = 0, sticky = tk.W)


    def affiche_info(self, affiche):
        if affiche:
            self._info.grid(column = 0, row = 1, sticky = tk.W)
        else:
            self._info.grid_forget()


    def définir_info(self, info = None):
        if info is None:
            self._info.configure(text = None)
        else:
            self._info.configure(text = info)
