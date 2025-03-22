from odoo import models, fields  # type: ignore

_STATE = ([
    ('Active', 'Active'),
    ('Classée', 'Classée'),
    ('Consultation', 'Consultation'),
])


class is_fiche_information_prospect(models.Model):
    _name='is.fiche.information.prospect'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Fiche information prospect"
    _rec_name = "nom_prospect"
    _order='nom_prospect'

    charge_affaire_id          = fields.Many2one('res.users', 'Charge affaire', required=True, default=lambda self: self.env.uid, tracking=True)
    active                     = fields.Boolean('Actif', default=True, tracking=True)
    date_ouverture             = fields.Date("Date d'ouverture", tracking=True)
    nom_prospect               = fields.Char("Nom du prospect", required=True, tracking=True)
    activite                   = fields.Char("Activité", required=True, tracking=True)
    secteur_activite           = fields.Char("Secteur d'activité", tracking=True)
    effectif                   = fields.Char("Effectif", tracking=True)
    ca                         = fields.Char("CA", tracking=True)
    adresse                    = fields.Char("Adresse", tracking=True)
    departement                = fields.Char("Département", tracking=True)
    telephone                  = fields.Char("Téléphone", tracking=True)
    fax                        = fields.Char("Fax", tracking=True)
    site_internet              = fields.Char("Site internet", tracking=True)
    etat                       = fields.Selection(_STATE, "Etat", default=_STATE[0][0], required=True, tracking=True)
    appel_offre_id             = fields.Many2one("is.dossier.appel.offre", string="Appel d'offre", index=True, tracking=True)
    dynacase_id                = fields.Integer(string="Id Dynacase", index=True, copy=False)

    contacts_ids               = fields.One2many('is.fiche.information.prospect.contact.line', 'information_prospect_id', string="Contact")

    suivi_ids                  = fields.One2many('is.fiche.information.prospect.suivi.line', 'information_prospect_id', string="Suivi")

    piece_jointe_ids           = fields.Many2many("ir.attachment", "is_fiche_information_prospect_piece_jointe_rel", "piece_jointe"  , "att_id", string="Pièce jointe")

    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }


class is_fiche_information_prospect_contact_line(models.Model):
    _name        = "is.fiche.information.prospect.contact.line"
    _description = "Lignes contact"
    _rec_name    = "contacts_nom"
    _order       = 'contacts_prenom'

    information_prospect_id    = fields.Many2one("is.fiche.information.prospect", string="Fiche information prospect", required=True, ondelete='cascade')
    contacts_nom               = fields.Char("Nom")
    contacts_prenom            = fields.Char("Prénom")
    conatcts_fonction          = fields.Char("Fonction")
    contacts_telephone         = fields.Char("Téléphone")
    contacts_portable          = fields.Char("Portable")
    contacts_fax               = fields.Char("Fax")
    contacts_mail              = fields.Char("Mail")


class is_fiche_information_prospect_suivi_line(models.Model):
    _name        = "is.fiche.information.prospect.suivi.line"
    _description = "Lignes de suivi"

    information_prospect_id    = fields.Many2one("is.fiche.information.prospect", string="Fiche information prospect", required=True, ondelete='cascade')
    suivi_date                 = fields.Date("Date")
    suivi_nature_contact       = fields.Char("Nature du contact")
    suivi_objet                = fields.Char("Objet")
    suivi_decision             = fields.Char("Décision")
    suivi_date_relance         = fields.Date("Date de relance")
    suivi_fichier_joint_ids    = fields.Many2many("ir.attachment", "is_fiche_information_prospect_suivi_line_fichier_joint_rel", "suivi_fichier_joint"  , "att_id", string="Pièce jointe")
