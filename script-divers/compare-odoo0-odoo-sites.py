#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script XML-RPC pour comparer le champ property_account_position_id
entre la base source (odoo0) et les bases de destination (odoo1, odoo3, odoo4)
"""

import xmlrpc.client
import ssl
from config import (
    ODOO_USER, ODOO_PASSWORD,
    DATABASES, SOURCE_DB, DEST_DBS, COMPARE_FIELD
)


def get_odoo_connection(db_key):
    """Établit une connexion XML-RPC à une base Odoo."""
    db_config = DATABASES[db_key]
    url = db_config["url"]
    db_name = db_config["db"]
    
    # Contexte SSL pour HTTPS (ignorer la vérification des certificats si auto-signés)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", context=context)
    uid = common.authenticate(db_name, ODOO_USER, ODOO_PASSWORD, {})
    
    if not uid:
        raise Exception(f"Échec d'authentification sur {db_name}")
    
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", context=context)
    return db_name, uid, models


def get_source_partners(field):
    """Récupère les partenaires de la base source, indexés par leur id."""
    db_name, uid, models = get_odoo_connection(SOURCE_DB)
    
    partners = models.execute_kw(
        db_name, uid, ODOO_PASSWORD,
        'res.partner', 'search_read',
        [[]],
        {
            'fields': ['id', 'name', 'is_code', 'is_adr_code', field],
            'order': 'id'
        }
    )
    
    result = {}
    for p in partners:
        val = p.get(field)
        result[p['id']] = {
            'id': p['id'],
            'name': p['name'],
            'is_code': p.get('is_code') or '',
            'is_adr_code': p.get('is_adr_code') or '',
            # Les champs many2one retournent [id, name] ou False
            'field_id': val[0] if isinstance(val, list) else val,
            'field_name': val[1] if isinstance(val, list) else val,
        }
    
    return result


def get_dest_partners(db_key, field):
    """Récupère les partenaires d'une base destination, indexés par is_database_origine_id."""
    db_name, uid, models = get_odoo_connection(db_key)
    
    partners = models.execute_kw(
        db_name, uid, ODOO_PASSWORD,
        'res.partner', 'search_read',
        [[['is_database_origine_id', '!=', False]]],
        {
            'fields': ['id', 'name', 'is_code', 'is_adr_code', 'is_database_origine_id', field],
            'order': 'is_database_origine_id'
        }
    )
    
    # Clé = id du partenaire dans odoo0
    result = {}
    for p in partners:
        origine_id = p['is_database_origine_id']
        val = p.get(field)
        result[origine_id] = {
            'id': p['id'],
            'name': p['name'],
            'is_code': p.get('is_code') or '',
            'is_adr_code': p.get('is_adr_code') or '',
            'field_id': val[0] if isinstance(val, list) else val,
            'field_name': val[1] if isinstance(val, list) else val,
        }
    
    return result


def compare_field(field=COMPARE_FIELD):
    """Compare un champ de res.partner entre la base source et les bases destination."""
    print("=" * 80)
    print(f"Comparaison du champ : {field}")
    print(f"Source : {SOURCE_DB} ({DATABASES[SOURCE_DB]['db']})")
    print("=" * 80)

    # Récupérer les données de la base source (indexées par id), filtrer sur is_code renseigné
    print(f"\nChargement des données de {SOURCE_DB}...")
    all_source = get_source_partners(field)
    source_partners = {k: v for k, v in all_source.items() if v['is_code']}
    print(f"  -> {len(source_partners)} partenaires avec is_code trouvés (sur {len(all_source)})")

    # Récupérer les données de toutes les bases destination
    dest_data_all = {}
    for dest_db in DEST_DBS:
        print(f"Chargement des données de {dest_db}...")
        dest_data_all[dest_db] = get_dest_partners(dest_db, field)
        print(f"  -> {len(dest_data_all[dest_db])} partenaires trouvés")

    # Construire les lignes du tableau final : une ligne par partenaire ayant au moins une différence
    rows = []
    for odoo0_id, src in source_partners.items():
        dest_values = {}
        has_diff = False
        src_val = src['field_id'] or False
        for dest_db in DEST_DBS:
            dest = dest_data_all[dest_db].get(odoo0_id)
            val = dest['field_name'] if dest else 'absent'
            dest_values[dest_db] = str(val)
            # Si absent dans la destination : pas une anomalie, ignorer
            if dest and (src_val or False) != (dest['field_id'] or False):
                has_diff = True
        if has_diff:
            rows.append({
                'name': src['name'],
                'is_code': src['is_code'],
                'is_adr_code': src['is_adr_code'],
                'source_name': str(src['field_name']),
                **dest_values,
            })

    # Afficher le tableau final
    print(f"\n{'=' * 80}")
    print(f"Tableau récapitulatif des différences")
    print(f"{'=' * 80}")
    print(f"  Différences trouvées: {len(rows)}")

    if rows:
        col_source = SOURCE_DB
        w_name   = max(len("Nom"),       max(len(r['name'])           for r in rows))
        w_code   = max(len("Code"),      max(len(r['is_code'])        for r in rows))
        w_adr    = max(len("Adr"),       max(len(r['is_adr_code'])    for r in rows))
        w_src    = max(len(col_source),  max(len(r['source_name'])    for r in rows))
        w_dests  = {db: max(len(db), max(len(r[db]) for r in rows)) for db in DEST_DBS}

        dest_sep    = "".join(f"-+-{'-'*w_dests[db]}" for db in DEST_DBS)
        dest_header = "".join(f" | {db:<{w_dests[db]}}" for db in DEST_DBS)

        sep    = f"  +-{'-'*w_name}-+-{'-'*w_code}-+-{'-'*w_adr}-+-{'-'*w_src}{dest_sep}-+"
        header = f"  | {'Nom':<{w_name}} | {'Code':<{w_code}} | {'Adr':<{w_adr}} | {col_source:<{w_src}}{dest_header} |"

        print(sep)
        print(header)
        print(sep)
        for r in rows:
            dest_vals = "".join(f" | {r[db]:<{w_dests[db]}}" for db in DEST_DBS)
            print(f"  | {r['name']:<{w_name}} | {r['is_code']:<{w_code}} | {r['is_adr_code']:<{w_adr}} | {r['source_name']:<{w_src}}{dest_vals} |")
        print(sep)


if __name__ == "__main__":
    try:
        compare_field()
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()

