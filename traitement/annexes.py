from outils import Outils
from latex import Latex


class Annexes(object):
    """
    Classe pour la création des annexes
    """
    @staticmethod
    def annexes(consolidation, plateforme, subgeneraux, subedition, dossier_annexe):
        """
        création des annexes de subsides
        """
        for code_client, dcl in consolidation.clients.items():
            code_client = Latex.echappe_caracteres(code_client)

            contenu = Latex.entete(plateforme)
            contenu += r'''
                \usepackage[margin=10mm, includehead]{geometry}
                \usepackage{changepage}
                \usepackage{graphicx}
                \usepackage{longtable}
                \usepackage{dcolumn}
                \usepackage[scriptsize]{caption}
                '''

            contenu += r'''
                \begin{document}
                \renewcommand{\arraystretch}{1.5}
                '''
            reference = "SUBS" + str(subedition.annee_fin)[2:] + Outils.mois_string(subedition.mois_fin) + "." + \
                        code_client

            contenu += r'''
                \begin{titlepage}
                \vspace*{8cm}
                \begin{adjustwidth}{5cm}{}
                \Large\textsc{Annexes subsides \newline Subsidies Appendices}\newline
                \Large\textsc{''' + reference + r'''}\newline\newline\newline
                '''

            dic_entete = {'code': code_client, 'code_sap': Latex.echappe_caracteres(dcl['sap']),
                          'nom': Latex.echappe_caracteres(dcl['abrev']),
                          'debut': str(subedition.mois_debut) + " " + str(subedition.annee_debut),
                          'fin': str(subedition.mois_fin) + " " + str(subedition.annee_fin)}

            contenu += r'''Client %(code)s - %(code_sap)s - %(nom)s \newline
                 %(debut)s - %(fin)s
                \end{adjustwidth}
                \end{titlepage}    
                \clearpage
                ''' % dic_entete
            contenu += Annexes.contenu_client(code_client, consolidation, subgeneraux, subedition)
            contenu += r'''\end{document}'''

            nom = "subside_" + str(subedition.annee_fin) + "_" + Outils.mois_string(subedition.mois_fin) + "_" + \
                  code_client

            Latex.creer_latex_pdf(nom, contenu, dossier_annexe)

    @staticmethod
    def contenu_client(code_client, consolidation, subgeneraux, subedition):
        """
        création du contenu de l'annexe pour un client
        :param code_client: code du client pour l'annexe
        """

        contenu = ""

        client = consolidation.clients[code_client]
        reference = "SUBS" + str(subedition.annee_fin)[2:] + Outils.mois_string(subedition.mois_fin) + "." + code_client

        contenu_recap_compte = ""
        contenu_detail_compte = ""
        inc_4 = 0
        taille_d3 = len(subgeneraux.articles_d3)

        for num_compte, compte in sorted(client['comptes'].items()):

            # ## COMPTE

            # ## ligne 3
            if compte['subs'] > 0:
                dico_recap_compte = {'numero': num_compte, 'intitule': compte['intitule'], 'code': compte['id_sub'],
                                     'type_s': compte['type_s'], 'type_p': compte['type_p'],
                                     'montant': Outils.format_2_dec(compte['subs'])}
                contenu_recap_compte += r'''
                    %(numero)s & %(intitule)s & %(code)s & %(type_s)s & %(type_p)s & %(montant)s \\
                    \hline
                      ''' % dico_recap_compte

            # ## 4

            dico_detail_compte = {'taille': (4 + taille_d3), 'numero': num_compte,
                                  'intitule': compte['intitule'], 'type': compte['type']}
            if inc_4 > 0:
                contenu_detail_compte += r'''
                    \multicolumn{%(taille)s}{c}{} \\ \noalign{\penalty-5000}
                      ''' % dico_detail_compte
            else:
                inc_4 = 1
            contenu_detail_compte += r'''
                \hline
                \multicolumn{%(taille)s}{|c|}{%(numero)s - %(intitule)s - %(type)s} \\*
                \hline
                Année & Mois & Machine & M.O. op. 
                  ''' % dico_detail_compte

            for article in subgeneraux.articles_d3:
                contenu_detail_compte += r''' &
                ''' + Latex.echappe_caracteres(article.intitule_court)

            for a, annee in sorted(compte['annees'].items()):
                for m, mois in sorted(annee['mois'].items()):
                    dico = {'annee': a, 'mois': m, 'maj': Outils.format_2_dec(mois['maj']),
                            'moj': Outils.format_2_dec(mois['moj'])}
                    contenu_detail_compte += r'''\\*
                        \hline
                        %(annee)s & %(mois)s & %(maj)s & %(moj)s
                        ''' % dico
                    for d3 in subgeneraux.codes_d3():
                        contenu_detail_compte += r''' & ''' + Outils.format_2_dec(mois[d3 + 'j'])

            dico_detail_compte = {'mat': Outils.format_2_dec(compte['mat']), 'mot': Outils.format_2_dec(compte['mot'])}

            contenu_detail_compte += r'''\\*
                \hline
                \multicolumn{2}{|c|}{Total période} & %(mat)s & %(mot)s
                ''' % dico_detail_compte
            for d3 in subgeneraux.codes_d3():
                contenu_detail_compte += r''' &
                ''' + Outils.format_2_dec(compte[d3 + 't'])

            dico_detail_compte = {'s-mat': Outils.format_2_dec(compte['s-mat']),
                                  's-mot': Outils.format_2_dec(compte['s-mot'])}

            contenu_detail_compte += r'''\\*
                \hline
                \multicolumn{2}{|c|}{Subsides} & %(s-mat)s & %(s-mot)s
                ''' % dico_detail_compte
            for d3 in subgeneraux.codes_d3():
                contenu_detail_compte += r''' &
                ''' + Outils.format_2_dec(compte['s-' + d3 + 't'])

            dico_detail_compte = {'taille': (4 + len(subgeneraux.articles_d3)),
                                  'subs': Outils.format_2_dec(compte['subs'])}
            contenu_detail_compte += r'''\\*
                \hline
                \multicolumn{%(taille)s}{|r|}{%(subs)s} \\ 
                \hline
                ''' % dico_detail_compte

        # ## 2

        if client['bonus'] > 0:
            structure_bonus = r'''{|c|c|c|c|}'''
            contenu_bonus = r'''
                \hline
                Année & Mois & Code & Montant \\
                \hline
                '''

            for a, annee in sorted(client['annees'].items()):
                for m, mois in sorted(annee['mois'].items()):
                    code = subgeneraux.article_t('B').texte_t_court
                    dico = {'annee': a, 'mois': m, 'bj': mois['bj'],
                            'code': code}
                    contenu_bonus += r'''
                        %(annee)s & %(mois)s & %(code)s & %(bj)s \\
                        \hline
                        ''' % dico

            contenu_bonus += r'''
                \multicolumn{3}{|r|}{TOTAL} & ''' + str(client['bonus']) + r''' \\
                \hline
                '''

            legende_bonus = r'''Table 2 - Bonus d'utilisation en heures creuses'''

            contenu += Latex.tableau(contenu_bonus, structure_bonus, legende_bonus)
        else:
            contenu += Latex.tableau_vide(r'''Table 2 - Pas de bonus d'utilisation en heures creuses''')


        # ## 3

        structure_recap = r'''{|c|c|c|c|c|c|}'''
        contenu_recap = r'''
            \hline
            N. compte & Intitulé compte & Code & Type Subsides & Type projet & Montant \\
            \hline
            '''
        contenu_recap += contenu_recap_compte
        contenu_recap += r'''
            \multicolumn{5}{|r|}{TOTAL} & ''' + Outils.format_2_dec(client['subs']) + r''' \\
            \hline
            '''

        legende_recap = r'''Table 3 - Récapitulatif des subsides par compte'''

        contenu += Latex.tableau(contenu_recap, structure_recap, legende_recap)

        contenu += r'''
            \clearpage
            '''

        # ## 4

        structure_detail = r'''{|c|c|c|c|'''
        for i in range(taille_d3):
            structure_detail += r'''c|'''
        structure_detail += r'''}'''

        legende_detail = r'''Table 4 - Détail des subsides'''

        contenu += Latex.long_tableau(contenu_detail_compte, structure_detail, legende_detail)

        return contenu
