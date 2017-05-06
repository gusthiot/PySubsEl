from outils import Outils
from erreurs import ErreurConsistance
from collections import namedtuple

_champs_article = ["indice_d", "code_d", "intitule_long", "intitule_court"]
Article = namedtuple("Article", _champs_article)


class SubGeneraux(object):
    """
    Classe pour l'importation des paramètres généraux
    """

    nom_fichier = "s-paramgen.csv"
    libelle = "Paramètres Généraux"
    cles = ['financier', 'fonds', 'lien', 'lecture', 'sauvegarde', 'indice_t', 'code_t', 'code_n', 'indice_d', 'code_d',
            'intitule_long', 'intitule_court']

    def __init__(self, dossier_source):
        """
        initialisation et importation des données

        :param dossier_source: Une instance de la classe dossier.DossierSource
        """
        self._donnees = {}
        try:
            for ligne in dossier_source.reader(self.nom_fichier):
                cle = ligne.pop(0)
                if cle not in self.cles:
                    Outils.fatal(ErreurConsistance(),
                                 "Clé inconnue dans %s: %s" % (self.nom_fichier, cle))
                while "" in ligne:
                    ligne.remove("")
                self._donnees[cle] = ligne
        except IOError as e:
            Outils.fatal(e, "impossible d'ouvrir le fichier : "+SubGeneraux.nom_fichier)

        erreurs = ""
        for cle in self.cles:
            if cle not in self._donnees:
                erreurs += "\nClé manquante dans %s: %s" % (self.nom_fichier, cle)

        codes_n = []
        for nn in self._donnees['code_n'][1:]:
            if nn not in codes_n:
                codes_n.append(nn)
            else:
                erreurs += "le code N '" + nn + "' n'est pas unique\n"
        codes_t = []
        for tt in self._donnees['code_t'][1:]:
            if tt not in codes_t:
                codes_t.append(tt)
            else:
                erreurs += "le code T '" + tt + "' n'est pas unique\n"
        codes_d = []
        for dd in self._donnees['code_d'][1:]:
            if dd not in codes_d:
                codes_d.append(dd)
            else:
                erreurs += "le code D '" + dd + "' n'est pas unique\n"

        if (len(self._donnees['code_d']) != len(self._donnees['indice_d'])) or \
                (len(self._donnees['code_d']) != len(self._donnees['intitule_long'])) or \
                (len(self._donnees['code_d']) != len(self._donnees['intitule_court'])):
            erreurs += "le nombre de colonees doit être le même pour le code D, l'indice D, l'intitulé long" \
                       " et l'intitulé court\n"

        if erreurs != "":
            Outils.fatal(ErreurConsistance(), self.libelle + "\n" + erreurs)

    def obtenir_code_n(self):
        """
        retourne les codes N
        :return: codes N
        """
        return self._donnees['code_n'][1:]

    def obtenir_code_t(self):
        """
        retourne les codes T
        :return: codes T
        """
        return self._donnees['code_t'][1:]

    @property
    def articles(self):
        """renvoie la liste des articles de facturation.

        Le premier (coûts procédés machines)
        s'appelle "D2"; les suivants (en nombre variable) s'appellent "D3".

        :return: une liste ordonnée d'objets Article
        """
        if not hasattr(self, "_articles"):
            self._articles = []
            for i in range(1, len(self._donnees['code_d'])):
                kw = dict((k, self._donnees[k][i]) for k in _champs_article)
                self._articles.append(Article(**kw))
        return self._articles

    @property
    def articles_d3(self):
        """
        retourne uniquement les articles D3

        :return: une liste ordonnée d'objets Article
        """
        return self.articles[1:]

    def codes_d3(self):
        return [a.code_d for a in self.articles_d3]

def ajoute_accesseur_pour_valeur_unique(cls, nom, cle_csv=None):
    if cle_csv is None:
        cle_csv = nom

    def accesseur(self):
        return self._donnees[cle_csv][1]
    setattr(cls, nom, property(accesseur))

ajoute_accesseur_pour_valeur_unique(SubGeneraux, "financier")

for champ_valeur_unique in ('fonds', 'lien', 'lecture', 'sauvegarde'):
    ajoute_accesseur_pour_valeur_unique(SubGeneraux, champ_valeur_unique)
