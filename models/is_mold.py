from odoo import models, fields # type: ignore
from odoo.addons.is_dynacase2odoo.models.is_param_project import GESTION_J, TYPE_DOCUMENT # type: ignore


class is_mold(models.Model):
    _inherit = 'is.mold'

    image                  = fields.Binary('Image')
    dossier_appel_offre_id = fields.Many2one("is.dossier.appel.offre", string="Dossier appel d'offre", copy=False, tracking=True)
    revue_contrat_id       = fields.Many2one("is.revue.de.contrat"   , string="Revue de contrat"     , copy=False, tracking=True)
    revue_lancement_id     = fields.Many2one("is.revue.lancement"    , string="Revue de lancement"   , copy=False, tracking=True)
    revue_risque_id        = fields.Many2one("is.revue.risque"       , string="Revue des risques"    , copy=False, tracking=True)
    j_actuelle             = fields.Selection(GESTION_J, string="J Actuelle"                         , copy=False, tracking=True)
    j_avancement           = fields.Integer(string="Avancement J (%)"                                , copy=False, tracking=True)
    date_fin_be            = fields.Date(string="Date fin BE"                                        , copy=False)
    article_ids            = fields.One2many('is.mold.dossierf.article', 'mold_id')

    def gantt_action(self):
        for obj in self:
            domain=[('idmoule', '=', obj.id)]
            view_mode = 'dhtmlxgantt_project,tree,form,kanban,calendar,pivot,graph'
            return self.env['is.doc.moule'].list_doc(obj,domain,view_mode=view_mode)

    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }


    def archiver_documents_action(self):
        for obj in self:
            domain=[
                ('idmoule'         ,'=', obj.id),
                #('dossierf_id'     ,'=', obj.id),
            ]
            docs=self.env['is.doc.moule'].search(domain)
            for doc in docs:
                doc.active = False


class is_mold_dossierf_article(models.Model):
    _name        = "is.mold.dossierf.article"
    _description = "Articles associés aux moules ou dossier F"
    _order       = 'article_id'

    mold_id          = fields.Many2one("is.mold", string="Moule"         , ondelete='cascade')
    dossierf_id      = fields.Many2one("is.dossierf", string="Dossier F", ondelete='cascade')
    article_id       = fields.Many2one("is.dossier.article", string="Dossier article")
    planning         = fields.Boolean(string="Utiliser ce planning",default=False, help="Utiliser le planning de ce moule ou dossier F pour cet article")
