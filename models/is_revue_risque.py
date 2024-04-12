# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class is_revue_risque(models.Model):
    _name        = "is.revue.risque"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = "Revue des risques projet"
    _rec_name    = "rr_title"

    def action_vers_diffuse(self):
        for record in self:
            record.state = "rr_diffuse"

    def action_vers_brouillon(self):
        for record in self:
            record.state = "rr_brouillon"

    rr_title                              = fields.Char(string="Revue des risques")
    rr_indice                             = fields.Integer(string="Indice")
    rr_j_actuelle                         = fields.Selection([
        ("J0", "Préparation J0"),
        ("J1", "Préparation J1"),
        ("J2", "Préparation J2"),
        ("J3", "Préparation J3"),
        ("J4", "Préparation J4"),
        ("J5", "Préparation J5"),
        ("J6", "J5 validé"),
    ], string="J actuelle")
    rr_mouleid                            = fields.Many2one("is.mold", string="Moule")
    rr_revue_lancementid                  = fields.Many2one("is.revue.lancement", string="Revue de lancement")
    rr_clientid                           = fields.Many2one("res.partner", string="Client", domain=[("is_company","=",True), ("customer","=",True)])
    rr_projetid                           = fields.Many2one("is.mold.project", string="Projet")
    rr_rpjid                              = fields.Many2one("is.revue.projet.jalon", string="Dernier CR projet jalon")
    rr_bilan_ar                           = fields.One2many("is.revue.risque.bilan", "rr_risqueid", string="Bilan")
    rr_risques_risque_design              = fields.Integer(string="Risque DESIGN / INDUSTRIALISATION ")
    rr_risques_risque_supply_chain        = fields.Integer(string="Risque SUPPLY CHAIN / ACHAT")
    rr_risques_risque_qualite             = fields.Integer(string="Risque QUALITE")
    rr_risques_risque_leadership          = fields.Integer(string="Risque LEADERSHIP / FINANCES")
    rr_retour_experience                  = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Retour d’expérience - Process similaire")
    rr_retour_experience_comment          = fields.Char(string="Retour d’expérience - Process similaire ")
    rr_exigence_specifique                = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Exigences spécifiques liées à la matière / mélange maître")
    rr_exigence_specifique_comment        = fields.Char(string="Exigences spécifiques liées à la matière / mélange maître ")
    rr_planning_previsionnel              = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Planning prévisionnel")
    rr_planning_previsionnel_comment      = fields.Char(string="Planning prévisionnel ")
    rr_plan_piece                         = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Plan pièce / CS produit-Process")
    rr_plan_piece_comment                 = fields.Char(string="Plan pièce / CS produit-Process ")
    rr_norme_applicable                   = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Normes applicables")
    rr_norme_applicable_comment           = fields.Char(string="Normes applicables ")
    rr_conception_piece                   = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Conception pièce")
    rr_conception_piece_comment           = fields.Char(string="Conception pièce ")
    rr_injection                          = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Injection (paramètres / passage en process 4.0)")
    rr_injection_comment                  = fields.Char(string="Injection (paramètres / passage en process 4.0) ")
    rr_design_moule                       = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Moule")
    rr_design_moule_comment               = fields.Char(string="Moule ")
    rr_methode_mesure                     = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Méthode de mesure / Gabarit de contrôle")
    rr_methode_mesure_comment             = fields.Char(string="Méthode de mesure / Gabarit de contrôle ")
    rr_composant                          = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Composants + Intégration de nouveaux produits chimiques")
    rr_composant_comment                  = fields.Char(string="Composants + Intégration de nouveaux produits chimiques ")
    rr_machine_speciale                   = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Machine Spéciale / Poka-Yoké")
    rr_machine_speciale_comment           = fields.Char(string="Machine Spéciale / Poka-Yoké ")
    rr_decoration                         = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Décoration (tampographie / Laser / Peinture)")
    rr_decoration_comment                 = fields.Char(string="Décoration (tampographie / Laser / Peinture) ")
    rr_parachevement                      = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Parachèvement (soudure / collage / Peinture ...)")
    rr_parachevement_comment              = fields.Char(string="Parachèvement (soudure / collage / Peinture ...) ")

    rr_capacitaire                        = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Capacitaire et montée en cadence")
    rr_capacitaire_comment                = fields.Char(string="Capacitaire et montée en cadence ")
    rr_conditionnement                    = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Conditionnement et transport")
    rr_conditionnement_comment            = fields.Char(string="Conditionnement et transport ")
    rr_identification_tracabilite         = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Identification et traçabilité")
    rr_identification_tracabilite_comment = fields.Char(string="Identification et traçabilité")
    rr_validation_fournisseur             = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Validation fournisseur ")
    rr_validation_fournisseur_comment     = fields.Char(string="Validation fournisseur ")
    rr_capacitaire_fournisseur            = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Capacitaires et montée en cadence fournisseurs")
    rr_capacitaire_fournisseur_comment    = fields.Char(string="Capacitaires et montée en cadence fournisseurs ")
    rr_presse_substitution                = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Presse de substitution")
    rr_presse_substitution_comment        = fields.Char(string="Presse de substitution ")
    rr_modification_csr                   = fields.Selection([
        ("0",  "0"),
        ("1",  "1"),
        ("2",  "2"),
        ("na", "N/A"),
    ], string="Revue des CSR client par rapport aux exigences propres au projet")
    rr_modification_csr_comment           = fields.Char(string="Revue des CSR client par rapport aux exigences propres au projet ")
    rr_critere_acceptation                = fields.Selection([
        ("0",  "0"),
        ("1",  "1"),
        ("2",  "2"),
        ("na", "N/A"),
    ], string="Critères d'acceptation sur le produit ")
    rr_critere_acceptation_comment        = fields.Char(string="Critères d'acceptation sur le produit  ")
    rr_exigence_reglementaire             = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Exigences réglementaires et légales sur le produit")
    rr_exigence_reglementaire_comment     = fields.Char(string="Exigences réglementaires et légales sur le produit ")
    rr_engagement_qualite                 = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Engagement qualité (PPM)")
    rr_engagement_qualite_comment         = fields.Char(string="Engagement qualité (PPM) ")
    rr_securite_produit                   = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Sécurité du produit (protection de l'utilisateur final) + information au PSR")
    rr_securite_produit_comment           = fields.Char(string="Sécurité du produit (protection de l'utilisateur final) + information au PSR ")
    rr_rentabilite                        = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Rentabilité")
    rr_rentabilite_comment                = fields.Char(string="Rentabilité")
    rr_investissement_necessaire          = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Investissements nécessaires")
    rr_investissement_necessaire_comment  = fields.Char(string="Investissements nécessaires ")
    rr_competence_effectif                = fields.Selection([
        ("0", "0"),
        ("1", "1"),
        ("2", "2"),
        ("na", "N/A"),
    ], string="Compétences et effectifs / Formation")
    rr_competence_effectif_comment        = fields.Char(string="Compétences et effectifs / Formation")
    rr_validation_revue_risque            = fields.Selection([
        ("ok", "OK"),
        ("nok", "non OK"),
    ], string="Validation de cette revue des risques")
    dynacase_id                           = fields.Integer(string="Id Dynacase")
    state                                 = fields.Selection([
        ("rr_brouillon", "Brouillon"),
        ("rr_diffuse",   "Diffusé"),
    ], string="État", tracking=True)


class is_revue_risque_bilan(models.Model):
    _name        = "is.revue.risque.bilan"
    _description = "Revue des risques projet - Bilan"
    _rec_name    = "rr_bilan_risque_j"

    rr_bilan_risque_j            = fields.Selection([
        ("J0", "Préparation J0"),
        ("J1", "Préparation J1"),
        ("J2", "Préparation J2"),
        ("J3", "Préparation J3"),
        ("J4", "Préparation J4"),
        ("J5", "Préparation J5"),
        ("J6", "J5 validé"),
    ], string="Jalon")
    rr_bilan_risque_design       = fields.Integer(string="Design/Industrialisation ")
    rr_bilan_risque_supply_chain = fields.Integer(string="Supply chain/Achat")
    rr_bilan_risque_qualite      = fields.Integer(string="Qualite")
    rr_bilan_risque_leadership   = fields.Integer(string="Leadership/Finances")
    rr_risqueid                  = fields.Many2one("is.revue.risque", string="Revue des risques projet")