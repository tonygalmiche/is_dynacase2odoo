# -*- coding: utf-8 -*-
from odoo import models, fields, api, _       # type: ignore
from odoo.exceptions import ValidationError   # type: ignore


#TODO : 
# Ajouter un champ 'name' comme la revue de contrat
# Dans le programme de syncro faire un compute du name et des autres champs

# Ajouter un champ name dans la revue des risques 
# Copie des données depuis la revue de contrat
# Duplication revue de lancement avec indice
# Contrainet pour revue de lancement en double
# Création invitessiiement achat moule


_RESPONSABLES={
    '1' : 'rl_commercial2id',
    '2' : 'rl_chef_projetid',
    '3' : 'rl_responsable_outillageid',
    '4' : 'rl_expert_injectionid',
    '5' : 'rl_methode_injectionid',
    '6' : 'rl_methode_assemblageid',
    '7' : 'rl_qualite_devid',
    '8' : 'rl_qualite_usineid',
    '9' : 'rl_logistiqueid',
    '10': 'rl_logistique_usineid',
    '11': 'rl_achatsid',
    '12': 'rl_responsable_projetid',
}


class is_revue_lancement(models.Model):
    _name        = "is.revue.lancement"
    _inherit     = ['mail.thread']
    #_inherit    = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
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
            record.state = "rl_diffuse"

    def action_vers_brouillon(self):
        for record in self:
            record.state = "rl_brouillon"

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

    rl_title                          = fields.Char(string="Revue de lancement", tracking=True)
    rl_indice                         = fields.Integer(string="Indice", tracking=True)
    rl_num_rcid                       = fields.Many2one("is.revue.de.contrat", string="Revue de contrat", tracking=True)
    rl_designation_rc                 = fields.Char(string="Désignation", tracking=True)
    rl_client_rcid                    = fields.Many2one("res.partner", string="Client", tracking=True)
    rl_projet_rcid                    = fields.Many2one("is.mold.project", string="Projet", tracking=True)
    rl_commercial_rcid                = fields.Many2one("res.users", string="Commercial", tracking=True)
    rl_lieu_production                = fields.Selection([
        ("g",  "Gray"),
        ("sb", "St-Brice"),
        ("pl", "Plasti-ka"),
        ("st", "Sous-Traitant"),
    ], string="Lieu de production", tracking=True)
    rl_nom_soutraitant                = fields.Char(string="Nom du sous-traitant", tracking=True)
    rl_affectation_presse             = fields.Char(string="Affectation presse", tracking=True)
    rl_choix_industriel               = fields.Text(string="Choix industriel et investissement éventuel", tracking=True)
    rl_validation_capacitaire         = fields.Selection([
        ("OK",  "OK"),
        ("NOK", "NOK"),
    ], string="Validation capacitaire", tracking=True)
    rl_validation_capacitaire_comment = fields.Char(string="Commentaire si validation capacitaire NOK", tracking=True)
    rl_chef_projetid                  = fields.Many2one("res.users", string="Chef de projet", tracking=True)
    rl_expert_injectionid             = fields.Many2one("res.users", string="Expert injection", tracking=True)
    rl_methode_injectionid            = fields.Many2one("res.users", string="Méthode injection", tracking=True)
    rl_methode_assemblageid           = fields.Many2one("res.users", string="Méthode assemblage", tracking=True)
    rl_qualite_devid                  = fields.Many2one("res.users", string="Métrologie", tracking=True)
    rl_qualite_usineid                = fields.Many2one("res.users", string="Qualité développement", tracking=True)
    rl_achatsid                       = fields.Many2one("res.users", string="Achats", tracking=True)
    rl_logistiqueid                   = fields.Many2one("res.users", string="Logistique", tracking=True)
    rl_logistique_usineid             = fields.Many2one("res.users", string="Logistique Usine", tracking=True)
    rl_commercial2id                  = fields.Many2one("res.users", string="Commercial ", tracking=True)
    rl_responsable_outillageid        = fields.Many2one("res.users", string="Responsable outillage", tracking=True)
    rl_responsable_projetid           = fields.Many2one("res.users", string="Responsable projets", tracking=True)
    rl_directeur_siteid               = fields.Many2one("res.users", string="Directeur site de production", tracking=True)
    rl_directeur_techniqueid          = fields.Many2one("res.users", string="Directeur technique", tracking=True)
    rl_date_j0                        = fields.Date(string="Date J0", tracking=True)
    rl_date_j1                        = fields.Date(string="Date J1", tracking=True)
    rl_date_j2                        = fields.Date(string="Date J2", tracking=True)
    rl_date_j3                        = fields.Date(string="Date J3", tracking=True)
    rl_date_j4                        = fields.Date(string="Date J4", tracking=True)
    rl_date_j5                        = fields.Date(string="Date J5", tracking=True)
    rl_pgrc_moule_mnt                 = fields.Float(string="Moule", tracking=True)
    rl_pgrc_moule_cmt                 = fields.Char(string="Commentaire", tracking=True)
    rl_pgrc_etude_mnt                 = fields.Float(string="Etude", tracking=True)
    rl_pgrc_etude_cmt                 = fields.Char(string="Commentaire 1", tracking=True)
    rl_pgrc_main_prehension_mnt       = fields.Float(string="Main de préhension", tracking=True)
    rl_pgrc_main_prehension_cmt       = fields.Char(string="Commentaire  2", tracking=True)
    rl_pgrc_barre_chaude_mnt          = fields.Float(string="Barre chaude", tracking=True)
    rl_pgrc_barre_chaude_cmt          = fields.Char(string="Commentaire 3", tracking=True)
    rl_pgrc_gabarit_controle_mnt      = fields.Float(string="Gabarit de contrôle", tracking=True)
    rl_pgrc_gabarit_controle_cmt      = fields.Char(string="Commentaire 4", tracking=True)
    rl_pgrc_machine_speciale_mnt      = fields.Float(string="Machine spéciale", tracking=True)
    rl_pgrc_machine_speciale_cmt      = fields.Char(string="Commentaire 5", tracking=True)
    rl_pgrc_plan_validation_mnt       = fields.Float(string="Plan de validation", tracking=True)
    rl_pgrc_plan_validation_cmt       = fields.Char(string="Commentaire 6", tracking=True)
    rl_pgrc_mise_point_mnt            = fields.Float(string="Mise au point", tracking=True)
    rl_pgrc_mise_point_cmt            = fields.Char(string="Commentaire 7", tracking=True)
    rl_pgrc_packaging_mnt             = fields.Float(string="Packaging", tracking=True)
    rl_pgrc_packaging_cmt             = fields.Char(string="Commentaire 8", tracking=True)
    rl_pgrc_amort_mnt                 = fields.Float(string="Amortissement", tracking=True)
    rl_pgrc_amort_cmt                 = fields.Char(string="Commentaire 9", tracking=True)
    rl_pgrc_total                     = fields.Float(string="Total ", compute="get_rl_pgrc_total", store=True)
    rl_be01                           = fields.Float(string="BE01a : Nouveau moule/ Moule transféré", tracking=True)
    rl_be01b                          = fields.Float(string="BE01b : Grainage", tracking=True)
    rl_be01c                          = fields.Float(string="BE01c : Barre chaude", tracking=True)
    rl_be02                           = fields.Float(string="BE02 : Etude, CAO, Rhéologie", tracking=True)
    rl_be03                           = fields.Float(string="BE03 : Prototype", tracking=True)
    rl_be04                           = fields.Float(string="BE04 : Main de préhension ", tracking=True)
    rl_be05                           = fields.Float(string="BE05 : Gabarit de contrôle ", tracking=True)
    rl_be06                           = fields.Float(string="BE06 : Mise au point", tracking=True)
    rl_be07                           = fields.Float(string="BE07 : Test ", tracking=True)
    rl_be09                           = fields.Float(string="BE09 : Essais + divers ", tracking=True)
    rl_be10                           = fields.Float(string="BE10 : Métrologie ", tracking=True)
    rl_be11                           = fields.Float(string="BE11 : Transports ", tracking=True)
    rl_be12                           = fields.Float(string="BE12 : Etude/Developpement Packaging ", tracking=True)
    rl_be13                           = fields.Float(string="BE13 : Poste d'assemblage ", tracking=True)
    rl_be14                           = fields.Float(string="BE14 : Developpement outillages divers ( découpe...) ", tracking=True)
    rl_be15                           = fields.Float(string="BE15 : Achat matière ", tracking=True)
    rl_be16                           = fields.Float(string="BE16 : Achat composants ", tracking=True)
    rl_be17                           = fields.Float(string="BE17 : Essai injection ", tracking=True)
    rl_be_total                       = fields.Float(string="Total", compute="get_rl_be_total", store=True)
    rl_annee_inv                      = fields.Char(string="Année d'enregistrement des investissements", size=4, tracking=True)
    state                             = fields.Selection([
        ("rl_brouillon",  "Brouillon"),
        ("rl_diffuse",    "Diffusé"),
    ], string="État", tracking=True)
    dynacase_id = fields.Integer(string="Id Dynacase",index=True,copy=False)
    active      = fields.Boolean('Actif', default=True, tracking=True)






    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
            
            
    def initialiser_responsable_doc_action(self):
        for obj in self:
            moule_id    = obj.rl_num_rcid.rc_mouleid.id
            dossierf_id = obj.rl_num_rcid.rc_dossierfid.id
            if moule_id:
                domain=[('idmoule', '=', moule_id)]
            if dossierf_id:
                domain=[('dossierf_id', '=', dossierf_id)]
            docs = self.env['is.doc.moule'].search(domain)
            for doc in docs:
                ppr_responsable = doc.param_project_id.ppr_responsable
                if ppr_responsable:
                    responsable = _RESPONSABLES.get(ppr_responsable)          
                    if hasattr(obj, responsable):
                        user = getattr(obj,responsable)
                        if user:
                            doc.idresp = user.id

