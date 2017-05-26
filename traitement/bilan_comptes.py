from outils import Outils


class BilanComptes(object):
    """
    Classe pour la création du bilan des comptes
    """

    @staticmethod
    def bilan(dossier_destination, subedition, subgeneraux, lignes):
        """
        création du bilan
        :param dossier_destination: Une instance de la classe dossier.DossierDestination
        :param subedition: paramètres d'édition
        :param subgeneraux: paramètres généraux
        :param lignes: lignes de données du bilan
        """
        nom = "bilan-subsides-comptes_" + str(subedition.annee_fin) + "_" + Outils.mois_string(subedition.mois_fin)\
              + ".csv"

        with dossier_destination.writer(nom) as fichier_writer:

            ligne = ["année", "mois", "code client", "code client sap", "abrév. labo", "nom labo", "type client",
                     "nature client", "id-compte", "numéro compte", "intitulé compte", "code type compte",
                     "code type subside", "Subsides MAj", "Subsides MOj"]
            for categorie in subgeneraux.codes_d3():
                ligne.append("Subsides " + categorie + "j")
            ligne += ["total Subsides"]
            fichier_writer.writerow(ligne)

            for ligne in lignes:
                fichier_writer.writerow(ligne)

    @staticmethod
    def creation_lignes(subedition, subgeneraux, consolidation):
        """
        génération des lignes de données du bilan
        :param subedition: paramètres d'édition
        :param subgeneraux: paramètres généraux
        :param consolidation: classe de consolidation des données des bilans
        :return: lignes de données du bilan
        """
        lignes = []
        for code_client, client in sorted(consolidation.clients.items()):
            for num_compte, compte in sorted(client['comptes'].items()):
                ligne = [subedition.annee_fin, subedition.mois_fin, code_client, client['sap'], client['abrev'],
                         client['nom'], client['type'], client['nature'], compte['id_compte'], num_compte,
                         compte['intitule'], compte['type'], compte['t3'], Outils.format_2_dec(compte['s-mat']),
                         Outils.format_2_dec(compte['s-mot'])]
                for categorie in subgeneraux.codes_d3():
                    ligne.append(Outils.format_2_dec(compte['s-' + categorie + 't']))
                ligne += [Outils.format_2_dec(compte['subs'])]
                lignes.append(ligne)
        return lignes