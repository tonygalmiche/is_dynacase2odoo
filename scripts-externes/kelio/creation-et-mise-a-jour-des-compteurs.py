#!/usr/bin/env python3
"""
Création et mise à jour d'initialisations de compteurs dans Kelio via Web Service SOAP.

Web Service : TransferFileService
Méthodes    : importBalanceInitializations   (créer/MAJ  — type Soldes)
              exportBalanceInitializations   (lire       — type Soldes)
WSDL        : <KELIO_BASE_URL>/open/services/TransferFileService?wsdl
Écran       : Fonctions avancées > Ajouts / Retraits > Initialisations de compteurs

Structure WSDL AbsenceBalanceInitialization (hérite AbstractTransferFile + EmployeeInformation) :
  Identifiant :
    employeeIdentificationNumber  — matricule
  Depuis AbstractTransferFile :
    accountAbbreviation           — abréviation du compteur  (ex: "S_RC")
    date                          — date de début
    days                          — valeur en jours
    hours                         — valeur en heures
    visualizedInThePrintouts      — visualisable dans les éditions
  Propres à AbsenceBalanceInitialization :
    keepTheRemainder              — conserver le reliquat
    comment                       — commentaire
    absenceBalanceInitializationKey — clé (en lecture)

Prérequis :
  pip install zeep requests

Utilisation :
  python3 creation-et-mise-a-jour-des-compteurs.py [--matricule MATRICULE]

Paramètres en ligne de commande :
  --matricule   Optionnel. Ne traiter que le salarié ayant ce matricule
                (filtre sur is_matricule dans Odoo). Sans ce paramètre,
                tous les salariés ayant un droit RC dans Odoo sont traités.

Paramètres à modifier en tête de script (section "Paramètres") :
  CREATION_ACTIVE         True = écriture réelle dans Kelio.
                          False = mode simulation (lecture seule, aucun
                          appel importBalanceInitializations).
  COMPTEUR_ABBREVIATION   Abréviation du compteur Kelio à créer/mettre à jour
                          (ex: "S_RCt"). Doit exister parmi les types de
                          compteurs listés à l'étape [0], sinon le script
                          s'arrête.
  COMPTEUR_DATE           Date de début de l'entrée à créer ou mettre à jour.
                          Toujours utilisée : le script écrit uniquement
                          l'entrée à cette date (création si absente, MAJ en
                          place si déjà présente) et ne touche à aucune autre
                          entrée existante à une autre date.
  ODOO_BASES              Liste des bases Odoo (clés définies dans config.py)
                          dans lesquelles lire les droits à congés RC.
  ODOO_TYPE_RC            Valeur du champ `name` dans is.droit.conges
                          identifiant le type de droit "RC" à synchroniser.

Fonctionnement résumé :
  1. Lecture des droits RC (is.droit.conges) dans chaque base ODOO_BASES.
  2. Lecture des initialisations de compteur COMPTEUR_ABBREVIATION déjà
     présentes dans Kelio pour chaque salarié.
  3. Pour chaque salarié : création ou mise à jour en place de l'entrée à
     COMPTEUR_DATE avec la nouvelle valeur. Les autres entrées existantes à
     d'autres dates ne sont pas modifiées.
  4. Affichage récapitulatif des initialisations du compteur dans Kelio.
"""

import sys
import os
import re
import html
import ssl
import argparse
import xmlrpc.client
import requests as req
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import config

NS = "http://echange.service.open.bodet.com"

# =============================================================================
# Paramètres
# =============================================================================
CREATION_ACTIVE       = True                # True = écriture réelle, False = lecture seule
COMPTEUR_ABBREVIATION = "S_RCt"             # Abréviation du compteur à créer
COMPTEUR_DATE         = date(2026, 7, 1)    # Date de début de l'initialisation (fixe, pour n'avoir qu'un seul compteur par salarié)
ODOO_BASES            = ["odoo1", "odoo4"]  # Bases Odoo source
ODOO_TYPE_RC          = "RC"                # Valeur du champ `name` dans is.droit.conges



# =============================================================================
# Lister les types de compteurs (exportAbsenceBalanceTypes)
# =============================================================================
def lister_types_compteurs():
    """Retourne la liste des types de compteurs (AbsenceBalanceType) définis dans Kelio :
    [{'abbreviation': str, 'description': str, 'key': str}, ...]
    """
    body = f"""<?xml version='1.0' encoding='utf-8'?>
<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/">
  <soap-env:Body>
    <ns0:exportAbsenceBalanceTypes xmlns:ns0="{NS}"/>
  </soap-env:Body>
</soap-env:Envelope>"""
    url = f"{config.KELIO_BASE_URL}/open/services/TypeService"
    headers = {"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "urn:exportAbsenceBalanceTypes"}
    response = req.post(
        url, data=body.encode("utf-8"), headers=headers,
        auth=(config.KELIO_USER, config.KELIO_PASSWORD), timeout=30,
    )
    if not response.ok:
        raise Exception(f"HTTP {response.status_code} — {response.text[:2000]}")
    import xml.etree.ElementTree as ET
    root = ET.fromstring(response.text)
    items = root.findall('.//' + '{' + NS + '}' + 'AbsenceBalanceType')
    result = []
    for item in items:
        def txt(name):
            t = item.find('{' + NS + '}' + name)
            return (t.text or '') if t is not None else ''
        result.append({
            'abbreviation': txt('typeAbbreviation'),
            'description': txt('typeDescription'),
            'key': txt('typeKey'),
        })
    return result


# =============================================================================
# Lire les initialisations de soldes (exportBalanceInitializations)
# =============================================================================
def lire_initialisations_soldes(start_date, end_date):
    """
    Exporte les initialisations de soldes entre deux dates.
    Retourne le texte XML brut de la réponse.
    """
    body = f"""<?xml version='1.0' encoding='utf-8'?>
<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/">
  <soap-env:Body>
    <ns0:exportBalanceInitializations xmlns:ns0="{NS}">
      <ns0:populationFilter></ns0:populationFilter>
      <ns0:groupFilter></ns0:groupFilter>
      <ns0:startDate>{start_date}</ns0:startDate>
      <ns0:endDate>{end_date}</ns0:endDate>
    </ns0:exportBalanceInitializations>
  </soap-env:Body>
</soap-env:Envelope>"""
    url = f"{config.KELIO_BASE_URL}/open/services/TransferFileService"
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "urn:exportBalanceInitializations",
    }
    response = req.post(
        url, data=body.encode("utf-8"), headers=headers,
        auth=(config.KELIO_USER, config.KELIO_PASSWORD),
        timeout=30,
    )
    if not response.ok:
        raise Exception(f"HTTP {response.status_code} — {response.text[:2000]}")
    return response.text


# =============================================================================
# Import SOAP : créer ou mettre à jour des initialisations de solde
# =============================================================================
def _balance_init_xml(matricule, date_debut, account_abbreviation, hours, account_type=4):
    return f"""        <ns0:AbsenceBalanceInitialization xmlns:ns0="{NS}">
          <ns0:employeeIdentificationNumber>{matricule}</ns0:employeeIdentificationNumber>
          <ns0:accountAbbreviation>{account_abbreviation}</ns0:accountAbbreviation>
          <ns0:accountType>{account_type}</ns0:accountType>
          <ns0:date>{date_debut}</ns0:date>
          <ns0:hours>{hours}</ns0:hours>
          <ns0:keepTheRemainder>false</ns0:keepTheRemainder>
          <ns0:visualizedInThePrintouts>false</ns0:visualizedInThePrintouts>
        </ns0:AbsenceBalanceInitialization>"""


def importer_initialisations(items_xml_list):
    """Envoie une liste d'éléments XML AbsenceBalanceInitialization via SOAP."""
    items_xml = "\n".join(items_xml_list)
    body = f"""<?xml version='1.0' encoding='utf-8'?>
<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/">
  <soap-env:Body>
    <ns0:importBalanceInitializations xmlns:ns0="{NS}">
      <ns0:balanceInitializationsToImport>
{items_xml}
      </ns0:balanceInitializationsToImport>
    </ns0:importBalanceInitializations>
  </soap-env:Body>
</soap-env:Envelope>"""
    url = f"{config.KELIO_BASE_URL}/open/services/TransferFileService"
    headers = {"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "urn:importBalanceInitializations"}
    response = req.post(url, data=body.encode("utf-8"), headers=headers,
                        auth=(config.KELIO_USER, config.KELIO_PASSWORD), timeout=60)
    if not response.ok:
        raise Exception(f"HTTP {response.status_code} — {response.text[:500]}")
    return response.text


def supprimer_initialisations_soldes(matricule, dates, account_abbreviation, account_type=4):
    """
    Tente de supprimer des initialisations de solde via deleteAccountInitializations.
    Limité à un matricule précis, une abréviation de compteur précise, et des dates précises.
    """
    items_xml = "\n".join(
        f"""        <ns0:AccountInitialization xmlns:ns0="{NS}">
          <ns0:employeeIdentificationNumber>{matricule}</ns0:employeeIdentificationNumber>
          <ns0:accountAbbreviation>{account_abbreviation}</ns0:accountAbbreviation>
          <ns0:accountType>{account_type}</ns0:accountType>
          <ns0:date>{dt}</ns0:date>
        </ns0:AccountInitialization>"""
        for dt in dates
    )
    body = f"""<?xml version='1.0' encoding='utf-8'?>
<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/">
  <soap-env:Body>
    <ns0:deleteAccountInitializations xmlns:ns0="{NS}">
      <ns0:accountInitializationsToDelete>
{items_xml}
      </ns0:accountInitializationsToDelete>
    </ns0:deleteAccountInitializations>
  </soap-env:Body>
</soap-env:Envelope>"""
    url = f"{config.KELIO_BASE_URL}/open/services/TransferFileService"
    headers = {"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "urn:deleteAccountInitializations"}
    response = req.post(url, data=body.encode("utf-8"), headers=headers,
                        auth=(config.KELIO_USER, config.KELIO_PASSWORD), timeout=60)
    if not response.ok:
        raise Exception(f"HTTP {response.status_code} — {response.text[:500]}")
    return response.text


# =============================================================================
# Lecture des compteurs RC depuis Odoo (is.droit.conges)
# Retourne dict {matricule: {'nom': str, 'nombre': float}}
# =============================================================================
def lire_rc_odoo(db_key):
    db_config = config.DATABASES[db_key]
    url       = db_config["url"]
    db_name   = db_config["db"]
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode    = ssl.CERT_NONE
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", context=ctx)
    uid    = common.authenticate(db_name, config.ODOO_USER, config.ODOO_PASSWORD, {})
    if not uid:
        raise Exception(f"Authentification échouée sur {db_name}")
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", context=ctx)

    droits = models.execute_kw(
        db_name, uid, config.ODOO_PASSWORD,
        'is.droit.conges', 'search_read',
        [[['name', '=', ODOO_TYPE_RC]]],
        {'fields': ['employe_id', 'nombre']},
    )
    if not droits:
        return {}

    employe_ids = list({d['employe_id'][0] for d in droits})
    employes = models.execute_kw(
        db_name, uid, config.ODOO_PASSWORD,
        'hr.employee', 'search_read',
        [[['id', 'in', employe_ids]]],
        {'fields': ['id', 'name', 'is_matricule']},
    )
    emp_by_id = {e['id']: e for e in employes}

    result = {}
    for d in droits:
        emp = emp_by_id.get(d['employe_id'][0])
        if not emp or not emp.get('is_matricule'):
            continue
        matricule = emp['is_matricule'].strip().zfill(10)
        result[matricule] = {'nom': emp['name'], 'nombre': d['nombre']}
    return result


# =============================================================================
# Programme principal
# =============================================================================
if __name__ == "__main__":

    import xml.etree.ElementTree as ET

    parser = argparse.ArgumentParser(description="Création/MAJ des initialisations de compteurs Kelio depuis Odoo.")
    parser.add_argument(
        "--matricule",
        help="Ne traiter que le salarié ayant ce matricule (filtre sur is_matricule dans Odoo).",
    )
    args = parser.parse_args()

    print(f"Serveur Kelio : {config.KELIO_BASE_URL}")
    print(f"Mode          : {'CREATION ACTIVE' if CREATION_ACTIVE else 'lecture seule (CREATION_ACTIVE = False)'}")
    print("=" * 60)

    # --- 0. Liste des types de compteurs disponibles dans Kelio ---
    print("\n[0] Types de compteurs disponibles dans Kelio :")
    types_compteurs = []
    try:
        types_compteurs = lister_types_compteurs()
        print(f"  {'Abréviation':15s} {'Description':30s} {'Clé'}")
        print(f"  {'-'*15} {'-'*30} {'-'*5}")
        for t in sorted(types_compteurs, key=lambda t: t['abbreviation']):
            print(f"  {t['abbreviation']:15s} {t['description']:30s} {t['key']}")
    except Exception as e:
        print(f"  Erreur lecture des types de compteurs : {e}")

    abbreviations = {t['abbreviation'] for t in types_compteurs}
    if types_compteurs and COMPTEUR_ABBREVIATION not in abbreviations:
        print(f"\n  /!\\ ATTENTION : l'abréviation configurée '{COMPTEUR_ABBREVIATION}' "
              f"n'existe pas parmi les types de compteurs ci-dessus.")
        print(f"  Arrêt du script — corriger COMPTEUR_ABBREVIATION avant de continuer.")
        sys.exit(1)

    def find_all(root, tag):
        items = root.findall('.//' + '{' + NS + '}' + tag)
        if not items:
            items = root.findall('.//' + tag)
        return items

    def tag_text(el, name):
        t = el.find('{' + NS + '}' + name)
        if t is None:
            t = el.find(name)
        return (t.text or '') if t is not None else ''

    def afficher_initialisations(titre):
        DATE_DEBUT = date(date.today().year, 1, 1)
        DATE_FIN   = date(date.today().year, 12, 31)
        print(f"\n{titre} ({DATE_DEBUT} → {DATE_FIN}) :")
        try:
            xml_response = lire_initialisations_soldes(DATE_DEBUT, DATE_FIN)
            root = ET.fromstring(xml_response)
            items = find_all(root, 'AbsenceBalanceInitialization')
            if not items:
                print("  Aucune initialisation trouvée.")
            else:
                filtered = sorted(
                    [i for i in items if tag_text(i, 'accountAbbreviation') == COMPTEUR_ABBREVIATION],
                    key=lambda i: (tag_text(i, 'employeeSurname'), tag_text(i, 'employeeFirstName')),
                )
                print(f"  ({len(filtered)} entrée(s) '{COMPTEUR_ABBREVIATION}' sur {len(items)} au total)\n")
                print(f"  {'Matricule':12s} {'Nom':20s} {'Prénom':15s} {'Compteur':12s} {'Jours':7s} {'Heures':7s} {'Date'}")
                print(f"  {'-'*12} {'-'*20} {'-'*15} {'-'*12} {'-'*7} {'-'*7} {'-'*12}")
                for item in filtered:
                    mat    = tag_text(item, 'employeeIdentificationNumber')
                    nom    = tag_text(item, 'employeeSurname')
                    prenom = tag_text(item, 'employeeFirstName')
                    compte = tag_text(item, 'accountAbbreviation')
                    jours  = tag_text(item, 'days')
                    heures = tag_text(item, 'hours')
                    dt     = tag_text(item, 'date')
                    print(f"  {mat:12s} {nom:20s} {prenom:15s} {compte:12s} {jours:7s} {heures:7s} {dt}")
        except Exception as e:
            print(f"  Erreur lecture initialisations : {e}")

    # --- 1. Lecture des RC depuis Odoo ---
    rc_par_matricule = {}
    for db_key in ODOO_BASES:
        print(f"\n[1] Lecture RC dans {db_key} :")
        try:
            data = lire_rc_odoo(db_key)
            print(f"  {len(data)} employé(s) avec RC trouvé(s).")
            for mat, info in sorted(data.items(), key=lambda x: x[1]['nom']):
                print(f"  {mat:12s}  {info['nom']:30s}  RC = {info['nombre']:.2f}h")
            rc_par_matricule.update(data)
        except Exception as e:
            print(f"  Erreur : {e}")

    if args.matricule:
        matricule_filtre = args.matricule.strip().zfill(10)
        rc_par_matricule = {
            mat: info for mat, info in rc_par_matricule.items() if mat == matricule_filtre
        }
        print(f"\n  Filtre --matricule={args.matricule} → {len(rc_par_matricule)} employé(s) retenu(s).")

    if not rc_par_matricule:
        print("\nAucun compteur RC trouvé dans Odoo.")
        sys.exit(0)

    print(f"\n  Total : {len(rc_par_matricule)} employé(s) avec RC.")

    # --- 2. Export de tous les S_RC existants dans Kelio ---
    # Kelio ne retourne pas de clé utilisable (absenceBalanceInitializationKey = nil).
    # On identifie les entrées existantes par (matricule, date) comme clé naturelle,
    # afin de savoir si une entrée existe déjà à COMPTEUR_DATE (MAJ) ou non (création).
    print(f"\n[2] Récupération des {COMPTEUR_ABBREVIATION} existants dans Kelio :")
    src_par_matricule = {}  # {matricule: [date_str, ...]}  — toutes les dates S_RC
    try:
        DATE_DEBUT = date(date.today().year - 1, 1, 1)
        DATE_FIN   = date(date.today().year + 1, 12, 31)
        xml_response = lire_initialisations_soldes(DATE_DEBUT, DATE_FIN)
        root = ET.fromstring(xml_response)
        items = find_all(root, 'AbsenceBalanceInitialization')
        for item in items:
            if tag_text(item, 'accountAbbreviation') != COMPTEUR_ABBREVIATION:
                continue
            mat = tag_text(item, 'employeeIdentificationNumber')
            dt  = tag_text(item, 'date')
            if mat and dt:
                src_par_matricule.setdefault(mat, []).append(dt)
        print(f"  {len(src_par_matricule)} matricule(s) avec {COMPTEUR_ABBREVIATION} existant(s).")
    except Exception as e:
        print(f"  Erreur lecture Kelio : {e}")

    # --- 3. Mise à jour / création dans Kelio ---
    # Stratégie : on écrit uniquement l'entrée à COMPTEUR_DATE avec la nouvelle valeur
    #             (création si elle n'existe pas encore à cette date, mise à jour en place sinon).
    #             Les éventuelles autres entrées existantes à d'autres dates ne sont pas touchées.
    print(f"\n[3] {'MAJ/Création' if CREATION_ACTIVE else 'Simulation'} des initialisations "
          f"'{COMPTEUR_ABBREVIATION}' dans Kelio :")

    ok = err = 0
    for matricule, info in sorted(rc_par_matricule.items(), key=lambda x: x[1]['nom']):
        dates_existantes = src_par_matricule.get(matricule, [])
        items_xml = [_balance_init_xml(matricule, COMPTEUR_DATE, COMPTEUR_ABBREVIATION, info['nombre'])]
        action = f"MAJ {COMPTEUR_DATE}" if str(COMPTEUR_DATE) in dates_existantes else f"NOUVEAU {COMPTEUR_DATE}"

        if not CREATION_ACTIVE:
            print(f"  {matricule:12s}  {info['nom']:30s}  {COMPTEUR_ABBREVIATION} = {info['nombre']:.2f}h  [{action} - simulation]")
            continue
        try:
            result_xml = importer_initialisations(items_xml)
            errors = [html.unescape(e) for e in
                      re.findall(r'<(?:ns\d+:)?errorMessage>(.+?)</(?:ns\d+:)?errorMessage>', result_xml)]
            if errors:
                print(f"  {matricule:12s}  {info['nom']:30s}  ERREUR : {errors}")
                err += 1
            else:
                print(f"  {matricule:12s}  {info['nom']:30s}  {action} — {COMPTEUR_ABBREVIATION} = {info['nombre']:.2f}h")
                ok += 1
        except Exception as ex:
            print(f"  {matricule:12s}  {info['nom']:30s}  EXCEPTION : {ex}")
            err += 1

    if CREATION_ACTIVE:
        print(f"\n  Résultat : {ok} OK, {err} erreur(s).")

    # --- 4. Afficher les initialisations S_RC dans Kelio ---
    afficher_initialisations(f"[4] Initialisations '{COMPTEUR_ABBREVIATION}' dans Kelio")
