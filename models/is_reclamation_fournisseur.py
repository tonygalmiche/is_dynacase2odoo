# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models


class IsReclamationFournisseur(models.Model):
    _name = "is.reclamation.fournisseur"
    _description = "Réclamation Fournisseur"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "num_reclamation"
    _order = "num_reclamation desc"


    @api.depends('date_detection_defaut')
    def _compute_annee_detection_defaut(self):
        for rec in self:
            if rec.date_detection_defaut:
                rec.annee_detection_defaut = rec.date_detection_defaut.year
            else:
                rec.annee_detection_defaut = False


    def _get_site_id(self):
        user = self.env['res.users'].browse(self._uid)
        site_id = user.is_site_id.id
        return site_id




    # rf_fr_identification
    site_id          = fields.Many2one('is.database', "Site", tracking=True, default=lambda self: self._get_site_id(),)
    telephone        = fields.Char(string="Téléphone", tracking=True)
    courriel         = fields.Char(string="Courriel", tracking=True)
    date_creation    = fields.Date("Date création", tracking=True, default=lambda *a: fields.datetime.now())
    num_reclamation  = fields.Integer(string="Numéro de la réclamation", tracking=True, index=True, copy=False, readonly=True)
    type_reclamation = fields.Selection(
        selection=[
            ("", ""),
            ("Comex", "Comex"),
            ("Alerte", "Alerte"),
            ("Réclamation", "Réclamation"),
        ],
        string="Type de réclamation",
        tracking=True,
    )
    nb_reclamations        = fields.Integer(string="Nombre de réclamations en 12 mois", tracking=True)
    date_detection_defaut  = fields.Date(string="Date détection", help="Date de détection du défaut", tracking=True, default=lambda *a: fields.datetime.now())
    annee_detection_defaut = fields.Char(string="Année détection", tracking=True, compute="_compute_annee_detection_defaut", store=True, readonly=True, copy=False)

    # rf_fr_nature_reclamation
    nature_qualite       = fields.Boolean(string="Qualité"      , tracking=True, default=False)
    nature_logistique    = fields.Boolean(string="Logistique"   , tracking=True, default=False)
    nature_administratif = fields.Boolean(string="Administratif", tracking=True, default=False)

    # rf_fr_rcp_concernee
    reception_id = fields.Many2one('is.reception', "Réception", tracking=True)
    num_reception = fields.Char(string="Numéro de réception", tracking=True)
    #fournisseur = fields.Char(string="Fournisseur", tracking=True)
    fournisseur_id = fields.Many2one('res.partner', 'Fournisseur', tracking=True, domain=[("is_company","=",True), ("supplier","=",True)])
    codepg = fields.Char(string="Référence PG", tracking=True)
    designation = fields.Char(string="Désignation", tracking=True)
    ref_fournisseur = fields.Char(string="Référence fournisseur", tracking=True)
    num_bl_fournisseur = fields.Char(string="Numéro de BL fournisseur", tracking=True)
    num_commande = fields.Char(string="Numéro de commande", tracking=True)
    prix_achat_commande = fields.Float(string="Prix achat commande", tracking=True, digits=(12, 4))
    quantite_livree = fields.Float(string="Quantité livrée", tracking=True)
    date_reception = fields.Date(string="Date de réception", tracking=True)

    # rf_fr_fournisseur_concerne
    nom_fournisseur = fields.Char(string="Nom du fournisseur", tracking=True)
    adr_fournisseur = fields.Char(string="Adresse du fournisseur", tracking=True)
    code_fournisseur = fields.Char(string="Code fournisseur", tracking=True)

    # rf_fr_description_reclamation
    quantite_nc = fields.Float(string="Quantité NC", tracking=True)
    quantite_a_facturer = fields.Float(string="Quantité à facturer", tracking=True)


    defaut_constate = fields.Text(string="Défaut constaté (ancien)", tracking=True)
    defaut_constate_choix = fields.Selection(
        selection=[
            ("", ""),
            ("01", "Aspect non conforme"),
            ("02", "Conditionnement abimé"),
            ("03", "Date de péremption dépassée"),
            ("04", "Dimensionnel / fonctionnel non conforme"),
            ("05", "Divers"),
            ("06", "Manque documentation qualité"),
            ("07", "Mélange pièce"),
            ("08", "Non respect date de livraison"),
            ("09", "Pièces souillées (sales;huileuses;rouillées;...)"),
            ("10", "Quantité non conforme"),
            ("11", "Référence non conforme"),
            ("12", "Transports exceptionnels"),
        ],
        string="Défaut constaté",
        tracking=True,
    )
    commentaire_description = fields.Text(string="Commentaire", tracking=True)
    reclamation_recurrente = fields.Selection(
        selection=[("", ""), ("OUI", "OUI"), ("NON", "NON")],
        string="Réclamation récurrente",
        tracking=True,
    )
    suppression_aqp = fields.Selection(
        selection=[("", ""), ("OUI", "OUI"), ("NON", "NON")],
        string="Suppression statut AQP",
        tracking=True,
    )

    # rf_fr_photo
    photo = fields.Binary(string="Photo", attachment=True, tracking=True)


    # rf_fr_tri_interne_pg
    motif_tri = fields.Char(string="Motif du tri", tracking=True)
    nombre_heures = fields.Float(string="Nombres d'heures", tracking=True)

    # rf_fr_reponse_fournisseur_reel
    date_secu_fourn_reel = fields.Date(string="Date de sécurisation fournisseur", tracking=True)
    date_analyse_reel = fields.Date(string="Date de l'analyse des causes", tracking=True)
    date_plan_reel = fields.Date(string="Date du plan d'action", tracking=True)
    date_cloture_reel = fields.Date(string="Date de clôture", tracking=True)

    # rf_fr_reponse_fournisseur_obj
    date_secu_fourn_obj = fields.Date(
        string="Date de sécurisation fournisseur (J+1)",
        tracking=True,
        default=lambda *a: fields.datetime.now() + timedelta(days=1)
    )
    date_analyse_obj = fields.Date(
        string="Date de l'analyse des causes (J+10)", tracking=True,
        default=lambda *a: fields.datetime.now() + timedelta(days=10)
    )
    date_plan_obj = fields.Date(
        string="Date du plan d'action (J+30)", tracking=True,
        default=lambda *a: fields.datetime.now() + timedelta(days=30)

    )
    date_cloture_obj = fields.Date(
        string="Date de clôture (J+60)", tracking=True,
        default=lambda *a: fields.datetime.now() + timedelta(days=60)
    )

    # rf_fr_commentaire
    commentaire_reponse = fields.Text(string="Commentaire réponse", tracking=True)

    couts_produits = fields.Float(
        string="Coûts des produits",
        tracking=True,
        help="Prix achat commande x Quantité à facturer",
        compute="_compute_couts_produits",
        store=True,
        readonly=True,
    )

    @api.depends('prix_achat_commande', 'quantite_a_facturer')
    def _compute_couts_produits(self):
        for rec in self:
            rec.couts_produits = (rec.prix_achat_commande or 0.0) * (rec.quantite_a_facturer or 0.0)


    couts_tris = fields.Float(
        string="Coûts des tris",
        tracking=True,
        compute="_compute_couts_tris",
        store=True,
        readonly=True,
    )

    @api.depends('annee_detection_defaut', 'nombre_heures')
    def _compute_couts_tris(self):
        for rec in self:
            try:
                annee = int(rec.annee_detection_defaut or 0)
            except (ValueError, TypeError):
                annee = 0
            cout_horaire = 25
            if annee >= 2025:
                cout_horaire = 30
            rec.couts_tris = round((rec.nombre_heures or 0) * cout_horaire)


    # Autres coûts (lignes)
    autre_cout_ids = fields.One2many(
        "is.reclamation.fournisseur.autre.cout",
        "reclamation_id",
        string="Détail autres coûts",
        tracking=True,
    )

    autres_couts = fields.Float(
        string="Autres coûts",
        tracking=True,
        help="Somme des montants des autres coûts",
        compute="_compute_autres_couts",
        store=True,
        readonly=True,
    )

    @api.depends('autre_cout_ids.montant_autre')
    def _compute_autres_couts(self):
        for rec in self:
            rec.autres_couts = sum(rec.autre_cout_ids.mapped('montant_autre'))

    # Coûts comptables (lignes)
    cout_compta_ids = fields.One2many(
        "is.reclamation.fournisseur.cout.compta",
        "reclamation_id",
        string="Détail facturation des coûts",
        tracking=True,
    )

    couts_compta = fields.Float(
        string="Total facturation des coûts",
        tracking=True,
        help="Somme des montants des factures des coûts",
        compute="_compute_couts_compta",
        store=True,
        readonly=True,
    )

    @api.depends('cout_compta_ids.montant')
    def _compute_couts_compta(self):
        for rec in self:
            rec.couts_compta = sum(rec.cout_compta_ids.mapped('montant'))

    somme_des_couts = fields.Float(
        string="Somme des coûts",
        tracking=True,
        help="Coûts des produits + Coûts des tris + Autres coûts + Coûts comptables",
        compute="_compute_somme_des_couts",
        store=True,
        readonly=True,
    )

    @api.depends('couts_produits', 'couts_tris', 'autre_cout_ids.montant_autre')
    def _compute_somme_des_couts(self):
        for rec in self:
            autres_couts = sum(rec.autre_cout_ids.mapped('montant_autre'))
            #couts_compta = sum(rec.cout_compta_ids.mapped('montant'))
            rec.somme_des_couts = (rec.couts_produits or 0.0) + (rec.couts_tris or 0.0) + autres_couts # + couts_compta

    ecart_cout = fields.Float(
        string="Écart coût",
        tracking=True,
        help="Somme des coûts - Coûts comptables",
        compute="_compute_ecart_cout",
        store=True,
        readonly=True,
    )

    @api.depends('somme_des_couts', 'couts_compta')
    def _compute_ecart_cout(self):
        for rec in self:
            rec.ecart_cout = (rec.somme_des_couts or 0.0) - (rec.couts_compta or 0.0)




    piece_jointe_ids = fields.Many2many("ir.attachment", "is_reclamation_fournisseur_piece_jointe_rel", "piece_jointe", "att_id", string="Pièce jointe")
    active = fields.Boolean(string="Actif", default=True, tracking=True)
    dynacase_id = fields.Integer(string="Id Dynacase", index=True, copy=False)





    def lien_vers_dynacase_action(self):
        for obj in self:
            url = "https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s" % obj.dynacase_id
            return {
                "type": "ir.actions.act_url",
                "url": url,
                "target": "new",
            }


    def action_recalculer_couts(self):
        """Action serveur pour recalculer tous les champs calculés liés aux coûts"""
        for rec in self:
            try:
                # Vérifie d'abord que la nature de réclamation est valide
                rec._validate_nature_reclamation()
                # Si pas d'erreur, on peut recalculer les coûts
                rec._compute_couts_produits()
                rec._compute_couts_tris()
                rec._compute_autres_couts()
                rec._compute_couts_compta()
                rec._compute_somme_des_couts()
                rec._compute_ecart_cout()
            except Exception as e:
                # Si la validation échoue, on passe à l'enregistrement suivant
                continue
        #return {'type': 'ir.actions.client', 'tag': 'reload'}



    def maj_quantite_livree_action(self):
        """Action serveur pour recalculer le champ 'Quantité livrée'"""
        for obj in self:
            if obj.reception_id and obj.reception_id.quantite_livree>0:
                obj.with_context(skip_nature_validation=True).write({'quantite_livree': obj.reception_id.quantite_livree})

            if not obj.reception_id and obj.num_reception:
                domain=[
                    ('database_id','=',obj.site_id.id),
                    ('numero_reception','=',obj.num_reception),
                ]
                receptions=self.env['is.reception'].search(domain,order='numero_reception desc', limit=1)
                for reception in receptions:
                    if reception.quantite_livree>0:
                        vals={
                            'reception_id'   : reception.id,
                            'quantite_livree': reception.quantite_livree,
                        }
                        obj.with_context(skip_nature_validation=True).write(vals)



    def _validate_nature_reclamation(self, vals=None):
        """Valide qu'exactement une des trois natures est cochée"""
        if vals is None:
            vals = {}
        
        # Récupère les valeurs actuelles ou celles à modifier
        nature_qualite = vals.get('nature_qualite', getattr(self, 'nature_qualite', False))
        nature_logistique = vals.get('nature_logistique', getattr(self, 'nature_logistique', False))
        nature_administratif = vals.get('nature_administratif', getattr(self, 'nature_administratif', False))
        
        # Compte le nombre de cases cochées
        nb_coches = sum([nature_qualite, nature_logistique, nature_administratif])
        
        if nb_coches == 0:
            raise models.ValidationError("Il est obligatoire de cocher au moins une nature de réclamation (Qualité, Logistique ou Administratif).")
        elif nb_coches > 1:
            raise models.ValidationError("Il est interdit de cocher plus d'une nature de réclamation. Veuillez sélectionner uniquement Qualité, Logistique ou Administratif.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Validation de la nature de réclamation
            self._validate_nature_reclamation(vals)
            
            lines=self.env['is.reclamation.fournisseur'].search([],order='num_reclamation desc', limit=1)
            num_reclamation=1
            for line in lines:
                num_reclamation = line.num_reclamation + 1
            vals['num_reclamation'] = num_reclamation
        return super().create(vals_list)

    def write(self, vals):
        # Validation de la nature de réclamation pour chaque enregistrement
        # Sauf si le contexte skip_nature_validation est activé
        if not self.env.context.get('skip_nature_validation'):
            for record in self:
                record._validate_nature_reclamation(vals)
        return super().write(vals)


    @api.onchange('reception_id')
    def onchange_reception_id(self):
        for obj in self:
            numero_reception = fournisseur_id = code_pg = designation = ref_fournisseur = False
            numero_bl_fournisseur = numero_commande = prix_achat_commande = quantite_livree = date_reception = False
            if obj.reception_id:
                numero_reception = obj.reception_id.numero_reception
                fournisseur_id   = obj.reception_id.fournisseur_id.id 
                code_pg          = obj.reception_id.code_pg
                designation      = obj.reception_id.designation
                ref_fournisseur = obj.reception_id.reference_fournisseur
                numero_bl_fournisseur = obj.reception_id.numero_bl_fournisseur
                numero_commande     = obj.reception_id.numero_commande
                prix_achat_commande = (obj.reception_id.prix_achat_commande / (obj.reception_id.unit_coef or 1))
                quantite_livree     = obj.reception_id.quantite_livree
                date_reception      = obj.reception_id.date_reception
            obj.num_reception = numero_reception
            obj.fournisseur_id = fournisseur_id
            obj.codepg = code_pg
            obj.designation = designation
            obj.ref_fournisseur = ref_fournisseur
            obj.num_bl_fournisseur = numero_bl_fournisseur
            obj.num_commande = numero_commande
            obj.prix_achat_commande = prix_achat_commande
            obj.quantite_livree = quantite_livree
            obj.date_reception = date_reception



    @api.onchange('fournisseur_id')
    def onchange_fournisseur_id(self):
        for obj in self:
            nom_fournisseur = adr_fournisseur = code_fournisseur = False
            if obj.fournisseur_id:
                nom_fournisseur = obj.fournisseur_id.name
                adr_fournisseur = "%s %s %s %s"%(obj.fournisseur_id.street,obj.fournisseur_id.street2,obj.fournisseur_id.zip,obj.fournisseur_id.city)
                code_fournisseur = obj.fournisseur_id.is_code
            obj.nom_fournisseur = nom_fournisseur
            obj.adr_fournisseur = adr_fournisseur
            obj.code_fournisseur = code_fournisseur


class IsReclamationFournisseurAutreCout(models.Model):
    _name = "is.reclamation.fournisseur.autre.cout"
    _description = "Réclamation Fournisseur - Autre coût"

    reclamation_id = fields.Many2one(
        "is.reclamation.fournisseur",
        string="Réclamation",
        required=True,
        ondelete="cascade",
    )
    type_cout = fields.Char(string="Type de coût")
    montant_autre = fields.Float(string="Montant")


class IsReclamationFournisseurCoutCompta(models.Model):
    _name = "is.reclamation.fournisseur.cout.compta"
    _description = "Réclamation Fournisseur - Coût comptable"

    reclamation_id = fields.Many2one(
        "is.reclamation.fournisseur",
        string="Réclamation",
        required=True,
        ondelete="cascade",
    )
    facture_id = fields.Many2one(
        "is.factures",
        string="Facture",
        domain="[('site_id', '=', site_id), ('move_type', 'in', ['in_invoice', 'in_refund'])]"
    )
    site_id = fields.Many2one(
        "is.database",
        string="Site",
        related="reclamation_id.site_id",
        store=True,
        readonly=True
    )
    num_facture = fields.Char(string="N°facture")
    date_cout = fields.Date(string="Date")
    montant = fields.Float(string="Montant")

    @api.onchange('facture_id')
    def onchange_facture_id(self):
        for obj in self:
            if obj.facture_id:
                num_facture = obj.facture_id.supplier_invoice_number
                # Ajouter un préfixe selon le type de facture
                if obj.facture_id.move_type == 'in_refund':
                    num_facture = f"AVOIR - {num_facture}"
                elif obj.facture_id.move_type == 'in_invoice':
                    num_facture = f"FACTURE - {num_facture}"
                obj.num_facture = num_facture
                obj.date_cout = obj.facture_id.date_facture
                obj.montant = obj.facture_id.montant_ht
            else:
                obj.num_facture = False
                obj.date_cout = False
                obj.montant = False

