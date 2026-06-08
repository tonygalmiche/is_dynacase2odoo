#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Liste des moyens de contrôle arrivant à échéance (avec retard par rapport au -10%).

Pour chacun des 4 modèles (gabarit de contrôle, instrument de mesure,
plaquette étalon, pièce de montabilité), les enregistrements dont la date
prochain contrôle moins 10 % de la périodicité est dépassée sont listés.

Un e-mail HTML est envoyé par site (Gray, ST-Brice, Plasti-ka)
via le serveur de messagerie sortant d'Odoo (XML-RPC).
"""

import sys
import os
import ssl
import xmlrpc.client
from datetime import date, timedelta, datetime

# --- chemin vers config.py (répertoire parent du script) ---
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import ODOO_USER, ODOO_PASSWORD, DATABASES, SOURCE_DB, ROBOT_EMAIL, MAIL_TEST, MAIL_TEST_CC

TABLES = {
    "is.gabarit.controle":  "Gabarit de contrôle",
    "is.instrument.mesure": "Instruments de mesure",
    "is.plaquette.etalon":  "Plaquette étalon",
    "is.piece.montabilite": "Pièce de montabilité",
}


# ---------------------------------------------------------------------------
# Connexion XML-RPC
# ---------------------------------------------------------------------------

def get_connection():
    cfg = DATABASES[SOURCE_DB]
    url = cfg["url"]
    db  = cfg["db"]

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", context=ctx, allow_none=True)
    uid = common.authenticate(db, ODOO_USER, ODOO_PASSWORD, {})
    if not uid:
        raise SystemExit(f"Échec d'authentification sur {db}")

    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", context=ctx, allow_none=True)
    return db, uid, models


# ---------------------------------------------------------------------------
# Récupération des sites depuis is.database
# ---------------------------------------------------------------------------

def get_sites(db, uid, models):
    """
    Retourne la liste des sites ayant au moins un destinataire moyen de contrôle,
    avec leurs e-mails destinataires et directeurs.
    """
    sites = models.execute_kw(
        db, uid, ODOO_PASSWORD,
        "is.database", "search_read",
        [[]],
        {"fields": ["id", "name", "moyen_controle_user_ids", "directeur_site_ids"]},
    )
    result = []
    for site in sites:
        if not site.get("moyen_controle_user_ids"):
            continue
        dest_users = models.execute_kw(
            db, uid, ODOO_PASSWORD,
            "res.users", "search_read",
            [[["id", "in", site["moyen_controle_user_ids"]]]],
            {"fields": ["email"]},
        )
        dest_emails = ",".join(u["email"] for u in dest_users if u.get("email"))
        dir_emails = ""
        if site.get("directeur_site_ids"):
            dir_users = models.execute_kw(
                db, uid, ODOO_PASSWORD,
                "res.users", "search_read",
                [[["id", "in", site["directeur_site_ids"]]]],
                {"fields": ["email"]},
            )
            dir_emails = ",".join(u["email"] for u in dir_users if u.get("email"))
        if dest_emails:
            result.append({
                "name":       site["name"],
                "dest":       dest_emails,
                "directeurs": dir_emails,
            })
    return result




# # ---------------------------------------------------------------------------
# # Récupération des enregistrements en retard pour un modèle et un site
# # ---------------------------------------------------------------------------

# def get_records_en_retard(db, uid, models, odoo_model, site_name):
#     """
#     Retourne les enregistrements dont la date prochain contrôle - 10% de la
#     périodicité est dépassée aujourd'hui.
#     """
#     domain = [
#         ("date_prochain_controle", "!=", False),
#         ("periodicite", "!=", False),
#         ("site_id.name", "=", site_name),
#     ]
#     records = models.execute_kw(
#         db, uid, ODOO_PASSWORD,
#         odoo_model, "search_read",
#         [domain],
#         {"fields": ["id", "code_pg", "designation", "date_prochain_controle", "periodicite", "site_id"],
#          "order": "date_prochain_controle asc"},
#     )

#     today = date.today()
#     results = []
#     for rec in records:
#         date_prochain_controle = rec.get("date_prochain_controle")
#         periodicite            = rec.get("periodicite") or 0

#         #d1 = datetime.strptime(d1_str, "%Y-%m-%d").date()
        
#         #p = float(periodicite)
#         #avance_jours = int((p / 10) * 30)
#         # Date de fin d'utilisation = Date prochain contrôle + 10% périodicité
#         #date_fin = d1 + timedelta(days=avance_jours)
#         # Nombre de jours avant fin d'utilisation :
#         #   si périodicité < 12 mois   : Date de fin d'utilisation - 10% périodicité par rapport à aujourd'hui
#         #   si périodicité >= 12 mois  : Date de fin d'utilisation - 60 jours par rapport à aujourd'hui
#         #if p < 12:
#         #    date_alert = date_fin - timedelta(days=avance_jours)
#         #else:
#         #    date_alert = date_fin - timedelta(days=60)

#         date_alert = date_prochain_controle - timedelta(days=60)
#         nb_jours = (date_prochain_controle - today).days

#         if nb_jours < 60:
#             rec["date_prochain_controle"] = date_prochain_controle.strftime("%d/%m/%Y")
#             rec["date_alert"]             = date_alert.strftime("%d/%m/%Y")
#             rec["nb_jours"]               = nb_jours
#             results.append(rec)

#     return results


def get_records_en_retard(db, uid, models, odoo_model, site_name):
    domain = [
        ("date_prochain_controle", "!=", False),
        ("periodicite", "!=", False),
        ("site_id.name", "=", site_name),
    ]
    records = models.execute_kw(
        db, uid, ODOO_PASSWORD,
        odoo_model, "search_read",
        [domain],
        {"fields": ["id", "code_pg", "designation", "date_prochain_controle", "periodicite", "site_id"],
        "order": "date_prochain_controle asc"},
    )

    today = date.today()
    results = []
    for rec in records:
        d1  = rec.get("date_prochain_controle")
        date_prochain_controle = datetime.strptime(d1, "%Y-%m-%d").date()
        nb_jours = (date_prochain_controle - today).days
        nb_jours_color='white'
        if nb_jours<0:
            nb_jours_color='red'
        if nb_jours < 60:
            rec["date_prochain_controle_fmt"] = date_prochain_controle.strftime("%d/%m/%Y")
            rec["nb_jours"]                   = nb_jours
            rec["nb_jours_color"]             = nb_jours_color
            results.append(rec)
    return results


# ---------------------------------------------------------------------------
# Construction du corps HTML pour un site
# ---------------------------------------------------------------------------

def build_html_body(db, uid, models, site_name):
    odoo_url = DATABASES[SOURCE_DB]["url"]
    ct = 0
    has_retard = False

    sections_html = ""
    for odoo_model, titre in TABLES.items():
        records = get_records_en_retard(db, uid, models, odoo_model, site_name)


        ct += len(records)
        if any(r["nb_jours"] < 0 for r in records):
            has_retard = True

        sections_html += f"<div style='font-size:1.2em;font-weight:bold;margin-top:12px'>{titre}</div>\n"
        sections_html += "<hr style='color:#0000CD'/>\n"

        if not records:
            sections_html += "<div style='color:red'>Aucun résultat !</div>\n"
        else:
            sections_html += (
                "<table style='width:1200px;border-spacing:0;border-collapse:collapse;border:1px solid #cccccc'>\n"
                "<tr style='background-color:#f2f2f2'>"
                "<th style='border:1px solid #cccccc;padding:2px;text-align:center'>Site</th>"
                "<th style='border:1px solid #cccccc;padding:2px;text-align:left'>Code PG</th>"
                "<th style='border:1px solid #cccccc;padding:2px;text-align:left'>Désignation</th>"
                "<th style='border:1px solid #cccccc;padding:2px;text-align:center'>Périodicité<br/>en mois</th>"
                "<th style='border:1px solid #cccccc;padding:2px;text-align:center'>Date prochain<br/>contrôle</th>"
                "<th style='border:1px solid #cccccc;padding:2px;text-align:right'>Nb jours avant<br/>prochain contrôle</th>"
                "</tr>\n"
            )
            for rec in records:
                site_label = rec["site_id"][1] if isinstance(rec.get("site_id"), list) else (rec.get("site_id") or "")
                code_pg     = rec.get("code_pg") or ""
                designation = rec.get("designation") or ""
                periodicite = rec.get("periodicite") or ""

                url = f"{odoo_url}/web#id={rec['id']}&view_type=form&model={odoo_model}"
                sections_html += (
                    "<tr>"
                    f"<td style='border:1px solid #cccccc;padding:2px;text-align:center'>{site_label}</td>"
                    f"<td style='border:1px solid #cccccc;padding:4px'><a href='{url}'>{code_pg}</a></td>"
                    f"<td style='border:1px solid #cccccc;padding:2px;font-size:0.9em'>{designation}</td>"
                    f"<td style='border:1px solid #cccccc;padding:2px;text-align:center'>{periodicite}</td>"
                    f"<td style='border:1px solid #cccccc;padding:2px;text-align:center'>{rec['date_prochain_controle_fmt']}</td>"
                    f"<td style='border:1px solid #cccccc;padding:2px;text-align:right;background-color:{rec['nb_jours_color']}'>{rec['nb_jours']}</td>"
                    "</tr>\n"
                )
            sections_html += "</table><br/><br/>\n"

    body = f"""<html><body>
<p>Bonjour,</p>
<p>Voici la liste des <strong>moyens de contrôle arrivant à échéance</strong>
pour le site <strong>{site_name}</strong> :</p>

{sections_html}
</body></html>"""

    return body, ct, has_retard


# ---------------------------------------------------------------------------
# Envoi d'un e-mail via mail.mail d'Odoo
# ---------------------------------------------------------------------------

def send_email(db, uid, models, site_name, dest_email, cc_email, subject, body, ct=0, has_retard=False):
    mail_vals = {
        "subject":     subject,
        "body_html":   body,
        "email_from":  ROBOT_EMAIL,
        "email_to":    dest_email,
        "state":       "outgoing",
        "auto_delete": False,
    }
    if MAIL_TEST:
        mail_vals["email_to"] = MAIL_TEST
    elif dest_email:
        mail_vals["email_to"] = dest_email
    if MAIL_TEST_CC:
        mail_vals["email_cc"] = MAIL_TEST_CC
    elif cc_email:
        mail_vals["email_cc"] = cc_email




    mail_id = models.execute_kw(
        db, uid, ODOO_PASSWORD,
        "mail.mail", "create",
        [mail_vals],
    )
    models.execute_kw(
        db, uid, ODOO_PASSWORD,
        "mail.mail", "write",
        [[mail_id], {"state": "outgoing"}],
    )
    suffix = f" [TEST]" if MAIL_TEST else ""
    cc_info = f" | CC : {mail_vals.get('email_cc', '')}" if mail_vals.get("email_cc") else ""
    retard_info = " | Retard détecté" if has_retard and cc_email else ""
    print(f"  Site {site_name} — {ct} enregistrement(s){retard_info} → {dest_email}{cc_info}{suffix} [has_retard={has_retard}]")


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def main():
    db, uid, models = get_connection()

    sites = get_sites(db, uid, models)
    if not sites:
        print("Aucun site avec des destinataires moyens de contrôle.")
        return

    for site_cfg in sites:
        site_name = site_cfg["name"]
        body, ct, has_retard = build_html_body(db, uid, models, site_name)

        dest_email = MAIL_TEST if MAIL_TEST else site_cfg["dest"]
        subject = f"Moyens de contrôles arrivant à échéance {site_name} ({ct})"

        # Directeurs en CC seulement si au moins une ligne en retard (nb_jours < 0)
        cc_email = site_cfg["directeurs"] if has_retard else ""

        send_email(db, uid, models, site_name, dest_email, cc_email, subject, body, ct, has_retard)


if __name__ == "__main__":
    main()
