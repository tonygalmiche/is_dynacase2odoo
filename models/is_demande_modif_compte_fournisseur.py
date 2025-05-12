from odoo import models, fields, api  # type: ignore

_STATE = ([
    ('brouillon', 'Brouillon'),
    ('diffuse', 'Diffusé'),
    ('termine', 'Terminé'),
])


class is_demande_modif_compte_fournisseur(models.Model):
    _name='is.demande.modif.compte.fournisseur'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Demande de création ou de modification d'un compte Fournisseur"
    _rec_name = "titre"
    _order='num_ordre desc'

    titre                     = fields.Char(string="Titre du document", tracking=True, compute='_compute_title', readonly=True, store=True)
    num_ordre                 = fields.Integer(string="Numéro d'ordre de la demande", tracking=True)
    societe_ids               = fields.Many2many('is.database','is_demande_modif_compte_fournisseur_database_rel','demande_modif_compte_fournisseur_id','database_id', string="Société", tracking=True)
    fournisseur_id            = fields.Many2one('res.partner', 'Nom du fournisseur', tracking=True, domain=[("is_company","=",True), ("supplier","=",True)])
    fournisseur_autre         = fields.Char(string="Nom du fournisseur (Autre pour création)", tracking=True)
    code_fournisseur          = fields.Char("Code fournisseur", tracking=True, compute="_compute_fournisseur", readonly=True, store=True)
    code_fournisseur_creation = fields.Char(string="Code fournisseur (si création)", tracking=True)
    date_creation             = fields.Date("Date de création de la demande", tracking=True, default=lambda *a: fields.datetime.now())
    createur_id               = fields.Many2one('res.users', "Créateur de la demande", tracking=True, default=lambda self: self.env.uid)
    responsable_action_id     = fields.Many2one("res.users", "Responsable de l'action", tracking=True, required=True)
    motif                     = fields.Text(string="Motif", tracking=True, required=True)
    state                     = fields.Selection(_STATE, "Etat", default=_STATE[0][0], required=True, tracking=True)
    dynacase_id               = fields.Integer(string="Id Dynacase", index=True, copy=False)
    piece_jointe_ids          = fields.Many2many("ir.attachment", "is_demande_modif_compte_fournisseur_piece_jointe_rel", "piece_jointe", "att_id", string="Pièce jointe")
    active                    = fields.Boolean('Actif', default=True, tracking=True)
    mail_to_ids               = fields.Many2many('res.users', compute='_compute_mail_to_cc_ids', string="Mail To")
    mail_cc_ids               = fields.Many2many('res.users', compute='_compute_mail_to_cc_ids', string="Mail Cc")
    vers_brouillon_vsb        = fields.Boolean(string="vers Brouillon"        , compute='_compute_vsb', readonly=True, store=False)
    vers_diffuse_vsb          = fields.Boolean(string="vers Diffusé"          , compute='_compute_vsb', readonly=True, store=False)
    vers_termine_vsb          = fields.Boolean(string="vers Terminé"          , compute='_compute_vsb', readonly=True, store=False)


    @api.depends("state")
    def _compute_vsb(self):
        uid = self._uid
        for obj in self:
            vsb = False
            if uid in (obj.responsable_action_id.id, obj.createur_id.id) and obj.state in ('diffuse'):
                vsb=True
            obj.vers_brouillon_vsb = vsb

            vsb = False
            if uid in (obj.responsable_action_id.id, obj.createur_id.id) and obj.state in ('brouillon'):
                vsb=True
            obj.vers_diffuse_vsb = vsb

            vsb = False
            if uid==obj.responsable_action_id.id and obj.state in ('diffuse'):
                vsb=True
            obj.vers_termine_vsb = vsb


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
            cc_ids=[]
            if obj.state=='diffuse':
                to_ids.append(obj.responsable_action_id)
            if obj.state=='termine':
                cc_ids = self.env['is.liste.diffusion.mail'].get_users('is.demande.modif.compte.fournisseur','cc')
                to_ids.append(obj.createur_id)
            obj.mail_to_ids = self.env['is.liste.diffusion.mail'].get_users_ids(users=to_ids)
            obj.mail_cc_ids = self.env['is.liste.diffusion.mail'].get_users_ids(users=cc_ids)


    def users2mail(self,users):
        return self.env['is.liste.diffusion.mail'].users2mail(users=users)
      

    def users2partner_ids(self,users):
        return self.env['is.liste.diffusion.mail'].users2partner_ids(users=users)


    def envoi_mail(self):
        template = self.env.ref('is_dynacase2odoo.is_demande_modif_compte_fournisseur_mail_template').sudo()     
        email_values = {
            'email_cc'      : self.users2mail(self.mail_cc_ids),
            'auto_delete'   : False,
            'recipient_ids' : self.users2partner_ids(self.mail_to_ids),
            'scheduled_date': False,
        }
        template.send_mail(self.id, force_send=True, raise_exception=False, email_values=email_values)




    def vers_diffuse_action(self):
        for obj in self:
            obj.state='diffuse'
            obj.envoi_mail()

    def vers_termine_action(self):
        for obj in self:
            obj.state='termine'
            obj.envoi_mail()

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
