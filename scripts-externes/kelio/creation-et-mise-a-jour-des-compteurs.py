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
"""

import sys
import os
import re
import ssl
import xmlrpc.client
import requests as req
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import config

NS = "http://echange.service.open.bodet.com"

# =============================================================================
# Paramètres
# =============================================================================
CREATION_ACTIVE       = True            # True = écriture réelle, False = lecture seule
COMPTEUR_ABBREVIATION = "S_RC"           # Abréviation du compteur à créer
COMPTEUR_DATE         = date.today()     # Date de début de l'initialisation
ODOO_BASES            = ["odoo1", "odoo4"]  # Bases Odoo source
ODOO_TYPE_RC          = "RC"             # Valeur du champ `name` dans is.droit.conges



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

    print(f"Serveur Kelio : {config.KELIO_BASE_URL}")
    print(f"Mode          : {'CREATION ACTIVE' if CREATION_ACTIVE else 'lecture seule (CREATION_ACTIVE = False)'}")
    print("=" * 60)

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

    if not rc_par_matricule:
        print("\nAucun compteur RC trouvé dans Odoo.")
        sys.exit(0)

    print(f"\n  Total : {len(rc_par_matricule)} employé(s) avec RC.")

    # --- 2. Export de tous les S_RC existants dans Kelio ---
    # Kelio ne retourne pas de clé utilisable (absenceBalanceInitializationKey = nil).
    # On identifie les entrées existantes par (matricule, date) comme clé naturelle.
    # Stratégie : 1ère entrée trouvée → MAJ date=aujourd'hui + valeur Odoo
    #             Autres entrées → mise à zéro (hours=0) pour leur date d'origine
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
    # Stratégie : si une entrée existe → réimporter à sa date la plus récente avec la nouvelle valeur
    #             (même date = mise à jour en place, pas de nouvelle entrée créée)
    #             les autres entrées plus anciennes sont mises à zéro
    #             si aucune entrée → créer avec la date du jour
    print(f"\n[3] {'MAJ/Création' if CREATION_ACTIVE else 'Simulation'} des initialisations "
          f"'{COMPTEUR_ABBREVIATION}' dans Kelio :")

    ok = err = 0
    for matricule, info in sorted(rc_par_matricule.items(), key=lambda x: x[1]['nom']):
        dates_existantes = src_par_matricule.get(matricule, [])
        items_xml = []

        if dates_existantes:
            dates_triees = sorted(dates_existantes)
            date_recente = dates_triees[-1]
            # Réimporter à la date la plus récente avec la nouvelle valeur → mise à jour en place
            items_xml.append(_balance_init_xml(matricule, date_recente, COMPTEUR_ABBREVIATION, info['nombre']))
            # Toutes les entrées plus anciennes → valeur 0 (date inchangée)
            for dt in dates_triees[:-1]:
                items_xml.append(_balance_init_xml(matricule, dt, COMPTEUR_ABBREVIATION, 0))
            n_zeroed = len(dates_triees) - 1
            action = f"MAJ {date_recente}" + (f" ({n_zeroed} ancienne(s) à zéro)" if n_zeroed else "")
        else:
            # Aucune entrée → création avec la date du jour
            items_xml.append(_balance_init_xml(matricule, COMPTEUR_DATE, COMPTEUR_ABBREVIATION, info['nombre']))
            action = f"NOUVEAU {COMPTEUR_DATE}"

        if not CREATION_ACTIVE:
            print(f"  {matricule:12s}  {info['nom']:30s}  {COMPTEUR_ABBREVIATION} = {info['nombre']:.2f}h  [{action} - simulation]")
            continue
        try:
            result_xml = importer_initialisations(items_xml)
            errors = re.findall(r'<(?:ns\d+:)?errorMessage>(.+?)</(?:ns\d+:)?errorMessage>', result_xml)
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
