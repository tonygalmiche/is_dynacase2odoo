from odoo import models, fields, api  # type: ignore

_STATE = ([
    ('brouillon', 'Brouillon'),
    ('diffuse', 'Diffusé'),
    ('termine', 'Terminé'),
])


class is_demande_modif_compte_fournisseur(models.Model):
    _name='is.demande.modif.compte.fournisseur'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Prise d'avance"
    _rec_name = "titre"
    _order='num_ordre desc'

    titre                     = fields.Char(string="Titre du document", tracking=True, compute='_compute_title', readonly=True, store=True)
    num_ordre                 = fields.Integer(string="Numéro d'ordre de la demande", tracking=True)
    societe_ids               = fields.Many2many('is.database','is_demande_modif_compte_fournisseur_database_rel','demande_modif_compte_fournisseur_id','database_id', string="Société", tracking=True)
    fournisseur_id            = fields.Many2one('res.partner', 'Nom du fournisseur', tracking=True)
    fournisseur_autre         = fields.Char(string="Nom du fournisseur (Autre pour création)", tracking=True)
    code_fournisseur          = fields.Integer("Code fournisseur", tracking=True, compute="_compute_fournisseur", readonly=True, store=True)
    code_fournisseur_creation = fields.Char(string="Code fournisseur (si création)", tracking=True)
    date_creation             = fields.Date("Date de création de la demande", tracking=True, default=lambda *a: fields.datetime.now())
    createur_id               = fields.Many2one('res.users', "Créateur de la demande", tracking=True, default=lambda self: self.env.uid)
    responsable_action_id     = fields.Many2one("res.users", "Responsable de l'action", tracking=True, required=True)
    motif                     = fields.Text(string="Motif", tracking=True, required=True)
    state                     = fields.Selection(_STATE, "Etat", default=_STATE[0][0], required=True, tracking=True)
    dynacase_id               = fields.Integer(string="Id Dynacase", index=True, copy=False)
    piece_jointe_ids          = fields.Many2many("ir.attachment", "is_demande_modif_compte_fournisseur_piece_jointe_rel", "piece_jointe", "att_id", string="Pièce jointe")
    active                     = fields.Boolean('Actif', default=True, tracking=True)


    def vers_diffuse_action(self):
        for obj in self:
            obj.state='diffuse'

    def vers_termine_action(self):
        for obj in self:
            obj.state='termine'

    def vers_brouillon_action(self):
        for obj in self:
            obj.state='brouillon'
            
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "num_ordre" not in vals:
                last = self.env["is.demande.modif.compte.fournisseur"].search([('num_ordre', '!=', None)], order="num_ordre desc", limit=1)
                if last:
                    num_ordre = last.num_ordre
                else:
                    num_ordre = 0
                vals["num_ordre"] = num_ordre + 1
        return super().create(vals_list)

    @api.depends('num_ordre', 'fournisseur_id', 'fournisseur_autre')
    def _compute_title(self):
        for obj in self:
            title = f"{obj.num_ordre} - "
            if obj.fournisseur_id:
                title += obj.fournisseur_id.name
            elif obj.fournisseur_autre:
                title += obj.fournisseur_autre
            obj.titre = title

    @api.depends('fournisseur_id')
    def _compute_fournisseur(self):
        for obj in self:
            obj.code_fournisseur = obj.fournisseur_id.is_code

    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
