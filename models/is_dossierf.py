from odoo import models, fields # type: ignore
from odoo.addons.is_dynacase2odoo.models.is_param_project import GESTION_J, TYPE_DOCUMENT # type: ignore
from datetime import datetime, timedelta, date


class is_dossierf(models.Model):
    _inherit = 'is.dossierf'

    image                  = fields.Binary('Image')
    dossier_appel_offre_id = fields.Many2one("is.dossier.appel.offre", string="Dossier appel d'offre", copy=False, tracking=True)
    revue_contrat_id       = fields.Many2one("is.revue.de.contrat"   , string="Revue de contrat"     , copy=False, tracking=True)
    revue_lancement_id     = fields.Many2one("is.revue.lancement"    , string="Revue de lancement"   , copy=False, tracking=True)
    revue_risque_id        = fields.Many2one("is.revue.risque"       , string="Revue des risques"    , copy=False, tracking=True)
    j_actuelle             = fields.Selection(GESTION_J              , string="J Actuelle"           , copy=False, tracking=True)
    j_avancement           = fields.Integer(string="Avancement J (%)"                                , copy=False, tracking=True)
    date_fin_be            = fields.Date(string="Date fin BE"                                        , copy=False, tracking=True)
    article_ids            = fields.One2many('is.mold.dossierf.article', 'dossierf_id'               , copy=False)

    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }

    def gantt_action(self):
        for obj in self:
            domain=[ ('dossierf_id', '=', obj.id) ]

            tree_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_dossierf_edit_tree_view').id
            gantt_id = self.env.ref('is_dynacase2odoo.is_doc_moule_moule_dhtmlxgantt_project_view').id
            ctx={
                'default_type_document' : 'Dossier F',
                'default_dossierf_id'   : obj.id,
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


    def archiver_documents_action(self):
        for obj in self:
            domain=[
                ('dossierf_id'     ,'=', obj.id),
            ]
            docs=self.env['is.doc.moule'].search(domain)
            for doc in docs:
                doc.active = False

