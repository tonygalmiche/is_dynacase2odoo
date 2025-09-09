# -*- coding: utf-8 -*-
from odoo import models, fields, api  # type: ignore


class IsFNC(models.Model):
	_name = "is.fnc"
	_description = "Fiche Non-Conformité (FNC)"
	_rec_name = "num_non_conformite"
	_order = "id desc"
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

	# ------------------------------------------------------------
	# Description (fr_description)
	# ------------------------------------------------------------
	#createur = fields.Char(string="Créateur de la FNC", tracking=True)
	#createurid = fields.Integer(string="Créateur de la FNC Id", index=True, tracking=True)

	#soc = fields.Char(string="Site", tracking=True)
	#socid = fields.Integer(string="ID du site", index=True, tracking=True)
	#soccode = fields.Integer(string="Code du site", tracking=True)
	#site = fields.Char(string="Site émetteur", tracking=True)
	#siteid = fields.Integer(string="Site émetteur ID", index=True, tracking=True)

	site_id = fields.Many2one('is.database', "Site")

	type_non_conformite = fields.Selection(
		selection=[
			("", ""),
			("FNC", "FNC"),
			("FNE", "FNE"),
			("FNI", "FNI"),
			("FNL", "FNL"),
			("ALERTE", "ALERTE"),
			("COMEX", "COMEX"),
		],
		string="Type de non-conformité",
		tracking=True,
	)
	num_non_conformite = fields.Char(string="N° de non-conformité PG", tracking=True)
	date_detection = fields.Date(string="Date de détection", tracking=True)

	#client = fields.Char(string="Client émetteur", tracking=True)
	#clientid = fields.Integer(string="Client émetteur ID", index=True, tracking=True)
	client_id    = fields.Many2one('res.partner', string='Client émetteur',tracking=True, domain=[('is_company', '=', True), ('customer', '=', True), ('is_code', 'ilike', '90%')]) 
	client_autre = fields.Char(string="Autre client", readonly=True)

	mail_commercial = fields.Char(string="Mail du commercial", tracking=True)


	num_reclamation = fields.Char(string="N° de réclamation client", tracking=True)
	contact_client = fields.Char(string="Contact Client", tracking=True)

	#famille_article = fields.Char(string="Famille article", tracking=True)
	total_non_conforme = fields.Float(
		string="Total pièces non conformes",
		digits=(16, 0),
		tracking=True,
		compute="_compute_total_non_conforme",
		store=False,
		readonly=True,
	)

	@api.depends('produit_ids.qt_non_conforme')
	def _compute_total_non_conforme(self):
		for rec in self:
			total = 0.0
			for line in rec.produit_ids:
				total += line.qt_non_conforme or 0.0
			rec.total_non_conforme = total



	description_probleme = fields.Char(string="Description du problème", tracking=True)
	type_defaut = fields.Selection(
		selection=[
			("", ""),
			("Accostage non conforme", "Accostage non conforme"),
			("Assemblage non conforme", "Assemblage non conforme"),
			("Déformation pièce", "Déformation pièce"),
			("Bavures", "Bavures"),
			("Brûlures", "Brûlures"),
			("Carotte non coupée", "Carotte non coupée"),
			("Composants non-conformes", "Composants non-conformes"),
			("Conditionnement non-conforme", "Conditionnement non-conforme"),
			("Défaut de marquage/sérigraphie", "Défaut de marquage/sérigraphie"),
			("Fils carottes", "Fils carottes"),
			("Fils plans de joints", "Fils plans de joints"),
			("Géométrie non conforme", "Géométrie non conforme"),
			("Identification non-conforme", "Identification non-conforme"),
			("Livraison non-conforme", "Livraison non-conforme"),
			("Manques composants", "Manques composants"),
			("Marque éjecteur", "Marque éjecteur"),
			("Mélange références", "Mélange références"),
			("Matière non-conforme", "Matière non-conforme"),
			("Pièces cassées", "Pièces cassées"),
			("Pièces incomplètes", "Pièces incomplètes"),
			("Pollution matière", "Pollution matière"),
			("Présence de chocs", "Présence de chocs"),
			("Présence de salissure", "Présence de salissure"),
			("Rayures", "Rayures"),
			("Rebut de chaîne client", "Rebut de chaîne client"),
			("Retassures", "Retassures"),
			("Surplus de matière", "Surplus de matière"),
			("Teinte non-conforme", "Teinte non-conforme"),
			("Traces de colorant", "Traces de colorant"),
			("Traces injection", "Traces injection"),
			("Zone de flux", "Zone de flux"),
		],
		string="Type de défaut",
		tracking=True,
	)
	tracabilite = fields.Char(string="Traçabilité (date fab° + OF + N°OP)", tracking=True)
	reclamation_recurrente = fields.Selection(
		selection=[("", ""), ("OUI", "OUI"), ("NON", "NON")],
		string="Réclamation récurrente",
		tracking=True,
	)

	# ------------------------------------------------------------
	# Action (fr_action)
	# ------------------------------------------------------------
	nb_retournees = fields.Float(string="Nbre de pièces retournées", digits=(16, 2), tracking=True)
	nb_detruites = fields.Float(string="Nbre de pièces détruites", digits=(16, 2), tracking=True)
	bl_retour = fields.Char(string="BL de retour", tracking=True)
	reponse = fields.Date(string="Date 1ère réponse", tracking=True)

	# ------------------------------------------------------------
	# Analyse (fr_analyse)
	# ------------------------------------------------------------
	equipe = fields.Char(string="Équipe", tracking=True)
	operateur = fields.Char(string="Opérateur", tracking=True)


	#presse = fields.Char(string="Presse", tracking=True)
	#presseid = fields.Integer(string="Presse ID", index=True, tracking=True)

	presse_id = fields.Many2one('is.equipement', "Presse", tracking=True, domain=[('type_id.name','=','PRESSE')])


	origine_defaut = fields.Selection(
		selection=[
			("", ""),
			("Fournisseur", "Fournisseur"),
			("Sous-Traitant", "Sous-Traitant"),
			("Transporteur", "Transporteur"),
			("Client", "Client"),
			("Plastigray - Gray", "Plastigray - Gray"),
			("Plastigray - Eloyes", "Plastigray - Eloyes"),
			("Plastigray - ST-Brice", "Plastigray - ST-Brice"),
			("Plasti-ka", "Plasti-ka"),
			("Développement", "Développement"),
		],
		string="Origine du défaut",
		tracking=True,
	)
	decision = fields.Selection(
		selection=[
			("?", "?"),
			("Acceptée", "Acceptée"),
			("Contestée", "Contestée"),
			("Annulée", "Annulée"),
		],
		string="Décision",
		tracking=True,
	)
	date_reponse_4d = fields.Date(string="Date réponse 4D", tracking=True)

	# ------------------------------------------------------------
	# Plan d'action (fr_planaction)
	# ------------------------------------------------------------
	date_8d = fields.Date(string="Date réponse 8D", tracking=True)

	# ------------------------------------------------------------
	# 8D (fr_8D)
	# ------------------------------------------------------------
	doc_amdec = fields.Selection(
		selection=[("", ""), ("OUI", "OUI"), ("NON", "NON")],
		string="Modification AMDEC",
		tracking=True,
	)
	doc_plan_surveillance = fields.Selection(
		selection=[("", ""), ("OUI", "OUI"), ("NON", "NON")],
		string="Modification Plans de surveillance, fiche de contrôle",
		tracking=True,
	)
	doc_moyen_controle = fields.Selection(
		selection=[("", ""), ("OUI", "OUI"), ("NON", "NON")],
		string="Modification Moyens de contrôle, gabarits",
		tracking=True,
	)
	doc_mode_operatoire = fields.Selection(
		selection=[("", ""), ("OUI", "OUI"), ("NON", "NON")],
		string="Modification Mode opératoire",
		tracking=True,
	)
	doc_plans = fields.Selection(
		selection=[("", ""), ("OUI", "OUI"), ("NON", "NON")],
		string="Modification Plans",
		tracking=True,
	)
	doc_autres = fields.Selection(
		selection=[("", ""), ("OUI", "OUI"), ("NON", "NON")],
		string="Modification Autres",
		tracking=True,
	)
	date_cloture = fields.Date(string="Date de clôture", tracking=True)

	# ------------------------------------------------------------
	# Coûts / Bilan
	# ------------------------------------------------------------
	total_avoir = fields.Float(string="Total des avoirs", digits=(16, 2), tracking=True)

	date_bilan = fields.Date(string="Date Bilan", tracking=True)
	situation_bilan = fields.Char(string="Décision bilan", tracking=True)

	cout_piece = fields.Float(string="Total coûts pièces", digits=(16, 2), tracking=True)
	cout_total_tri = fields.Float(string="Total coûts tri", digits=(16, 2), tracking=True)
	total_autrecouts = fields.Float(string="Total autres coûts non-qualité", digits=(16, 2), tracking=True)

	cout_total = fields.Float(string="Coût TOTAL", digits=(16, 2), tracking=True)
	cout_facture = fields.Float(string="Coût facturé FIF", digits=(16, 2), tracking=True)
	total_perte = fields.Float(string="TOTAL coût non-qualité", digits=(16, 2), tracking=True)

	# ------------------------------------------------------------
	# Produits
	# ------------------------------------------------------------
	produit_ids = fields.One2many(
		"is.fnc.produit",
		"fnc_id",
		string="Produits",
		copy=True,
	)

	# ------------------------------------------------------------
	# Actions (stocks/tri)
	# ------------------------------------------------------------
	action_ids = fields.One2many(
		"is.fnc.action",
		"fnc_id",
		string="Actions",
		copy=True,
	)

	# Actions curatives
	action_curative_ids = fields.One2many(
		"is.fnc.action.curative",
		"fnc_id",
		string="Actions curatives",
		copy=True,
	)

	# Actions correctives
	action_corrective_ids = fields.One2many(
		"is.fnc.action.corrective",
		"fnc_id",
		string="Actions correctives",
		copy=True,
	)

	# Actions préventives
	action_preventive_ids = fields.One2many(
		"is.fnc.action.preventive",
		"fnc_id",
		string="Actions préventives",
		copy=True,
	)

	# Mesure de l'efficacité des actions
	action_efficacite_ids = fields.One2many(
		"is.fnc.action.efficacite",
		"fnc_id",
		string="Mesure de l'efficacité",
		copy=True,
	)

	# Avoirs / Factures
	avoir_ids = fields.One2many(
		"is.fnc.avoir",
		"fnc_id",
		string="Avoirs / Factures",
		copy=True,
	)

	# Autres coûts non qualité
	autre_cout_ids = fields.One2many(
		"is.fnc.autre.cout",
		"fnc_id",
		string="Autres coûts non qualité",
		copy=True,
	)

	# Causes
	cause_ids = fields.One2many(
		"is.fnc.cause",
		"fnc_id",
		string="Causes",
		copy=True,
	)


class IsFNCProduit(models.Model):
	_name = "is.fnc.produit"
	_description = "Ligne produit pour FNC"
	_order = "id"

	fnc_id = fields.Many2one(
		"is.fnc", string="FNC", required=True, ondelete="cascade", index=True
	)
	article_id      = fields.Many2one('is.article', 'Article')
	moule_id        = fields.Many2one("is.mold", string="Moule")
	dossierf_id     = fields.Many2one("is.dossierf", string="Dossier F")
	project_id      = fields.Many2one('is.mold.project', 'Projet')
	designation     = fields.Char(string="Désignation")
	ref_client      = fields.Char(string="Référence client")
	prix_vente      = fields.Float(string="Prix de vente ou coût", digits=(16, 4))
	qt_non_conforme = fields.Float(string="Quantité non-conforme", digits=(16, 2))
	qt_retournee    = fields.Float(string="Quantité retournée", digits=(16, 2))
	qt_detruite     = fields.Float(string="Quantité détruite", digits=(16, 2))


	@api.onchange('article_id')
	def onchange_article_id(self):
		designation = moule_id = dossierf_id = project_id = ref_client = False
		if self.article_id:
			designation = self.article_id.designation
			ref_client  = self.article_id.ref_client
			if self.article_id.moule:
				if str(self.article_id.moule).startswith('F'):
					domain = [
						('name', '=', self.article_id.moule)
					]
					lines = self.env['is.dossierf'].search(domain, limit=1)
					for line in lines:
						dossierf_id = line.id	
						project_id  = line.project.id
				else:
					domain = [
						('name', '=', self.article_id.moule)
					]
					lines = self.env['is.mold'].search(domain, limit=1)
					for line in lines:
						moule_id   = line.id	
						project_id = line.project.id
		self.designation = designation
		self.moule_id    = moule_id
		self.dossierf_id = dossierf_id
		self.project_id  = project_id
		self.ref_client  = ref_client


class IsFNCAction(models.Model):
	_name = "is.fnc.action"
	_description = "Action de tri/stock pour FNC"
	_order = "id"

	fnc_id = fields.Many2one(
		"is.fnc", string="FNC", required=True, ondelete="cascade", index=True
	)
	tri_stock = fields.Selection(
		selection=[
			("Client"      , "Client"), 
			("Client final", "Client final"), 
			("PG"          , "PG"), 
			("Fournisseur" , "Fournisseur")
		],
		string="Tri des stocks",
	)
	action_stock = fields.Char(string="Actions sur les stocks")
	responsable_tri = fields.Char(string="Responsable du tri")
	date_tri = fields.Date(string="Date du tri")
	nb_non_conforme = fields.Float(string="Nbre de pcs non-conformes", digits=(16, 2))
	cout_tri = fields.Float(string="Coût du tri", digits=(16, 2))


class IsFNCActionCurative(models.Model):
	_name = "is.fnc.action.curative"
	_description = "Action curative pour FNC"
	_order = "id"

	fnc_id = fields.Many2one(
		"is.fnc", string="FNC", required=True, ondelete="cascade", index=True
	)

	cur_action = fields.Char(string="Actions")
	cur_responsable = fields.Char(string="Responsable")
	cur_delai = fields.Date(string="Délai")
	cur_date = fields.Date(string="Date de réalisation")


class IsFNCActionCorrective(models.Model):
	_name = "is.fnc.action.corrective"
	_description = "Action corrective pour FNC"
	_order = "id"

	fnc_id = fields.Many2one(
		"is.fnc", string="FNC", required=True, ondelete="cascade", index=True
	)

	cor_action = fields.Char(string="Actions")
	cor_responsable = fields.Char(string="Responsable")
	cor_delai = fields.Date(string="Délai")
	cor_date = fields.Date(string="Date de réalisation")


class IsFNCActionPreventive(models.Model):
	_name = "is.fnc.action.preventive"
	_description = "Action préventive pour FNC"
	_order = "id"

	fnc_id = fields.Many2one(
		"is.fnc", string="FNC", required=True, ondelete="cascade", index=True
	)

	pre_action = fields.Char(string="Actions")
	pre_responsable = fields.Char(string="Responsable")
	pre_delai = fields.Date(string="Délai")
	pre_date = fields.Date(string="Date de réalisation")


class IsFNCActionEfficacite(models.Model):
	_name = "is.fnc.action.efficacite"
	_description = "Mesure de l'efficacité des actions pour FNC"
	_order = "id"

	fnc_id = fields.Many2one(
		"is.fnc", string="FNC", required=True, ondelete="cascade", index=True
	)

	eff_action = fields.Char(string="Actions")
	eff_responsable = fields.Char(string="Responsable")
	eff_delai = fields.Date(string="Délai")
	eff_date = fields.Date(string="Date de réalisation")
	eff_conclusion = fields.Char(string="Conclusion")


class IsFNCAvoir(models.Model):
	_name = "is.fnc.avoir"
	_description = "Avoir / Facture lié à une FNC"
	_order = "id"

	fnc_id = fields.Many2one(
		"is.fnc", string="FNC", required=True, ondelete="cascade", index=True
	)

	num_avoir = fields.Char(string="N° avoir / facture")
	date_avoir = fields.Date(string="Date")
	montant_avoir = fields.Float(string="Montant", digits=(16, 2))


class IsFNCAutreCout(models.Model):
	_name = "is.fnc.autre.cout"
	_description = "Autre coût non qualité lié à une FNC"
	_order = "id"

	fnc_id = fields.Many2one(
		"is.fnc", string="FNC", required=True, ondelete="cascade", index=True
	)

	# Anciennes colonnes: fnc_coutype, fnc_coutmontant (sans le préfixe fnc_)
	type_cout = fields.Char(string="Type de coût")
	montant = fields.Float(string="Coût", digits=(16, 2))


class IsFNCCause(models.Model):
	_name = "is.fnc.cause"
	_description = "Cause associée à une FNC"
	_order = "id"

	fnc_id = fields.Many2one(
		"is.fnc", string="FNC", required=True, ondelete="cascade", index=True
	)

	cause = fields.Char(string="Cause")
	type = fields.Selection(
		selection=[("", ""), ("Création", "Création"), ("Non-détection", "Non-détection")],
		string="Type",
	)
	type_cause = fields.Selection(
		selection=[
			("", ""),
			("Processus injection non capable", "Processus injection non capable"),
			("Dossier process non-respecté", "Dossier process non-respecté"),
			("Dossier produit non-respecté", "Dossier produit non-respecté"),
			("Opérateur non habilité", "Opérateur non habilité"),
			("Cycle de refroidissement non respecté", "Cycle de refroidissement non respecté"),
			("Processus assemblage non respecté", "Processus assemblage non respecté"),
			("Panne ou incident moyen de production", "Panne ou incident moyen de production"),
			("Développement pièce", "Développement pièce"),
			("Développement conditionnement", "Développement conditionnement"),
			("Manipulation box", "Manipulation box"),
			("Procédures non respectées", "Procédures non respectées"),
			("Rebut de chaîne client", "Rebut de chaîne client"),
		],
		string="Type de cause",
	)
	contribution = fields.Integer(string="% de contribution")

