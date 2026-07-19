from odoo import models, fields, api # type: ignore
from odoo.addons.is_dynacase2odoo.models.is_param_project import GESTION_J, TYPE_DOCUMENT # type: ignore
from odoo.addons.is_dynacase2odoo.models.is_mold_maintenance_preventive import TYPE_CONTROLE # type: ignore


NOK_LABEL_BY_TYPE_CONTROLE = {
    'torpille':        'Remplacée',
    'point_injection': 'Réparé',
}


TYPE_EXPORT = [
    ("definitif", "Définitif"),
    ("temporaire", "Temporaire"),
]


OUI_NON = [
    ("oui", "Oui"),
    ("non", "Non"),
    ]


TYPE_IMPORT = [
    ("retour_definitif", "Retour définitif"),
    ("admission_temporaire_reparation", "Admission temporaire réparation"),
    ("perfectionnement_actifi_reparation", "Perfectionnement actif réparation"),
    ("retour_suite_export_temporaire", "Retour suite export temporaire"),
]


class is_mold(models.Model):
    _inherit = 'is.mold'

    image                  = fields.Binary('Image')
    dossier_appel_offre_id = fields.Many2one("is.dossier.appel.offre", string="Dossier appel d'offre", copy=False, tracking=True)
    revue_contrat_id       = fields.Many2one("is.revue.de.contrat"   , string="Revue de contrat"     , copy=False, tracking=True)
    revue_lancement_id     = fields.Many2one("is.revue.lancement"    , string="Revue de lancement"   , copy=False, tracking=True)
    revue_risque_id        = fields.Many2one("is.revue.risque"       , string="Revue des risques"    , copy=False, tracking=True)
    j_actuelle             = fields.Selection(GESTION_J, string="J Actuelle", default="J0"           , copy=False, tracking=True)
    j_avancement           = fields.Integer(string="Avancement J (%)"                                , copy=False, tracking=True)
    date_fin_be            = fields.Date(string="Date fin BE"                                        , copy=False)
    article_ids            = fields.One2many('is.mold.dossierf.article', 'mold_id')
    fermeture_id           = fields.Many2one("is.fermeture.gantt", string="Fermeture planning")
    logo_rs                = fields.Char(string="Logo RS"         , compute='_compute_logo_rs'      , store=False, readonly=True)
    j_actuelle_rw          = fields.Boolean(string="J Actuelle rw", compute='_compute_j_actuelle_rw', store=False, readonly=True)

    is_modele              = fields.Boolean("Modèle", default=False, tracking=True,
        help="Cochez cette case pour marquer ce moule comme un modèle.\n"
             "Seul le groupe 'Directeur technique' peut cocher/décocher ce champ.\n"
             "Un moule modèle est visible par tous les utilisateurs en lecture seule,\n"
             "mais il ne peut être modifié, et aucun document ne peut y être créé ou modifié,\n"
             "sauf par le groupe 'Directeur technique'.")
    is_modele_rw           = fields.Boolean(string="Modèle rw", compute='_compute_is_modele_rw', store=False, readonly=True)

    date_export            = fields.Date("Date d'exportation", tracking=True)
    type_export            = fields.Selection(TYPE_EXPORT, string="Type d'exportation", tracking=True)
    marche_ce_export       = fields.Selection(OUI_NON, string="Outillage pour marché CE", tracking=True)
    valeur_declaree_export = fields.Float("Valeur déclarée", tracking=True)
    commentaire_export     = fields.Text("Commentaire exportation", tracking=True)
    pj_export_ids          = fields.Many2many("ir.attachment", "is_mold_pj_export_rel", "piece_jointe", "att_id", string="Pièce jointe exportation")

    date_import            = fields.Date(string="Date d'importation", tracking=True)
    type_import            = fields.Selection(TYPE_IMPORT, string="Type d'importation", tracking=True)
    date_taxation_import   = fields.Date(string="Date taxation moule", tracking=True)
    commentaire_import     = fields.Text("Commentaire importation", tracking=True)
    pj_import_ids          = fields.Many2many("ir.attachment", "is_mold_pj_import_rel", "piece_jointe", "att_id", string="Pièce jointe importation")


    @api.model_create_multi
    def create(self, vals_list):
        res=super().create(vals_list)
        company = self.env.user.company_id
        if company.is_base_principale:
            res.envoi_mail()
        return res


    def envoi_mail(self):
        template = self.env.ref('is_dynacase2odoo.is_mold_mail_template').sudo()     
        email_values = {
            'email_to'      : self.get_email_to(),
            'auto_delete'   : False,
            'scheduled_date': False,
        }
        template.send_mail(self.id, force_send=True, raise_exception=False, email_values=email_values)


    def get_users(self):
        for obj in self:
            users=[]
            users.append(self.env.user)
            if obj.chef_projet_id:
                users.append(obj.chef_projet_id)
            if obj.client_id.user_id:
                users.append(obj.client_id.user_id)
            return users


    def get_email_to(self):
        for obj in self:
            email_to=False
            users = obj.get_users()
            if users:
                email_to=[]
                for user in users:
                    email_to.append(user.partner_id.email)
                email_to = ', '.join(email_to)
            return email_to


    def get_doc_url(self):
        for obj in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = base_url + '/web#id=%s' '&view_type=form&model=%s'%(obj.id,self._name)
            return url


    @api.depends('j_actuelle')
    def _compute_j_actuelle_rw(self):
        admin = self.env.user.has_group('base.group_system')
        for obj in self:
            rw = False
            if admin:
                rw=True
            obj.j_actuelle_rw = rw

    def _compute_is_modele_rw(self):
        rw = self.env.user.has_group('is_plastigray16.is_directeur_technique_group')
        for obj in self:
            obj.is_modele_rw = rw


    @api.depends('revue_contrat_id')
    def _compute_logo_rs(self):
        for obj in self:
            logo_rs = False
            if obj.revue_contrat_id:
                logo_rs = obj.revue_contrat_id.get_logo_rs()
            obj.logo_rs = logo_rs


    @api.depends('revue_contrat_id')
    def _compute_logo_rs(self):
        for obj in self:
            logo_rs = False
            if obj.revue_contrat_id:
                logo_rs = obj.revue_contrat_id.get_logo_rs()
            obj.logo_rs = logo_rs


    def creer_fiche_maintenance_preventive_action(self):
        self.ensure_one()
        fiche_en_cours = self.env['is.mold.maintenance.preventive'].search([
            ('moule_id', '=', self.id),
            ('state', '=', 'en_cours'),
        ], limit=1)
        return {
            'name': 'Maintenance préventive moule',
            'type': 'ir.actions.act_window',
            'res_model': 'is.mold.maintenance.preventive',
            'view_mode': 'form',
            'res_id': fiche_en_cours.id,
            'target': 'current',
            'context': {'default_moule_id': self.id},
        }


    def gantt_action(self):
        for obj in self:
            domain=[('idmoule', '=', obj.id)]
            view_mode = 'dhtmlxgantt_project,tree,form,kanban,calendar,pivot,graph'
            return self.env['is.doc.moule'].list_doc(obj,domain,view_mode=view_mode)


    def archiver_documents_action(self):
        for obj in self:
            domain=[
                ('idmoule'         ,'=', obj.id),
                #('dossierf_id'     ,'=', obj.id),
            ]
            docs=self.env['is.doc.moule'].search(domain)
            for doc in docs:
                doc.active = False

    def _get_preventive_matrix(self):
        self.ensure_one()
        fiches = self.env['is.mold.maintenance.preventive'].search([('moule_id', '=', self.id)], order='date, id')
        blocks = []
        for type_value, type_label in TYPE_CONTROLE:
            key_field = 'empreinte_numero' if type_value in ('torpille', 'point_injection') else 'numero'
            row_labels = {}
            row_order = []
            cell_map = {}
            for fiche in fiches:
                lines = fiche.line_ids.filtered(lambda line, tv=type_value: line.type_controle == tv)
                for line in lines:
                    key = line[key_field]
                    if key not in row_labels:
                        row_labels[key] = line.nom_controle or str(key)
                        row_order.append(key)
                    cell_map[(key, fiche.id)] = line
            if not row_order:
                continue
            row_order.sort(key=lambda k: k or 0)
            rows = []
            for key in row_order:
                cells = [self._build_preventive_cell(cell_map.get((key, fiche.id))) for fiche in fiches]
                rows.append({'label': row_labels[key], 'numero': key, 'cells': cells})
            blocks.append({'type_controle': type_value, 'label': type_label, 'fiches': fiches, 'rows': rows})
        return blocks


    def _build_preventive_cell(self, line):
        if not line:
            return False
        etat = line.maintenance_id._line_etat(line)
        badge_label = {'ok': 'OK', 'nok': NOK_LABEL_BY_TYPE_CONTROLE.get(line.type_controle, 'nOK')}.get(etat, '')
        return {
            'etat'           : etat,
            'badge_label'    : badge_label,
            'valeur'         : line._historique_valeur(),
            'nouvelle_valeur': line._historique_nouvelle_valeur() if etat == 'nok' else False,
            'commentaire'    : line.commentaire,
        }


    def get_dimensions(self):
        """Retourne les dimensions du moule sous la forme Largeur*Hauteur*Epaisseur.
        Utilise les dimensions hors tout si renseignées, sinon les dimensions standard."""
        self.ensure_one()
        larg = self.largeur_hors_tout or self.largeur
        haut = self.hauteur_hors_tout or self.hauteur
        epai = self.epaisseur_hors_tout or self.epaisseur
        return f"{larg}*{haut}*{epai}" if (larg or haut or epai) else ""


class is_mold_dossierf_article(models.Model):
    _name        = "is.mold.dossierf.article"
    _description = "Articles associés aux moules ou dossier F"
    _order       = 'article_id'

    mold_id          = fields.Many2one("is.mold", string="Moule"         , ondelete='cascade')
    dossierf_id      = fields.Many2one("is.dossierf", string="Dossier F", ondelete='cascade')
    article_id       = fields.Many2one("is.dossier.article", string="Dossier article")
    planning         = fields.Boolean(string="Utiliser ce planning",default=False, help="Utiliser le planning de ce moule ou dossier F pour cet article")
