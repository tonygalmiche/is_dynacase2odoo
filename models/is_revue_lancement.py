# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class is_revue_lancement(models.Model):
    _name        = "is.revue.lancement"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = "Revue de lancement"
    _rec_name    = "rl_title"

    @api.depends("rl_pgrc_moule_mnt", "rl_pgrc_etude_mnt", "rl_pgrc_main_prehension_mnt", "rl_pgrc_barre_chaude_mnt",
                 "rl_pgrc_gabarit_controle_mnt", "rl_pgrc_machine_speciale_mnt", "rl_pgrc_plan_validation_mnt",
                 "rl_pgrc_mise_point_mnt", "rl_pgrc_packaging_mnt", "rl_pgrc_amort_mnt")
    def get_rl_pgrc_total(self):
        for record in self:
            record.rl_pgrc_total = record.rl_pgrc_moule_mnt + record.rl_pgrc_etude_mnt + record.rl_pgrc_main_prehension_mnt + \
                                   record.rl_pgrc_barre_chaude_mnt + record.rl_pgrc_gabarit_controle_mnt + record.rl_pgrc_machine_speciale_mnt + \
                                   record.rl_pgrc_mise_point_mnt + record.rl_pgrc_plan_validation_mnt + record.rl_pgrc_packaging_mnt + record.rl_pgrc_amort_mnt

    @api.depends("rl_be01", "rl_be01b", "rl_be01c", "rl_be02", "rl_be03", "rl_be04", "rl_be05", "rl_be06", "rl_be07",
                "rl_be09", "rl_be10", "rl_be11", "rl_be12", "rl_be13", "rl_be14", "rl_be15", "rl_be16", "rl_be17")
    def get_rl_be_total(self):
        for record in self:
            record.rl_be_total = record.rl_be01 + record.rl_be01b +  record.rl_be01c + record.rl_be02 + record.rl_be03 + \
                                record.rl_be04 + record.rl_be05 + record.rl_be06 + record.rl_be07 + record.rl_be09 + \
                                record.rl_be10 + record.rl_be11 + record.rl_be12 + record.rl_be13 + record.rl_be14 + \
                                record.rl_be15 + record.rl_be16 + record.rl_be17

    def action_vers_diffuse(self):
        for record in self:
            record.state = "diffuse"

    def action_vers_brouillon(self):
        for record in self:
            record.state = "brouillon"

    @api.constrains("rl_be_total", "rl_pgrc_total", "rl_annee_inv")
    def _check_vals(self):
        for obj in self:
            if obj.rl_pgrc_total != obj.rl_be_total:
                raise ValidationError(_("Données moule and revue de lancement total must be same!"))
            if obj.rl_annee_inv:
                try:
                    rl_annee_inv = int(obj.rl_annee_inv)
                    if len(str(rl_annee_inv)) != 4:
                        raise ValidationError(_("Please enter 'Année d'enregistrement des investissements' field value between > 2000 and < 2099 !"))
                    if rl_annee_inv < 2000 or rl_annee_inv > 2099:
                        raise ValidationError(_("Please enter 'Année d'enregistrement des investissements' field value between > 2000 and < 2099 !"))
                except Exception as e:
                    raise ValidationError(_("Please enter 'Année d'enregistrement des investissements' field value between > 2000 and < 2099 !"))

    rl_title                          = fields.Char(string="Revue de lancement")
    rl_indice                         = fields.Integer(string="Indice")
    rl_num_rcid                       = fields.Many2one("is.revue.de.contrat", string="Revue de contrat")
    rl_designation_rc                 = fields.Char(string="Désignation")
    rl_client_rcid                    = fields.Many2one("res.partner", string="Client")
    rl_projet_rcid                    = fields.Many2one("is.mold.project", string="Projet")
    rl_commercial_rcid                = fields.Many2one("res.users", string="Commercial")
    rl_lieu_production                = fields.Selection([
        ("g",  "Gray"),
        ("sb", "St-Brice"),
        ("pl", "Plasti-ka"),
        ("st", "Sous-Traitant"),
    ], string="Lieu de production")
    rl_nom_soutraitant                = fields.Char(string="Nom du sous-traitant")
    rl_affectation_presse             = fields.Char(string="Affectation presse")
    rl_choix_industriel               = fields.Text(string="Choix industriel et investissement éventuel")
    rl_validation_capacitaire         = fields.Selection([
        ("OK",  "OK"),
        ("NOK", "NOK"),
    ], string="Validation capacitaire")
    rl_validation_capacitaire_comment = fields.Char(string="Commentaire si validation capacitaire NOK")
    rl_chef_projetid                  = fields.Many2one("res.users", string="Chef de projet")
    rl_expert_injectionid             = fields.Many2one("res.users", string="Expert injection")
    rl_methode_injectionid            = fields.Many2one("res.users", string="Méthode injection")
    rl_methode_assemblageid           = fields.Many2one("res.users", string="Méthode assemblage")
    rl_qualite_devid                  = fields.Many2one("res.users", string="Métrologie")
    rl_qualite_usineid                = fields.Many2one("res.users", string="Qualité développement")
    rl_achatsid                       = fields.Many2one("res.users", string="Achats")
    rl_logistiqueid                   = fields.Many2one("res.users", string="Logistique")
    rl_logistique_usineid             = fields.Many2one("res.users", string="Logistique Usine")
    rl_commercial2id                  = fields.Many2one("res.users", string="Commercial ")
    rl_responsable_outillageid        = fields.Many2one("res.users", string="Responsable outillage")
    rl_responsable_projetid           = fields.Many2one("res.users", string="Responsable projets")
    rl_directeur_siteid               = fields.Many2one("res.users", string="Directeur site de production")
    rl_directeur_techniqueid          = fields.Many2one("res.users", string="Directeur technique")
    rl_date_j0                        = fields.Date(string="Date J0")
    rl_date_j1                        = fields.Date(string="Date J1")
    rl_date_j2                        = fields.Date(string="Date J2")
    rl_date_j3                        = fields.Date(string="Date J3")
    rl_date_j4                        = fields.Date(string="Date J4")
    rl_date_j5                        = fields.Date(string="Date J5")
    rl_pgrc_moule_mnt                 = fields.Float(string="Moule")
    rl_pgrc_moule_cmt                 = fields.Char(string="Commentaire")
    rl_pgrc_etude_mnt                 = fields.Float(string="Etude")
    rl_pgrc_etude_cmt                 = fields.Char(string="Commentaire 1")
    rl_pgrc_main_prehension_mnt       = fields.Float(string="Main de préhension")
    rl_pgrc_main_prehension_cmt       = fields.Char(string="Commentaire  2")
    rl_pgrc_barre_chaude_mnt          = fields.Float(string="Barre chaude")
    rl_pgrc_barre_chaude_cmt          = fields.Char(string="Commentaire 3")
    rl_pgrc_gabarit_controle_mnt      = fields.Float(string="Gabarit de contrôle")
    rl_pgrc_gabarit_controle_cmt      = fields.Char(string="Commentaire 4")
    rl_pgrc_machine_speciale_mnt      = fields.Float(string="Machine spéciale")
    rl_pgrc_machine_speciale_cmt      = fields.Char(string="Commentaire 5")
    rl_pgrc_plan_validation_mnt       = fields.Float(string="Plan de validation")
    rl_pgrc_plan_validation_cmt       = fields.Char(string="Commentaire 6")
    rl_pgrc_mise_point_mnt            = fields.Float(string="Mise au point")
    rl_pgrc_mise_point_cmt            = fields.Char(string="Commentaire 7")
    rl_pgrc_packaging_mnt             = fields.Float(string="Packaging")
    rl_pgrc_packaging_cmt             = fields.Char(string="Commentaire 8")
    rl_pgrc_amort_mnt                 = fields.Float(string="Amortissement")
    rl_pgrc_amort_cmt                 = fields.Char(string="Commentaire 9")
    rl_pgrc_total                     = fields.Float(string="Total ", compute="get_rl_pgrc_total", store=True)
    rl_be01                           = fields.Float(string="BE01a : Nouveau moule/ Moule transféré")
    rl_be01b                          = fields.Float(string="BE01b : Grainage")
    rl_be01c                          = fields.Float(string="BE01c : Barre chaude")
    rl_be02                           = fields.Float(string="BE02 : Etude, CAO, Rhéologie")
    rl_be03                           = fields.Float(string="BE03 : Prototype")
    rl_be04                           = fields.Float(string="BE04 : Main de préhension ")
    rl_be05                           = fields.Float(string="BE05 : Gabarit de contrôle ")
    rl_be06                           = fields.Float(string="BE06 : Mise au point")
    rl_be07                           = fields.Float(string="BE07 : Test ")
    rl_be09                           = fields.Float(string="BE09 : Essais + divers ")
    rl_be10                           = fields.Float(string="BE10 : Métrologie ")
    rl_be11                           = fields.Float(string="BE11 : Transports ")
    rl_be12                           = fields.Float(string="BE12 : Etude/Developpement Packaging ")
    rl_be13                           = fields.Float(string="BE13 : Poste d'assemblage ")
    rl_be14                           = fields.Float(string="BE14 : Developpement outillages divers ( découpe...) ")
    rl_be15                           = fields.Float(string="BE15 : Achat matière ")
    rl_be16                           = fields.Float(string="BE16 : Achat composants ")
    rl_be17                           = fields.Float(string="BE17 : Essai injection ")
    rl_be_total                       = fields.Float(string="Total", compute="get_rl_be_total", store=True)
    rl_annee_inv                      = fields.Char(string="Année d'enregistrement des investissements", size=4)
    state                             = fields.Selection([
        ("brouillon", "Brouillon"),
        ("diffuse",    "Diffusé"),
    ], string="État")
    dynacase_id                       = fields.Integer(string="Id Dynacase")



