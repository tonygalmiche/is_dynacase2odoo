from odoo import models, fields, api  # type: ignore

_STATE = ([
    ('brouillon', 'Brouillon'),
    ('diffuse', 'Diffusé'),
    ('termine', 'Terminé'),
])
_TARIF = ([
    ('creation', 'Créateur'),
    ('modification', 'Modification'),
])
_TYPE_COMMANDE = ([
     ('Commande ouverte', 'Commande ouverte'),
     ('Commande ferme uniquement', 'Commande ferme uniquement'),
     ('commande ferme avec horizon', 'Commande ferme avec horizon'),
    ])
_GESTIONNAIRE = ([
     ('02', '2 - Matières/Composants série'),
     ('09', '09 - Matières/Composants fournis par le client'),
     ('16', '16 - Achats en stock dépôt consignation'),
     ('17', '17 - Achats leviers'),
     ('18', '18 - MATIERES-COMPOSANTS ACHETES VIA LE SERVICE ACHAT'),
])
_EVOLUTION = ([
     ('Hausse', 'Hausse'),
     ('Baisse', 'Baisse'),
])
_UNITE = ([
    ('Tonne', 'Tonne'),
    ('Mille', 'Mille'),
    ('Unitaire', 'Unitaire'),
])


class is_demande_modif_tarif_fournisseur(models.Model):
    _name='is.demande.modif.tarif.fournisseur'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Prise d'avance"
    _rec_name = "titre"
    _order='num_ordre desc'

    titre                          = fields.Char(string="Titre du document", tracking=True, compute='_compute_title', readonly=True, store=True)
    active                         = fields.Boolean('Actif', default=True, tracking=True, readonly=True)
    num_ordre                      = fields.Integer(string="Numéro d'ordre de la demande", tracking=True)
    societe_ids                    = fields.Many2many('is.database','demande_modif_tarif_fournisseur_database_rel','demande_modif_tarif_fournisseur_id','database_id', string="Société", tracking=True)
    type_tarif                     = fields.Selection(_TARIF, "Type tarif", default=_TARIF[0][0], required=True, tracking=True)
    fournisseur_id                 = fields.Many2one('res.partner', 'Nom du fournisseur', tracking=True)
    date_creation                  = fields.Date("Date de création de la demande", tracking=True, default=lambda *a: fields.datetime.now())
    createur_id                    = fields.Many2one('res.users', "Créateur de la demande", tracking=True, default=lambda self: self.env.uid)
    responsable_action_id          = fields.Many2one("res.users", "Responsable de l'action", tracking=True, required=True)
    motif                          = fields.Text(string="Motif", tracking=True, required=True)
    date_application               = fields.Date("Date d'application", tracking=True)
    type_commande                  = fields.Selection(_TYPE_COMMANDE, "Type de commande", default=_TYPE_COMMANDE[0][0], required=True, tracking=True)
    gestionnaire                   = fields.Selection(_GESTIONNAIRE, "Gestionnaire", default=_GESTIONNAIRE[0][0], required=True, tracking=True)
    code_douanier                  = fields.Char(string="Code douanier", tracking=True)
    origine                        = fields.Char(string="Origine", tracking=True)
    maj_cde                        = fields.Boolean('Mise à jour des commandes', tracking=True)
    productivite                   = fields.Boolean('Productivité annuelle', tracking=True)
    evolution_tarif                = fields.Selection(_EVOLUTION, "Evolution tarif", default=_EVOLUTION[0][0], required=True, tracking=True)

    code_article                   = fields.Char(string="Code article", tracking=True)
    designation                    = fields.Char(string="Désignation", tracking=True)
    unite_tarif                    = fields.Selection(_UNITE, "Unité tarif", default=_UNITE[0][0], required=True, tracking=True)
    unite_tarif_autre              = fields.Char(string="Unité tarif (autre)", tracking=True)
    conditionnement                = fields.Char(string="Conditionnement", tracking=True)
    lot_approvisionnement          = fields.Integer(string="Lot d'approvisionnement minimum", tracking=True)
    lot_ids                        = fields.One2many('is.demande.modif.tarif.fournisseur.lot.line', 'demande_id', string="Tarif par Lot")

    delai_appro                    = fields.Integer(string="Délai d'approvisionnement (en semaines)", tracking=True)
    modif_article                  = fields.Boolean("Modification fiche article", tracking=True)
    code_article_desactiver        = fields.Char(string="Code Article à désactiver", tracking=True) 
    designation_article_desactiver = fields.Char(string="Désignation article désactivé", tracking=True) 
    code_fournisseur_desactiver_id = fields.Many2one('res.partner', 'Code fournisseur', tracking=True)
    commentaire                    = fields.Char(string="Commentaires", tracking=True) 

    state                          = fields.Selection(_STATE, "Etat", default=_STATE[0][0], required=True, tracking=True)
    dynacase_id                    = fields.Integer(string="Id Dynacase", index=True, copy=False)


    def vers_diffuse_action(self):
        for obj in self:
            obj.state='diffuse'

    def vers_termine_action(self):
        for obj in self:
            obj.state='termine'

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


class is_demande_modif_tarif_fournisseur_lot_line(models.Model):
    _name        = 'is.demande.modif.tarif.fournisseur.lot.line'
    _description = "Tarif par Lot"

    demande_id    = fields.Many2one("is.demande.modif.tarif.fournisseur", string="Demande", required=True, ondelete='cascade')
    lot           = fields.Char(string="Lot")
    tarif         = fields.Char(string="Tarif")
