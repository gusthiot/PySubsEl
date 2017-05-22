from outils import Outils


class Consolidation(object):
    """
    Classe servant à consolider les données des bilans
    """

    def __init__(self):
        self.clients = {}
        self.a_verifier = 1

    def coherence_bilans(self, bilans, subcomptes, subgeneraux, force):
        """
        vérifie que les données importées dans les bilan soit cohérentes, et construit la base consolidée
        :param bilans: bilans importés
        :param subcomptes: comptes subsides importés
        :param subgeneraux: paramètres généraux
        :param force: comptes forcés importés
        :return: > 0 s'il y a une erreur, 0 sinon
        """
        coherence_clients = 0
        coherence_comptes = 0

        for bilan in reversed(bilans):
            for donnee in bilan.donnees:
                client = donnee[bilan.cles['code client']]
                sap = donnee[bilan.cles['code client sap']]
                nature = donnee[bilan.cles['nature client']]
                type = donnee[bilan.cles['type client']]
                abrev = donnee[bilan.cles['abrév. labo']]
                nom = donnee[bilan.cles['nom labo']]
                compte = donnee[bilan.cles['id-compte']]
                numero = donnee[bilan.cles['numéro compte']]
                intitule = donnee[bilan.cles['intitulé compte']]
                if force and compte in force.obtenir_comptes():
                    type_compte = force.obtenir_comptes()[compte]
                else:
                    type_compte = donnee[bilan.cles['code type compte']]
                if client not in self.clients:
                    self.clients[client] = {'comptes': {}, 'nature': nature, 'type': type, 'abrev': abrev, 'sap': sap,
                                            'coherent': True, 'nom': nom}
                else:
                    if nature != self.clients[client]['nature']:
                        self.clients[client]['coherent'] = False
                        coherence_clients +=1
                    if type != self.clients[client]['type']:
                        self.clients[client]['coherent'] = False
                        coherence_clients += 1
                comptes = self.clients[client]['comptes']
                id_sub = subcomptes.obtenir_id(nature, type_compte)
                if id_sub:
                    mois = {'bj': donnee[bilan.cles['bonus']], 'maj': donnee[bilan.cles['maj']],
                            'moj': donnee[bilan.cles['moj']]}
                    for d3 in subgeneraux.codes_d3():
                        mois[d3 + 'j'] = donnee[bilan.cles[d3 + 'j']]
                    if compte not in comptes:
                        annees = {bilan.annee: {'mois': {bilan.mois: mois}}}
                        comptes[compte] = {'id_sub': id_sub, 'numero':numero, 'intitule':intitule, 'coherent': True,
                                           'annees': annees}
                    else:
                        if id_sub != comptes[compte]['id_sub']:
                            comptes[compte]['coherent'] = False
                            coherence_comptes += 1
                        if bilan.annee in comptes[compte]['annees']:
                            comptes[compte]['annees'][bilan.annee]['mois'][bilan.mois] = mois
                        else:
                            comptes[compte]['annees'][bilan.annee] = {'mois': {bilan.mois: mois}}

        if coherence_clients > 0:
            msg = "Les clients suivants ne sont pas homogènes sur la période, " \
                  "soit pour la nature du client soit pour le type du client : \n"
            for k, v in self.clients.items():
                if not v['coherent']:
                    msg += " - " + k + "/" + v['abrev'] + "\n"
            Outils.affiche_message(msg)

        if coherence_comptes > 0:
            msg = "Les comptes suivants ne sont pas homogènes sur la période, " \
                  "soit pour la nature du client soit pour le code type compte : \n"
            for k, v in self.clients.items():
                for l, w in v['comptes'].items():
                    if not w['coherent']:
                        msg += " - " + k + "/" + v['abrev'] + "/" + l + "/" + w['numero'] + "/" + w['intitule'] + "\n"
            Outils.affiche_message(msg)

        reponse = coherence_clients + coherence_comptes
        self.a_verifier = 0

        if reponse > 0:
            a_effacer = []
            for k, v in self.clients.items():
                if len(v['comptes']) == 0:
                    a_effacer.append(k)
                    continue
                del v['coherent']
                for l, w in v['comptes'].items():
                    del w['coherent']
            for k in a_effacer:
                del self.clients[k]

        return reponse