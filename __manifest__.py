# -*- coding: utf-8 -*-
{
    "name"     : "Module Odoo 16 pour Plastigray pour migrer les développements de Dynacase dans Odoo",
    "version"  : "0.1",
    "author"   : "InfoSaône",
    "category" : "InfoSaône",
    "description": """
Module Odoo 16 pour Plastigray pour migrer les développements de Dynacase dans Odoo
===================================================
""",
    "maintainer" : "InfoSaône",
    "website"    : "http://www.infosaone.com",
    "depends"    : [
        "is_plastigray16",
    ],
    "data" : [
        "security/ir.model.access.csv",
        "views/is_param_project_view.xml",
        "views/is_doc_moule_view.xml",
        "views/menu.xml",
    ], 
    "qweb": [
    ],
    "assets": {
        'web.assets_backend': [
            'is_dynacase2odoo/static/src/dhtmlxgantt_project/*',
         ],
    },
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}

