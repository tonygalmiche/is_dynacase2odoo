from odoo import models, fields, api         # type: ignore
from odoo.exceptions import ValidationError  # type: ignore


_STATE = ([
    ('actif' , 'Actif'),
    ('solde'  , 'Soldé'),
    ('annule'    , 'Annulé'),
])


class is_plan_action(models.Model):
    _name='is.plan.action'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Plan d'action"
    _rec_name = "num_int"
    _order='num_int desc'

    title               = fields.Char('Libellé', required=True, tracking=True)
    num_int             = fields.Integer('Numéro interne', tracking=True)
    state               = fields.Selection(_STATE, "Etat", default=_STATE[0][0], tracking=True)
    active              = fields.Boolean('Actif', default=True, tracking=True)
    client_id           = fields.Many2one('res.partner', 'Client', tracking=True, domain=[("is_company","=",True), ("customer","=",True)])
    moule_id            = fields.Many2one('is.mold', 'Moule', tracking=True)
    dossierf_id         = fields.Many2one("is.dossierf", string="Dossier F", tracking=True)
    pilot_id            = fields.Many2one('res.users', 'Pilote', required=True, default=lambda self: self.env.uid, tracking=True)
    group_id            = fields.Many2one('res.groups', "Groupe d'accès en consultation", tracking=True)
    obj                 = fields.Text('Objectif', tracking=True)
    date_beg            = fields.Date("Date début", default=lambda *a: fields.datetime.now(), tracking=True)
    date_end            = fields.Date("Date clôture", tracking=True)
    action_prev         = fields.Text("action préventive ou transversalisable", tracking=True)
    piece_jointe_ids    = fields.Many2many("ir.attachment", "is_plan_action_piece_jointe_rel", "piece_jointe", "att_id", string="Pièce jointe")
    dynacase_id         = fields.Integer(string="Id Dynacase", index=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if self._rec_name not in vals:
                last = self.env[self._name].search([(self._rec_name, '!=', None)], order=self._rec_name + " desc", limit=1)
                if last:
                    vals[self._rec_name] = getattr(last, self._rec_name) + 1
                else:
                    vals[self._rec_name] = 0
        return super().create(vals_list)

    def vers_actif_action(self):
        for obj in self:
            obj.state='actif'

    def vers_solde_action(self):
        for obj in self:
            obj.state='solde'

    def vers_annule_action(self):
        for obj in self:
            obj.state='annule'

    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
