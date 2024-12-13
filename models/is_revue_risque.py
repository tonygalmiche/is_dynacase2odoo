# -*- coding: utf-8 -*-
from odoo import models, fields, api, _ # type: ignore
from odoo.exceptions import AccessError, ValidationError, UserError  # type: ignore


_SELECT_RISQUE=[
    ("0" , "0"),
    ("1" , "1"),
    ("2" , "2"),
    ("NA", "N/A")
]


#TODO : 
# - Lors de la sycnro récupérer les champs create_date, create_uid, write_date, write_uid
# - Supprimer un N/A de la liste de choix


class is_revue_risque(models.Model):
    _name        = "is.revue.risque"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = "Revue des risques projet"
    _rec_name    = "rr_mouleid"
    _order = "id desc"


    rr_mouleid  = fields.Many2one("is.mold"    , string="Moule"    , tracking=True, index=True)
    dossierf_id = fields.Many2one("is.dossierf", string="Dossier F", tracking=True, index=True)

    rr_indice  = fields.Integer(string="Indice", tracking=True)
    rr_j_actuelle = fields.Selection([
        ("J0", "Préparation J0"),
        ("J1", "Préparation J1"),
        ("J2", "Préparation J2"),
        ("J3", "Préparation J3"),
        ("J4", "Préparation J4"),
        ("J5", "Préparation J5"),
        ("J6", "J5 validé"),
    ], string="J actuelle", compute='_compute',store=True, readonly=True)
    rr_revue_lancementid                  = fields.Many2one("is.revue.lancement", string="Revue de lancement"        , compute='_compute',store=True, readonly=True)
    rr_clientid                           = fields.Many2one("res.partner", string="Client"                           , compute='_compute',store=True, readonly=True)
    rr_projetid                           = fields.Many2one("is.mold.project", string="Projet"                       , compute='_compute',store=True, readonly=True)
    rr_rpjid                              = fields.Many2one("is.revue.projet.jalon", string="Dernier CR projet jalon", compute='_compute',store=True, readonly=True)

    rr_bilan_ar                           = fields.One2many("is.revue.risque.bilan", "rr_risqueid", string="Bilan", compute='_compute_rr_bilan_ar', store=True, readonly=True, copy=False)

    rr_risques_risque_design              = fields.Integer(string="Design / Industrialisation", compute='_compute_risque_design'      , store=True, readonly=True, copy=False)
    rr_risques_risque_supply_chain        = fields.Integer(string="Supply chain / Achat"      , compute='_compute_risque_supply_chain', store=True, readonly=True, copy=False)
    rr_risques_risque_qualite             = fields.Integer(string="Qualite"                   , compute='_compute_risque_qualite'     , store=True, readonly=True, copy=False)
    rr_risques_risque_leadership          = fields.Integer(string="Leadership / Finances"     , compute='_compute_risque_leadership'  , store=True, readonly=True, copy=False)

    rr_retour_experience                  = fields.Selection(_SELECT_RISQUE, string="Retour d’expérience - Process similaire", tracking=True, default=False)
    rr_retour_experience_comment          = fields.Char(string="Retour d’expérience - Process similaire ", tracking=True)
    rr_exigence_specifique                = fields.Selection(_SELECT_RISQUE, string="Exigences spécifiques liées à la matière / mélange maître", tracking=True)
    rr_exigence_specifique_comment        = fields.Char(string="Exigences spécifiques liées à la matière / mélange maître ", tracking=True)
    rr_planning_previsionnel              = fields.Selection(_SELECT_RISQUE, string="Planning prévisionnel", tracking=True)
    rr_planning_previsionnel_comment      = fields.Char(string="Planning prévisionnel ", tracking=True)
    rr_plan_piece                         = fields.Selection(_SELECT_RISQUE, string="Plan pièce / CS produit-Process", tracking=True)
    rr_plan_piece_comment                 = fields.Char(string="Plan pièce / CS produit-Process ", tracking=True)
    rr_norme_applicable                   = fields.Selection(_SELECT_RISQUE, string="Normes applicables", tracking=True)
    rr_norme_applicable_comment           = fields.Char(string="Normes applicables ", tracking=True)
    rr_conception_piece                   = fields.Selection(_SELECT_RISQUE, string="Conception pièce", tracking=True)
    rr_conception_piece_comment           = fields.Char(string="Conception pièce ", tracking=True)
    rr_injection                          = fields.Selection(_SELECT_RISQUE, string="Injection (paramètres / passage en process 4.0)", tracking=True)
    rr_injection_comment                  = fields.Char(string="Injection (paramètres / passage en process 4.0) ", tracking=True)
    rr_design_moule                       = fields.Selection(_SELECT_RISQUE, string="Moule ", tracking=True)
    rr_design_moule_comment               = fields.Char(string="Moule.", tracking=True)
    rr_methode_mesure                     = fields.Selection(_SELECT_RISQUE, string="Méthode de mesure / Gabarit de contrôle", tracking=True)
    rr_methode_mesure_comment             = fields.Char(string="Méthode de mesure / Gabarit de contrôle.", tracking=True)
    rr_composant                          = fields.Selection(_SELECT_RISQUE, string="Composants + Intégration de nouveaux produits chimiques", tracking=True)
    rr_composant_comment                  = fields.Char(string="Composants + Intégration de nouveaux produits chimiques ", tracking=True)
    rr_machine_speciale                   = fields.Selection(_SELECT_RISQUE, string="Machine Spéciale / Poka-Yoké", tracking=True)
    rr_machine_speciale_comment           = fields.Char(string="Machine Spéciale / Poka-Yoké.", tracking=True)
    rr_decoration                         = fields.Selection(_SELECT_RISQUE, string="Décoration (tampographie / Laser / Peinture)", tracking=True)
    rr_decoration_comment                 = fields.Char(string="Décoration (tampographie / Laser / Peinture) ", tracking=True)
    rr_parachevement                      = fields.Selection(_SELECT_RISQUE, string="Parachèvement (soudure / collage / Peinture ...)", tracking=True)
    rr_parachevement_comment              = fields.Char(string="Parachèvement (soudure / collage / Peinture ...) ", tracking=True)

    rr_capacitaire                        = fields.Selection(_SELECT_RISQUE, string="Capacitaire et montée en cadence", tracking=True)
    rr_capacitaire_comment                = fields.Char(string="Capacitaire et montée en cadence ", tracking=True)
    rr_conditionnement                    = fields.Selection(_SELECT_RISQUE, string="Conditionnement et transport", tracking=True)
    rr_conditionnement_comment            = fields.Char(string="Conditionnement et transport ", tracking=True)
    rr_identification_tracabilite         = fields.Selection(_SELECT_RISQUE, string="Identification et traçabilité", tracking=True)
    rr_identification_tracabilite_comment = fields.Char(string="Identification et traçabilité.", tracking=True)
    rr_validation_fournisseur             = fields.Selection(_SELECT_RISQUE, string="Validation fournisseur ", tracking=True)
    rr_validation_fournisseur_comment     = fields.Char(string="Validation fournisseur.", tracking=True)
    rr_capacitaire_fournisseur            = fields.Selection(_SELECT_RISQUE, string="Capacitaires et montée en cadence fournisseurs", tracking=True)
    rr_capacitaire_fournisseur_comment    = fields.Char(string="Capacitaires et montée en cadence fournisseurs ", tracking=True)
    rr_presse_substitution                = fields.Selection(_SELECT_RISQUE, string="Presse de substitution", tracking=True)
    rr_presse_substitution_comment        = fields.Char(string="Presse de substitution ", tracking=True)
    rr_modification_csr                   = fields.Selection(_SELECT_RISQUE, string="Revue des CSR client par rapport aux exigences propres au projet", tracking=True)
    rr_modification_csr_comment           = fields.Char(string="Revue des CSR client par rapport aux exigences propres au projet ", tracking=True)
    rr_critere_acceptation                = fields.Selection(_SELECT_RISQUE, string="Critères d'acceptation sur le produit ", tracking=True)
    rr_critere_acceptation_comment        = fields.Char(string="Critères d'acceptation sur le produit  ", tracking=True)
    rr_exigence_reglementaire             = fields.Selection(_SELECT_RISQUE, string="Exigences réglementaires et légales sur le produit", tracking=True)
    rr_exigence_reglementaire_comment     = fields.Char(string="Exigences réglementaires et légales sur le produit ", tracking=True)
    rr_engagement_qualite                 = fields.Selection(_SELECT_RISQUE, string="Engagement qualité (PPM)", tracking=True)
    rr_engagement_qualite_comment         = fields.Char(string="Engagement qualité (PPM) ", tracking=True)
    rr_securite_produit                   = fields.Selection(_SELECT_RISQUE, string="Sécurité du produit (protection de l'utilisateur final) + information au PSR", tracking=True)
    rr_securite_produit_comment           = fields.Char(string="Sécurité du produit (protection de l'utilisateur final) + information au PSR ", tracking=True)
    rr_rentabilite                        = fields.Selection(_SELECT_RISQUE, string="Rentabilité", tracking=True)
    rr_rentabilite_comment                = fields.Char(string="Rentabilité.", tracking=True)
    rr_investissement_necessaire          = fields.Selection(_SELECT_RISQUE, string="Investissements nécessaires", tracking=True)
    rr_investissement_necessaire_comment  = fields.Char(string="Investissements nécessaires ", tracking=True)
    rr_competence_effectif                = fields.Selection(_SELECT_RISQUE, string="Compétences et effectifs / Formation", tracking=True)
    rr_competence_effectif_comment        = fields.Char(string="Compétences et effectifs / Formation.", tracking=True)
    rr_validation_revue_risque            = fields.Selection([
        ("OK",  "OK"),
        ("nOK", "non OK"),
    ], string="Validation de cette revue des risques", tracking=True)
    dynacase_id                           = fields.Integer(string="Id Dynacase",index=True,copy=False)
    state                                 = fields.Selection([
        ("rr_brouillon", "Brouillon"),
        ("rr_diffuse",   "Diffusé"),
    ], string="État", tracking=True, default='rr_brouillon')
    rr_title = fields.Char(string="Revue des risques (champ à supprimer)")


    def name_get(self):
        result = []
        for obj in self:
            name=""
            if obj.rr_mouleid:
                name = obj.rr_mouleid.name
            if obj.dossierf_id:
                name = obj.dossierf_id.name
            if obj.rr_j_actuelle:
                name="%s-%s"%(name,obj.rr_j_actuelle)
            result.append((obj.id, name))
        return result





    def _get_val_risque(self,name_field):
        res = getattr(self, name_field)
        val=0
        if res=='1':
            val=1
        if res=='2':
            val=2
        return val
       

    @api.depends('rr_retour_experience','rr_exigence_specifique','rr_planning_previsionnel','rr_plan_piece','rr_norme_applicable','rr_conception_piece',
                 'rr_injection','rr_design_moule','rr_methode_mesure','rr_composant','rr_machine_speciale','rr_decoration','rr_parachevement')
    def _compute_risque_design(self):
        for obj in self:
            risque_design       = 0
            list=['rr_retour_experience','rr_exigence_specifique','rr_planning_previsionnel','rr_plan_piece','rr_norme_applicable','rr_conception_piece',
                 'rr_injection','rr_design_moule','rr_methode_mesure','rr_composant','rr_machine_speciale','rr_decoration','rr_parachevement']
            for name_field in list:
                risque_design+=obj._get_val_risque(name_field)
            obj.rr_risques_risque_design       = risque_design


    @api.depends('rr_capacitaire','rr_conditionnement','rr_identification_tracabilite','rr_validation_fournisseur','rr_capacitaire_fournisseur','rr_presse_substitution')
    def _compute_risque_supply_chain(self):
        for obj in self:
            risque_supply_chain = 0
            list=['rr_capacitaire','rr_conditionnement','rr_identification_tracabilite','rr_validation_fournisseur','rr_capacitaire_fournisseur','rr_presse_substitution']
            for name_field in list:
                risque_supply_chain+=obj._get_val_risque(name_field)
            obj.rr_risques_risque_supply_chain = risque_supply_chain


    @api.depends('rr_modification_csr','rr_critere_acceptation','rr_exigence_reglementaire','rr_engagement_qualite','rr_securite_produit')
    def _compute_risque_qualite(self):
        for obj in self:
            risque_qualite      = 0
            list=['rr_modification_csr','rr_critere_acceptation','rr_exigence_reglementaire','rr_engagement_qualite','rr_securite_produit']
            for name_field in list:
                risque_qualite+=obj._get_val_risque(name_field)
            obj.rr_risques_risque_qualite      = risque_qualite

 
    @api.depends('rr_rentabilite','rr_investissement_necessaire','rr_competence_effectif')
    def _compute_risque_leadership(self):
        for obj in self:
            risque_leadership   = 0
            list=['rr_rentabilite','rr_investissement_necessaire','rr_competence_effectif']
            for name_field in list:
                risque_leadership+=obj._get_val_risque(name_field)
            obj.rr_risques_risque_leadership   = risque_leadership

 
    @api.depends("rr_mouleid","dossierf_id")
    def _compute(self):
        for obj in self:
            j_actuelle = revue_lancement_id = client_id = projet_id = False
            if obj.rr_mouleid:
                j_actuelle         = obj.rr_mouleid.j_actuelle
                revue_lancement_id = obj.rr_mouleid.revue_lancement_id.id
                client_id          = obj.rr_mouleid.client_id.id
                projet_id          = obj.rr_mouleid.project.id
            if obj.dossierf_id:
                j_actuelle         = obj.dossierf_id.j_actuelle
                revue_lancement_id = obj.dossierf_id.revue_lancement_id.id
                client_id          = obj.dossierf_id.client_id.id
                projet_id          = obj.dossierf_id.project.id
            obj.rr_j_actuelle        = j_actuelle
            obj.rr_revue_lancementid = revue_lancement_id
            obj.rr_clientid          = client_id
            obj.rr_projetid          = projet_id
            revue_id=False
            if obj.rr_mouleid or obj.dossierf_id:
                if obj.rr_mouleid:
                    domain=[('rpj_mouleid', '=', obj.rr_mouleid.id)]
                if obj.dossierf_id:
                    domain=[('dossierf_id', '=', obj.dossierf_id.id)]
                revues=self.env['is.revue.projet.jalon'].search(domain,order='id desc',limit=1)
                for revue in revues:
                    revue_id=revue.id
            obj.rr_rpjid = revue_id


    @api.depends("rr_mouleid","dossierf_id",'state',
        'rr_retour_experience','rr_exigence_specifique','rr_planning_previsionnel','rr_plan_piece','rr_norme_applicable','rr_conception_piece',
        'rr_injection','rr_design_moule','rr_methode_mesure','rr_composant','rr_machine_speciale','rr_decoration','rr_parachevement',
        'rr_capacitaire','rr_conditionnement','rr_identification_tracabilite','rr_validation_fournisseur','rr_capacitaire_fournisseur','rr_presse_substitution',
        'rr_modification_csr','rr_critere_acceptation','rr_exigence_reglementaire','rr_engagement_qualite','rr_securite_produit',
        'rr_rentabilite','rr_investissement_necessaire','rr_competence_effectif',
    )
    def _compute_rr_bilan_ar(self):
        for obj in self:
            ids=[]
            obj.rr_bilan_ar = False
            if obj.rr_mouleid or obj.dossierf_id:
                if obj.rr_mouleid:
                    domain=[('rr_mouleid', '=' , obj.rr_mouleid.id), ('rr_mouleid', '!=' , False)]
                if obj.dossierf_id:
                    domain=[('dossierf_id', '=' , obj.dossierf_id.id), ('dossierf_id', '!=' , False)]
                if obj._origin.id:
                    domain.append(('id', '!=', obj._origin.id))
                revues=self.env['is.revue.risque'].search(domain,order='id')
                for revue in revues:
                    vals={
                        'rr_bilan_risque_j'           : revue.rr_j_actuelle,
                        'rr_bilan_risque_design'      : revue.rr_risques_risque_design,
                        'rr_bilan_risque_supply_chain': revue.rr_risques_risque_supply_chain,
                        'rr_bilan_risque_qualite'     : revue.rr_risques_risque_qualite,
                        'rr_bilan_risque_leadership'  : revue.rr_risques_risque_leadership,
                    }
                    ids.append([0,False,vals])    
                vals={
                    'rr_bilan_risque_j'           : obj.rr_j_actuelle,
                    'rr_bilan_risque_design'      : obj.rr_risques_risque_design,
                    'rr_bilan_risque_supply_chain': obj.rr_risques_risque_supply_chain,
                    'rr_bilan_risque_qualite'     : obj.rr_risques_risque_qualite,
                    'rr_bilan_risque_leadership'  : obj.rr_risques_risque_leadership,
                }
                ids.append([0,False,vals])    
            obj.rr_bilan_ar = ids



    def action_vers_diffuse(self):
        for obj in self:
            if not obj.rr_validation_revue_risque:
                raise ValidationError("Le champ 'Validation de cette revue des risques' est obligatoire !")
            obj.rr_mouleid.revue_risque_id  = obj.id
            obj.dossierf_id.revue_risque_id = obj.id
            obj.state = "rr_diffuse"




    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }






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
    rr_bilan_risque_design       = fields.Integer(string="Design / Industrialisation ")
    rr_bilan_risque_supply_chain = fields.Integer(string="Supply chain / Achat")
    rr_bilan_risque_qualite      = fields.Integer(string="Qualite")
    rr_bilan_risque_leadership   = fields.Integer(string="Leadership / Finances")
    rr_risqueid                  = fields.Many2one("is.revue.risque", string="Revue des risques projet")