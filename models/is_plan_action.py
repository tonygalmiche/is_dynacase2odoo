import zlib
from odoo import models, fields, api         # type: ignore
from odoo.exceptions import ValidationError  # type: ignore


# Clé de verrou pour éviter les doublons de num_int lors de créations concurrentes (attente, pas d'erreur)
_NUM_INT_LOCK_KEY = zlib.crc32(b'is.plan.action.num_int')


_STATE_ACTION = ([
    ('plan'  , 'Plan'),
    ('do'    , 'Do'),
    ('check' , 'Check'),
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
    constat          = fields.Text("Constat", tracking=True)
    causes_retenues  = fields.Text("Causes retenues", tracking=True)
    preuves_efficacite = fields.Text("Preuves d'efficacité", tracking=True)

    date             = fields.Date("Date de création", default=lambda *a: fields.datetime.now(), tracking=True, copy=False)
    dateplan         = fields.Date("Date prévisionnelle", required=False, tracking=True, copy=False)
    datedo           = fields.Date("Date de réalisation", tracking=True, copy=False)
    datecheck        = fields.Date("Date de vérification", tracking=True, copy=False)

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
    indicateur          = fields.Html(string="Indicateur", compute="_compute_indicateur", store=False)


    @api.depends('state', 'dateplan')
    def _compute_indicateur(self):
        "Indicateur coloré selon l'état (Plan gris ou rouge si en retard, Do bleu, Check vert) avec la date prévisionnelle si en retard"
        gris  = '#dee2e6'  # Gris standard Odoo ($o-gray-300)
        rouge = '#dc3545'  # Rouge standard Odoo ($o-danger)
        colors = {
            'plan'  : gris,
            'do'    : '#17a2b8',  # Bleu standard Odoo ($o-info)
            'check' : '#28a745',  # Vert standard Odoo ($o-success)
            'annule': gris,
        }
        today = fields.Date.context_today(self)
        for obj in self:
            color = colors.get(obj.state, gris)
            label = dict(_STATE_ACTION).get(obj.state, '')
            if obj.state in ('plan', 'do') and obj.dateplan and obj.dateplan < today:
                if obj.state == 'plan':
                    color = rouge
                label += '<br/>%s' % obj.dateplan.strftime('%d/%m/%Y')
            # Texte blanc sur les couleurs foncées (bleu, vert et rouge)
            text_color = 'white' if color in ('#17a2b8', '#28a745', rouge) else 'black'
            obj.indicateur = (
                '<div style="background-color:%s;color:%s;text-align:center;padding:2px 6px;">'
                '%s</div>' % (color, text_color, label)
            )


    def _compute_readonly_all(self):
        """Détermine si l'utilisateur courant peut modifier cet enregistrement"""
        for record in self:
            readonly = True
            if not record.resp_id:
                readonly=False
            else:
                if record.state in ['plan','do']:
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
            # Action sans plan, ou responsable de l'action et pilote du plan : pas besoin de s'autovalider, Check direct
            if not obj.plan_action_id or obj.resp_id == obj.plan_action_id.pilot_id:
                obj.vers_check_action()

    def vers_check_action(self):
        for obj in self:
            obj.state='check'
            obj.datecheck = fields.datetime.now()

    def vers_annule_action(self):
        for obj in self:
            obj.state='annule'

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

    title               = fields.Char('Titre', required=True, tracking=True)
    num_int             = fields.Integer('Numéro interne', tracking=True, copy=False)
    state               = fields.Selection(_STATE, "Etat", default=_STATE[0][0], tracking=True)
    active              = fields.Boolean('Actif', default=True, tracking=True)
    client_id           = fields.Many2one(
        'res.partner',
        'Client',
        tracking=True,
        domain=[("is_company", "=", True), ("customer", "=", True), ("is_code", "like", "90%")]
    )
    processus_id        = fields.Many2one('is.processus', "Processus", tracking=True)
    moule_id            = fields.Many2one('is.mold', 'Moule', tracking=True)
    dossierf_id         = fields.Many2one("is.dossierf", string="Dossier F", tracking=True)
    designation         = fields.Char(string="Désignation Moule/Dossier F", compute="_compute_designation", store=True, readonly=True)
    pilot_id            = fields.Many2one('res.users', 'Pilote', required=True, default=lambda self: self.env.uid, tracking=True)
    group_id            = fields.Many2one('res.groups', "Groupe de consultation", tracking=True)
    obj                 = fields.Text('Objectif', tracking=True)
    date_beg            = fields.Date("Date de création", default=lambda *a: fields.datetime.now(), tracking=True, copy=False)
    date_end            = fields.Date("Date prévisionnelle de clôture", tracking=True, copy=False)
    piece_jointe_ids    = fields.Many2many("ir.attachment", "is_plan_action_piece_jointe_rel", "piece_jointe", "att_id", string="Pièce jointe")
    is_action_ids       = fields.One2many("is.action", "plan_action_id", tracking=True, copy=True)
    nb_actions          = fields.Integer("Nombre d'actions", compute="_compute_nb_actions")
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


    @api.depends('is_action_ids')
    def _compute_nb_actions(self):
        for record in self:
            record.nb_actions = len(record.is_action_ids)


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
        to_assign = [vals for vals in vals_list if "num_int" not in vals]
        if to_assign:
            # Verrou pour éviter que deux créations concurrentes (batch ou transactions différentes)
            # ne calculent le même numéro interne
            self.env.cr.execute("SELECT pg_advisory_xact_lock(%s)", (_NUM_INT_LOCK_KEY,))
            self.env.cr.execute("SELECT COALESCE(MAX(num_int), -1) FROM is_plan_action")
            next_num = self.env.cr.fetchone()[0] + 1
            for vals in to_assign:
                vals["num_int"] = next_num
                next_num += 1
        return super().create(vals_list)

    def copy(self, default=None):
        default = dict(default or {})
        default['title'] = (self.title or '') + ' (copie)'
        new_record = super().copy(default)
        # Poster un message dans le chatter avec le lien vers le plan d'action d'origine
        url = f"/web#id={self.id}&model={self._name}&view_type=form"
        message = f"Copie du plan d'action <a href='{url}'>{self.num_int} - {self.title}</a>"
        new_record.message_post(body=message)
        return new_record

    def vers_actif_action(self):
        for obj in self:
            obj.state='actif'

    def vers_solde_action(self):
        for obj in self:
            obj.state='solde'

    def vers_annule_action(self):
        for obj in self:
            obj.state='annule'

    def action_view_actions(self):
        """Ouvre la liste des actions du plan : depuis la liste, la fiche permet de passer d'une action à l'autre"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': "Actions du plan %s" % self.num_int,
            'res_model': 'is.action',
            'view_mode': 'tree,form',
            'domain': [('plan_action_id', '=', self.id)],
            'context': {'default_plan_action_id': self.id},
        }

    def open_plan_action_form(self):
        """Ouvre la fiche du plan d'action"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': "Plan d'action",
            'res_model': 'is.plan.action',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }
