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
    ], 
    "qweb": [
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}

