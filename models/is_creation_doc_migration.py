from odoo import models, fields, api, _ # type: ignore
from odoo.addons.is_dynacase2odoo.models.is_param_project import GESTION_J  # type: ignore
from datetime import datetime, timedelta


TYPE_DOCUMENT=[
    ("Moule"                 , "Moule"),
    ("Dossier F"             , "Dossier F"),
]


class is_creation_doc_migration(models.Model):
    _name        = "is.creation.doc.migration"
    _description = "Gantt Copie"
    _order = "id desc"

    name          = fields.Char("N°", readonly=True)
    type_document = fields.Selection(TYPE_DOCUMENT,string="Type de document", default="Moule", required=True)
    moule_id      = fields.Many2one("is.mold"    , string="Moule")
    dossierf_id   = fields.Many2one("is.dossierf", string="Dossier")
    analyse       = fields.Text("Analyse", readonly=True)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('is.creation.doc.migration')
        return super().create(vals_list)


    def creer_doc_action(self):
        for obj in self:
            domain=[
                ('idmoule','=', obj.moule_id.id)
            ]
            lines=self.env['is.doc.moule'].search(domain)
            analyse=[]
            j_actuelle=dict(GESTION_J).get(obj.moule_id.j_actuelle)
            analyse.append('%s documents actuellement'%len(lines))
            analyse.append('J actuelle : %s'%j_actuelle)
            for line in lines:
                j_prevue=str(dict(GESTION_J).get(line.j_prevue)).ljust(15)


                analyse.append('- %s : %s'%(j_prevue,line.param_project_id.ppr_famille))



            obj.analyse = '\n'.join(analyse)