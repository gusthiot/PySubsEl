from outils import Outils


class Verification(object):
    """
    Classe servant à vérifier les dates et la cohérence de toutes les données importées
    """

    def __init__(self):
        """
        initialisation
        """
        self.a_verifier = 2

    def verification_date(self, bilans):
        """
        vérifie les dates de tous les bilans importés
        :param bilans: bilans importés
        :return: 0 si ok, sinon le nombre d'échecs à la vérification
        """
        verif = 0
        for bilan in bilans:
            verif += bilan.verification_date()
        self.a_verifier = 1
        return verif

    def verification_coherence(self, subgeneraux, subcomptes, submachines, subprestations, bilans):
        """
        vérifie la cohérence des données importées
        :param subgeneraux: paramètres généraux
        :param subcomptes: comptes subsides importés
        :param submachines: plafonds machines importées
        :param subprestations: plafonds prestations importées
        :param bilans: bilans importés
        :return: 0 si ok, sinon le nombre d'échecs à la vérification
        """
        verif = 0

        verif += subcomptes.est_coherent(subgeneraux)
        verif += submachines.est_coherent(subcomptes)
        verif += subprestations.est_coherent(subgeneraux, subcomptes)
        verif += self.coherence_bilans(bilans)
        self.a_verifier = 0
        return verif

    def coherence_bilans(self, bilans):
        coherence_clients = 0
        coherence_comptes = 0
        clients = {}

        for bilan in bilans:
            for donnee in bilan.donnees:
                client = donnee[bilan.cles['code client']]
                nature = donnee[bilan.cles['nature client']]
                type = donnee[bilan.cles['type client']]
                abrev = donnee[bilan.cles['abrév. labo']]
                compte = donnee[bilan.cles['id-compte']]
                numero = donnee[bilan.cles['numéro compte']]
                intitule = donnee[bilan.cles['intitulé compte']]
                code_type = donnee[bilan.cles['code type compte']]
                if client not in clients:
                    clients[client] = {'comptes': {}, 'nature': nature, 'type': type, 'abrev': abrev, 'coherent': True}
                else:
                    if nature != clients[client]['nature']:
                        clients[client]['coherent'] = False
                        coherence_clients +=1
                    if type != clients[client]['type']:
                        clients[client]['coherent'] = False
                        coherence_clients += 1

        if coherence_clients > 0:
            msg = "Les clients suivants ne sont pas homogènes sur la période, " \
                  "soit pour la nature du client soit pour le type du client : \n"
            for client in clients.keys():
                if not clients[client]['coherent']:
                    msg += " - " + client + "/" + clients[client]['abrev'] + "\n"
            Outils.affiche_message(msg)

        return coherence_clients + coherence_comptes
