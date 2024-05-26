# -*- coding: utf-8 -*-
from odoo import models,fields,api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class is_mold_project(models.Model):
    _inherit = 'is.mold.project'

    fermeture_id = fields.Many2one("is.fermeture.gantt", string="Fermeture du Gantt")

    def gantt_action(self):
        for obj in self:
            docs=self.env['is.doc.moule'].search([ ('idproject', '=', obj.id) ])
            ids=[]
            initial_date=str(datetime.today())
            for doc in docs:
                if str(doc.dateend)<initial_date:
                    initial_date=str(doc.dateend)
                ids.append(doc.id)
            tree_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_edit_tree_view').id
            gantt_id = self.env.ref('is_dynacase2odoo.is_doc_moule_moule_dhtmlxgantt_project_view').id
            ctx={
                'default_etat'         :'AF',
                'default_dateend'      : datetime.today(),
                'default_idresp'       : self._uid,
                'initial_date'         : initial_date,
            }
            return {
                'name': obj.name,
                'view_mode': 'dhtmlxgantt_project,tree,form,kanban,calendar,pivot,graph',
                "views"    : [
                    (gantt_id, "dhtmlxgantt_project"),
                    (tree_id, "tree"),
                    (False, "form"),(False, "kanban"),(False, "calendar"),(False, "pivot"),(False, "graph")],
                'res_model': 'is.doc.moule',
                'domain': [
                    ('id','in',ids),
                ],
                'type': 'ir.actions.act_window',
                "context": ctx,
                'limit': 1000,
            }
        
