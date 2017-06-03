from outils import Outils
from erreurs import ErreurConsistance


class SubEdition(object):
    """
    Classe pour l'importation des paramètres d'édition des Subsides
    """

    nom_fichier = "s-paramedit.csv"
    libelle = "Paramètres d'Edition des Subsides"

    def __init__(self, dossier_source):
        """
        initialisation et importation des données

        :param dossier_source: Une instance de la classe dossier.DossierSource
        """
        donnees_csv = []
        try:
            for ligne in dossier_source.reader(self.nom_fichier):
                donnees_csv.append(ligne)
        except IOError as e:
            Outils.fatal(e, "impossible d'ouvrir le fichier : " + SubEdition.nom_fichier)

        num = 3
        if len(donnees_csv) != num:
            Outils.fatal(ErreurConsistance(),
                         SubEdition.libelle + ": nombre de lignes incorrect : " +
                         str(len(donnees_csv)) + ", attendu : " + str(num))
        if len(donnees_csv[0]) != 3 and len(donnees_csv[1]) != 3:
            Outils.fatal(ErreurConsistance(), SubEdition.libelle + ": nombre de colonnes incorrect")
        try:
            self.annee_debut = int(donnees_csv[0][1])
            self.mois_debut = int(donnees_csv[0][2])
            self.annee_fin = int(donnees_csv[1][1])
            self.mois_fin = int(donnees_csv[1][2])
        except ValueError as e:
            Outils.fatal(e, SubEdition.libelle + "\nles mois et les années doivent être des nombres entiers")

        if self.annee_debut > self.annee_fin or self.annee_debut == self.annee_fin and self.mois_debut > self.mois_fin:
            Outils.fatal(ErreurConsistance(), SubEdition.libelle + ": la fin ne peut être avant le début")

        self.filigrane = donnees_csv[2][1]
