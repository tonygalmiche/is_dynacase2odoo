# -*- coding: utf-8 -*-
from odoo import models,fields,api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class is_mold_project(models.Model):
    _inherit = 'is.mold.project'

    fermeture_id = fields.Many2one("is.fermeture.gantt", string="Fermeture du Gantt")

    def gantt_action(self):
        for obj in self:
            domain=[ ('idproject', '=', obj.id) ]
            tree_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_edit_tree_view').id
            gantt_id = self.env.ref('is_dynacase2odoo.is_doc_moule_moule_dhtmlxgantt_project_view').id
            ctx={
                'default_etat'          :'AF',
                'default_date_fin_gantt': datetime.today(),
                'default_idresp'        : self._uid,
            }
            return {
                'name': obj.name,
                'view_mode': 'dhtmlxgantt_project,tree,form,kanban,calendar,pivot,graph',
                "views"    : [
                    (gantt_id, "dhtmlxgantt_project"),
                    (tree_id, "tree"),
                    (False, "form"),(False, "kanban"),(False, "calendar"),(False, "pivot"),(False, "graph")],
                'res_model': 'is.doc.moule',
                'domain': domain,
                'type': 'ir.actions.act_window',
                "context": ctx,
                'limit': 1000,
            }
        
