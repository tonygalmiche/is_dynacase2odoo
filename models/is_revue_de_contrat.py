# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class is_revue_de_contrat(models.Model):
    _name        = "is.revue.de.contrat"
    _description = "Revue de contrat"
    _rec_name    = "rc_mouleid"

    @api.depends("rc_eiv_moule", "rc_eiv_etude", "rc_eiv_main_prehension", "rc_eiv_barre_chaude" , "rc_eiv_gab_controle", "rc_eiv_mach_spec", "rc_eiv_plan_valid", "rc_eiv_mis_point" ,"rc_eiv_pack", "rc_eiv_amort")
    def get_rc_eiv_total(self):
        for record in self:
            record.rc_eiv_total = record.rc_eiv_moule +  record.rc_eiv_etude +  record.rc_eiv_main_prehension + \
                                  record.rc_eiv_barre_chaude + record.rc_eiv_gab_controle +record.rc_eiv_mach_spec + \
                                  record.rc_eiv_plan_valid + record.rc_eiv_mis_point + record.rc_eiv_pack + record.rc_eiv_amort

    rc_mouleid                         = fields.Many2one("is.mold", string="Revue de contrat (Moule)")
    rc_dossierfid                      = fields.Many2one("is.dossierf", string="Revue de contrat (Dossier F)")
    rc_indice                          = fields.Integer(string="Indice")
    rc_doc_moule_assemblage            = fields.Selection([
        ("c1", "La revue de contrat est attachée à un dossier d'assemblage"),
        ("c2", "La revue de contrat est attachée à un moule autonome"),
        ("c3", "La revue de contrat est attachée à un moule appartenant à un dossier d'assemblage"),
    ], string="Dossier moule ou assemblage")
    rc_type_automobile                 = fields.Selection([
        ("Non", "hors Automobile"),
        ("Oui", "Automobile"),
    ], string="Type automobile")
    rc_projetid                        = fields.Many2one(related="rc_mouleid.project", string="Projet")
    rc_revue_contrat_assid             = fields.Many2one("is.revue.de.contrat", string="Revue de contrat du dossier d'assemblage")
    rc_ass_mouleid                     = fields.Many2many("is.mold", "is_revue_mold_rel", "revue_id", "mold_id", string="Moule")
    rc_client                          = fields.Many2one("res.partner", string="Client")
    rc_designation                     = fields.Char(string="Désignation")
    rc_num_outillageid                 = fields.Many2one("is.mold", string="N° outillage")
    rc_dao                             = fields.Char(string="Dossier d'appel d'offre")
    rc_commercial                      = fields.Many2one("res.users", string="Nom du commercial")
    rc_duration                        = fields.Float(string="Durée de vie")
    rc_product_dest                    = fields.Char(string="Destination du produit")
    rc_cust_wait                       = fields.Char(string="Attentes de notre client et points particuliers")
    rc_done_study                      = fields.Selection([
        ("Oui", "Oui"),
        ("Non", "Non"),
    ], string="Étude pièce faite par PG")
    rc_cmd_date                        = fields.Date(string="Date de la commande")
    rc_cmd_date_semaine                = fields.Integer(string="Semaine de la commande")
    rc_cmd_date_nb                     = fields.Char(string="Nombre de pièces vendues")
    rc_dfn_ro_date                     = fields.Date(string="Date de la DFN RO")
    rc_dfn_ro_date_semaine             = fields.Integer(string="Semaine de la DFN RO")
    rc_dfn_ro_date_nb                  = fields.Char(string="Nombre de pièces vendues 1")
    rc_first_m_try                     = fields.Date(string="Date 1er essai moule (IOD) ")
    rc_first_m_try_semaine             = fields.Integer(string="Semaine 1er essai moule (IOD) ")
    rc_first_m_try_nb                  = fields.Char(string="Nombre de pièces vendues 2")
    rc_ei_pres                         = fields.Date(string="Date Présentation EI")
    rc_ei_pres_semaine                 = fields.Integer(string="Semaine Présentation EI")
    rc_ei_pres_nb                      = fields.Char(string="Nombre de pièces vendues 3")
    rc_dms_date                        = fields.Date(string="Date DMS")
    rc_dms_date_semaine                = fields.Integer(string="Semaine DMS")
    rc_dms_date_nb                     = fields.Char(string="Nombre de pièces vendues 4")
    rc_eop_date                        = fields.Date(string="Date EOP (Fin de vie)")
    rc_eop_date_semaine                = fields.Integer(string="Semaine EOP")
    rc_eop_date_nb                     = fields.Char(string="Nombre de pièces vendues 5")
    rc_nb_pce_p_jal                    = fields.Text(string="Commentaire spécifique (essais supplémentaire)")
    decomposition_prix_ids             = fields.One2many("is.revue.de.contrat.decomposition.prix", "is_revue_id")
    productivite_ids                   = fields.One2many("is.revue.de.contrat.decomposition.productivite", "is_revue_id")
    previsions_ids                     = fields.One2many("is.revue.de.contrat.decomposition.previsions", "is_revue_id")
    rc_eiv_moule                       = fields.Float(string="Moule ")
    rc_eiv_moule_cmt                   = fields.Char(string="Commentaire")
    rc_eiv_etude                       = fields.Float(string="Étude")
    rc_eiv_etude_cmt                   = fields.Char(string="Commentaire 1")
    rc_eiv_main_prehension             = fields.Float(string="Main de préhension")
    rc_eiv_main_prehension_cmt         = fields.Char(string="Commentaire 2")
    rc_eiv_barre_chaude                = fields.Float(string="Barre chaude")
    rc_eiv_barre_chaude_cmt            = fields.Char(string="Commentaire 3")
    rc_eiv_gab_controle                = fields.Float(string="Gabarit de contrôle")
    rc_eiv_gab_controle_cmt            = fields.Char(string="Commentaire 4")
    rc_eiv_mach_spec                   = fields.Float(string="Machine spéciale")
    rc_eiv_mach_spec_cmt               = fields.Char(string="Commentaire 5")
    rc_eiv_plan_valid                  = fields.Float(string="Plan de validation")
    rc_eiv_plan_valid_cmt              = fields.Char(string="Commentaire 6")
    rc_eiv_mis_point                   = fields.Float(string="Mise au point")
    rc_eiv_mis_point_cmt               = fields.Char(string="Commentaire 7")
    rc_eiv_pack                        = fields.Float(string="Packaging")
    rc_eiv_pack_cmt                    = fields.Char(string="Commentaire 8")
    rc_eiv_amort                       = fields.Float(string="Amortissement")
    rc_eiv_amort_cmt                   = fields.Char(string="Commentaire 9")
    rc_eiv_total                       = fields.Float(string="Total", compute="get_rc_eiv_total")
    rc_sp_type_piece                   = fields.Selection([
        ("PLS", "PLS"),
        ("POE", "POE"),
    ], string="Type de pièce")
    rc_sp_aspect                       = fields.Boolean(string="Type de pièce")
    rc_sp_aspect                       = fields.Boolean(string="Pièce d'aspect")
    rc_sp_piece_technique              = fields.Boolean(string="Pièce technique")
    rc_sp_piece_reglem                 = fields.Boolean(string="Pièce soumise à réglementation")
    rc_sp_piece_reglem_cmt             = fields.Text(string="Commentaire Pièce soumise à réglementation")
    rc_sp_piece_sec                    = fields.Boolean(string="Sécurité du produit")
    rc_sp_piece_sec_cmt                = fields.Text(string="Commentaire Sécurité du produit")
    rc_sp_piece_sec2                   = fields.Boolean(string="Pièce de sécurité")
    rc_sp_piece_sec2_cmt               = fields.Text(string="Commentaire pièce de sécurité")
    rc_sp_com_exig_part                = fields.Boolean(string="Exigences particulières ( légales, environnementales...)")
    rc_sp_com_exig_part_cmt            = fields.Text(string="Définition exigences particulières")
    rc_sp_crs                          = fields.Selection([
        ("analysee",  "Reçue et analysée"),
        ("recue",     "Reçue"),
        ("inchangee", "Inchangée"),
        ("non_recue", "Non reçue"),
    ], string="CSR ou Exigences spécifiques du client")
    rc_sp_crs_cmt                      = fields.Text(string="Commentaire CSR ou Exigences spécifiques du client")
    rc_sp_carac_spec                   = fields.Boolean(string="Caractéristiques spéciales définies")
    rc_sp_carac_spec_cmt               = fields.Text(string="Définition caractéristiques spéciales")
    rc_sp_mat_con_pg                   = fields.Boolean(string="Matière connue à PG")
    rc_sp_mat_con_pg_cmt               = fields.Text(string="Désignation matière connue à PG")
    rc_edl_at_n_ppm                    = fields.Char(string="Niveau ppm")
    rc_edl_at_eng_fais                 = fields.Boolean(string="Engagement de faisabilité")
    rc_edl_at_syn_am_proc              = fields.Boolean(string="Synthèse AMDEC Process")
    rc_edl_at_synop_fabr               = fields.Boolean(string="Synoptique de fabrication")
    rc_edl_at_plan_surv                = fields.Boolean(string="Plan de surveillance")
    rc_edl_at_car_spec                 = fields.Boolean(string="Caractéristiques spéciales")
    rc_edl_at_plan_piece               = fields.Boolean(string="Plan pièce")
    rc_edl_at_pres_util                = fields.Boolean(string="Préconisation d'utilisation")
    rc_edl_at_fiche_tech_mat           = fields.Boolean(string="Fiche technique matière")
    rc_edl_at_rapport_ctrl             = fields.Boolean(string="Rapport de contrôle")
    rc_edl_at_cap                      = fields.Boolean(string="Capabilité")
    rc_edl_at_plan_m_ctrl              = fields.Boolean(string="Plan du moyen de contrôle")
    rc_edl_at_moy_ctrl                 = fields.Boolean(string="R&amp;R Moyen de contrôle")
    rc_edl_at_ut_moy_ctrl              = fields.Boolean(string="Utilisation moyen de contrôle ")
    rc_edl_at_plan_valid               = fields.Boolean(string="Plan de validation ")
    rc_edl_at_rap_ess_lab              = fields.Boolean(string="Rapport essai laboratoire")
    rc_edl_at_acc_mont                 = fields.Boolean(string="Acceptation montabilité")
    rc_edl_at_acc_style                = fields.Boolean(string="Acceptation de style")
    rc_edl_at_fic_cond                 = fields.Boolean(string="Fiche de conditionnement")
    rc_edl_at_dec_idms                 = fields.Boolean(string="Déclaration IMDS")
    rc_edl_at_fic_cap                  = fields.Boolean(string="Fiche capacitaire")
    rc_edl_at_aud_proc                 = fields.Boolean(string="Audit process")
    rc_edl_at_acc_ei                   = fields.Boolean(string="Acceptation EI")
    rc_edl_n_at_n_ppm                  = fields.Boolean(string="Niveau ppm ")
    rc_edl_n_at_synt_amdec_proc        = fields.Boolean(string="Synthèse AMDEC Process ")
    rc_edl_n_at_syn_fab                = fields.Boolean(string="Synoptique de fabrication ")
    rc_edl_n_at_plan_surv              = fields.Boolean(string="Plan de surveillance ")
    rc_edl_n_at_carac_spec             = fields.Boolean(string="Caractéristiques spéciales ")
    rc_edl_n_at_plan_piece             = fields.Boolean(string="Plan pièce ")
    rc_edl_n_at_prec_ut                = fields.Boolean(string="Préconisation d'utilisation ")
    rc_edl_n_at_f_t_mat                = fields.Boolean(string="Fiche technique matière ")
    rc_edl_n_at_rprt_ctrl              = fields.Boolean(string="Rapport de contrôle ")
    rc_edl_n_at_cap                    = fields.Boolean(string="Capabilité ")
    rc_edl_n_at_fic_cond               = fields.Boolean(string="Fiche de conditionnement ")
    rc_edl_n_at_aud_proc               = fields.Boolean(string="Audit process ")
    rc_edl_n_at_acc_ei                 = fields.Boolean(string="Acceptation EI ")
    rc_synthese_amdec_process_choix    = fields.Selection([
        ("PG",     "Standard Plastigray"),
        ("CLIENT", "Standard Client"),
        ("AIAG",   "Standard AIAG"),
    ], string="Standard AMDEC Process")
    rc_num_plan                        = fields.Char(string="N°plan")
    rc_num_dfn                         = fields.Char(string="N°DFN")
    rc_num_cdc                         = fields.Char(string="N°CDC")
    rc_eqs_comment                     = fields.Text(string="Commentaire libre")
    rc_eqs_pj                          = fields.Many2many("ir.attachment", "is_revue_rc_eqs_pj_rel", "revu_id", "att_id", string="Pièce jointe")
    rc_site_fabrication                = fields.Selection([
        ("1",      "1-Gray"),
        ("3",     "3-Plasti-ka"),
        ("4",     "4-St-Brice"),
        ("autre", "Autre"),
    ], string="Site de fabrication")
    rc_site_fabrication_autre          = fields.Char(string="Autre site de fabrication")
    rc_process_fabrication             = fields.Text(string="Process de fabrication")
    rc_nb_empreintes_moule             = fields.Char(string="Nombre d'empreintes du moule")
    rc_moulage_sur                     = fields.Char(string="Moulage sur (empreintes)")
    rc_tonnage_presse_vendu            = fields.Selection([
        ("25T",   "25T"),
        ("40T",   "40T"),
        ("60T",   "60T"),
        ("90T",   "90T"),
        ("140T",  "140T"),
        ("200T",  "200T"),
        ("250T",  "250T"),
        ("300T",  "300T"),
        ("450T",  "450T"),
        ("550T",  "550T"),
        ("600T",  "600T"),
        ("750T",  "750T"),
        ("1000T", "1000T"),
        ("1500T", "1500T"),
        ("2000T", "2000T"),
    ], string="Tonnage presse vendu")
    rc_stock_securite                  = fields.Selection([
        ("Non", "Non"),
        ("Oui", "Oui"),
    ], string="Stock de sécurité")
    rc_stock_securite_commentaire      = fields.Char(string="Stock de sécurité commentaire")
    rc_dfi_process_fab                 = fields.Char(string="Process et site de fabrication vendu")
    rc_dfi_schema_lieu_fab             = fields.Text(string="Schéma de flux vendu (Logistique)")
    rc_dfi_classe_comrc                = fields.Selection([
        ("Classe 1", "Classe 1 : 50T - 75T"),
        ("Classe 2", "Classe 2 : 100T - 125T"),
        ("Classe 3", "Classe 3 : 150T - 250T"),
        ("Classe 4", "Classe 4 : 350T - 450T"),
        ("Classe 5", "Classe 5 : 600T - 700T"),
        ("Classe 6", "Classe 6 : 800T - 1000T"),
    ], string="Classe commerciale")
    version_ids                        = fields.One2many("is.revue.de.contrat.version", "is_revue_id")
    rc_dfi_temp_occ_pm                 = fields.Float(string="Temps occupation presse mensuelle")
    rc_dfe_desc_proc                   = fields.Text(string="Descriptif du process et site de fabrication vendu")
    rc_dfe_sch_lieu_fab                = fields.Text(string="Schéma de flux vendu (Logistique) ")
    rc_df_engagement_faisabilite       = fields.Many2many("ir.attachment", "is_revue_engagement_faisabilite_rel", "revu_id", "att_id", string="Engagement de faisabilité ")
    rc_df_engagement_faisabilite_autre = fields.Many2many("ir.attachment", "is_revue_engagement_autre_faisabilite_rel", "revu_id", "att_id", string="Pièce jointe ")
    rc_df_fiche_capacitaire            = fields.Many2many("ir.attachment", "is_revue_rc_df_fiche_capacitaire_rel", "revu_id", "att_id", string="Fiche capacitaire ")
    dfe_version_ids                    = fields.One2many("is.revue.de.contrat.dfe.version", "is_revue_id")
    dynacase_id = fields.Integer(string="Id Dynacase")


    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
            
            




class is_revue_de_contrat_decomposition_prix(models.Model):
    _name        = "is.revue.de.contrat.decomposition.prix"
    _description = "Revue de contrat Décomposition prix"
    _rec_name    = "rc_price_comp_article"

    rc_price_comp_article           = fields.Char(string="Désignation pièce")
    rc_reference_client             = fields.Char(string="Référence client")
    rc_year_quantity                = fields.Integer(string="Quantité annuelle")
    rc_price_clientid               = fields.Many2one("res.partner", string="Site de livraison client")
    rc_mat_part                     = fields.Float(string="Part matière")
    rc_comp_part                    = fields.Float(string="Part composant")
    rc_va_injection                 = fields.Float(string="VA injection")
    rc_va_assembly                  = fields.Float(string="VA assemblage")
    rc_emb_part                     = fields.Float(string="Part emballage")
    rc_port_fee                     = fields.Float(string="Frais port")
    rc_logistic                     = fields.Float(string="Logistique (Coût stockage)")
    rc_moul_amort                   = fields.Float(string="Amortissement client")
    rc_moul_amort_interne           = fields.Float(string="Amortissement interne")
    rc_moul_cagnotage               = fields.Float(string="Cagnotage")
    rc_moul_amort_commentaire       = fields.Char(string="Amortissement Commentaire")
    rc_preserie_surcout             = fields.Float(string="Surcoût présérie")
    rc_preserie_surcout_commentaire = fields.Char(string="Surcoût présérie Commentaire")
    rc_sell_price                   = fields.Float(string="Prix de vente")
    rc_ca_annuel                    = fields.Float(string="CA annuel")
    rc_vac                          = fields.Float(string="VAC")
    is_revue_id = fields.Many2one("is.revue.de.contrat", string="Revue de contrat")


class is_revue_de_contrat_decomposition_productivite(models.Model):
    _name        = "is.revue.de.contrat.decomposition.productivite"
    _description = "Revue de contrat Productivité"
    _rec_name    = "rc_productivite_article"

    rc_productivite_article      = fields.Char(string="Article")
    rc_productivite_annee        = fields.Char(string="Année")
    rc_productivite_productivite = fields.Char(string="Productivité")
    is_revue_id                  = fields.Many2one("is.revue.de.contrat", string="Revue de contrat")


class is_revue_de_contrat_decomposition_previsions(models.Model):
    _name        = "is.revue.de.contrat.decomposition.previsions"
    _description = "Revue de contrat Prévisions"
    _rec_name    = "rc_previsions_article"

    rc_previsions_article      = fields.Char(string="Article")
    rc_previsions_annee        = fields.Char(string="Année")
    rc_previsions_quantite     = fields.Char(string="Productivité")
    is_revue_id                = fields.Many2one("is.revue.de.contrat", string="Revue de contrat")


class is_revue_de_contrat_version(models.Model):
    _name        = "is.revue.de.contrat.version"
    _description = "Revue de contrat Versions"
    _rec_name    = "rc_dfi_article"

    rc_dfi_version             = fields.Selection([
        ("Non", "Non"),
        ("Oui", "Oui"),
    ], string="Version")
    rc_dfi_article             = fields.Char(string="Article")
    rc_dfi_cycle               = fields.Char(string="Cycle par pièce")
    rc_dfi_nb_emp              = fields.Char(string="Nb empreintes par référence")
    rc_dfi_mod                 = fields.Selection([
        ("0.25", "0.25"),
        ("0.5", "0.5"),
        ("0.75", "0.75"),
        ("1", "1"),
        ("1.5", "1.5"),
        ("2", "2"),
    ], string="MOD totale pour le poste")
    rc_dfi_taux_rebut          = fields.Char(string="Tx rebut vendu")
    rc_dfi_poids_piece         = fields.Char(string="Poids pièce (en g)")
    rc_dfi_poids_carotte       = fields.Char(string="Poids carotte (en g)")
    rc_dfi_car_reb             = fields.Selection([
        ("Non", "Non"),
        ("Oui", "Oui"),
    ], string="Carotte rebroyée")
    rc_dfi_car_reb_pourcentage = fields.Float(string="Pourcentage de rebroyé admis par le client")
    rc_dfi_matiere             = fields.Text(string="Matière")
    rc_dfi_mat_prix_vendu      = fields.Text(string="Prix vendu matière")
    rc_dfi_comp                = fields.Text(string="Composants")
    rc_dfi_comp_prix_vendu     = fields.Text(string="Prix vendu composants")
    rc_dfi_sous_traitance      = fields.Text(string="Sous-traitance (description)")
    rc_dfi_sous_traitance_prix = fields.Text(string="Prix vendu sous-traitance")
    rc_dfi_desc_emb            = fields.Text(string="Descriptif emballage")
    rc_dfi_qte_carton          = fields.Char(string="Qt par UC")
    rc_dfi_qte_palette         = fields.Char(string="Nb UC par palette")
    rc_dfi_lot_liv             = fields.Char(string="Lot de livraison (en pièces)")
    rc_dfi_multiple_liv        = fields.Char(string="Multiple de livraison")
    rc_dfi_lot_fab             = fields.Char(string="Lot de fabrication (en pièces)")
    is_revue_id                = fields.Many2one("is.revue.de.contrat", string="Revue de contrat")


class is_revue_de_contrat_dfe_version(models.Model):
    _name        = "is.revue.de.contrat.dfe.version"
    _description = "Revue de contrat Versions"
    _rec_name    = "rc_dfe_comp"

    rc_dfe_version             = fields.Selection([
        ("Non", "Non"),
        ("Oui", "Oui"),
    ], string="Version")
    rc_dfe_comp                = fields.Text(string="Composants")
    rc_dfe_comp_pri_vendu      = fields.Text(string="Composants &#58; prix vendu")
    rc_dfe_cycle               = fields.Char(string="Cycle par pièce")
    rc_dfe_mod                 = fields.Selection([
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
    ], string="MOD pour le poste")
    rc_dfe_taux_rebut = fields.Char(string="Tx rebut vendu")
    rc_dfe_desc_emaballage     = fields.Text(string="Descriptif emballage")
    rc_dfe_sous_traitance      = fields.Text(string="Sous-traitance (description)")
    rc_dfe_sous_traitance_prix = fields.Text(string="Prix vendu sous-traitance")
    rc_dfe_qte_carton          = fields.Char(string="Quantité par carton")
    rc_dfe_qte_palette         = fields.Char(string="Quantité par palette")
    rc_dfe_lot_livraison       = fields.Char(string="Lot de livraison (en pièces)")
    rc_dfe_multiple_liv        = fields.Char(string="Multiple de livraison")
    rc_dfe_lot_fab             = fields.Char(string="Lot de fabrication (en pièces)")
    is_revue_id                = fields.Many2one("is.revue.de.contrat", string="Revue de contrat")
