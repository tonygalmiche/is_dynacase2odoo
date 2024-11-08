from odoo import models, fields # type: ignore
from odoo.addons.is_dynacase2odoo.models.is_param_project import GESTION_J, TYPE_DOCUMENT # type: ignore


class is_mold(models.Model):
    _inherit = 'is.mold'

    image                  = fields.Binary('Image')
    dossier_appel_offre_id = fields.Many2one("is.dossier.appel.offre", string="Dossier appel d'offre", copy=False)
    revue_contrat_id       = fields.Many2one("is.revue.de.contrat"   , string="Revue de contrat"     , copy=False)
    revue_lancement_id     = fields.Many2one("is.revue.lancement"    , string="Revue de lancement"   , copy=False)
    revue_risque_id        = fields.Many2one("is.revue.risque"       , string="Revue des risques"    , copy=False)
    j_actuelle             = fields.Selection(GESTION_J, string="J Actuelle", tracking=True          , copy=False)
    j_avancement           = fields.Integer(string="Avancement J (%)"       , tracking=True          , copy=False)
    date_fin_be            = fields.Date(string="Date fin BE"               , tracking=True          , copy=False)


    def gantt_action(self):
        for obj in self:
            domain=[('idmoule', '=', obj.id)]
            view_mode = 'dhtmlxgantt_project,tree,form,kanban,calendar,pivot,graph'
            return self.env['is.doc.moule'].list_doc(obj,domain,view_mode=view_mode)

