LATEX = r'''
\documentclass[12pt]{standalone}
\usepackage{pgfplots}
\pgfplotsset{compat=1.17}
\usepackage{xcolor}
\usepackage{etoolbox}
\usepgflibrary{arrows.meta}
\usetikzlibrary{backgrounds}

% Paramètres
___VARIABLES___

\pgfmathsetmacro{\ymaxfn}{\ymax + 2 * (\ymax - \ymin)}
\pgfmathsetmacro{\yminfn}{\ymin - 2 * (\ymax - \ymin)}
\newcommand\objets{
    \foreach \i in {1, ..., 999} {
        \ifcsname objet\romannumeral\i equation\endcsname
            \expandafter\newcommand\csname objet\romannumeral\i domaine\endcsname{\xmin:\xmax}
            \expandafter\edef\csname objet\romannumeral\i domaine\endcsname{\ifcsempty{objet\romannumeral\i domainemin}{\xmin - 1}{\csname objet\romannumeral\i domainemin\endcsname}:\ifcsempty{objet\romannumeral\i domainemax}{\xmax + 1}{\csname objet\romannumeral\i domainemax\endcsname}}

            \edef\temp{
                \ifcsstring{objet\romannumeral\i type}{x}{
                    \noexpand\addplot[domain = \csname objet\romannumeral\i domaine\endcsname, restrict y to domain = \yminfn:\ymaxfn, \csname objet\romannumeral\i style\endcsname, objet\romannumeral\i couleur] {\csname objet\romannumeral\i equation\endcsname}
                        node[anchor = \csname objet\romannumeral\i etiquetterel\endcsname, pos=\csname objet\romannumeral\i etiquettepos\endcsname, overlay] {\csname objet\romannumeral\i etiquette\endcsname};
                }{}
                \ifcsstring{objet\romannumeral\i type}{y}{
                    \noexpand\addplot[variable = y, variable y = x, domain = \csname objet\romannumeral\i domaine\endcsname, restrict y to domain = \yminfn:\ymaxfn, \csname objet\romannumeral\i style\endcsname, objet\romannumeral\i couleur] ({\csname objet\romannumeral\i equation\endcsname}, {y})
                        node[anchor = \csname objet\romannumeral\i etiquetterel\endcsname, pos=\csname objet\romannumeral\i etiquettepos\endcsname, overlay] {\csname objet\romannumeral\i etiquette\endcsname};
                }{}
                \ifcsstring{objet\romannumeral\i type}{t}{
                    \noexpand\addplot[variable = t, domain = \csname objet\romannumeral\i domaine\endcsname, \csname objet\romannumeral\i style\endcsname, objet\romannumeral\i couleur] (\csname objet\romannumeral\i equation\endcsname)
                        node[anchor = \csname objet\romannumeral\i etiquetterel\endcsname, pos=\csname objet\romannumeral\i etiquettepos\endcsname, overlay] {\csname objet\romannumeral\i etiquette\endcsname};
                }{
                    \ifcsempty{objet\romannumeral\i cerclesfermes}{}{
                        \noexpand\addplot[only marks, mark = *, mark options = {fill = white}, domain = \xmin:\xmax, restrict y to domain = \ymin:\ymax, objet\romannumeral\i couleur, samples at = {\csname objet\romannumeral\i cerclesouverts\endcsname}]  {\csname objet\romannumeral\i equation\endcsname};
                    }
                    \ifcsvoid{objet\romannumeral\i cerclesouverts}{}{
                        \noexpand\addplot[only marks, mark = *, domain = \xmin:\xmax, restrict y to domain = \ymin:\ymax, objet\romannumeral\i couleur, samples at = {\csname objet\romannumeral\i cerclesfermes\endcsname}]  {\csname objet\romannumeral\i equation\endcsname};
                    }
                }

            }
            \temp
        \else
            \breakforeach
        \fi
    }
}

\tikzset{
    avec flèche/.style={
        -{Stealth[scale = 1.5]}
    },
%
    sans flèche/.style={
        -
    }
}

\pagecolor{plancouleur}
\ifdefstring{\axex}{true}{
    \pgfplotsset{axexvisibilite/.style = }
}{
    \pgfplotsset{axexvisibilite/.style = {
        x axis line style = {opacity = 0},
        xticklabel style = {opacity = 0},
        xtick style = {opacity = 0},
        xlabel style = {opacity = 0}
    }}
    \pgfplotsset{
        extra y ticks = {0},
        extra y tick style = {
            grid = major
        }
    }
}
\ifdefstring{\axey}{true}{
    \pgfplotsset{axeyvisibilite/.style = }
}{
    \pgfplotsset{axeyvisibilite/.style = {
        y axis line style = {opacity = 0},
        yticklabel style = {opacity = 0},
        ytick style = {opacity = 0},
        ylabel style = {opacity = 0}
    }}
    \pgfplotsset{
        extra x ticks = {0},
        extra x tick style = {
            grid = major
        }
    }
}
\ifdefstring{\xdir}{normal}{
    \pgfplotsset{xdir/.style = { x dir = normal }}
}{
    \pgfplotsset{xdir/.style = {
        x dir = reverse,
        x label style = { anchor = south west, at = {(current axis.west)} }
    }}
}
\ifdefstring{\ydir}{normal}{
    \pgfplotsset{ydir/.style = { y dir = normal }}
}{
    \pgfplotsset{ydir/.style = {
        y dir = reverse,
        y label style = { anchor = south west, at = {(current axis.south)} }
    }}
}
\ifdefstring{\grillageouvert}{true}{
    \edef\xminajuste{\xmin + \valeursxdistance / \valeursxmineur / 10}
    \edef\xmaxajuste{\xmax + -\valeursxdistance / \valeursxmineur / 10}
    \edef\yminajuste{\ymin + \valeursydistance / \valeursymineur / 10}
    \edef\ymaxajuste{\ymax + -\valeursydistance / \valeursymineur / 10}
}{
    \edef\xminajuste{\xmin}
    \edef\xmaxajuste{\xmax}
    \edef\yminajuste{\ymin}
    \edef\ymaxajuste{\ymax}
}
\pgfplotsset{
    compat=newest,
%
    graphique/.style={
%
        %%% GÉNÉRAL
%
        % Angles (rad ou deg)
        trig format plots = \angles,
%
        %%% GRILLAGE
%
        % Exlus les éléments à l'extérieur du grillage pour
        % les dimensions
        scale only axis,
%
        % Rendre le grillage mineur, majeur ou les deux
        xminorgrids = \grillagexmineur,
        xmajorgrids = \grillagexmajeur,
        yminorgrids = \grillageymineur,
        ymajorgrids = \grillageymajeur,
%
        % Style des grillages
        major x grid style = { thin, grillagexmajeurcouleur },
        minor x grid style = { thin, grillagexmineurcouleur },
        major y grid style = { thin, grillageymajeurcouleur },
        minor y grid style = { thin, grillageymineurcouleur },
%
        % Dimensions du grillage
        width = \largeur,
        height = \hauteur,
%
        % Bornes du grillage
        xmin = \xminajuste,
        xmax = \xmaxajuste,
        ymin = \yminajuste,
        ymax = \ymaxajuste,
%
        % Préserve la taille des échelles si les bornes ne
        % sont pas définies
        unit rescale keep size = unless limits declared,
%
        % Étire les axes pour combler l'espace
        scale mode = stretch to fill,
%
        % Empêche le changement des bornes pour combler
        % l'espace
        enlargelimits = false,
%
        %%% AXES
%
        % Positionne les axes au zéro
        axis lines = center,
%
        % Style graphique des axes
        x axis line style = { thick, axexcouleur, \axexstyle },
        axexvisibilite,
        y axis line style = { thick, axeycouleur, \axeystyle },
        axeyvisibilite,
%
        %%% ÉCHELLES
%
        % Nombre d'unités entre les valeurs sur le grillage
        % majeur
        xtick distance = \valeursxdistance,
        ytick distance = \valeursydistance,
%
        % Nombre de lignes mineures dans le grillage majeur
        minor x tick num = \valeursxmineur,
        minor y tick num = \valeursymineur,
%
        % Empêche de factoriser un facteur commun pour les grands nombres.
        scaled ticks = false,
%
        % Style des marques pour les valeurs sur les axes.
        xtick style = { thin, axexcouleur },
        ytick style = { thin, axeycouleur },
%
        %%% ÉTIQUETTES
%
        % Texte
        xlabel = \axexetiquette,
        ylabel = \axeyetiquette,
%
        %%% FONCTIONS
%
        % Nombre de valeurs utilisées pour dessiner les
        % fonctions
        samples = 1000,
%
        % Épaisseur des lignes des fonctions
        thick,
%
        % Direction des axes
        xdir,
        ydir,
        % trim axis right, ???
    },
%
    graphique sans valeurs/.style={
        graphique,
        grid = none,
        xtick = \empty,
        ytick = \empty
    },
%
    graphique sans plan/.style={
        graphique sans valeurs,
        axis line style = {opacity = 0}
    },
%
    droite numérique/.style={
        scale only axis,
        unit rescale keep size = unless limits declared,
        scale mode = scale uniformly,
        scale uniformly strategy = change vertical limits,
        minor tick length = \pgfkeysvalueof{/pgfplots/major tick length},
        axis x line = center,
        axis y line = none,
        axis line style = {-{Stealth[scale = 1.5]}},
        ymin = -1, ymax = 1,
        height = 50pt,
        thick
    },
%
    droite numérique y/.style={
        scale only axis,
        unit rescale keep size = unless limits declared,
        scale mode = scale uniformly,
        scale uniformly strategy = change vertical limits,
        minor tick length = \pgfkeysvalueof{/pgfplots/major tick length},
        axis x line = none,
        axis y line = center,
        axis line style = {-{Stealth[scale = 1.5]}},
        xmin = -1, xmax = 1,
        width = 50pt,
        thick
    }
}

\begin{document}
\begin{tikzpicture}
\begin{axis}[
    graphique
]
\objets
\end{axis}
\end{tikzpicture}
\end{document}
'''