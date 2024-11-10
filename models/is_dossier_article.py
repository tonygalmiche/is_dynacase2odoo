# -*- coding: utf-8 -*-
from odoo import models,fields,api

class is_dossier_article(models.Model):
    _inherit = 'is.dossier.article'

    dynacase_id = fields.Integer(string="Id Dynacase",index=True,copy=False)


    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }

