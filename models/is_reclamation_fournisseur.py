# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IsReclamationFournisseur(models.Model):
	_name = "is.reclamation.fournisseur"
	_description = "Réclamation Fournisseur"
	_inherit = ["mail.thread", "mail.activity.mixin"]

	# Archivage standard Odoo
	active = fields.Boolean(string="Actif", default=True, tracking=True)

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

	# rf_fr_identification
	createur = fields.Char(string="Créateur", tracking=True)
	createurid = fields.Char(string="Créateur Id", tracking=True)
	telephone = fields.Char(string="Téléphone", tracking=True)
	courriel = fields.Char(string="Courriel", tracking=True)
	soc = fields.Char(string="Site", tracking=True)
	socid = fields.Char(string="ID du site", tracking=True)
	soccode = fields.Integer(string="Code du site", tracking=True)
	date_creation = fields.Date(string="Date de création", tracking=True)
	num_reclamation = fields.Integer(string="Numéro de la réclamation", tracking=True)
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
	nb_reclamations = fields.Integer(string="Nombre de réclamations en 12 mois", tracking=True)
	date_detection_defaut = fields.Date(string="Date de détection du défaut", tracking=True)
	annee_detection_defaut = fields.Char(string="Année de détection du défaut", tracking=True)

	# rf_fr_nature_reclamation
	nature_qualite = fields.Selection(
		selection=[("Non", "Non"), ("Oui", "Oui")], string="Qualité"
		, tracking=True)
	nature_logistique = fields.Selection(
		selection=[("Non", "Non"), ("Oui", "Oui")], string="Logistique"
		, tracking=True)
	nature_administratif = fields.Selection(
		selection=[("Non", "Non"), ("Oui", "Oui")], string="Administratif"
		, tracking=True)

	# rf_fr_rcp_concernee
	num_reception = fields.Char(string="Numéro de réception", tracking=True)
	fournisseur = fields.Char(string="Fournisseur", tracking=True)
	codepg = fields.Char(string="Référence PG", tracking=True)
	designation = fields.Char(string="Désignation", tracking=True)
	ref_fournisseur = fields.Char(string="Référence fournisseur", tracking=True)
	num_bl_fournisseur = fields.Char(string="Numéro de BL fournisseur", tracking=True)
	num_commande = fields.Char(string="Numéro de commande", tracking=True)
	prix_achat_commande = fields.Float(string="Prix achat commande", tracking=True)
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
	)
	date_analyse_obj = fields.Date(string="Date de l'analyse des causes (J+10)", tracking=True)
	date_plan_obj = fields.Date(string="Date du plan d'action (J+30)", tracking=True)
	date_cloture_obj = fields.Date(string="Date de clôture (J+60)", tracking=True)

	# rf_fr_commentaire
	commentaire_reponse = fields.Text(string="Commentaire réponse", tracking=True)

	# rf_fr_couts
	couts_produits = fields.Float(string="Coûts des produits", tracking=True)
	couts_tris = fields.Float(string="Coûts des tris", tracking=True)

	# Autres coûts (lignes)
	autre_cout_ids = fields.One2many(
		"is.reclamation.fournisseur.autre.cout",
		"reclamation_id",
		string="Autres coûts",
		tracking=True,
	)

	# Coûts comptables (lignes)
	cout_compta_ids = fields.One2many(
		"is.reclamation.fournisseur.cout.compta",
		"reclamation_id",
		string="Coûts comptables",
		tracking=True,
	)


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
	num_facture = fields.Char(string="N°facture")
	date_cout = fields.Date(string="Date")
	montant = fields.Float(string="Montant")

