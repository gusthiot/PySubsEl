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
                id_compte = donnee[bilan.cles['id-compte']]
                num_compte = donnee[bilan.cles['numéro compte']]
                intitule = donnee[bilan.cles['intitulé compte']]
                if force and id_compte in force.obtenir_comptes():
                    type_compte = force.obtenir_comptes()[id_compte]
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
                    try:
                        bj = float(donnee[bilan.cles['bonus']])
                        maj = float(donnee[bilan.cles['maj']])
                        moj = float(donnee[bilan.cles['moj']])
                    except ValueError:
                        Outils.affiche_message("Certaines valeurs (maj, moj, bonus) ne sont pas des nombres")
                        return 1
                    mois = {'bj': bj, 'maj': maj, 'moj': moj}
                    for d3 in subgeneraux.codes_d3():
                        try:
                            j = float(donnee[bilan.cles[d3 + 'j']])
                        except ValueError:
                            Outils.affiche_message("Certaines valeurs d3 ne sont pas des nombres")
                            return 1
                        mois[d3 + 'j'] = j
                    if num_compte not in comptes:
                        annees = {bilan.annee: {'mois': {bilan.mois: mois}}}
                        type_s = subgeneraux.article_t3(subcomptes.donnees[id_sub]['type_subside']).texte_t_court
                        comptes[num_compte] = {'id_sub': id_sub, 'id_compte': id_compte, 'intitule': intitule,
                                               'type_p': subcomptes.donnees[id_sub]['intitule'], 'type': type_compte,
                                               'type_s': type_s, 'coherent': True,
                                               'annees': annees}
                    else:
                        if id_sub != comptes[num_compte]['id_sub']:
                            comptes[num_compte]['coherent'] = False
                            coherence_comptes += 1
                        if bilan.annee in comptes[num_compte]['annees']:
                            comptes[num_compte]['annees'][bilan.annee]['mois'][bilan.mois] = mois
                        else:
                            comptes[num_compte]['annees'][bilan.annee] = {'mois': {bilan.mois: mois}}

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

        if reponse == 0:
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

    def calcul_sommes(self, subgeneraux, submachines, subprestations):
        for cl, client in self.clients.items():
            client['subs'] = 0
            for co, compte in client['comptes'].items():
                compte['mat'] = 0
                compte['mot'] = 0
                for d3 in subgeneraux.codes_d3():
                    compte[d3 + 't'] = 0
                for a, annee in compte['annees'].items():
                    for m, mois in annee['mois'].items():
                        compte['mat'] += mois['maj']
                        compte['mot'] += mois['moj']
                        for d3 in subgeneraux.codes_d3():
                            compte[d3 + 't'] += mois[d3 + 'j']
                compte['s-mat'] = min(compte['mat'], submachines.donnees[compte['id_sub']]['max_ma'])
                compte['s-mot'] = min(compte['mot'], submachines.donnees[compte['id_sub']]['max_mo'])
                compte['subs'] = compte['s-mat'] + compte['s-mot']
                for d3 in subgeneraux.codes_d3():
                    compte['s-' + d3 + 't'] = min(compte[d3 + 't'], subprestations.donnees[compte['id_sub']+d3]['max'])
                    compte['subs'] += compte['s-' + d3 + 't']
                client['subs'] += compte['subs']
