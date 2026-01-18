from odoo import models, fields, api         # type: ignore
from datetime import datetime, timedelta


_TYPE = [

         ('client', 'Client'),
         ('fournisseur', 'Fournisseur'),
         ('process', 'Process'),
         ('systeme', 'Système'),
         ('produit', 'Produit'),
         ('pre-serie', 'Pré-série'),
         ('securite', 'Sécurité'),
         ('environnement', 'Environnement'),

        # ('poste', 'Poste'), # Fusion de poste et process le 18/01/26
        # ('application', 'Application'),      # Supression le 18/01/26
        # ('comprehension', 'Compréhension'),  # Supression le 18/01/26
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


    numero            = fields.Integer("Numéro d'audit", tracking=True, copy=False)
    emetteur_id       = fields.Many2one("res.users", string="Émetteur", default=lambda self: self.env.uid, tracking=True)
    site_id           = fields.Many2one('is.database', "Site", tracking=True, default=lambda self: self._get_site_id(),)
    responsable_id    = fields.Many2one("res.users", string="Responsable qualité du site", tracking=True)
    type_audit        = fields.Selection(_TYPE, "Type audit", tracking=True)
    jour_nuit         = fields.Selection(_JOUR_NUIT, "Jour / Nuit", tracking=True)
    moule_id          = fields.Many2one('is.mold', string="Moule", tracking=True)
    dossierf_id       = fields.Many2one("is.dossierf", string="Dossier F", tracking=True)
    article_id        = fields.Many2one('is.article', 'Article', tracking=True)
    ref_client        = fields.Char("Référence client", tracking=True)
    description       = fields.Char("Description", tracking=True)
    client_id         = fields.Many2one("res.partner", string="Client", tracking=True, domain=[("is_company","=",True), ("customer","=",True), ("is_code", "like", "90%")])
    fournisseur_id    = fields.Many2one('res.partner', 'Fournisseur'  , tracking=True, domain=[("is_company","=",True), ("supplier","=",True)])
    demandeur_id      = fields.Many2one("res.users", "Demandeur", default=lambda self: self.env.uid, tracking=True)
    date_prev         = fields.Date("Date prévisionnelle", tracking=True, copy=False)
    mois_prev         = fields.Char("Mois prévisionnel", tracking=True, copy=False, compute="_compute_mois_prev", store=True)
    date_realise      = fields.Date("Date réalisée", tracking=True, copy=False)
    mois_realise      = fields.Char("Mois réalisé", tracking=True, copy=False, compute="_compute_mois_realise", store=True)
    auditeur1_id      = fields.Many2one("res.users", string="Auditeur 1", tracking=True)
    auditeur2_id      = fields.Many2one("res.users", string="Auditeur 2 interne", tracking=True)
    auditeur2_externe = fields.Char(string="Auditeur 2 externe", tracking=True)
    commentaire       = fields.Text(string="Commentaire", tracking=True)
    nb_crit_conformes = fields.Float("Nombre de critères non conformes", tracking=True)
    nb_crit_audites   = fields.Float("Nombre de critères audités", tracking=True)
    pourcent_conform  = fields.Float("% de conformité", compute="_compute_pourcent_conform", store=True, tracking=True)
    note              = fields.Float("Note", tracking=True)
    plan_actions_id   = fields.Many2one('is.plan.action', string="Plan d'actions", tracking=True)
    plan_actions_intitule = fields.Char(related="plan_actions_id.title")
    etat_plan_actions = fields.Selection(string="État du plan d'actions", related="plan_actions_id.state")
    replan_calculee   = fields.Date("Replanification calculée", compute="_compute_replan_calculee", store=True, tracking=True)
    replan_saisie     = fields.Date("Replanification saisie", tracking=True)
    piece_jointe_ids  = fields.Many2many("ir.attachment", "is_planification_audit_pieces_jointes_rel", "piece_jointe", "att_id", string="Pièce jointe")
    date_cloture      = fields.Date("Date de cloture", tracking=True)
    active            = fields.Boolean('Actif', default=True, tracking=True)
    dynacase_id       = fields.Integer(string="Id Dynacase", index=True, copy=False)





    @api.depends('type_audit', 'pourcent_conform', 'date_realise')
    def _compute_replan_calculee(self):
        for record in self:
            replan_calculee = False
            if record.type_audit in ['poste', 'produit'] and record.date_realise:
                # Déterminer le nombre de jours selon le pourcentage de conformité
                if record.pourcent_conform < 75:
                    nb_jours = 30
                elif record.pourcent_conform >= 75 and record.pourcent_conform < 85:
                    nb_jours = 90
                elif record.pourcent_conform >= 85:
                    nb_jours = 365
                else:
                    nb_jours = 30  # valeur par défaut
                # Calculer la date de replanification
                replan_calculee = record.date_realise + timedelta(days=nb_jours)
                # Réinitialiser replan_saisie 
                record.replan_saisie = False
            record.replan_calculee = replan_calculee


    @api.depends('date_realise')
    def _compute_mois_realise(self):
        for record in self:
            if record.date_realise:
                record.mois_realise = record.date_realise.strftime('%m/%Y')
            else:
                record.mois_realise = False



    @api.depends('date_prev')
    def _compute_mois_prev(self):
        for record in self:
            if record.date_prev:
                record.mois_prev = record.date_prev.strftime('%m/%Y')
            else:
                record.mois_prev = False

    @api.depends('nb_crit_conformes', 'nb_crit_audites')
    def _compute_pourcent_conform(self):
        for record in self:
            if record.nb_crit_audites != 0:
                record.pourcent_conform = 100 - 100 * record.nb_crit_conformes / record.nb_crit_audites
            else:
                record.pourcent_conform = 0


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
            self.ref_client     = self.article_id.ref_client
            self.fournisseur_id = self.article_id.fournisseur_id.id
        else:
            self.ref_client     = False
            self.fournisseur_id = False

    @api.onchange('article_id', 'moule_id', 'dossierf_id')
    def onchange_client_fields(self):
        """Méthode pour mettre à jour client_id selon l'ordre de priorité"""
        client_id = False
        
        # Ordre de priorité : article_id, moule_id, dossierf_id
        if self.article_id and self.article_id.client_id:
            client_id = self.article_id.client_id.id
        elif self.moule_id and self.moule_id.client_id:
            client_id = self.moule_id.client_id.id
        elif self.dossierf_id and self.dossierf_id.client_id:
            client_id = self.dossierf_id.client_id.id
        
        self.client_id = client_id
