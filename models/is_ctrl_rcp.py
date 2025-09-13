from odoo import models, fields, api  # type: ignore


class IsCtrlRcpGamme(models.Model):
    _name = "is.ctrl.rcp.gamme"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Gamme Contrôle Réception"
    _rec_name = "dossier_article_id"
    _order = "dossier_article_id"

    dossier_article_id = fields.Many2one("is.dossier.article", string="Dossier article", required=False, index=True, tracking=True)
    dossier_article    = fields.Char(string="Dossier article (archivé)", tracking=True, copy=False, readonly=True)
    responsable_id     = fields.Many2one("res.users", string="Responsable", tracking=True, default=lambda self: self.env.uid)
    date_fin_prevue    = fields.Date(string="Date de fin prévue", tracking=True, default=lambda *a: fields.datetime.now())
    etat = fields.Selection(
        [
            ("", ""),
            ("AF", "A Faire"),
            ("F", "Fait"),
        ],
        string="État",
        default="F",
        tracking=True,
    )

    # Archivage standard Odoo
    active = fields.Boolean(string="Actif", default=True, tracking=True)

    # piece_jointe_ids = fields.Many2many(
    #     "ir.attachment",
    #     "is_ctrl_rcp_gamme_attachment_rel",
    #     "gamme_id",
    #     "attachment_id",
    #     string="Pièces jointes",
    #     tracking=True,
    # )

    piece_jointe_ids = fields.Many2many("ir.attachment", "is_ctrl_rcp_gamme_piece_jointe_rel", "piece_jointe", "att_id", string="Pièce jointe")

    # Lignes de contrôles
    controle_ids = fields.One2many(
        "is.ctrl.rcp.gamme.controle",
        "gamme_id",
        string="Contrôles",
        tracking=True,
    )

    # Intégration Dynacase
    dynacase_id = fields.Integer(string="Id Dynacase", index=True, copy=False)

    def lien_vers_dynacase_action(self):
        for obj in self:
            url = "https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s" % obj.dynacase_id
            return {
                "type": "ir.actions.act_url",
                "url": url,
                "target": "new",
            }



class IsCtrlRcpGammeControle(models.Model):
    _name = "is.ctrl.rcp.gamme.controle"
    _description = "Contrôle de la gamme RCP"
    _order = "id"

    gamme_id = fields.Many2one(
        "is.ctrl.rcp.gamme",
        string="Gamme",
        required=True,
        ondelete="cascade",
        index=True,
    )
    intitule_controle = fields.Char(string="Intitulé du contrôle", required=True)
    tolerance_mini    = fields.Char(string="Tolérance mini")
    tolerance_maxi    = fields.Char(string="Tolérance maxi")



class IsCtrlRcpSaisie(models.Model):
    _name = "is.ctrl.rcp.saisie"
    _description = "Saisie Contrôle Réception"
    _rec_name = "num_saisie"
    _order = "id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Identification
    num_saisie   = fields.Integer(string="N° de saisie", tracking=True)
    soc          = fields.Char(string="Code société Prodstar", tracking=True)
    num_rcp      = fields.Char(string="N° de réception", tracking=True)
    codepg       = fields.Char(string="Code PG", tracking=True)
    designation  = fields.Char(string="Désignation", tracking=True)
    moule        = fields.Char(string="Moule", tracking=True)
    fournisseur  = fields.Char(string="Fournisseur", tracking=True)
    num_lot_fourn = fields.Char(string="N° lot fournisseur", tracking=True)

    # Contrôle RCP (liens Dynacase/rapport)
    rapport      = fields.Char(string="Rapport de contrôle", tracking=True)
    rapportid    = fields.Integer(string="Rapport de contrôle Id", tracking=True)  # docid
    rapport_lig  = fields.Integer(string="Ligne du rapport", tracking=True)

    # Dates
    date_ctrl    = fields.Date(string="Date du contrôle", tracking=True)

    # Création
    createur     = fields.Char(string="Créateur", tracking=True)
    createurid   = fields.Integer(string="Créateur Id", tracking=True)  # docid

    # Détails de contrôle
    controle_a_effectuer = fields.Char(string="Contrôle à effectuer", tracking=True)
    tolerance_mini       = fields.Char(string="Tolérance mini", tracking=True)
    tolerance_maxi       = fields.Char(string="Tolérance maxi", tracking=True)

    # Résultat
    resultat     = fields.Char(string="Résultat du contrôle", tracking=True)

    # Archivage standard Odoo
    active = fields.Boolean(string="Actif", default=True, tracking=True)

    # Intégration Dynacase
    dynacase_id = fields.Integer(string="Id Dynacase", index=True, copy=False, tracking=True)

    # Mesures
    mesure_ids = fields.One2many(
        "is.ctrl.rcp.saisie.mesure",
        "saisie_id",
        string="Mesures",
    )

    def lien_vers_dynacase_action(self):
        for obj in self:
            url = "https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s" % obj.dynacase_id
            return {
                "type": "ir.actions.act_url",
                "url": url,
                "target": "new",
            }



class IsCtrlRcpSaisieMesure(models.Model):
    _name = "is.ctrl.rcp.saisie.mesure"
    _description = "Mesure de saisie de contrôle réception"
    _order = "id"

    saisie_id = fields.Many2one(
        "is.ctrl.rcp.saisie",
        string="Saisie",
        required=True,
        ondelete="cascade",
        index=True,
    )
    num_mesure       = fields.Integer(string="N° de la mesure")
    valeur_mesuree   = fields.Char(string="Valeur mesurée")
    valeur_resultat  = fields.Char(string="Résultat")


class IsCtrlRcpRapport(models.Model):
    _name = "is.ctrl.rcp.rapport"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Rapport Contrôle Réception"
    _rec_name = "num_rapport"
    _order = "num_rapport desc"


    # Identification
    #titre = fields.Char(string="Titre", tracking=True)
    # soc = fields.Selection(
    #     selection=[("", ""), ("1", "1"), ("3", "3"), ("4", "4")],
    #     string="Code société Prodstar",
    #     default="",
    #     tracking=True,
    # )

    num_rapport      = fields.Integer(string="N° du rapport", tracking=True, readonly=1, index=True)
    site_id          = fields.Many2one('is.database', "Site", tracking=True, default=lambda self: self._get_site_id(),)
    reception_id     = fields.Many2one('is.reception', "Réception", tracking=True)
    fournisseur_id   = fields.Many2one('res.partner', 'Fournisseur', tracking=True, domain=[("is_company","=",True), ("supplier","=",True)])
    fournisseur      = fields.Char(string="Nom fournisseur", tracking=True)
    code_fournisseur = fields.Char(string="Code fournisseur", tracking=True)

    codepg        = fields.Char(string="Code PG", tracking=True)
    designation   = fields.Char(string="Désignation", tracking=True)
    moule         = fields.Char(string="Moule", tracking=True)
    qt_annonce    = fields.Float(string="Quantité annoncée", tracking=True)
    qt_recue      = fields.Float(string="Quantité reçue", tracking=True)
    num_lot_fourn = fields.Char(string="N° lot fournisseur", tracking=True)
    date_rcp      = fields.Date(string="Date de réception", tracking=True)
    num_bl        = fields.Char(string="N° BL Fournisseur", tracking=True)
    num_lot_of    = fields.Char(string="N° de lot ou d'OF", tracking=True)

    # Contrôle RCP
    date_ctrl = fields.Date(string="Date du contrôle", tracking=True)
    gamme_id  = fields.Many2one("is.ctrl.rcp.gamme", string="Gamme de contrôle", tracking=True)

    # Pièce jointe de la gamme de contrôle (PDF)
    # gamme_ctrl_rcp_pdf = fields.Binary(
    #     string="PDF de la gamme de contrôle", attachment=True
    # )

    # Résultats des contrôles
    condi_resultat = fields.Selection(
        selection=[("", ""), ("Conforme", "Conforme"), ("Non conforme", "Non conforme")],
        string="Conditionnement",
        default="",
        tracking=True,
    )
    conform_resultat = fields.Selection(
        selection=[("", ""), ("Conforme", "Conforme"), ("Non conforme", "Non conforme")],
        string="Conformité produit",
        default="",
        tracking=True,
    )

    decision_rcp = fields.Selection(
        selection=[
            ("Livraison refusée", "Livraison refusée"),
            ("Livraison acceptée", "Livraison acceptée"),
            ("Livraison dérogée", "Livraison dérogée"),
        ],
        string="Décision de la réception",
        tracking=True,
    )
    commentaire      = fields.Text(string="Commentaire", tracking=True)
    piece_jointe_ids = fields.Many2many("ir.attachment", "is_ctrl_rcp_rapport_piece_jointe_rel", "piece_jointe", "att_id", string="Pièce jointe")
    active           = fields.Boolean(string="Actif", default=True, tracking=True)
    dynacase_id      = fields.Integer(string="Id Dynacase", index=True, copy=False, tracking=True)



    def _get_site_id(self):
        user = self.env['res.users'].browse(self._uid)
        site_id = user.is_site_id.id
        return site_id




    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            num_rapport=1
            if 'num_rapport' not in vals:
                last = self.env[self._name].search([('num_rapport', '!=', None)], order="num_rapport desc", limit=1)
                if last:
                    num_rapport = last.num_rapport + 1
            vals['num_rapport'] = num_rapport
            return super().create(vals_list)


    def lien_vers_dynacase_action(self):
        for obj in self:
            url = "https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s" % obj.dynacase_id
            return {
                "type": "ir.actions.act_url",
                "url": url,
                "target": "new",
            }
