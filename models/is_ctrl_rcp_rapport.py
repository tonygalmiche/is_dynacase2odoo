from odoo import models, fields  # type: ignore


class IsCtrlRcpRapport(models.Model):
    _name = "is.ctrl.rcp.rapport"
    _description = "Rapport Contrôle Réception"
    _rec_name = "titre"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Identification
    titre = fields.Char(string="Titre", tracking=True)
    num_rapport = fields.Integer(string="N° du rapport", tracking=True)
    soc = fields.Selection(
        selection=[("", ""), ("1", "1"), ("3", "3"), ("4", "4")],
        string="Code société Prodstar",
        default="",
        tracking=True,
    )
    num_rcp = fields.Char(string="N° de réception", tracking=True)
    codepg = fields.Char(string="Code PG", tracking=True)
    designation = fields.Char(string="Désignation", tracking=True)
    moule = fields.Char(string="Moule", tracking=True)
    fournisseur = fields.Char(string="Fournisseur", tracking=True)
    code_fournisseur = fields.Char(string="Code Fournisseur", tracking=True)
    qt_annonce = fields.Float(string="Quantité annoncée", tracking=True)
    qt_recue = fields.Float(string="Quantité reçue", tracking=True)
    num_lot_fourn = fields.Char(string="N° lot fournisseur", tracking=True)
    date_rcp = fields.Date(string="Date de réception", tracking=True)
    num_bl = fields.Char(string="N° BL Fournisseur", tracking=True)
    num_lot_of = fields.Char(string="N° de lot ou d'OF", tracking=True)

    # Contrôle RCP
    date_ctrl = fields.Date(string="Date du contrôle", tracking=True)

    createur = fields.Char(string="Créateur", tracking=True)
    # Référence utilisateur (nommage conservé sans underscore pour coller au besoin "sans le prefix crr_")
    createurid = fields.Many2one(
        "res.users", string="Créateur Id", ondelete="set null", tracking=True
    )

    # Gamme de contrôle (libellé + lien)
    gamme_ctrl_rcp = fields.Char(string="Gamme de contrôle", tracking=True)
    gamme_ctrl_rcpid = fields.Many2one(
        "is.ctrl.rcp.gamme",
        string="Gamme de contrôle Id",
        ondelete="set null",
        tracking=True,
    )

    # Pièce jointe de la gamme de contrôle (PDF)
    gamme_ctrl_rcp_pdf = fields.Binary(
        string="PDF de la gamme de contrôle", attachment=True
    )

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
    commentaire = fields.Text(string="Commentaire", tracking=True)

    # Pièces jointes multiples
    pieces_jointes = fields.Many2many(
        "ir.attachment",
        "is_ctrl_rcp_rapport_attachment_rel",
        "rapport_id",
        "attachment_id",
        string="Pièces jointes",
    )

    # Archivage standard Odoo
    active = fields.Boolean(string="Actif", default=True, tracking=True)

    # Intégration Dynacase
    dynacase_id = fields.Integer(string="Id Dynacase", index=True, copy=False, tracking=True)

    def lien_vers_dynacase_action(self):
        for obj in self:
            url = "https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s" % obj.dynacase_id
            return {
                "type": "ir.actions.act_url",
                "url": url,
                "target": "new",
            }
