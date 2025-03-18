from odoo import models, fields  # type: ignore

_STATE = ([
    ('brouillon', 'Brouillon'),
    ('diffuse', 'Diffusé'),
    ('realise', 'Réalisé'),
])


class is_prise_avance(models.Model):
    _name='is.prise.avance'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Prise d'avance"
    _rec_name = "num_moule_id"
    _order='num_moule_id'

    num_moule_id                = fields.Many2one('is.mold', 'Numéro du moule', required=True, tracking=True)
    active                      = fields.Boolean('Actif', default=True, tracking=True)
    user_id                     = fields.Many2one('res.users', 'Demandeur', tracking=True, default=lambda self: self.env.uid)
    resp_prise_avance_id        = fields.Many2one('res.users', "Responsable de la prise d'avance", tracking=True)
    motif_prise_avance          = fields.Selection([('m', 'Modification outillage'), ('t', 'Transfert outillage')], "Motif de la prise d'avance", tracking=True)
    immobilisation              = fields.Boolean("Immobilisation complète", tracking=True)
    pieces_modif                = fields.Boolean("Pièces avant modification livrables", tracking=True)
    duree_immobilisation        = fields.Integer(string="Durée de l'immobilisation en jours ouvrables")
    nb_jours                    = fields.Integer(string="Nombre de jours à couvrir", tracking=True)
    pieces_stck                 = fields.Integer(string="Nombre de pièces à avoir en stock à la fin de la prise d'avance", tracking=True)
    date_outillage              = fields.Date("Date de mise à disposition de l'outillage", tracking=True)
    date_retour_outillage       = fields.Date("Date de retour souhaité de l'outillage", tracking=True)
    state                       = fields.Selection(_STATE, "Etat", default=_STATE[0][0], required=True, tracking=True)
    dynacase_id                 = fields.Integer(string="Id Dynacase", index=True, copy=False)

    def vers_diffuse_action(self):
        for obj in self:
            obj.state='diffuse'

    def vers_realise_action(self):
        for obj in self:
            obj.state='realise'

    def vers_brouillon_action(self):
        for obj in self:
            obj.state='brouillon'

    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
