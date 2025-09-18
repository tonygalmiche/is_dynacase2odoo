from odoo import models, fields, api         # type: ignore
from datetime import datetime


_TYPE = [
         ('poste', 'Poste'),
         ('produit', 'Produit'),
         ('process', 'Process'),
         ('fournisseur', 'Fournisseur'),
         ('systeme', 'Système'),
         ('application', 'Application'),
         ('environnement', 'Environnement'),
         ('securite', 'Sécurité'),
         ('pre-serie', 'Pré-série'),
         ('comprehension', 'Compréhension'),
         ]


_JOUR_NUIT = [
              ('jour', 'Jour'),
              ('nuit', 'Nuit'),
              ]


class is_planification_audit(models.Model):
    _name='is.planification.audit'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Planification audit"
    _rec_name = "numero"
    _order='create_date desc'


    active                      = fields.Boolean('Actif', default=True, tracking=True)
    dynacase_id                 = fields.Integer(string="Id Dynacase", index=True, copy=False)

    numero                      = fields.Integer("Numéro d'audit", tracking=True, copy=False)
    emetteur_id                 = fields.Many2one("res.users", string="Émetteur", default=lambda self: self.env.uid, tracking=True)
    site_id                     = fields.Many2one('is.database', "Site", tracking=True, default=lambda self: self._get_site_id(),)
    responsable_id              = fields.Many2one("res.users", string="Responsable qualité du site", tracking=True)
    type_audit                  = fields.Selection(_TYPE, "Type audit", tracking=True)
    jour_nuit                   = fields.Selection(_JOUR_NUIT, "Jour / Nuit", tracking=True)
    moule_id                    = fields.Many2one('is.mold', string="Moule", tracking=True)
    dossierf_id                 = fields.Many2one("is.dossierf", string="Dossier F", tracking=True)
    article_id                  = fields.Many2one('is.article', 'Article', tracking=True)
    ref_client                  = fields.Char("Référence client", tracking=True)
    description                 = fields.Char("Description", tracking=True)
    client_id                   = fields.Many2one("res.partner", string="Client", tracking=True, domain=[("is_company","=",True), ("customer","=",True), ("is_code", "like", "90%")])
    fournisseur_id              = fields.Many2one('res.partner', 'Nom du fournisseur', tracking=True, domain=[("is_company","=",True), ("supplier","=",True)])
    demandeur_id                = fields.Many2one("res.users", "Demandeur", default=lambda self: self.env.uid, tracking=True)
    date_prev                   = fields.Date("Date prévisionnelle", tracking=True, copy=False)
    mois_prev = fields.Char("Mois prévisionnel", tracking=True, copy=False, compute="_compute_mois_prev", store=True)

    @api.depends('date_prev')
    def _compute_mois_prev(self):
        for record in self:
            if record.date_prev:
                record.mois_prev = record.date_prev.strftime('%m/%Y')
            else:
                record.mois_prev = False
    
    date_realise                = fields.Date("Date réalisée", tracking=True, copy=False)
    mois_realise = fields.Char("Mois réalisé", tracking=True, copy=False, compute="_compute_mois_realise", store=True)

    @api.depends('date_realise')
    def _compute_mois_realise(self):
        for record in self:
            if record.date_realise:
                record.mois_realise = record.date_realise.strftime('%m/%Y')
            else:
                record.mois_realise = False

    auditeur1_id                = fields.Many2one("res.users", string="Auditeur 1", tracking=True)
    auditeur2_id                = fields.Many2one("res.users", string="Auditeur 2", tracking=True)
    
    nb_crit_conformes           = fields.Float("Nombre de critères non conformes", tracking=True)
    nb_crit_audites             = fields.Float("Nombre de critères audités", tracking=True)
    pourcent_conform            = fields.Float("% de conformité", tracking=True)
    note                        = fields.Float("Note", tracking=True)
    plan_actions_id             = fields.Many2one('is.plan.action', string="Plan d'actions", tracking=True)
    etat_plan_actions           = fields.Char("État du plan d'actions", tracking=True)
    replan_calculee             = fields.Date("Replanification calculée", tracking=True)
    replan_saisie               = fields.Date("Replanification saisie", tracking=True)
    
    piece_jointe_ids            = fields.Many2many("ir.attachment", "is_planification_audit_pieces_jointes_rel", "piece_jointe", "att_id", string="Pièce jointe")



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'numero' not in vals:
                last = self.env[self._name].search([('numero', '!=', None)], order="numero desc", limit=1)
                if last:
                    vals['numero'] = last.numero + 1
                else:
                    vals['numero'] = 1
        return super().create(vals_list)




    def _get_site_id(self):
        user = self.env['res.users'].browse(self._uid)
        site_id = user.is_site_id.id
        return site_id



    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }

    @api.onchange('article_id')
    def onchange_article_id(self):
        if self.article_id:
            self.ref_client = self.article_id.ref_client
        else:
            self.ref_client = False
