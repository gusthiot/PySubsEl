from outils import Outils


class Subside(object):

    def __init__(self):
        self.clients = {}
        self.a_verifier = 1

    def coherence_bilans(self, bilans, subcomptes):
        coherence_clients = 0
        coherence_comptes = 0

        for bilan in bilans:
            for donnee in bilan.donnees:
                client = donnee[bilan.cles['code client']]
                nature = donnee[bilan.cles['nature client']]
                type = donnee[bilan.cles['type client']]
                abrev = donnee[bilan.cles['abrév. labo']]
                compte = donnee[bilan.cles['id-compte']]
                numero = donnee[bilan.cles['numéro compte']]
                intitule = donnee[bilan.cles['intitulé compte']]
                type_compte = donnee[bilan.cles['code type compte']]
                if client not in self.clients:
                    self.clients[client] = {'comptes': {}, 'nature': nature, 'type': type, 'abrev': abrev,
                                            'coherent': True}
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
                    if compte not in comptes:
                        comptes[compte] = {'id_sub': id_sub, 'numero':numero, 'intitule':intitule, 'coherent': True}
                    else:
                        if id_sub != comptes[compte]['id_sub']:
                            print(bilan.mois, bilan.annee, compte, id_sub, comptes[compte]['id_sub'])
                            comptes[compte]['coherent'] = False
                            coherence_comptes += 1

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




        self.a_verifier = 0
        return coherence_clients + coherence_comptes