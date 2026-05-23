#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Relance par e-mail pour les FNC non clôturées :
  - doc_amdec = OUI
  - date_prev_recotation_amdec dépassée

Un e-mail est envoyé au créateur de chaque FNC concernée,
via le serveur de messagerie sortant d'Odoo (XML-RPC).
"""

import sys
import os
import ssl
import xmlrpc.client
from datetime import date

# --- chemin vers config.py (répertoire parent du script) ---
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import ODOO_USER, ODOO_PASSWORD, DATABASES, SOURCE_DB, ROBOT_EMAIL, MAIL_TEST, MAIL_TEST_CC


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
# Recherche des FNC concernées
# ---------------------------------------------------------------------------

def get_fnc_a_relancer(db, uid, models):
    today = date.today().isoformat()
    domain = [
        ("date_cloture",             "=",   False),
        ("doc_amdec",                "=",   "OUI"),
        ("date_prev_recotation_amdec","!=",  False),
        ("date_prev_recotation_amdec","<",   today),
    ]
    records = models.execute_kw(
        db, uid, ODOO_PASSWORD,
        "is.fnc", "search_read",
        [domain],
        {"fields": ["id", "num_non_conformite", "type_non_conformite",
                    "date_detection", "client_id", "num_reclamation",
                    "total_non_conforme", "description_probleme", "type_defaut",
                    "date_prev_recotation_amdec", "create_uid", "create_date"]},
    )
    return records


# ---------------------------------------------------------------------------
# Envoi des e-mails via mail.mail d'Odoo
# ---------------------------------------------------------------------------

def get_user_email(db, uid, models, user_id):
    users = models.execute_kw(
        db, uid, ODOO_PASSWORD,
        "res.users", "search_read",
        [[["id", "=", user_id]]],
        {"fields": ["name", "email"], "limit": 1},
    )
    if users and users[0].get("email"):
        return users[0]["name"], users[0]["email"]
    return None, None


def send_relance(db, uid, models, creator_id, fncs):
    user_name, user_email = get_user_email(db, uid, models, creator_id)

    dest_email = MAIL_TEST if MAIL_TEST else user_email

    if not dest_email:
        nums = ", ".join(f["num_non_conformite"] or f"ID {f['id']}" for f in fncs)
        print(f"  [IGNORÉ] Créateur ID {creator_id} sans e-mail — FNC : {nums}")
        return

    odoo_url = DATABASES[SOURCE_DB]["url"]
    lignes_html = ""
    for fnc in fncs:
        fnc_num       = fnc.get("num_non_conformite") or f"ID {fnc['id']}"
        fnc_link      = f"<a href='{odoo_url}/web#id={fnc['id']}&model=is.fnc&view_type=form'>{fnc_num}</a>"
        type_nc       = fnc.get("type_non_conformite") or ""
        date_det      = fnc.get("date_detection") or ""
        client        = fnc["client_id"][1] if isinstance(fnc.get("client_id"), list) else (fnc.get("client_id") or "")
        num_reclam    = fnc.get("num_reclamation") or ""
        total_nc      = int(fnc.get("total_non_conforme") or 0)
        desc          = fnc.get("description_probleme") or ""
        type_def      = fnc.get("type_defaut") or ""
        date_prev     = fnc.get("date_prev_recotation_amdec") or "?"
        lignes_html += (
            f"<tr>"
            f"<td style='border:1px solid #cccccc'>{fnc_link}</td>"
            f"<td style='border:1px solid #cccccc'>{type_nc}</td>"
            f"<td style='border:1px solid #cccccc'>{date_det}</td>"
            f"<td style='border:1px solid #cccccc'>{client}</td>"
            f"<td style='border:1px solid #cccccc'>{num_reclam}</td>"
            f"<td style='border:1px solid #cccccc;text-align:right'>{total_nc}</td>"
            f"<td style='border:1px solid #cccccc'>{desc}</td>"
            f"<td style='border:1px solid #cccccc'>{type_def}</td>"
            f"<td style='border:1px solid #cccccc'>{date_prev}</td>"
            f"</tr>\n"
        )

    subject = "[FNC] Re-cotation AMDEC à réaliser"
    body = f"""
<p>Bonjour {user_name},</p>

<p>Les FNC suivantes nécessitent une re-cotation :</p>
<table style="border-collapse:collapse;width:100%" cellpadding="6" cellspacing="0">
    <thead>
        <tr style="background-color:#f2f2f2">
            <th style="border:1px solid #cccccc">N° FNC</th>
            <th style="border:1px solid #cccccc">Type NC</th>
            <th style="border:1px solid #cccccc">Date détection</th>
            <th style="border:1px solid #cccccc">Client émetteur</th>
            <th style="border:1px solid #cccccc">N° réclamation</th>
            <th style="border:1px solid #cccccc">Total pièces NC</th>
            <th style="border:1px solid #cccccc">Description du problème</th>
            <th style="border:1px solid #cccccc">Type de défaut</th>
            <th style="border:1px solid #cccccc">Date prévisionnelle re-cotation AMDEC</th>
        </tr>
    </thead>
    <tbody>
        {lignes_html}
    </tbody>
</table>

<p>Pour chacune de ces FNC :</p>
<ul>
    <li>Modification AMDEC : <strong>OUI</strong></li>
    <li>Date prévisionnelle de re-cotation AMDEC dépassée</li>
    <li>Date de clôture : non renseignée</li>
</ul>

<p>Merci de procéder à la re-cotation AMDEC et de renseigner la date correspondante
afin de pouvoir clôturer ces FNC.</p>
"""

    mail_vals = {
            "subject":     subject,
            "body_html":   body,
            "email_from":  ROBOT_EMAIL,
            "email_to":    dest_email,
            "state":       "outgoing",
            "auto_delete": True,
        }
    if MAIL_TEST_CC:
        mail_vals["email_cc"] = MAIL_TEST_CC

    mail_id = models.execute_kw(
        db, uid, ODOO_PASSWORD,
        "mail.mail", "create",
        [mail_vals],
    )

    # On force l'envoi immédiat via write sur state (évite mail.send qui retourne None)
    models.execute_kw(
        db, uid, ODOO_PASSWORD,
        "mail.mail", "write",
        [[mail_id], {"state": "outgoing"}],
    )

    # Post d'un message dans le chatter de chaque FNC
    today_str = date.today().strftime("%d/%m/%Y")
    for fnc in fncs:
        models.execute_kw(
            db, uid, ODOO_PASSWORD,
            "is.fnc", "message_post",
            [[fnc["id"]]],
            {
                "body": f"Relance automatique envoyée le {today_str} à {user_name} &lt;{user_email}&gt; concernant la re-cotation AMDEC (date prévisionnelle dépassée).",
                "message_type": "comment",
                "subtype_xmlid": "mail.mt_note",
            },
        )

    nums = ", ".join(f.get("num_non_conformite") or f"ID {f['id']}" for f in fncs)
    suffix = f" [TEST → {dest_email}]" if MAIL_TEST else ""
    print(f"  [OK] {len(fncs)} FNC(s) — e-mail mis en file d'envoi pour {user_name} <{user_email}>{suffix} ({nums})")


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def main():
    print(f"Connexion à la base '{SOURCE_DB}' ({DATABASES[SOURCE_DB]['db']})...")
    db, uid, models = get_connection()
    print("Connexion établie.")

    print("\nRecherche des FNC à relancer...")
    fncs = get_fnc_a_relancer(db, uid, models)

    if not fncs:
        print("Aucune FNC à relancer.")
        return

    print(f"{len(fncs)} FNC(s) trouvée(s).\n")

    # Regroupement par créateur
    par_createur = {}
    for fnc in fncs:
        creator_id = fnc["create_uid"][0] if isinstance(fnc["create_uid"], list) else fnc["create_uid"]
        par_createur.setdefault(creator_id, []).append(fnc)

    print(f"{len(par_createur)} créateur(s) concerné(s) :\n")
    for creator_id, fncs_createur in par_createur.items():
        send_relance(db, uid, models, creator_id, fncs_createur)

    print("\nTerminé.")


if __name__ == "__main__":
    main()
