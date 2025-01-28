from odoo import models, fields  # type: ignore


class is_fiche_codification(models.Model):
    _name='is.fiche.codification'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Fiche de codification"
#    _order='name desc'

    active             = fields.Boolean('Actif', default=True, tracking=True)
    etabli_par_id      = fields.Many2one('res.users', 'Établi par', required=True, default=lambda self: self.env.uid)
    date               = fields.Date("Date", required=True, default=lambda *a: fields.datetime.now())
    dossier_commercial = fields.Many2one("is.dossier.appel.offre", string="Dossier commercial, Moule ou RC", index=True, tracking=True, required=True)
    type_dossier       = fields.Char("Origine de la fiche", tracking=True)
    chef_de_projet_id  = fields.Many2one('res.users', 'Chef de projet', required=True)
    creation_modif     = fields.Selection([('creation', 'Création'), ('modification', 'Modification')], "Création / Modification", required=True)  #, default="creation")
    client_id          = fields.Many2one('res.partner', 'Client', required=True)
    project_id         = fields.Many2one('is.mold.project', 'Projet')
    is_mold_id         = fields.Many2one('is.mold', 'Moule')
    dynacase_id        = fields.Integer(string="Id Dynacase", index=True, copy=False)

    code_pg            = fields.Char("Code PG", tracking=True)
    designation        = fields.Char("Désignation", tracking=True)
    code_client        = fields.Char("Code client", tracking=True)
    ref_plan           = fields.Char("Référence plan", tracking=True)
    indice_plan        = fields.Char("Indice plan", tracking=True)
    type_uc            = fields.Char("Type UC", tracking=True)
    qt_uc              = fields.Char("Quantité / UC", tracking=True)
    commentaire        = fields.Text("Commentaire", tracking=True)

    type_presse        = fields.Char("Type presse", tracking=True)
    tps_cycle          = fields.Char("Temps de cycle", tracking=True)
    nb_empreintes      = fields.Char("Nombre d'empreintes", tracking=True)
    nb_mod             = fields.Char("Nombre de mod", tracking=True)

    prev_annuelle      = fields.Char("Prévisions annuelles", tracking=True)
    date_dms           = fields.Date("Date dms", tracking=True)
    duree_vie          = fields.Char("Durée de vie", tracking=True)
    lot_livraison      = fields.Char("Lot de livraison", tracking=True)
    site_livraison     = fields.Char("Site de livraison", tracking=True)

    nomenclature_ids   = fields.One2many('is.fiche.codification.nomenclature.line', 'codification_id', string="Nomenclature")

    decomposition_ids   = fields.One2many('is.fiche.codification.decomposition.line', 'codification_id', string="Décomposition")


class is_fiche_codification_nomenclature_line(models.Model):
    _name        = "is.fiche.codification.nomenclature.line"
    _description = "Lignes nomenclature codification"
    _rec_name    = "nom_code_pg"
    _order       = 'nom_code_pg'

    codification_id    = fields.Many2one("is.fiche.codification", string="Codification", required=True, ondelete='cascade')
    nom_code_pg        = fields.Char("Nomenclature code PG")
    nom_designation	   = fields.Char("Désignation nomenclature")
    nom_qt	           = fields.Char("Quantité")

class is_fiche_codification_decomposition_line(models.Model):
    _name        = "is.fiche.codification.decomposition.line"
    _description = "Décomposition du prix de vente"

    codification_id    = fields.Many2one("is.fiche.codification", string="Codification", required=True, ondelete='cascade')
    part_mat	       = fields.Float("Part mat", digits=(12, 4))
    part_comp	       = fields.Float("Part comp", digits=(12, 4))
    part_emb	       = fields.Float("Part emb", digits=(12, 4))
    va_inj	           = fields.Float("VA inj", digits=(12, 4))
    va_ass	           = fields.Float("VA ass", digits=(12, 4))
    frais_port	       = fields.Float("Frais port", digits=(12, 4))
    logis	           = fields.Float("Logis", digits=(12, 4))
    amt_moule	       = fields.Float("Amt moule", digits=(12, 4))
    surcout_pre_serie  = fields.Float("Surcôut pré-série", digits=(12, 4))
    prix_vente	       = fields.Float("Prix vente", digits=(12, 4))
#
#    #piece_jointe
