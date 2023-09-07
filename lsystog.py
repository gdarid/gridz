"""
@author: GDA

Lindenmayer System (L-system) with a grid (and a subgrid, ...)

"""

import random as rnd
import numpy as np

from typing import Callable, Optional


# Tool functions
# ----------------------

def strc_2_array(chaine: str) -> list[list[str]]:
    """
    Donne le "tableau" (liste de listes) correspondant à une chaîne (de coloriage)

    !!! La couleur de fond n'est pas traitée

    En retour :
        le tableau résultat (voir decoupe_str pour la "shape" correspondante)

    Exemple :
        'RG_BY' ==> [['R','G'],['B','Y']]
    """

    # shape = decoupe_str(chaine)

    res = chaine.split('_')

    return [[elem for elem in ligne] for ligne in res]


def array_2_strc(tab: list[list[str]]) -> str:
    """
    Donne la chaîne (de coloriage) correspondant à un tableau

    En retour :
        la chaîne "de coloriage"

    Exemple :
        [['R','G'],['B','Y']] ==> 'RG_BY'
    """

    return '_'.join([''.join(ligne) for ligne in tab])


def strc_2_strc_90(chaine: str) -> str:
    """
    Donne la nouvelle chaîne (de coloriage) à partir d'une première chaîne
    en appliquant une rotation à 90° (sens horaire)

    !!! La couleur de fond n'est pas traitée

    fonction utilisable comme paramètre "func_transf"

    En retour :
        la chaîne résultat (de coloriage)

    Exemple :
        'RG_BY' ==> 'BR_YG'
    """

    tab = strc_2_array(chaine)

    # On inverse l'ordre des lignes
    tab.reverse()

    # On transpose
    tab_np = np.array(tab)
    tab_np = tab_np.T

    return array_2_strc(tab_np)


def func_alea_iter(seq: list, numalea: int) -> str:
    """
    Fonction de retour "aléatoire" sur la séquence seq en fonction de numalea

    cette fonction peut être utilisée en param "func_alea"

    Le choix dans seq se fait simplement en fonction de numalea (du 1 par 1 à base de modulo)

    Retour : un élément de seq
    """

    nb = len(seq)
    assert (nb > 0)

    return seq[numalea % nb]


# Classes
# ----------------------
class LsystError(Exception):
    """ Specific errors """
    def __init__(self, *args) -> None:
        super().__init__(*args)


class Lsystg:
    """
    L-Syst with grid colors
    """

    def __init__(self, axiom: str | None, rules, nbiter: int, func_transf: Optional[Callable] = None,
                 func_alea: Optional[Callable] = None, patterns: list[str] | None = None, colors: str | None = None,
                 banned_colors: str = '', nb_dest: int = 1, test: bool = False, verbose: bool = False,
                 rnd_seed: int = 123456789) -> None:
        self.axiom = axiom
        self.rules = rules
        self.nbiter = nbiter
        self.func_transf = func_transf
        self.func_alea = func_alea
        self.patterns = patterns
        self.colors = colors
        self.banned_colors = banned_colors
        self.nb_dest = nb_dest  # If nb_dest > 1 then it will be not deterministic
        self.test = test
        self.verbose = verbose
        self.rnd_seed = rnd_seed

        self.arbitrary_color = 'A'  # An arbitrary color (when a color is missing in input)
        self.sep2 = '_'
        self.x_basis, self.y_basis = 4, 4  # Numbers of pixels at lowest level
        self.max_result_size = 1500000  # Maximum size accepted for the result (the current algo uses too much space)

        self.dev_prf = ''

        if rnd_seed is not None:
            rnd.seed(rnd_seed)

        if patterns is None:
            # Use axiom and rules
            self.developpe_prf()
        else:
            # Use patterns to generate axiom and rules
            self.patterns = [pat.strip(" " + self.sep2) for pat in patterns if pat.strip(" " + self.sep2)]
            if not self.patterns:
                raise LsystError("The patterns are not valid")

            self.developpe_prf_patterns()

    # Static methods
    # --------------

    @staticmethod
    def x_y_tx_ty(pos: list[list[int]], niveaux, mmx: int, mmy: int) -> tuple[int, int, int, int]:
        """
        Retourne (x,y,tx,ty) à partir d'une "position", ...
            pos : [[lx, ly], ...] où lx, ly est la position locale pour chaque niveau
                la position locale de départ est 0, 0
            niveaux : les tailles des niveaux
            mmx, mmy : multiplicateurs pour tous les niveaux
        """

        x, y, tx, ty = 0, 0, niveaux[0][0], niveaux[0][1]

        if pos[-1][0] == -1:
            # Cas du fond : on remonte d'un niveau (on enlève le dernier niveau)
            tpos = pos[0:-1]
        else:
            # Cas du carré local
            tpos = pos

        for lniv, lpos in enumerate(tpos):
            tx = niveaux[lniv + 1][0]
            ty = niveaux[lniv + 1][1]
            x += lpos[0] * tx
            y += lpos[1] * ty

        return mmx * x, mmy * y, mmx * tx, mmy * ty

    def img_remplir(self, img, x: int, y: int, tx: int, ty: int, couleur: str) -> None:
        """
        Remplir une image avec un rectangle
            img : image du même type que PIL.ImageDraw.Draw
            x, y : x, y de départ
            tx, ty : taille en x, y
            couleur : couleur à appliquer (pour un mode RGBA)
        """

        tcouleur = couleur.upper()

        if tcouleur == self.arbitrary_color:
            # Dark gray
            pcoul = (10, 10, 10, 255)
        elif tcouleur == 'R':
            # Red
            pcoul = (255, 0, 0, 255)
        elif tcouleur == 'G':
            # "Green" ( lime in fact )
            pcoul = (0, 255, 0, 255)
        elif tcouleur == 'B':
            # Blue
            pcoul = (0, 0, 255, 255)
        elif tcouleur == 'W':
            # White
            pcoul = (255, 255, 255, 255)
        elif tcouleur == 'K':
            # Black
            pcoul = (0, 0, 0, 255)
        elif tcouleur == 'Y':
            # Yellow
            pcoul = (255, 255, 0, 255)
        elif tcouleur == 'M':
            # Magenta / Fuchsia
            pcoul = (255, 0, 255, 255)
        elif tcouleur == 'O':
            # Orange
            pcoul = (255, 165, 0, 255)
        elif tcouleur == 'P':
            # Purple
            pcoul = (128, 0, 128, 255)
        elif tcouleur == 'D':
            # Dim gray
            pcoul = (105, 105, 105, 255)
        elif tcouleur == '?':
            # Random color
            pcoul = (rnd.randint(0, 255), rnd.randint(0, 255), rnd.randint(0, 255), 255)
        elif tcouleur in self.banned_colors or tcouleur == 'T':
            # No color = Background color
            return
        elif tcouleur == 'F':
            # Forest green
            pcoul = (34, 139, 34, 255)
        elif tcouleur == 'N':
            # Navy
            pcoul = (0, 0, 128, 255)
        else:
            # No color = Background color
            return

        # img du même type que PIL.ImageDraw.Draw
        img.rectangle([(x, y), (x + tx - 1, y + ty - 1)], fill=pcoul, outline=None)

    @staticmethod
    def pattern_colors(pattern: str) -> list[str]:
        """
        Returns a sorted list of the colors of a pattern

        Example : '01_10' -> ['0','1']
        """

        res = list({lt for lt in pattern if lt.isdigit()})  # not (lt in ('&','_'))
        res.sort()

        return res

    # Normal methods
    # --------------
    def warning(self, msg: str) -> None:
        if self.verbose:
            print(msg)

    def error(self, msg: str) -> None:
        if self.verbose:
            print(msg)

        raise LsystError(msg)

    def img_remplir_gen(self, draw, lpos: list[list[int]], niveaux: list[tuple[int, int]],
                        mmx: int, mmy: int, car: str) -> None:
        """
        Remplir une image avec
            draw : image du même type que PIL.ImageDraw.Draw
            lpos : "position"
            niveaux : rappel des niveaux
            mmx, mmy : taille "atomique" en x, y
            car : couleur à appliquer (pour un mode RGBA)
        """

        self.img_remplir(draw, *Lsystg.x_y_tx_ty(lpos, niveaux, mmx, mmy), couleur=car)

    def decoupe_str(self, chaine: str) -> tuple[int, int]:
        """
        Donne la "découpe" d'une chaîne pour le "coloriage en quadrillage"

        En retour :

            (width,height) ou (multx,multy)

        Exemples (si sep2 == '_') :

        Cas classique
            'RGB_BGR' ===> (3,2)

        Cas où au début est définie une couleur de fond (les 2 premiers caractères sont à ignorer)
            '&BRG0_0GR' ===> (3,2)

        """

        if chaine[0] == '&':
            tchaine = chaine[2:]
        else:
            tchaine = chaine

        width = tchaine.find(self.sep2)
        if width == -1:
            width = len(tchaine)
        height = tchaine.count(self.sep2) + 1

        return width, height

    def developpe_unit_prf(self, chaine: str, li: int) -> tuple[str, tuple[int, int]]:
        """
        Développe un chaîne à partir d'une collection itérable de règles

            chaine : chaîne à transformer
            // regles : séquence des règles de remplacement
            li : numéro d'itération (dans 0 .. nbiter-1) -- pour func_transf
            // nbiter : nombre d'itérations maximal -- pour func_transf
            // func_transf : fonction éventuelle de transformation du motif à appliquer
                A faire autant de fois qu'il y a d'itérations (car les règles ne sont pas modifiées)

        Par rapport à `developpe_unit`,
            Le retour est étendu (un tuple ... au lieu d'une chaîne)
            On remplace avec '(' et ')' comme préfixe et suffixe

        Voir la fonction `developpe_prf` pour le detail d'une règle

        En retour :

            (resultat,ndecoupe) avec
                resultat : la chaîne transformée
                ndecoupe : la nouvelle "découpe" ajoutée (voir decoupe_str) ou None
        """
        resultat = chaine
        position = 0
        ndecoupe = None

        if self.func_alea is not None:
            from collections import Counter
            stockalea = Counter()
        else:
            stockalea = None

        while True:
            if len(resultat) > self.max_result_size:
                self.warning(f"The size limit is reached : {len(resultat)} > {self.max_result_size}")
                self.error("The result is over the accepted size limit ! The number of iterations may be too high ")

            # On recherche la plus "petite règle" (plus petite en position) à appliquer
            newpos = None
            lreg = -1
            for lr, regle in enumerate(self.rules):
                # regle :
                #      (chaine_depart, chaine_arrivee)
                #   OU (chaine_depart, liste_arrivee) avec liste_arrivee = [chaine_arrivee, ...]
                #   OU (arg1, arg2, fonction_filtre)

                if len(regle) >= 3:
                    lb_res = regle[2](li, self.nbiter)  # On vérifie que la règle peut être appliquée

                    if not lb_res:
                        continue

                lpos = resultat.find(regle[0], position)
                if lpos >= 0:
                    if newpos is None or lpos < newpos:
                        newpos = lpos
                        lreg = lr

            if newpos is None:
                break

            if isinstance(self.rules[lreg][1], str):
                # Chaîne
                nchaine = self.rules[lreg][1]
            else:
                # Pas chaîne : itérable de chaînes
                if self.func_alea is None:
                    nchaine = rnd.choice(self.rules[lreg][1])
                else:
                    stockalea[self.rules[lreg][0]] += 1
                    nchaine = self.func_alea(self.rules[lreg][1], stockalea[self.rules[lreg][0]] - 1)

            if ndecoupe is None:
                ndecoupe = self.decoupe_str(nchaine)

            if self.func_transf is not None:
                # On "transforme" le motif de destination (nchaine) avec func_transf
                for lni in range(li):
                    nchaine = self.func_transf(nchaine)

            nchaine = '(' + nchaine + ')'

            resultat = resultat[0:newpos] + resultat[newpos:].replace(self.rules[lreg][0], nchaine, 1)
            position = newpos + len(nchaine)

        if self.verbose:
            print(f"Resulting string with {len(resultat)} characters")
            print(f"First 50 characters : {resultat[:50]}")
            print(f"Last 50 characters : {resultat[-50:]}")

        return resultat, ndecoupe

    def developpe_prf(self) -> list:
        """
        Développe un axiome à partir d'une collection itérable de règles, sur nbiter itérations

        Ce développement se fait "en profondeur" (prf) avec conservation des niveaux,
        pour la possibilité de quadrillage

        L'ordre des règles important

        Une règle est un couple (depart, arrivee) où `depart` est la chaîne à remplacer par `arrivee`

        OU

        Une règle est un triplet (depart, arrivee, fonc) où
            ...

            fonc est une fonction de 2 paramètres (numiter, nbiter) qui renvoit un booléen

                numiter correspond au numéro d'itération
                nbiter ... nombre total d'itération

            La règle ne sera appliquée que si fonc renvoit True

        Voir aussi la fonction developpe

        En retour :

            [chaine,niveaux] avec `chaine` la chaîne résultante et `niveaux` la liste des niveaux

                niveaux = [(multx, multy), ...]

        """

        niveaux = []

        if '(' in self.axiom or ')' in self.axiom:
            self.error(f"Axiom with '(' or ')'")

        if self.sep2 in self.axiom:
            niveaux.append(self.decoupe_str(self.axiom))

            # A chaque niveau doit correspondre un couple '(', ')'
            source = '(' + self.axiom + ')'
        else:
            source = self.axiom

        resultat = source

        for li in range(self.nbiter):
            resultat, ndecoupe = self.developpe_unit_prf(resultat, li)
            if ndecoupe:
                niveaux.append(ndecoupe)

        # La valeur de retour est une liste pour avoir la possibilité de modification
        self.dev_prf = [resultat, niveaux]
        return self.dev_prf

    def developpe_prf_patterns(self) -> list:
        """
        This method generates an axiom and some rules from s.patterns, s.colors, s.banned_colors (s = self)
        """

        nb_motif = len(self.patterns)
        nb_coul = len(self.colors)

        if nb_motif == 0:
            self.error("There is no valid pattern")

        if nb_coul == 0:
            self.error("There is no valid color")

        self.axiom = self.colors[0]  # # The axiom is simply the first color

        possible_col = [coul for coul in self.colors if coul not in self.banned_colors]
        nb_possible = len(possible_col)

        if nb_possible == 0:
            self.error("There is no valid usable color")

        self.rules = []

        for lic, coul in enumerate(self.colors):

            motif = self.patterns[lic % nb_motif]  # % ... : Cycle over patterns

            coulm = Lsystg.pattern_colors(motif)
            nb_coulm = len(coulm)

            n_possible_col = possible_col
            n_nb_possible = nb_possible

            # assert (nb_possible >= nb_coulm)  # This former necessary condition is treated below
            if nb_possible < nb_coulm:
                # Fill n_possible_col with an arbitrary color
                for ll_new in range(nb_coulm - nb_possible):
                    n_possible_col.append(self.arbitrary_color)
                n_nb_possible = nb_coulm

            if coul in coulm:
                self.error("This is not a possible case")

            # Définir la règle pour motif, couleur
            cont_dest = []
            motif_dest = None

            for lidest in range(self.nb_dest):

                motif_dest = motif

                for lie, elem_motif in enumerate(coulm):
                    # % ... : Cycle over n_possible_col
                    motif_dest = motif_dest.replace(elem_motif,
                                                    n_possible_col[(lidest + lic + lie) % n_nb_possible])  # 1 +

                cont_dest.append(motif_dest)

            if self.nb_dest == 1:
                self.rules.append((coul, motif_dest))
            else:
                # Several destinations ( nb_dest > 1 ) so it will be not deterministic
                self.rules.append((coul, cont_dest))

        self.warning(f'Rules for {self.patterns} and {self.colors} : {self.rules} ')

        if self.test:
            return ['Mode test', self.rules]

        return self.developpe_prf()

    def img(self, img_fpath: str, func_img: Optional[Callable] = None,
            col_fond: tuple[int, int, int, int] = (0, 0, 0, 0)):
        """
        Sauvegarde l'image "contenue" dans `dev_prf` dans `img_fpath` (chemin)

            // dev_prf : même type qu'un retour de `developpe_prf`
            img_fpath : chemin - Exemple : "images/test.png" ou "" pour un stockage mémoire, seulement
            func_img (opt) : fonction de traitement de l'image avant sauvegarde
            col_fond : couleur de fond - (0,0,0,0) pour un fond transparent

        Retour :
            Image obtenue
        """

        if not isinstance(self.dev_prf, list):
            self.error('dev_prf is not usable in img_decoupe : test mode ?')

        chaine, niveaux = self.dev_prf
        nbniv = len(niveaux)
        if nbniv == 0:
            self.error('There is no level')

        niveaux = niveaux[:]  # Une copie pour ne pas modifier dev_prf
        niveaux.append((1, 1))  # Un ajout qui sert à x_y_tx_ty(...)

        # Définir les détails des niveaux
        # On modifie `niveaux` pour avoir des tailles (global) au lieu des multiplicateurs (local)
        mx, my = 1, 1

        for lniv in reversed(range(nbniv)):
            mx = mx * niveaux[lniv][0]
            my = my * niveaux[lniv][1]
            niveaux[lniv] = (mx, my)

        # Définir les nombres de pixels de base (pour "agrandir" l'image)
        mmx, mmy = self.x_basis, self.y_basis

        # Créer l'image
        from PIL import Image as pim, ImageDraw

        tx, ty = mmx * niveaux[0][0], mmy * niveaux[0][1]

        imgn = pim.new("RGBA", (tx, ty), color=col_fond)
        draw = ImageDraw.Draw(imgn)  # Pour accéder à imgn en mode "draw"

        # Parcourir la chaîne pour remplir l'image
        lpos = []  # La position locale est une liste [[lx, ly], ...]
        lbfond = False

        # Exemple de chaîne : '((KW_WK)W_W(KW_WK))' avec niveaux = [(4,4),(2,2),(1,1)]
        # Autre exemple de chaîne avec fond précisé : '(&G(W/_/W)/_/(W/_/W))' avec niveaux = [(4,4),(2,2),(1,1)]
        for car in chaine:
            if car == '(':
                if lpos:
                    lpos[-1][0] += 1
                lpos.append([-1, 0])
            elif car == ')':
                lpos.pop()
            elif car == '_':
                lpos[-1][0] = -1
                lpos[-1][1] += 1
            elif car == '&':
                # Couleur de fond à venir
                lbfond = True
            else:
                # Un caractère de couleur à traiter
                if lbfond:
                    # Pour le fond ( on a normalement : lpos[-1][0] = -1 )
                    self.img_remplir_gen(draw, lpos, niveaux, mmx, mmy, car)

                else:
                    # Pour le carré local
                    lpos[-1][0] += 1

                    self.img_remplir_gen(draw, lpos, niveaux, mmx, mmy, car)

                lbfond = False

        # Pour finir
        if func_img is not None:
            imgn = func_img(imgn)

        if img_fpath:
            imgn.save(img_fpath)

        # Retour de l'image obtenue
        return imgn
