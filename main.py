# This Python file uses the following encoding: utf-8

"""
Fichier principal à lancer pour faire tourner le logiciel

Usage:
  main.py [options]

Options:

  -h   --help              Affiche le présent message
  --entrees <chemin>       Chemin des fichiers d'entrée
  --sansgraphiques         Pas d'interface graphique
"""
import sys
from docopt import docopt

from importes import (SubPrestation,
                      SubCompte,
                      DossierSource,
                      SubMachine)
from parametres import (SubEdition,
                        SubGeneraux)
from traitement import Verification
from outils import Outils

arguments = docopt(__doc__)

plateforme = sys.platform

if arguments["--sansgraphiques"]:
    Outils.interface_graphique(False)

if arguments["--entrees"]:
    dossier_data = arguments["--entrees"]
else:
    dossier_data = Outils.choisir_dossier(plateforme)
dossier_source = DossierSource(dossier_data)

subedition = SubEdition(dossier_source)
subgeneraux = SubGeneraux(dossier_source)

subcomptes = SubCompte(dossier_source)
submachines = SubMachine(dossier_source)
subprestations = SubPrestation(dossier_source)

mois = subedition.mois_debut
annee = subedition.annee_debut
while 1:
    fichier_complet = "bilan-comptes_" + str(annee) + "_" + Outils.mois_string(mois) + ".csv"
    if not Outils.existe([dossier_data, fichier_complet], plateforme):
        msg = "Le fichier '" + fichier_complet + "' manque dans le dossier !"
        print("msg : " + msg)
        Outils.affiche_message(msg)
        sys.exit("Erreur sur les fichiers")
    if mois == subedition.mois_fin and annee == subedition.annee_fin:
        break
    if mois < 12:
        mois += 1
    else:
        mois = 1
        annee += 1

verification = Verification()
if verification.verification_cohérence(subgeneraux, subcomptes, submachines, subprestations) > 0:
    sys.exit("Erreur dans la cohérence")

Outils.affiche_message("OK !!!")
