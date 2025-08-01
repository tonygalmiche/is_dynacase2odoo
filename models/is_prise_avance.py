from odoo import models, fields, api  # type: ignore

_STATE = ([
    ('brouillon', 'Brouillon'),
    ('diffuse', 'Diffusé'),
    ('realise', 'Planifié'),
])

class is_prise_avance(models.Model):
    _name='is.prise.avance'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Prise d'avance"
    _rec_name = "num_moule_id"
    _order='create_date desc'

    vers_brouillon_vsb          = fields.Boolean('vers_brouillon_vsb', compute='_compute_vsb', readonly=True, store=False)
    vers_diffuse_vsb            = fields.Boolean('vers_diffuse_vsb', compute='_compute_vsb', readonly=True, store=False)
    vers_realise_vsb            = fields.Boolean('vers_realise_vsb', compute='_compute_vsb', readonly=True, store=False)
    num_moule_id                = fields.Many2one('is.mold', 'Numéro du moule', required=True, tracking=True)
    num_moule_id_ro             = fields.Boolean('num_moule_ro', compute='_compute_ro', readonly=True, store=False)
    active                      = fields.Boolean('Actif', default=True, tracking=True)
    user_id                     = fields.Many2one('res.users', 'Demandeur', tracking=True, default=lambda self: self.env.uid, copy=False)
    user_id_ro                  = fields.Boolean('user_id_ro', compute='_compute_ro', readonly=True, store=False)
    user_id_vsb                 = fields.Boolean('user_id_vsb', compute='_compute_vsb', readonly=True, store=False)
    resp_prise_avance_id        = fields.Many2one('res.users', "Responsable de la prise d'avance", help="Membres du groupe <Chef d'équipe et assistante logistique>", domain=lambda self: [( "groups_id", "=", self.env.ref("is_plastigray16.is_chef_equipe_group").id)], tracking=True)
    resp_prise_avance_id_ro     = fields.Boolean('resp_prise_avance_id_ro', compute="_compute_ro", readonly=True, store=False)
    motif_prise_avance          = fields.Selection([('m', 'Modification outillage'), ('t', 'Transfert outillage')], "Motif de la prise d'avance", tracking=True)
    motif_prise_avance_ro       = fields.Boolean('motif_prise_avance_ro', compute="_compute_ro", readonly=True, store=False)
    immobilisation              = fields.Boolean("Immobilisation complète", tracking=True)
    immobilisation_ro           = fields.Boolean('immobilisation_ro', compute="_compute_ro", readonly=True, store=False)
    immobilisation_vsb          = fields.Boolean('immobilisation_vsb', compute="_compute_vsb", readonly=True, store=False)
    pieces_modif                = fields.Boolean("Pièces avant modification livrables", tracking=True)
    pieces_modif_ro             = fields.Boolean("pieces_modif_ro", compute="_compute_ro", readonly=True, store=False)
    pieces_modif_vsb            = fields.Boolean("pieces_modif_vsb", compute="_compute_vsb", readonly=True, store=False)
    duree_immobilisation        = fields.Integer(string="Durée de l'immobilisation en jours ouvrables")
    duree_immobilisation_ro     = fields.Boolean("duree_immobilisation_ro", compute="_compute_ro", readonly=True, store=False)
    duree_immobilisation_vsb    = fields.Boolean("duree_immobilisation_vsb", compute="_compute_vsb", readonly=True, store=False)
    nb_jours                    = fields.Integer(string="Nombre de jours à couvrir", tracking=True)
    nb_jours_ro                 = fields.Boolean("nb_jours_ro", compute="_compute_ro", readonly=True, store=False)
    nb_jours_vsb                = fields.Boolean("nb_jours_vsb", compute="_compute_vsb", readonly=True, store=False)
    pieces_stck                 = fields.Integer(string="Nombre de pièces à avoir en stock à la fin de la prise d'avance", tracking=True)
    pieces_stck_ro              = fields.Boolean('pieces_stck_ro', compute='_compute_ro', readonly=True, store=False)
    pieces_stck_vsb             = fields.Boolean('pieces_stck_vsb' , compute='_compute_vsb', readonly=True, store=False)
    date_outillage              = fields.Date("Date de mise à disposition de l'outillage", tracking=True)
    date_outillage_ro           = fields.Boolean("date_outillage_ro", compute="_compute_ro", readonly=True, store=False)
    date_outillage_vsb          = fields.Boolean("date_outillage_vsb", compute="_compute_vsb", readonly=True, store=False)
    date_retour_outillage       = fields.Date("Date de retour souhaité de l'outillage", tracking=True)
    date_retour_outillage_ro    = fields.Boolean("date_retour_outillage_ro", compute="_compute_ro", readonly=True, store=False)
    date_retour_outillage_vsb   = fields.Boolean("date_retour_outillage_vsb", compute="_compute_vsb", readonly=True, store=False)
    state                       = fields.Selection(_STATE, "Etat", default=_STATE[0][0], required=True, tracking=True)
    dynacase_id                 = fields.Integer(string="Id Dynacase", index=True, copy=False)
    mail_to_ids                 = fields.Many2many('res.users', compute='_compute_mail_to_cc_ids', string="Mail To")
    mail_cc_ids                 = fields.Many2many('res.users', compute='_compute_mail_to_cc_ids', string="Mail Cc")


    def get_doc_url(self):
        for obj in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = base_url + '/web#id=%s' '&view_type=form&model=%s'%(obj.id,self._name)
            return url


    def get_state_name(self):
        for obj in self:
            return dict(self._fields['state'].selection).get(self.state)


    @api.depends("state")
    def _compute_mail_to_cc_ids(self):
        for obj in self:
            to_ids=[]
            if obj.state=='diffuse':
                to_ids.append(obj.resp_prise_avance_id)
            if obj.state=='realise':
                to_ids.append(obj.user_id)
            obj.mail_to_ids = self.env['is.liste.diffusion.mail'].get_users_ids(users=to_ids)
            obj.mail_cc_ids = []


    def users2mail(self,users):
        return self.env['is.liste.diffusion.mail'].users2mail(users=users)
      

    def users2partner_ids(self,users):
        return self.env['is.liste.diffusion.mail'].users2partner_ids(users=users)


    def envoi_mail(self):
        template = self.env.ref('is_dynacase2odoo.is_prise_avance_mail_template').sudo()     
        email_values = {
            'email_cc'      : self.users2mail(self.mail_cc_ids),
            'auto_delete'   : False,
            'recipient_ids' : self.users2partner_ids(self.mail_to_ids),
            'scheduled_date': False,
        }
        template.send_mail(self.id, force_send=True, raise_exception=False, email_values=email_values)


    @api.depends("state")
    def _compute_ro(self):
        for obj in self:
            is_user = self.env.user == obj.user_id
            is_resp = self.env.user == obj.resp_prise_avance_id
            if (is_user or is_resp) and obj.state in 'brouillon':
                obj.num_moule_id_ro = False
                obj.user_id_ro = True
                obj.resp_prise_avance_id_ro = False
                obj.motif_prise_avance_ro = False
                obj.immobilisation_ro = False
                obj.pieces_modif_ro = False
                obj.duree_immobilisation_ro = False
                obj.nb_jours_ro = False
                obj.pieces_stck_ro = True
                obj.date_outillage_ro = True
                obj.date_retour_outillage_ro = True
            elif is_resp and obj.state in 'diffuse':
                obj.num_moule_id_ro = True
                obj.user_id_ro = True
                obj.resp_prise_avance_id_ro = True
                obj.motif_prise_avance_ro = True
                obj.immobilisation_ro = True
                obj.duree_immobilisation_ro = True
                obj.pieces_modif_ro = True
                obj.nb_jours_ro = False
                obj.pieces_stck_ro = False
                obj.date_outillage_ro = False
                obj.date_retour_outillage_ro = False
            else:
                obj.num_moule_id_ro = True
                obj.user_id_ro = True
                obj.resp_prise_avance_id_ro = True
                obj.motif_prise_avance_ro = True
                obj.immobilisation_ro = True
                obj.duree_immobilisation_ro = True
                obj.pieces_modif_ro = True
                obj.nb_jours_ro = True
                obj.pieces_stck_ro = True
                obj.date_outillage_ro = True
                obj.date_retour_outillage_ro = True

    @api.depends("state")
    def _compute_vsb(self):
        for obj in self:
            is_user = self.env.user == obj.user_id
            is_resp = self.env.user == obj.resp_prise_avance_id
            obj.duree_immobilisation_vsb = True
            obj.immobilisation_vsb       = True
            obj.pieces_modif_vsb         = True
            obj.nb_jours_vsb             = True
            obj.user_id_vsb              = True
            if obj.state == 'brouillon':
                obj.vers_brouillon_vsb = False
                obj.vers_diffuse_vsb = is_user or is_resp
                obj.vers_realise_vsb = False
                obj.pieces_stck_vsb = False
                obj.date_outillage_vsb = False
                obj.date_retour_outillage_vsb = False
                obj.nb_jours_vsb = False
            if obj.state == 'diffuse':
                obj.vers_brouillon_vsb = is_user or is_resp
                obj.vers_diffuse_vsb = False
                obj.vers_realise_vsb = is_resp
                obj.pieces_stck_vsb = True
                obj.date_outillage_vsb = True
                obj.date_retour_outillage_vsb = True
            if obj.state == 'realise':
                obj.vers_brouillon_vsb = False
                obj.vers_diffuse_vsb = is_resp
                obj.vers_realise_vsb = False
                obj.pieces_stck_vsb = True
                obj.date_outillage_vsb = True
                obj.date_retour_outillage_vsb = True

    def vers_diffuse_action(self):
        for obj in self:
            obj.state='diffuse'
            obj.envoi_mail()

    def vers_realise_action(self):
        for obj in self:
            obj.state='realise'
            obj.envoi_mail()

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
