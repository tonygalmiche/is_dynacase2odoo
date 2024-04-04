# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class is_revue_projet_jalon(models.Model):
    _name        = "is.revue.projet.jalon"
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = "Compte-rendu revue de projet jalon"
    _rec_name    = "rpj_chrono"

    @api.depends("state")
    def _compute_vsb(self):
        for obj in self:
            vsb = False
            if obj.state in ["directeur_technique"]:
                vsb = True
            obj.vers_brouillon_vsb = vsb
            vsb = False
            if obj.state in ["brouillon"]:
                vsb = True
            obj.vers_directeur_technique_vsb = vsb
            vsb = False
            if obj.state in ["directeur_technique"]:
                vsb = True
            obj.vers_direceeur_de_site_vsb = vsb
            vsb = False
            if obj.state in ["brouillon"]:
                vsb = True
            obj.vers_pour_information_vsb = vsb
            vsb = False
            if obj.state in ["brouillon", "direceeur_de_site"]:
                vsb = True
            obj.vers_valide_vsb = vsb
            vsb = False
            if obj.state in ["directeur_technique", "direceeur_de_site"]:
                vsb = True
            obj.vers_refuse_vsb = vsb

    def vers_brouillon_action(self):
        for obj in self:
            obj.sudo().state = "brouillon"

    def vers_directeur_technique_action(self):
        for obj in self:
            obj.sudo().state = "directeur_technique"

    def vers_direceeur_de_site_action(self):
        for obj in self:
            obj.sudo().state = "direceeur_de_site"

    def vers_pour_information_action(self):
        for obj in self:
            obj.sudo().state = "pour_information"

    def vers_valide_action(self):
        for obj in self:
            obj.sudo().state = "valide"

    def vers_refuse_action(self):
        for obj in self:
            obj.sudo().state = "refuse"

    rpj_chrono                   = fields.Char(string="Chrono", required=True)
    rpj_mouleid                  = fields.Many2one("is.mold", string="Moule", required=True)
    rpj_j = fields.Selection([
        ("J0", "Préparation J0"),
        ("J1", "Préparation J1"),
        ("J2", "Préparation J2"),
        ("J3", "Préparation J3"),
        ("J4", "Préparation J4"),
        ("J5", "Préparation J5"),
        ("J6", "J5 validé"),
    ], string="J actuelle")
    rpj_date_planning_j          = fields.Date(string="Date planning J")
    rpj_indice                   = fields.Char(string="Indice")
    rpj_date_creation            = fields.Date(string="Date de réalisation", default=fields.Date.context_today)
    rpj_plan_action              = fields.Char(string="Plan d'action associé")
    rpj_niveau_ppm               = fields.Char(string="Niveau ppm revue de contrat")
    rpj_commentaire              = fields.Text(string="Commentaire")
    rpj_motif_refus              = fields.Text(string="Motif du refus")
    rpj_photo                    = fields.Image(string="Photo de la pièce")
    rpj_lieu_production          = fields.Selection([
        ("g", "Gray"),
        ("sb", "St-Brice"),
        ("pl", "Plasti-ka"),
        ("st", "Sous-Traitant"),
    ], string="Lieu de production (Revue de lancement)")
    rpj_affectation_presse       = fields.Char(string="Affectation presse (Revue de lancement)")
    rpj_lieu_production2         = fields.Selection([
        ("g",  "Gray"),
        ("sb", "St-Brice"),
        ("pl", "Plasti-ka"),
        ("st", "Sous-Traitant"),
    ], string="Lieu de production actuel")
    rpj_affectation_presse2      = fields.Char(string="Affectation presse actuelle")
    rpj_clientid                 = fields.Many2one("res.partner", string="Client", domain=[("is_company","=",True), ("customer","=",True)])
    rpj_rcid                     = fields.Many2one("is.revue.de.contrat", string="Revue de contrat")
    rpj_indice                   = fields.Integer(string="Indice")
    rpj_rlid                     = fields.Many2one("is.revue.lancement", string="Revue de lancement")
    rpj_rp                       = fields.Char(string="Revue de projet")
    rpj_rr                       = fields.Char(string="Revue des risques")
    bilan_ids                    = fields.One2many("is.revue.projet.jalon.bilan", "is_revue_project_jalon_id")
    rpj_piece_jointe             = fields.Many2many("ir.attachment", "is_jalon_rpj_jointe_rel", "rpj_jointe_id", "att_id", string="Pièces jointes")
    equipe_projet_ids            = fields.One2many("is.revue.projet.jalon.equipe.projet", "is_revue_project_jalon_id")
    rpj_chef_projetid            = fields.Many2one("res.users", string="Chef de projet")
    rpj_expert_injectionid       = fields.Many2one("res.users", string="Expert injection")
    rpj_methode_injectionid      = fields.Many2one("res.users", string="Méthode injection")
    rpj_methode_assemblageid     = fields.Many2one("res.users", string="Méthode assemblage")
    rpj_qualite_devid            = fields.Many2one("res.users", string="Métrologie")
    rpj_qualite_usineid          = fields.Many2one("res.users", string="Qualité développement")
    rpj_achatsid                 = fields.Many2one("res.users", string="Achats")
    rpj_logistiqueid             = fields.Many2one("res.users", string="Logistique")
    rpj_logistique_usineid       = fields.Many2one("res.users", string="Logistique Usine")
    rpj_commercial2id            = fields.Many2one("res.users", string="Commercial")
    rpj_responsable_outillageid  = fields.Many2one("res.users", string="Responsable outillage")
    rpj_responsable_projetid     = fields.Many2one("res.users", string="Responsable projets")
    rpj_directeur_siteid         = fields.Many2one("res.users", string="Directeur site de production")
    rpj_directeur_techniqueid    = fields.Many2one("res.users", string="Directeur technique")
    rpj_critere_a_risque         = fields.Text(string="Critères à risque")
    rpj_date_j0                  = fields.Date(string="J0")
    rpj_date_j1                  = fields.Date(string="J1")
    rpj_date_j2                  = fields.Date(string="J2")
    rpj_date_j3                  = fields.Date(string="J3")
    rpj_date_j4                  = fields.Date(string="J4")
    rpj_date_j5                  = fields.Date(string="J5")
    rpj_avancement_j0            = fields.Integer(string="Avancement J0")
    rpj_avancement_j1            = fields.Integer(string="Avancement J1")
    rpj_avancement_j2            = fields.Integer(string="Avancement J2")
    rpj_avancement_j3            = fields.Integer(string="Avancement J3")
    rpj_avancement_j4            = fields.Integer(string="Avancement J4")
    rpj_avancement_j5            = fields.Integer(string="Avancement J5")
    rpj_date_valide_j0           = fields.Date(string="Date validation J0")
    rpj_date_valide_j1           = fields.Date(string="Date validation J1")
    rpj_date_valide_j2           = fields.Date(string="Date validation J2")
    rpj_date_valide_j3           = fields.Date(string="Date validation J3")
    rpj_date_valide_j4           = fields.Date(string="Date validation J4")
    rpj_date_valide_j5           = fields.Date(string="Date validation J5")
    documents_ids                = fields.One2many("is.revue.projet.jalon.documents", "is_revue_project_jalon_id")
    rpj_point_bloquant           = fields.Integer(string="Nombre de points bloquants")
    rpj_point_bloquant_liste     = fields.Text(string="Liste des points bloquants")
    rpj_note                     = fields.Integer(string="Note finale (%)")
    revue_de_contrat_ids         = fields.One2many("is.revue.projet.jalon.revue.de.contrat", "is_revue_project_jalon_id")
    revue_de_projet_jalon_ids    = fields.One2many("is.revue.projet.jalon.revue.de.projet.jalon", "is_revue_project_jalon_id")
    rpj_total_vente_moule        = fields.Float(string="Total vente moule")
    rpj_total_achat_moule        = fields.Float(string="Total achat moule")
    rp_marge_brute_moule         = fields.Float(string="Marge brute moule (%)")
    decomposition_prix_ids       = fields.One2many("is.revue.projet.jalon.decomposition.prix", "is_revue_project_jalon_id")
    rpj_dp_ca_annuel             = fields.Float(string="CA Annuel")
    rpj_dp_vac                   = fields.Float(string="VAC")
    rpj_dp_eiv_total             = fields.Float(string="Total investissement")
    rpj_dp_schema_flux_vendu     = fields.Char(string="Schéma de flux vendu")
    dynacase_id                  = fields.Integer(string="Id Dynacase")
    state = fields.Selection([
        ("brouillon",           "Brouillon"),
        ("directeur_technique", "Directeur Technique"),
        ("direceeur_de_site",   "Direceeur de Site"),
        ("pour_information",    "Pour Information"),
        ("valide",              "Validé"),
        ("refuse",              "Refusé"),
    ], default="brouillon", string="State", tracking=True)
    vers_brouillon_vsb           = fields.Boolean(string="Brouillon", compute='_compute_vsb', readonly=True, store=False)
    vers_directeur_technique_vsb = fields.Boolean(string="Directeur Technique", compute='_compute_vsb', readonly=True, store=False)
    vers_direceeur_de_site_vsb   = fields.Boolean(string="Direceeur de Site", compute='_compute_vsb', readonly=True, store=False)
    vers_pour_information_vsb    = fields.Boolean(string="Pour Information", compute='_compute_vsb', readonly=True, store=False)
    vers_valide_vsb              = fields.Boolean(string="Validé", compute='_compute_vsb', readonly=True, store=False)
    vers_refuse_vsb              = fields.Boolean(string="Refusé", compute='_compute_vsb', readonly=True, store=False)


class is_revue_projet_jalon_bilan(models.Model):
    _name        = "is.revue.projet.jalon.bilan"
    _description = "Compte-rendu revue de projet jalon - Bilan"
    _rec_name    = "rpj_bilan_risque_j"

    rpj_bilan_risque_j            = fields.Selection([
        ("J0", "Préparation J0"),
        ("J1", "Préparation J1"),
        ("J2", "Préparation J2"),
        ("J3", "Préparation J3"),
        ("J4", "Préparation J4"),
        ("J5", "Préparation J5"),
        ("J6", "J5 validé"),
    ], string="Jalon")
    rpj_bilan_risque_design       = fields.Integer(string="DESIGN / INDUSTRIALISATION ")
    rpj_bilan_risque_supply_chain = fields.Integer(string="SUPPLY CHAIN / ACHAT")
    rpj_bilan_risque_qualite      = fields.Integer(string="QUALITE")
    rpj_bilan_risque_leadership   = fields.Integer(string="LEADERSHIP / FINANCES")
    is_revue_project_jalon_id     = fields.Many2one("is.revue.projet.jalon")


class is_revue_projet_jalon_equipe_projet(models.Model):
    _name        = "is.revue.projet.jalon.equipe.projet"
    _description = "Compte-rendu revue de projet jalon Bilan - Équipe projet"
    _rec_name    = "rpj_equipe_projet_fonction"

    rpj_equipe_projet_fonction = fields.Char(string="Fonction")
    rpj_equipe_projet_nomid    = fields.Many2one("res.users", string="Nom")
    rpj_equipe_projet_presence = fields.Selection([
        ("a", "Absent"),
        ("p", "Présent"),
        ("e", "Excusé"),
        ("n", "Non convoqué"),
    ], string="Présence")
    is_revue_project_jalon_id  = fields.Many2one("is.revue.projet.jalon")


class is_revue_projet_jalon_documents(models.Model):
    _name        = "is.revue.projet.jalon.documents"
    _description = "Compte-rendu revue de projet jalon Bilan - Documents"
    _rec_name    = "rpj_doc_documentid"

    rpj_doc_documentid        = fields.Many2one("is.doc.moule", string="Document")
    rpj_doc_action            = fields.Char(string="Action")
    rpj_doc_bloquant          = fields.Char(string="Point bloquant")
    rpj_doc_respid            = fields.Many2one("res.users", string="Responsable")
    rpj_doc_etat              = fields.Char(string="État")
    rpj_doc_coeff             = fields.Integer(string="Coefficient")
    rpj_doc_note              = fields.Integer(string="Note")
    is_revue_project_jalon_id = fields.Many2one("is.revue.projet.jalon")


class is_revue_projet_jalon_revue_de_contrat(models.Model):
    _name        = "is.revue.projet.jalon.revue.de.contrat"
    _description = "Compte-rendu revue de projet jalon Bilan - Revue de contrat"
    _rec_name    = "rpj_de1_article"

    rpj_de1_article           = fields.Char(string="Article")
    rpj_de1_cycle             = fields.Char(string="Cycle par pièce")
    rpj_de1_nb_emp            = fields.Char(string="Nb empreintes")
    rpj_de1_mod               = fields.Selection([
        ("0_25", "0.25"),
        ("0_5",  "0.5"),
        ("0_75", "0.75"),
        ("1",    "1"),
        ("1_5",  "1.5"),
        ("2",    "2"),
    ], string="MOD")
    rpj_de1_taux_rebut        = fields.Char(string="Tx rebut vendu")
    rpj_de1_poids_piece       = fields.Char(string="Poids pièce (en g)")
    rpj_de1_poids_carotte     = fields.Char(string="Poids carotte (en g)")
    is_revue_project_jalon_id = fields.Many2one("is.revue.projet.jalon")


class is_revue_projet_jalon_revue_de_projet_jalon(models.Model):
    _name        = "is.revue.projet.jalon.revue.de.projet.jalon"
    _description = "Compte-rendu revue de projet jalon Bilan - Revue de projet jalon"
    _rec_name    = "rpj_de2_article"

    rpj_de2_article = fields.Char(string="Article")
    rpj_de2_cycle = fields.Char(string="Cycle par pièce")
    rpj_de2_nb_emp = fields.Char(string="Nb empreintes")
    rpj_de2_mod = fields.Selection([
        ("0_25", "0.25"),
        ("0_5", "0.5"),
        ("0_75", "0.75"),
        ("1", "1"),
        ("1_5", "1.5"),
        ("2", "2"),
    ], string="MOD")
    rpj_de2_taux_rebut        = fields.Char(string="Tx rebut vendu")
    rpj_de2_poids_piece       = fields.Char(string="Poids pièce (en g)")
    rpj_de2_poids_carotte     = fields.Char(string="Poids carotte (en g)")
    is_revue_project_jalon_id = fields.Many2one("is.revue.projet.jalon")


class is_revue_projet_jalon_decomposition_prix(models.Model):
    _name        = "is.revue.projet.jalon.decomposition.prix"
    _description = "Compte-rendu revue de projet jalon Bilan - Décomposition prix"
    _rec_name    = "rpj_dp_article"

    rpj_dp_article            = fields.Float(string="Article")
    rpj_dp_qt_annuelle        = fields.Float(string="Quantité annuelle")
    rpj_dp_part_matiere       = fields.Float(string="Part matière")
    rpj_dp_part_composant     = fields.Float(string="Part composant")
    rpj_dp_part_emballage     = fields.Float(string="Part emballage")
    rpj_dp_va_injection       = fields.Float(string="VA injection")
    rpj_dp_va_assemblage      = fields.Float(string="VA assemblage")
    rpj_dp_frais_port         = fields.Float(string="Frais port")
    rpj_dp_logistique         = fields.Float(string="Logistique")
    rpj_dp_amt_moule          = fields.Float(string="Amortissement moule")
    rpj_dp_prix_piece         = fields.Float(string="Prix pièce")
    is_revue_project_jalon_id = fields.Many2one("is.revue.projet.jalon")
