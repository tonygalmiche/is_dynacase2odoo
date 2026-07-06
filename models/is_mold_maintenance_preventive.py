from odoo import models, fields, api # type: ignore
from odoo.exceptions import ValidationError # type: ignore


TYPE_CONTROLE = [
    ("operation_systematique", "Opération systématique"),
    ("operation_particuliere", "Opération particulière"),
    ("circuit_eau_fixe",       "Circuit d'eau partie fixe"),
    ("circuit_eau_mobile",     "Circuit d'eau partie mobile"),
    ("torpille",               "Torpille"),
    ("point_injection",        "Point d'injection"),
]


OK_NOK = [
    ("ok",  "OK"),
    ("nok", "nOK"),
]


ETAT_TORPILLE = [
    ("ok",        "OK"),
    ("remplacee", "Remplacée"),
]


ETAT_POINT_INJECTION = [
    ("ok",     "OK"),
    ("repare", "Réparé"),
]


FORM_VIEW_BY_TYPE_CONTROLE = {
    'operation_systematique': 'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_operation',
    'operation_particuliere': 'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_operation',
    'circuit_eau_fixe':       'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_circuit',
    'circuit_eau_mobile':     'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_circuit',
    'torpille':               'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_torpille',
    'point_injection':        'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_point_injection',
}


class is_mold_maintenance_preventive(models.Model):
    _name        = "is.mold.maintenance.preventive"
    _description = "Maintenance préventive moule"
    _order       = "id desc"

    name           = fields.Char("Chrono", readonly=True, copy=False)
    date           = fields.Date("Date", default=fields.Date.context_today)
    createur_id    = fields.Many2one("res.users", string="Créateur", default=lambda self: self.env.user)
    moule_id       = fields.Many2one("is.mold", string="Moule", required=True)
    autres_travaux = fields.Text("Autres travaux réalisés")
    line_ids       = fields.One2many("is.mold.maintenance.preventive.line", "maintenance_id", string="Contrôles")
    operations_specifiques_info = fields.Text("Opérations spécifiques (information)")


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('is.mold.maintenance.preventive')
            if vals.get('moule_id') and not vals.get('line_ids'):
                vals['line_ids'] = self._get_default_line_commands(self.env['is.mold'].browse(vals['moule_id']))
        return super().create(vals_list)


    def _get_default_line_commands(self, moule):
        commands = []
        for op in moule.systematique_ids.filtered('activer'):
            commands.append((0, 0, {
                'type_controle': 'operation_systematique',
                'nom_controle' : op.operation_systematique_id.name,
            }))
        for spec in moule.specification_ids.filtered('activer'):
            commands.append((0, 0, {
                'type_controle': 'operation_particuliere',
                'nom_controle' : spec.specification_particuliere_id.name,
            }))
        for _ in range(int(moule.nb_circuit_eau_fixe or 0)):
            commands.append((0, 0, {'type_controle': 'circuit_eau_fixe'}))
        for _ in range(int(moule.nb_circuit_eau_mobile or 0)):
            commands.append((0, 0, {'type_controle': 'circuit_eau_mobile'}))
        for _ in range(moule.nb_torpilles or 0):
            commands.append((0, 0, {'type_controle': 'torpille'}))
        for _ in range(moule.nb_points_injection or 0):
            commands.append((0, 0, {'type_controle': 'point_injection'}))
        return commands


    @api.onchange('moule_id')
    def _onchange_moule_id(self):
        for obj in self:
            obj.line_ids = obj._get_default_line_commands(obj.moule_id) if obj.moule_id else [(5, 0, 0)]
            noms = obj.moule_id.specifique_ids.filtered('activer').mapped('operation_specifique_id.name')
            obj.operations_specifiques_info = '\n'.join(noms) if noms else False


    def _open_lines_action(self, type_controle, name, tree_view_xmlid, form_view_xmlid):
        self.ensure_one()
        tree_id = self.env.ref(tree_view_xmlid).id
        form_id = self.env.ref(form_view_xmlid).id
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'res_model': 'is.mold.maintenance.preventive.line',
            'view_mode': 'tree,form',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'domain': [('maintenance_id', '=', self.id), ('type_controle', '=', type_controle)],
            'context': {'default_maintenance_id': self.id, 'default_type_controle': type_controle},
            'target': 'current',
        }


    def open_lines_operation_systematique_action(self):
        return self._open_lines_action('operation_systematique', "Opérations systématiques",
            'is_dynacase2odoo.is_mold_maintenance_preventive_line_tree_operation',
            'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_operation')

    def open_lines_operation_particuliere_action(self):
        return self._open_lines_action('operation_particuliere', "Spécifications particulières",
            'is_dynacase2odoo.is_mold_maintenance_preventive_line_tree_operation',
            'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_operation')

    def open_lines_circuit_eau_fixe_action(self):
        return self._open_lines_action('circuit_eau_fixe', "Circuit d'eau partie fixe",
            'is_dynacase2odoo.is_mold_maintenance_preventive_line_tree_circuit',
            'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_circuit')

    def open_lines_circuit_eau_mobile_action(self):
        return self._open_lines_action('circuit_eau_mobile', "Circuit d'eau partie mobile",
            'is_dynacase2odoo.is_mold_maintenance_preventive_line_tree_circuit',
            'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_circuit')

    def open_lines_torpille_action(self):
        return self._open_lines_action('torpille', "Torpilles",
            'is_dynacase2odoo.is_mold_maintenance_preventive_line_tree_torpille',
            'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_torpille')

    def open_lines_point_injection_action(self):
        return self._open_lines_action('point_injection', "Points d'injection",
            'is_dynacase2odoo.is_mold_maintenance_preventive_line_tree_point_injection',
            'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_point_injection')


class is_mold_maintenance_preventive_line(models.Model):
    _name        = "is.mold.maintenance.preventive.line"
    _description = "Ligne de maintenance préventive moule"
    _rec_name    = "id"


    maintenance_id  = fields.Many2one("is.mold.maintenance.preventive", ondelete='cascade', required=True)
    type_controle   = fields.Selection(TYPE_CONTROLE, string="Type de contrôle", required=True)
    nom_controle    = fields.Char("Nom du contrôle", readonly=True)
    numero          = fields.Integer("N°")
    valeur          = fields.Float("Valeur", digits=(16, 2))
    ok_nok          = fields.Selection(OK_NOK, string="OK ou nOK")
    commentaire     = fields.Text("Commentaire")
    historique_html = fields.Html("Historique", readonly=True)

    empreinte_numero            = fields.Integer("N° empreinte")
    hauteur_torpille             = fields.Float("Hauteur torpille (mm)", digits=(16, 2))
    etat_torpille                = fields.Selection(ETAT_TORPILLE, string="État torpille")
    hauteur_torpille_remplacee   = fields.Float("Hauteur torpille remplacée (mm)", digits=(16, 2))

    diametre_point_injection         = fields.Float("Diamètre point d'injection (mm)", digits=(16, 2))
    etat_point_injection             = fields.Selection(ETAT_POINT_INJECTION, string="État point d'injection")
    diametre_point_injection_repare  = fields.Float("Diamètre point d'injection réparé (mm)", digits=(16, 2))

    pager_info = fields.Char("Position", compute='_compute_pager_info')


    def _get_siblings_ids(self):
        self.ensure_one()
        return self.search([
            ('maintenance_id', '=', self.maintenance_id.id),
            ('type_controle', '=', self.type_controle),
        ], order='id').ids


    @api.depends('maintenance_id', 'type_controle')
    def _compute_pager_info(self):
        for obj in self:
            ids = obj._get_siblings_ids() if obj.id else []
            obj.pager_info = "(%s/%s)" % (ids.index(obj.id) + 1, len(ids)) if obj.id in ids else False


    def _navigate_action(self, delta):
        self.ensure_one()
        ids = self._get_siblings_ids()
        new_index = ids.index(self.id) + delta
        if not 0 <= new_index < len(ids):
            return False
        res_id = ids[new_index]
        form_id = self.env.ref(FORM_VIEW_BY_TYPE_CONTROLE[self.type_controle]).id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'is.mold.maintenance.preventive.line',
            'res_id': res_id,
            'view_mode': 'form',
            'views': [(form_id, 'form')],
            'target': 'current',
        }


    def action_precedent(self):
        return self._navigate_action(-1)

    def action_suivant(self):
        return self._navigate_action(1)


    @api.onchange('etat_torpille')
    def _onchange_etat_torpille(self):
        for obj in self:
            if obj.etat_torpille == 'remplacee':
                obj.historique_html = (obj.historique_html or '') + '<p>R</p>'


    def write(self, vals):
        res = super().write(vals)
        for obj in self:
            if obj.type_controle in ('operation_systematique', 'operation_particuliere') and obj.numero <= 0:
                raise ValidationError("Le N° doit être supérieur à 0 pour une opération systématique ou particulière.")
            if obj.type_controle in ('circuit_eau_fixe', 'circuit_eau_mobile'):
                if obj.numero <= 0:
                    raise ValidationError("Le N° doit être supérieur à 0 pour un circuit d'eau.")
                if obj.valeur <= 0:
                    raise ValidationError("La valeur doit être supérieure à 0 pour un circuit d'eau.")
            if obj.type_controle == 'torpille':
                if obj.empreinte_numero <= 0:
                    raise ValidationError("Le N° empreinte doit être supérieur à 0 pour une torpille.")
                if obj.hauteur_torpille <= 0:
                    raise ValidationError("La hauteur torpille doit être supérieure à 0.")
                if obj.etat_torpille == 'remplacee' and obj.hauteur_torpille_remplacee <= 0:
                    raise ValidationError("La hauteur torpille remplacée doit être supérieure à 0.")
            if obj.type_controle == 'point_injection':
                if obj.empreinte_numero <= 0:
                    raise ValidationError("Le N° empreinte doit être supérieur à 0 pour un point d'injection.")
                if obj.diametre_point_injection <= 0:
                    raise ValidationError("Le diamètre point d'injection doit être supérieur à 0.")
                if obj.etat_point_injection == 'repare' and obj.diametre_point_injection_repare <= 0:
                    raise ValidationError("Le diamètre point d'injection réparé doit être supérieur à 0.")
            obj._check_numero_unique()
        return res


    def _check_numero_unique(self):
        self.ensure_one()
        field_name = 'empreinte_numero' if self.type_controle in ('torpille', 'point_injection') else 'numero'
        value = self[field_name]
        doublon = self.search([
            ('maintenance_id', '=', self.maintenance_id.id),
            ('type_controle', '=', self.type_controle),
            (field_name, '=', value),
            ('id', '!=', self.id),
        ])
        if doublon:
            label = "N° empreinte" if field_name == 'empreinte_numero' else "N°"
            raise ValidationError("Ce %s est déjà utilisé pour ce type de contrôle sur cette fiche." % label)
