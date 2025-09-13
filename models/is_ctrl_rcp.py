from odoo import models, fields  # type: ignore


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
	# 	"ir.attachment",
	# 	"is_ctrl_rcp_gamme_attachment_rel",
	# 	"gamme_id",
	# 	"attachment_id",
	# 	string="Pièces jointes",
	# 	tracking=True,
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
	tolerance_mini    = fields.Float(string="Tolérance mini")
	tolerance_maxi    = fields.Float(string="Tolérance maxi")


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

