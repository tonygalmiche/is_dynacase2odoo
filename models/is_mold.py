from odoo import models, fields, api # type: ignore
from odoo.addons.is_dynacase2odoo.models.is_param_project import GESTION_J, TYPE_DOCUMENT # type: ignore


TYPE_EXPORT =[
    ("definitif", "Définitif"),
    ("temporaire", "Temporaire"),
]


TYPE_IMPORT =[
    ("retour_definitif", "Retour définitif"),
    ("admission_temporaire_reparation", "Admission temporaire réparation"),
    ("perfectionnement_actifi_reparation", "Perfectionnement actif réparation"),
    ("retour_suite_export_temporaire", "Retour suite export temporaire"),
]


class is_mold(models.Model):
    _inherit = 'is.mold'

    image                  = fields.Binary('Image')
    dossier_appel_offre_id = fields.Many2one("is.dossier.appel.offre", string="Dossier appel d'offre", copy=False, tracking=True)
    revue_contrat_id       = fields.Many2one("is.revue.de.contrat"   , string="Revue de contrat"     , copy=False, tracking=True)
    revue_lancement_id     = fields.Many2one("is.revue.lancement"    , string="Revue de lancement"   , copy=False, tracking=True)
    revue_risque_id        = fields.Many2one("is.revue.risque"       , string="Revue des risques"    , copy=False, tracking=True)
    j_actuelle             = fields.Selection(GESTION_J, string="J Actuelle", default="J0"           , copy=False, tracking=True)
    j_avancement           = fields.Integer(string="Avancement J (%)"                                , copy=False, tracking=True)
    date_fin_be            = fields.Date(string="Date fin BE"                                        , copy=False)
    article_ids            = fields.One2many('is.mold.dossierf.article', 'mold_id')
    fermeture_id           = fields.Many2one("is.fermeture.gantt", string="Fermeture planning")
    logo_rs                = fields.Char(string="Logo RS"         , compute='_compute_logo_rs'      , store=False, readonly=True)
    j_actuelle_rw          = fields.Boolean(string="J Actuelle rw", compute='_compute_j_actuelle_rw', store=False, readonly=True)

    date_export            = fields.Date("Date d'exportation", tracking=True)
    type_export            = fields.Selection(TYPE_EXPORT, string="Type d'exportation", tracking=True)
    marche_ce_export       = fields.Boolean(string="Outillage pour marché CE", tracking=True)
    valeur_declaree_export = fields.Float("Valeur déclarée", tracking=True)
    commentaire_export     = fields.Text("Commentaire exportation", tracking=True)
    pj_export_ids          = fields.Many2many("ir.attachment", "is_mold_pj_export_rel", "piece_jointe", "att_id", string="Pièce jointe exportation")

    date_import            = fields.Date(string="Date d'importation", tracking=True)
    type_import            = fields.Selection(TYPE_IMPORT, string="Type d'importation", tracking=True)
    date_taxation_import   = fields.Date(string="Date taxation moule", tracking=True)
    commentaire_import     = fields.Text("Commentaire importation", tracking=True)
    pj_import_ids          = fields.Many2many("ir.attachment", "is_mold_pj_import_rel", "piece_jointe", "att_id", string="Pièce jointe importation")


    @api.depends('j_actuelle')
    def _compute_j_actuelle_rw(self):
        admin = self.env.user.has_group('base.group_system')
        for obj in self:
            rw = False
            if admin:
                rw=True
            obj.j_actuelle_rw = rw


    @api.depends('revue_contrat_id')
    def _compute_logo_rs(self):
        for obj in self:
            logo_rs = False
            if obj.revue_contrat_id:
                logo_rs = obj.revue_contrat_id.get_logo_rs()
            obj.logo_rs = logo_rs




    @api.depends('revue_contrat_id')
    def _compute_logo_rs(self):
        for obj in self:
            logo_rs = False
            if obj.revue_contrat_id:
                logo_rs = obj.revue_contrat_id.get_logo_rs()
            obj.logo_rs = logo_rs


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
