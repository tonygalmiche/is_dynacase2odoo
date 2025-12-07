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
    dateplan         = fields.Date("Date de fin prévue", required=False, tracking=True)
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

    # Champ calculé pour détecter si l'utilisateur peut modifier
    readonly_all        = fields.Boolean(string="Lecture seule", compute="_compute_readonly_all", store=False)


    def _compute_readonly_all(self):
        """Détermine si l'utilisateur courant peut modifier cet enregistrement"""
        for record in self:
            readonly = True
            if not record.resp_id:
                readonly=False
            else:
                if record.state in ['plan','do','check']:
                    try:
                        # Vérifier si l'utilisateur peut écrire sur cet enregistrement
                        record.check_access_rights('write')
                        record.check_access_rule('write')
                        readonly = False
                    except Exception:
                        # Si une exception est levée, l'utilisateur n'a pas le droit d'écriture
                        readonly = True
            record.readonly_all = readonly


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

    def open_action_form(self):
        """Ouvre la fiche complète de l'action"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Action',
            'res_model': 'is.action',
            'res_id': self.id,
            'view_mode': 'form',
        }


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
    client_id           = fields.Many2one(
        'res.partner',
        'Client',
        tracking=True,
        domain=[("is_company", "=", True), ("customer", "=", True), ("is_code", "like", "90%")]
    )
    moule_id            = fields.Many2one('is.mold', 'Moule', tracking=True)
    dossierf_id         = fields.Many2one("is.dossierf", string="Dossier F", tracking=True)
    designation         = fields.Char(string="Désignation Moule/Dossier F", compute="_compute_designation", store=True, readonly=True)
    pilot_id            = fields.Many2one('res.users', 'Pilote', required=True, default=lambda self: self.env.uid, tracking=True)
    group_id            = fields.Many2one('res.groups', "Groupe d'accès en consultation", tracking=True)
    obj                 = fields.Text('Objectif', tracking=True)
    date_beg            = fields.Date("Date début", default=lambda *a: fields.datetime.now(), tracking=True)
    date_end            = fields.Date("Date clôture", tracking=True)
    action_prev         = fields.Text("action préventive ou transversalisable", tracking=True)
    piece_jointe_ids    = fields.Many2many("ir.attachment", "is_plan_action_piece_jointe_rel", "piece_jointe", "att_id", string="Pièce jointe")
    is_action_ids       = fields.One2many("is.action", "plan_action_id", tracking=True)
    dynacase_id         = fields.Integer(string="Id Dynacase", index=True, copy=False)
    responsables_ids    = fields.Many2many("res.users", string="Responsables des actions", compute="_compute_responsables_ids", store=True, readonly=True)
    readonly_all        = fields.Boolean(string="Lecture seule", compute="_compute_readonly_all", store=False)

    def name_get(self):
        result = []
        for record in self:
            name = str(record.num_int or '')
            if record.title:
                name = f"{name} - {record.title}"
            result.append((record.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('num_int', '=', name if name.isdigit() else 0), ('title', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)


    @api.depends('moule_id', 'dossierf_id')
    def _compute_designation(self):
        for record in self:
            if record.moule_id:
                record.designation = record.moule_id.designation
            elif record.dossierf_id:
                record.designation = record.dossierf_id.designation
            else:
                record.designation = ''


    @api.depends('is_action_ids.resp_id')
    def _compute_responsables_ids(self):
        """Calcule la liste des responsables des actions associées"""
        for record in self:
            responsables = record.is_action_ids.mapped('resp_id')
            record.responsables_ids = responsables

    @api.depends('pilot_id')
    def _compute_readonly_all(self):
        """Détermine si l'utilisateur courant peut modifier cet enregistrement"""
        for record in self:
            readonly = True
            if record.state=='actif':
                try:
                    # Vérifier si l'utilisateur peut écrire sur cet enregistrement
                    record.check_access_rights('write')
                    record.check_access_rule('write')
                    readonly = False
                except Exception:
                    # Si une exception est levée, l'utilisateur n'a pas le droit d'écriture
                    readonly = True
            record.readonly_all = readonly


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
