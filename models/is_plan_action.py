from odoo import models, fields, api         # type: ignore
from odoo.exceptions import ValidationError  # type: ignore


_STATE_ACTION = ([
    ('plan'  , 'Plan'),
    ('do'    , 'Do'),
    ('check' , 'Check'),
    ('act'   , 'Act'),
    ('annule', 'Annulé'),
])


_STATE = ([
    ('actif'  , 'Actif'),
    ('solde'  , 'Soldé'),
    ('annule' , 'Annulé'),
])


class is_action(models.Model):
    _name = "is.action"
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Action"
    _rec_name = "title"
#    _order='order desc'

    state            = fields.Selection(_STATE_ACTION, "Etat", default=_STATE_ACTION[0][0], tracking=True)
    active           = fields.Boolean('Actif', default=True, tracking=True)
    title            = fields.Text("Action à réaliser", required=True, tracking=True)
    resp_id          = fields.Many2one("res.users", string="Responsable", required=True, tracking=True)
    risque           = fields.Text("Risque", tracking=True)
    comment          = fields.Text("Commentaire", tracking=True)

    date             = fields.Date("Date de création", default=lambda *a: fields.datetime.now(), tracking=True)
    dateplan         = fields.Date("Date de fin prévue", required=True, tracking=True)
    datedo           = fields.Date("Date terminée", tracking=True)
    datecheck        = fields.Date("Date de vérification", tracking=True)

    file_ids         = fields.Many2many("ir.attachment", "is_action_file_rel", "file", "att_id", string="Fichiers")

#    site       = fields.Char("Site", tracking=True)
#    service    = fields.Char("Service", tracking=True)
    plan_action_id   = fields.Many2one('is.plan.action', "Plan d'action")
    pilot_id         = fields.Many2one(related='plan_action_id.pilot_id')
    num_moule        = fields.Many2one(related='plan_action_id.moule_id')
    num_dossierf     = fields.Many2one(related='plan_action_id.dossierf_id')
    client           = fields.Many2one(related='plan_action_id.client_id')
    date_beg         = fields.Date(related='plan_action_id.date_beg')
    date_end         = fields.Date(related='plan_action_id.date_end')
    dynacase_id      = fields.Integer(string="Id Dynacase", index=True, copy=False)

    def vers_plan_action(self):
        for obj in self:
            obj.state='plan'

    def vers_do_action(self):
        for obj in self:
            obj.state='do'
            obj.datedo = fields.datetime.now()

    def vers_check_action(self):
        for obj in self:
            obj.state='check'
            obj.datecheck = fields.datetime.now()

    def vers_act_action(self):
        for obj in self:
            obj.state='act'

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


class is_plan_action(models.Model):
    _name='is.plan.action'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Plan d'action"
    _rec_name = "title"
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
    is_action_ids       = fields.One2many("is.action", "plan_action_id", tracking=True)
    dynacase_id         = fields.Integer(string="Id Dynacase", index=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "num_int" not in vals:
                last = self.env[self._name].search([("num_int", '!=', None)], order="num_int desc", limit=1)
                if last:
                    vals["num_int"] = last.num_int + 1
                else:
                    vals["num_int"] = 0
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
