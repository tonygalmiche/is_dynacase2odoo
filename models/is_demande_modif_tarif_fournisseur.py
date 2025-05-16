from odoo import models, fields, api  # type: ignore

_STATE = ([
    ('brouillon', 'Brouillon'),
    ('diffuse', 'Diffusé'),
    ('termine', 'Terminé'),
])
_TARIF = ([
    ('creation', 'Création'),
    ('modification', 'Modification'),
])
_TYPE_COMMANDE_TARIF = ([
     ('commande_ouverte'           , 'Commande ouverte'),
     ('commande_ferme_uniquement'  , 'Commande ferme uniquement'),
     ('commande_ferme_avec_horizon', 'Commande ferme avec horizon'),
])
_EVOLUTION = ([
     ('hausse', 'Hausse'),
     ('baisse', 'Baisse'),
])
_UNITE = ([
    ('tonne', 'Tonne'),
    ('mille', 'Mille'),
    ('unitaire', 'Unitaire'),
])


class is_demande_modif_tarif_fournisseur(models.Model):
    _name='is.demande.modif.tarif.fournisseur'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Demande de création ou de modification d'un tarif Fournisseur"
    _rec_name = "titre"
    _order='id desc'

    titre                          = fields.Char(string="Titre du document", tracking=True, compute='_compute_title', readonly=True, store=True)
    num_ordre                      = fields.Integer(string="Numéro d'ordre de la demande", tracking=True,copy=False)
    societe_ids                    = fields.Many2many('is.database','is_demande_modif_tarif_fournisseur_database_rel','demande_modif_tarif_fournisseur_id','database_id', string="Société", tracking=True)
    type_tarif                     = fields.Selection(_TARIF, "Type tarif", default=_TARIF[0][0], required=True, tracking=True)
    fournisseur_id                 = fields.Many2one('res.partner', 'Nom du fournisseur', tracking=True, domain=[("is_company","=",True), ("supplier","=",True)])
    date_creation                  = fields.Date("Date de création de la demande", tracking=True, default=lambda *a: fields.datetime.now())
    createur_id                    = fields.Many2one('res.users', "Créateur de la demande", tracking=True, default=lambda self: self.env.uid)
    responsable_action_id          = fields.Many2one("res.users", "Responsable de l'action", tracking=True, required=True)
    motif                          = fields.Text(string="Motif", tracking=True, required=True)
    date_application               = fields.Date("Date d'application", tracking=True)
    type_commande                  = fields.Selection(_TYPE_COMMANDE_TARIF, "Type de commande", tracking=True)
    gestionnaire_id                = fields.Many2one('is.gestionnaire', 'Gestionnaire', tracking=True)
    code_douanier                  = fields.Char(string="Code douanier", tracking=True)
    origine                        = fields.Char(string="Origine (Dynacase)", readonly=True)
    origine_id                     = fields.Many2one('res.country', 'Origine', tracking=True, domain=[])
    maj_cde                        = fields.Boolean('Mise à jour des commandes', tracking=True)
    productivite                   = fields.Boolean('Productivité annuelle', tracking=True)
    evolution_tarif                = fields.Selection(_EVOLUTION, "Evolution tarif", tracking=True)
    article_id                     = fields.Many2one('is.article', 'Article', tracking=True)
    unite_tarif                    = fields.Selection(_UNITE, "Unité tarif", tracking=True)
    unite_tarif_autre              = fields.Char(string="Unité tarif (autre)", tracking=True)
    conditionnement                = fields.Char(string="Conditionnement", tracking=True)
    lot_approvisionnement          = fields.Integer(string="Lot d'approvisionnement minimum", tracking=True)
    lot_ids                        = fields.One2many('is.demande.modif.tarif.fournisseur.lot.line', 'demande_id', string="Tarif par Lot",copy=True)
    delai_appro                    = fields.Integer(string="Délai d'approvisionnement (en semaines)", tracking=True)
    modif_article                  = fields.Boolean("Modification fiche article", tracking=True)
    article_desactiver_id          = fields.Many2one('is.article', 'Article à désactiver', tracking=True)
    code_fournisseur_desactiver_id = fields.Many2one('res.partner', 'Code fournisseur', tracking=True, domain=[("is_company","=",True), ("supplier","=",True)])
    commentaire                    = fields.Char(string="Commentaires", tracking=True) 
    piece_jointe_ids               = fields.Many2many("ir.attachment", "is_demande_modif_tarif_fournisseur_piece_jointe_rel", "piece_jointe", "att_id", string="Pièce jointe")
    state                          = fields.Selection(_STATE, "Etat", default=_STATE[0][0], required=True, tracking=True)
    dynacase_id                    = fields.Integer(string="Id Dynacase", index=True, copy=False)
    active                         = fields.Boolean('Actif', default=True, tracking=True)
    mail_to_ids                    = fields.Many2many('res.users', compute='_compute_mail_to_cc_ids', string="Mail To")
    mail_cc_ids                    = fields.Many2many('res.users', compute='_compute_mail_to_cc_ids', string="Mail Cc")
    vers_brouillon_vsb             = fields.Boolean(string="vers Brouillon"        , compute='_compute_vsb', readonly=True, store=False)
    vers_diffuse_vsb               = fields.Boolean(string="vers Diffusé"          , compute='_compute_vsb', readonly=True, store=False)
    vers_termine_vsb               = fields.Boolean(string="vers Terminé"          , compute='_compute_vsb', readonly=True, store=False)


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
            if obj.state=='diffuse':
                to_ids.append(obj.responsable_action_id)
            if obj.state=='termine':
                to_ids.append(obj.createur_id)
            obj.mail_to_ids = self.env['is.liste.diffusion.mail'].get_users_ids(users=to_ids)
            obj.mail_cc_ids = []


    def users2mail(self,users):
        return self.env['is.liste.diffusion.mail'].users2mail(users=users)
      

    def users2partner_ids(self,users):
        return self.env['is.liste.diffusion.mail'].users2partner_ids(users=users)


    def envoi_mail(self):
        template = self.env.ref('is_dynacase2odoo.is_demande_modif_tarif_fournisseur_mail_template').sudo()     
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
                last = self.env["is.demande.modif.tarif.fournisseur"].search([('num_ordre', '!=', None)], order="num_ordre desc", limit=1)
                if last:
                    num_ordre = last.num_ordre
                else:
                    num_ordre = 0
                vals["num_ordre"] = num_ordre + 1
        return super().create(vals_list)

    @api.depends('num_ordre', 'fournisseur_id')
    def _compute_title(self):
        for obj in self:
            title = f"{obj.num_ordre} - "
            if obj.fournisseur_id:
                title += obj.fournisseur_id.name
            obj.titre = title

    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }


class is_demande_modif_tarif_fournisseur_lot_line(models.Model):
    _name        = 'is.demande.modif.tarif.fournisseur.lot.line'
    _description = "Tarif par Lot"

    demande_id    = fields.Many2one("is.demande.modif.tarif.fournisseur", string="Demande", required=True, ondelete='cascade')
    lot           = fields.Char(string="Lot")
    tarif         = fields.Char(string="Tarif")
