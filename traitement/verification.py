

class Verification(object):
    """
    Classe servant à vérifier les dates et la cohérence de toutes les données importées
    """

    def __init__(self):
        """
        initialisation
        """
        self.a_verifier = 1

    def verification_cohérence(self, subgeneraux, subcomptes, submachines, subprestations):
        """
        vérifie la cohérence des données importées
        :param subgeneraux: paramètres généraux
        :param subcomptes: comptes subsides importés
        :param submachines: plafonds machines importées
        :param subprestations: plafonds prestations importées
        :return: 0 si ok, sinon le nombre d'échecs à la vérification
        """
        verif = 0

        verif += subcomptes.est_coherent(subgeneraux)
        verif += submachines.est_coherent(subcomptes)
        verif += subprestations.est_coherent(subgeneraux, subcomptes)

        self.a_verifier = 0
        return verif
