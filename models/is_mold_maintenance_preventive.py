from datetime import date # type: ignore
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


STATE_MAINTENANCE = [
    ("en_cours", "En cours"),
    ("termine",  "Terminé"),
]


FORM_VIEW_BY_TYPE_CONTROLE = {
    'operation_systematique': 'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_operation',
    'operation_particuliere': 'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_operation',
    'circuit_eau_fixe':       'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_circuit',
    'circuit_eau_mobile':     'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_circuit',
    'torpille':               'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_torpille',
    'point_injection':        'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_point_injection',
}


LINES_ACTION_INFO = {
    'operation_systematique': (
        "Opérations systématiques",
        'is_dynacase2odoo.is_mold_maintenance_preventive_line_tree_operation',
        'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_operation',
    ),
    'operation_particuliere': (
        "Spécifications particulières",
        'is_dynacase2odoo.is_mold_maintenance_preventive_line_tree_operation',
        'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_operation',
    ),
    'circuit_eau_fixe': (
        "Circuit d'eau partie fixe",
        'is_dynacase2odoo.is_mold_maintenance_preventive_line_tree_circuit',
        'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_circuit',
    ),
    'circuit_eau_mobile': (
        "Circuit d'eau partie mobile",
        'is_dynacase2odoo.is_mold_maintenance_preventive_line_tree_circuit',
        'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_circuit',
    ),
    'torpille': (
        "Torpilles",
        'is_dynacase2odoo.is_mold_maintenance_preventive_line_tree_torpille',
        'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_torpille',
    ),
    'point_injection': (
        "Points d'injection",
        'is_dynacase2odoo.is_mold_maintenance_preventive_line_tree_point_injection',
        'is_dynacase2odoo.is_mold_maintenance_preventive_line_form_point_injection',
    ),
}


class is_mold_maintenance_preventive(models.Model):
    _name        = "is.mold.maintenance.preventive"
    _description = "Maintenance préventive moule"
    _order       = "id desc"
    _inherit     = ["mail.thread", "mail.activity.mixin"]

    name           = fields.Char("Chrono", readonly=True, copy=False, tracking=True)
    date           = fields.Date("Date", default=fields.Date.context_today, tracking=True)
    createur_id    = fields.Many2one("res.users", string="Créateur", default=lambda self: self.env.user, tracking=True)
    moule_id       = fields.Many2one("is.mold", string="Moule", required=True, tracking=True)
    autres_travaux = fields.Text("Autres travaux réalisés", tracking=True)
    line_ids       = fields.One2many("is.mold.maintenance.preventive.line", "maintenance_id", string="Contrôles")
    operations_specifiques_info = fields.Text("Opérations spécifiques (information)", readonly=True)
    articles_moule_html = fields.Html("Articles liés au moule (information)", compute='_compute_articles_moule_html')
    state          = fields.Selection(STATE_MAINTENANCE, string="État", default="en_cours", required=True, copy=False, tracking=True)
    avancement_ids = fields.One2many("is.mold.maintenance.preventive.avancement", "maintenance_id", string="Avancement")
    nb_lines_operation_systematique = fields.Integer(compute='_compute_nb_lines')
    nb_lines_operation_particuliere = fields.Integer(compute='_compute_nb_lines')
    nb_lines_circuit_eau_fixe       = fields.Integer(compute='_compute_nb_lines')
    nb_lines_circuit_eau_mobile     = fields.Integer(compute='_compute_nb_lines')
    nb_lines_torpille               = fields.Integer(compute='_compute_nb_lines')
    nb_lines_point_injection        = fields.Integer(compute='_compute_nb_lines')


    def action_terminer(self):
        self._check_lines_completed()
        self.write({'state': 'termine'})


    def action_remettre_en_cours(self):
        self.write({'state': 'en_cours'})


    def _line_is_completed(self, line):
        if line.type_controle in ('operation_systematique', 'operation_particuliere'):
            return bool(line.numero and line.numero > 0 and line.ok_nok)
        if line.type_controle in ('circuit_eau_fixe', 'circuit_eau_mobile'):
            return bool(line.numero and line.numero > 0 and line.valeur and line.ok_nok)
        if line.type_controle == 'torpille':
            return bool(line.empreinte_numero and line.empreinte_numero > 0 and line.hauteur_torpille and line.etat_torpille)
        if line.type_controle == 'point_injection':
            return bool(line.empreinte_numero and line.empreinte_numero > 0 and line.diametre_point_injection and line.etat_point_injection)
        return True


    def _check_lines_completed(self):
        for obj in self:
            nb_restant = len(obj.line_ids.filtered(lambda line: not obj._line_is_completed(line)))
            if nb_restant:
                raise ValidationError(
                    "Toutes les lignes doivent être renseignées avant de passer la fiche à l'état 'Terminé'.\n"
                    "Il reste %s point(s) à traiter." % nb_restant
                )


    def _line_etat(self, line):
        if line.type_controle in ('operation_systematique', 'operation_particuliere', 'circuit_eau_fixe', 'circuit_eau_mobile'):
            return line.ok_nok or False
        if line.type_controle == 'torpille':
            return {'ok': 'ok', 'remplacee': 'nok'}.get(line.etat_torpille, False)
        if line.type_controle == 'point_injection':
            return {'ok': 'ok', 'repare': 'nok'}.get(line.etat_point_injection, False)
        return False


    def _build_avancement_commands(self):
        self.ensure_one()
        commands = [(5, 0, 0)]
        for type_value, type_label in TYPE_CONTROLE:
            lines = self.line_ids.filtered(lambda line, type_value=type_value: line.type_controle == type_value)
            total = len(lines)
            if not total:
                continue
            traites = len(lines.filtered(self._line_is_completed))
            nb_ok = len(lines.filtered(lambda line: self._line_etat(line) == 'ok'))
            nb_nok = len(lines.filtered(lambda line: self._line_etat(line) == 'nok'))
            commands.append((0, 0, {
                'type_controle': type_value,
                'nb_ok'        : nb_ok,
                'nb_nok'       : nb_nok,
                'nb_traites'   : traites,
                'nb_total'     : total,
            }))
        return commands


    def _sync_avancement(self):
        for obj in self:
            obj.avancement_ids = obj._build_avancement_commands()


    @api.depends('line_ids.type_controle')
    def _compute_nb_lines(self):
        for obj in self:
            for type_value, _ in TYPE_CONTROLE:
                obj['nb_lines_%s' % type_value] = len(obj.line_ids.filtered(lambda line, type_value=type_value: line.type_controle == type_value))


    @api.depends('moule_id.article_ids.article_id.sous_famille', 'moule_id.article_ids.article_id.temp_transformation')
    def _compute_articles_moule_html(self):
        for obj in self:
            obj.articles_moule_html = obj._build_articles_moule_html()


    def _build_articles_moule_html(self):
        self.ensure_one()
        links = self.moule_id.article_ids
        if not links:
            return False
        rows = []
        for link in links:
            article = link.article_id
            rows.append(
                '<tr>'
                '<td style="padding:4px 8px;">%s</td>'
                '<td style="padding:4px 8px;">%s</td>'
                '<td style="padding:4px 8px;">%s</td>'
                '</tr>' % (article.code_pg or '', article.sous_famille or '', article.temp_transformation or '')
            )
        header = (
            '<tr>'
            '<th style="padding:4px 8px;text-align:left;">Dossier article</th>'
            '<th style="padding:4px 8px;text-align:left;">Sous-Famille</th>'
            '<th style="padding:4px 8px;text-align:left;">T°C transformation (°C)</th>'
            '</tr>'
        )
        return '<table style="width:100%%;border-collapse:collapse;"><thead>%s</thead><tbody>%s</tbody></table>' % (header, ''.join(rows))


    @api.constrains('moule_id', 'state')
    def _check_unique_en_cours(self):
        for obj in self:
            if obj.state == 'en_cours':
                doublon = self.search([
                    ('moule_id', '=', obj.moule_id.id),
                    ('state', '=', 'en_cours'),
                    ('id', '!=', obj.id),
                ])
                if doublon:
                    raise ValidationError("Il existe déjà une fiche de maintenance préventive en cours pour ce moule.")


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('is.mold.maintenance.preventive')
            if vals.get('moule_id') and not vals.get('line_ids'):
                vals['line_ids'] = self._get_default_line_commands(self.env['is.mold'].browse(vals['moule_id']))
        records = super().create(vals_list)
        records._sync_avancement()
        return records


    def _get_default_line_commands(self, moule):
        commands = []
        for op in moule.systematique_ids.filtered('activer'):
            commands.append((0, 0, {
                'type_controle': 'operation_systematique',
                'nom_controle' : op.operation_systematique_id.name,
                'numero'       : op.id,
            }))
        for spec in moule.specification_ids.filtered('activer'):
            commands.append((0, 0, {
                'type_controle': 'operation_particuliere',
                'nom_controle' : spec.specification_particuliere_id.name,
                'numero'       : spec.id,
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
            obj.avancement_ids = obj._build_avancement_commands()


    def _open_lines_action(self, type_controle):
        self.ensure_one()
        name, tree_view_xmlid, form_view_xmlid = LINES_ACTION_INFO[type_controle]
        tree_id = self.env.ref(tree_view_xmlid).id
        form_id = self.env.ref(form_view_xmlid).id
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'res_model': 'is.mold.maintenance.preventive.line',
            'view_mode': 'tree,form',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'domain': [('maintenance_id', '=', self.id), ('type_controle', '=', type_controle)],
            'context': {
                'default_maintenance_id': self.id,
                'default_type_controle': type_controle,
                'readonly_lines': self.state == 'termine',
            },
            'target': 'current',
        }


    def open_lines_operation_systematique_action(self):
        return self._open_lines_action('operation_systematique')

    def open_lines_operation_particuliere_action(self):
        return self._open_lines_action('operation_particuliere')

    def open_lines_circuit_eau_fixe_action(self):
        return self._open_lines_action('circuit_eau_fixe')

    def open_lines_circuit_eau_mobile_action(self):
        return self._open_lines_action('circuit_eau_mobile')

    def open_lines_torpille_action(self):
        return self._open_lines_action('torpille')

    def open_lines_point_injection_action(self):
        return self._open_lines_action('point_injection')


class is_mold_maintenance_preventive_avancement(models.Model):
    _name        = "is.mold.maintenance.preventive.avancement"
    _description = "Avancement maintenance préventive moule"
    _rec_name    = "type_controle"

    maintenance_id = fields.Many2one("is.mold.maintenance.preventive", ondelete='cascade', required=True)
    type_controle   = fields.Selection(TYPE_CONTROLE, string="Type de contrôle", readonly=True)
    nb_ok           = fields.Integer("OK", readonly=True)
    nb_nok          = fields.Integer("nOK", readonly=True)
    nb_traites      = fields.Integer("Traités", readonly=True)
    nb_total        = fields.Integer("Total", readonly=True)
    avancement      = fields.Char("Avancement", compute='_compute_avancement')
    is_complete     = fields.Boolean(compute='_compute_avancement')

    @api.depends('nb_traites', 'nb_total')
    def _compute_avancement(self):
        for obj in self:
            obj.avancement = "%s/%s" % (obj.nb_traites, obj.nb_total)
            obj.is_complete = obj.nb_traites == obj.nb_total

    def open_lines_action(self):
        self.ensure_one()
        return self.maintenance_id._open_lines_action(self.type_controle)


class is_mold_maintenance_preventive_line(models.Model):
    _name        = "is.mold.maintenance.preventive.line"
    _description = "Ligne de maintenance préventive moule"
    _rec_name    = "id"


    maintenance_id     = fields.Many2one("is.mold.maintenance.preventive", ondelete='cascade', required=True)
    maintenance_state  = fields.Selection(related='maintenance_id.state', string="État maintenance")
    type_controle   = fields.Selection(TYPE_CONTROLE, string="Type de contrôle", required=True)
    nom_controle    = fields.Char("Nom du contrôle", readonly=True)
    numero          = fields.Integer("N°")
    valeur          = fields.Float("Valeur", digits=(16, 2))
    ok_nok          = fields.Selection(OK_NOK, string="OK ou nOK")
    commentaire     = fields.Text("Commentaire")
    historique_html = fields.Html("Historique", compute='_compute_historique_html')

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


    def _historique_key_field(self):
        self.ensure_one()
        return 'empreinte_numero' if self.type_controle in ('torpille', 'point_injection') else 'numero'


    def _historique_valeur(self):
        self.ensure_one()
        if self.type_controle in ('circuit_eau_fixe', 'circuit_eau_mobile'):
            return self.valeur
        if self.type_controle == 'torpille':
            return self.hauteur_torpille
        if self.type_controle == 'point_injection':
            return self.diametre_point_injection
        return False


    def _historique_nouvelle_valeur(self):
        self.ensure_one()
        if self.type_controle == 'torpille':
            return self.hauteur_torpille_remplacee
        if self.type_controle == 'point_injection':
            return self.diametre_point_injection_repare
        return False


    @api.depends(
        'maintenance_id.moule_id', 'maintenance_id.date', 'type_controle', 'numero', 'empreinte_numero',
        'valeur', 'hauteur_torpille', 'diametre_point_injection', 'ok_nok', 'etat_torpille', 'etat_point_injection',
        'hauteur_torpille_remplacee', 'diametre_point_injection_repare',
    )
    def _compute_historique_html(self):
        for obj in self:
            obj.historique_html = obj._build_historique_html()


    def _build_historique_html(self):
        self.ensure_one()
        moule = self.maintenance_id.moule_id
        key_field = self._historique_key_field()
        key_value = self[key_field]
        if not moule or not key_value:
            return False
        siblings = self.search([
            ('maintenance_id.moule_id', '=', moule.id),
            ('type_controle', '=', self.type_controle),
            (key_field, '=', key_value),
        ])
        siblings = siblings.sorted(key=lambda line: (line.maintenance_id.date or date.min, line.id))
        if not siblings:
            return False
        has_valeur = self.type_controle not in ('operation_systematique', 'operation_particuliere')
        has_nouvelle_valeur = self.type_controle in ('torpille', 'point_injection')
        badge_style = 'display:inline-block;padding:2px 10px;border-radius:10px;color:#fff;font-weight:bold;'
        rows = []
        nok_label = {'torpille': 'Remplacée', 'point_injection': 'Réparé'}.get(self.type_controle, 'nOK')
        for line in siblings:
            etat = self.maintenance_id._line_etat(line)
            if etat == 'ok':
                badge = '<span style="%sbackground-color:#28a745;">OK</span>' % badge_style
            elif etat == 'nok':
                badge = '<span style="%sbackground-color:#dc3545;">%s</span>' % (badge_style, nok_label)
            else:
                badge = ''
            cell_valeur = '<td style="padding:4px 8px;">%s</td>' % line._historique_valeur() if has_valeur else ''
            if has_nouvelle_valeur:
                nouvelle_valeur = line._historique_nouvelle_valeur() if etat == 'nok' else ''
                cell_nouvelle_valeur = '<td style="padding:4px 8px;">%s</td>' % (nouvelle_valeur or '')
            else:
                cell_nouvelle_valeur = ''
            date_str = line.maintenance_id.date.strftime('%d/%m/%Y') if line.maintenance_id.date else ''
            rows.append(
                '<tr>'
                '<td style="padding:4px 8px;">%s</td>'
                '%s'
                '%s'
                '<td style="padding:4px 8px;">%s</td>'
                '</tr>' % (date_str, cell_valeur, cell_nouvelle_valeur, badge)
            )
        header = (
            '<tr>'
            '<th style="padding:4px 8px;text-align:left;">Date</th>'
            '%s'
            '%s'
            '<th style="padding:4px 8px;text-align:left;">État</th>'
            '</tr>' % (
                '<th style="padding:4px 8px;text-align:left;">Valeur</th>' if has_valeur else '',
                '<th style="padding:4px 8px;text-align:left;">Nouvelle valeur</th>' if has_nouvelle_valeur else '',
            )
        )
        return '<table style="width:100%%;border-collapse:collapse;"><thead>%s</thead><tbody>%s</tbody></table>' % (header, ''.join(rows))


    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines.mapped('maintenance_id')._sync_avancement()
        for obj in lines:
            if obj.type_controle in ('circuit_eau_fixe', 'circuit_eau_mobile'):
                obj._update_ok_nok_circuit()
        return lines


    def unlink(self):
        maintenances = self.mapped('maintenance_id')
        res = super().unlink()
        maintenances._sync_avancement()
        return res


    def _compute_ok_nok_circuit(self):
        self.ensure_one()
        moule = self.maintenance_id.moule_id
        if not moule or not self.numero or not self.valeur:
            return False
        domain = [
            ('maintenance_id.moule_id', '=', moule.id),
            ('type_controle', '=', self.type_controle),
            ('numero', '=', self.numero),
            ('valeur', '!=', 0),
        ]
        if isinstance(self.id, int):
            domain.append(('id', '!=', self.id))
        siblings = self.search(domain)
        siblings = siblings.sorted(key=lambda line: (line.maintenance_id.date or date.min, line.id))
        if not siblings:
            return 'ok'
        premiere_valeur = siblings[0].valeur
        if not premiere_valeur:
            return 'ok'
        ecart = abs(self.valeur - premiere_valeur) / premiere_valeur
        return 'nok' if ecart > 0.25 else 'ok'


    def _update_ok_nok_circuit(self):
        self.ensure_one()
        ok_nok = self._compute_ok_nok_circuit()
        if ok_nok and self.ok_nok != ok_nok:
            super(is_mold_maintenance_preventive_line, self).write({'ok_nok': ok_nok})


    @api.onchange('valeur', 'numero')
    def _onchange_valeur_circuit(self):
        for obj in self:
            if obj.type_controle in ('circuit_eau_fixe', 'circuit_eau_mobile'):
                ok_nok = obj._compute_ok_nok_circuit()
                if ok_nok:
                    obj.ok_nok = ok_nok


    def write(self, vals):
        res = super().write(vals)
        self.mapped('maintenance_id')._sync_avancement()
        for obj in self:
            if obj.type_controle in ('circuit_eau_fixe', 'circuit_eau_mobile'):
                obj._update_ok_nok_circuit()
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


def _check_no_preventive_maintenance_line(records, type_controle):
    lines = records.env['is.mold.maintenance.preventive.line'].search([
        ('type_controle', '=', type_controle),
        ('numero', 'in', records.ids),
    ])
    if lines:
        numeros = ', '.join(str(numero) for numero in sorted(set(lines.mapped('numero'))))
        raise ValidationError(
            "Impossible de supprimer cette ligne : une saisie de maintenance préventive existe déjà "
            "pour le(s) N° %s." % numeros
        )


class is_mold_systematique_array(models.Model):
    _inherit = 'is.mold.systematique.array'

    def unlink(self):
        _check_no_preventive_maintenance_line(self, 'operation_systematique')
        return super().unlink()


class is_mold_specification_array(models.Model):
    _inherit = 'is.mold.specification.array'

    def unlink(self):
        _check_no_preventive_maintenance_line(self, 'operation_particuliere')
        return super().unlink()
