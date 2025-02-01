# -*- coding: utf-8 -*-
from odoo import models, fields, api, _      # type: ignore
from odoo.exceptions import ValidationError  # type: ignore


#TODO : 
# Vérfier la class et la methode en PHP dans Dynacase
# Dans le programme de syncro faire un compute du name et des autres champs

# Ajouter ces 3 contraites : 

#   function m1_vers_diffuse($newstate,$oldstate){
#     $nb1=count($this->doc->getTValue("rc_dfi_article"));
#     $nb2=count($this->doc->getTValue("rc_dfe_comp"));
#     $err="";
#     if($nb1==0 and $nb2==0) $err="Les versions dans l'onglet 'Données de fabrication' ne sont pas renseignées !";
#     return $err;
#   }

#   function m1_vers_brouillon($newstate,$oldstate){
#     $dbaccess= GetParam("FREEDOM_DB");
#     $docid=$this->doc->getValue("rc_num_outillageid");
#     if ($docid>0) {
#       $doc = new_Doc($dbaccess, $docid);
#       if (is_object($doc)) {
#         $rlid=$doc->getValue("MOUL_RLID");
#         if ($rlid>0) {
#           $err="Impossible de repasser à l'état 'Brouillon' car une revue de lancement existe !";
#         }
#       }
#     }
#     return $err;
#   }


# //** Recherche revue de projet jalon ***************************************
# if ($err==""){
#     $filter=array();
#     foreach ($tid as $k=>$v) {
#         $filter[]="RPJ_MOULEID ~ E'\\\\y".$v."\\\\y'";
#     }
#     $mouleid=$rc->getValue("rc_mouleid");
#     $filter=array();
#     $tid=array();
#     if ($mouleid>0) {
#         $moule = new_Doc($dbaccess, $mouleid,true);
#         if (is_object($moule)) {
#             $trev=$moule->getRevisions("TABLE");
#             foreach ($trev as $k=>$v) {
#                 $tid[]=$v["id"];
#                 $filter[]="RPJ_MOULEID ~ E'\\\\y".$v["id"]."\\\\y'";
#             }

#         }
#     }
#     if (count($filter)>0) {
#         $filter=implode(" or ",$filter);
#         $s=new SearchDoc($dbaccess,"PG_REVUE_PROJET_JALON");
#         $s->setObjectReturn();
#         $s->addFilter($filter); 
#         $s->addFilter("state='rpj_valide'"); 
#         $s->search();
#         while ($doc=$s->nextDoc()) {
#             $err="Il existe déjà une revue de projet jalon de validée => Duplication impossible !".$doc->title;
#         }
#     }
# }
# //**************************************************************************



# Ajouter ces champs calculés

# function calcul_champs() {


#     error_log("### TEST calcul_champs #### ");


#     //** chiffre d'affaire annuel **********************************************
#     $sell_price       = $this->getTValue('rc_sell_price');
#     $moul_amort       = $this->getTValue('rc_moul_amort');
#     $preserie_surcout = $this->getTValue('rc_preserie_surcout');
#     $qte_annuelle     = $this->getTValue('rc_year_quantity');
#         $X=0;
#         for ($i=0;$i<count($sell_price);$i++) {
#             $ca_annuel=$ca_annuel+$qte_annuelle[$i]*($sell_price[$i]-$moul_amort[$i]-$preserie_surcout[$i]);
#         }
#         if ($ca_annuel==0) $ca_annuel=" ";
#     $this->setValue('rc_ca_annuel', $ca_annuel);
#     //**************************************************************************


#     //** vac *******************************************************************
#     $va_injection     = $this->getTValue('rc_va_injection');
#     $va_assembly      = $this->getTValue('rc_va_assembly');
#         for ($i=0;$i<count($sell_price);$i++) {
#             $vac = $vac + ($va_injection[$i] + $va_assembly[$i])*$qte_annuelle[$i];
#         }
#         if ($vac==0) $vac=" ";
#     $this->setValue('rc_vac', $vac);
#     //**************************************************************************


#     //** Total Enveloppe investissement vendue *********************************
#     $moule           = $this->getValue('rc_eiv_moule');
#     $etude           = $this->getValue('rc_eiv_etude');
#     $main_prehension = $this->getValue('rc_eiv_main_prehension');
#     $barre_chaude    = $this->getValue('rc_eiv_barre_chaude');
#     $gab_controle    = $this->getValue('rc_eiv_gab_controle');
#     $mach_spec       = $this->getValue('rc_eiv_mach_spec');
#     $plan_valid      = $this->getValue('rc_eiv_plan_valid');
#     $mis_point       = $this->getValue('rc_eiv_mis_point');
#     $pack            = $this->getValue('rc_eiv_pack');
#     $amort           = $this->getValue('rc_eiv_amort');
#     $eiv_total=$moule+$etude+$main_prehension+$barre_chaude+$gab_controle+$mach_spec+$plan_valid+$mis_point+$pack; //+$amort;
#     if ($eiv_total==0) $eiv_total=" ";
#     $this->setValue('rc_eiv_total',$eiv_total);
#     //**************************************************************************

#     $cycle  = $this->getTValue('rc_dfi_cycle');
#     $nb_emp = $this->getTValue('rc_dfi_nb_emp');
#         $temp_occ_pm=0;
#         for ($i=0;$i<count($qte_annuelle);$i++) {
#             $temp_occ_pm = $temp_occ_pm + ($qte_annuelle[$i]/11) * $cycle[$i] /3600;
#         }
#         if ($temp_occ_pm==0) {
#             $temp_occ_pm=" ";
#         } else {
#             $temp_occ_pm=number_format(floatval($temp_occ_pm), 2);
#         }
#     $this->setValue('rc_dfi_temp_occ_pm', $temp_occ_pm);
#     //**************************************************************************



#     //** Recopie du champ moule pour lien vers le moule ************************
#     $mouleid  = $this->getValue('rc_mouleid');
#     $this->setValue('rc_num_outillageid',$mouleid);
#     //**************************************************************************
# }





# Liste de choix des clients livrés et des articles

# function lclientlivre($dbaccess,$rc_price_client){
#     global $action;

#     $filter=array();
#     $filter[]="title like '%$rc_price_client%'";
#     $filter[]="cli_etiquete like '%LIVRAISON%'";

#     $tdoc = getChildDoc($dbaccess,
#                         0,
#                         0,
#                         10,
#                         $filter,
#                         $action->user->id,
#                         "ITEM",
#                         "CLIENT",
# 			$distinct,
# 			"title");
#     $tr = array();
#     while ($doc=getNextDoc($dbaccess,$tdoc)) {
#         $tr[] = array(    $doc->title,
#                 $doc->id,
#                 $doc->title);
#     }
#     return $tr;
# }


# function larticle($docid) {
# 	include_once("FDL/Class.Doc.php");
# 	$dbaccess = GetParam("FREEDOM_DB");

# 	$tr=array();
# 	if ($docid>0) {
# 		$doc = new_Doc($dbaccess, $docid,true);
# 		$article=$doc->getTValue("rc_price_comp_article");
# 		foreach($article as $v) {
# 			$tr[]=array($v,$v);
# 		}
# 	}
#   return $tr;
# }









class is_revue_de_contrat(models.Model):
    _name        = "is.revue.de.contrat"
    _inherit=['mail.thread']
    _description = "Revue de contrat"


    @api.depends("rc_eiv_moule", "rc_eiv_etude", "rc_eiv_main_prehension", "rc_eiv_barre_chaude" , "rc_eiv_gab_controle", "rc_eiv_mach_spec", "rc_eiv_plan_valid", "rc_eiv_mis_point" ,"rc_eiv_pack", "rc_eiv_amort")
    def _compute_rc_eiv_total(self):
        for record in self:
            record.rc_eiv_total = record.rc_eiv_moule +  record.rc_eiv_etude +  record.rc_eiv_main_prehension + \
                                  record.rc_eiv_barre_chaude + record.rc_eiv_gab_controle +record.rc_eiv_mach_spec + \
                                  record.rc_eiv_plan_valid + record.rc_eiv_mis_point + record.rc_eiv_pack + record.rc_eiv_amort

    @api.depends("rc_mouleid","rc_dossierfid","rc_mouleid.project","rc_dossierfid.project","rc_mouleid.project.client_id","rc_dossierfid.project.client_id")
    def _compute_rc_projetid(self):
        for obj in self:
            projetid = False
            client_id = False
            if obj.rc_mouleid:
                projetid  = obj.rc_mouleid.project.id
                client_id = obj.rc_mouleid.project.client_id.id
            if obj.rc_dossierfid:
                projetid  = obj.rc_dossierfid.project.id
                client_id = obj.rc_dossierfid.project.client_id.id
            obj.rc_projetid = projetid
            obj.rc_client = client_id


    @api.depends("rc_dossierfid")
    def _compute_rc_ass_mouleid(self):
        for obj in self:
            ids=[]
            if obj.rc_dossierfid:
                for mold in obj.rc_dossierfid.mold_ids:
                    ids.append(mold.id)
            obj.rc_ass_mouleid = ids


    @api.depends("rc_mouleid","rc_dossierfid","rc_indice")
    def _compute_name(self):
        for obj in self:
            name="x"
            if obj.rc_mouleid:
                name = obj.rc_mouleid.name
            if obj.rc_dossierfid:
                name = obj.rc_dossierfid.name
            obj.name='RC-%s-%s'%(name,obj.rc_indice)


    name                               = fields.Char(string="N°", compute="_compute_name", store=True, readonly=True)
    rc_mouleid                         = fields.Many2one("is.mold", string="Moule", tracking=True)
    rc_dossierfid                      = fields.Many2one("is.dossierf", string="Dossier F", tracking=True)
    rc_indice                          = fields.Integer(string="Indice", readonly=True, default=0)
    rc_doc_moule_assemblage            = fields.Selection([
        ("c1", "La revue de contrat est attachée à un dossier d'assemblage"),
        ("c2", "La revue de contrat est attachée à un moule autonome"),
        ("c3", "La revue de contrat est attachée à un moule appartenant à un dossier d'assemblage"),
    ], string="Dossier moule ou assemblage", tracking=True, required=True)
    rc_type_automobile                 = fields.Selection([
        ("Non", "hors Automobile"),
        ("Oui", "Automobile"),
    ], string="Type automobile", tracking=True, required=True)
    rc_projetid                        = fields.Many2one("is.mold.project", string="Projet", compute="_compute_rc_projetid", store=True, readonly=True)
    rc_revue_contrat_assid             = fields.Many2one("is.revue.de.contrat", string="RC dossier F", readonly=True)
    rc_ass_mouleid                     = fields.Many2many("is.mold", "is_revue_mold_rel", "revue_id", "mold_id", string="Moules Dossier F", compute="_compute_rc_ass_mouleid", store=False, readonly=True)
    rc_client                          = fields.Many2one("res.partner", string="Client", compute="_compute_rc_projetid", store=True, readonly=True)
    rc_designation                     = fields.Char(string="Désignation", tracking=True)
    rc_num_outillageid                 = fields.Many2one("is.mold", string="N° outillage", tracking=True) 
    rc_daoid                           = fields.Many2one("is.dossier.appel.offre", string="Dossier d'appel d'offre", tracking=True)
    rc_commercial                      = fields.Many2one("res.users", string="Nom du commercial", tracking=True)
    rc_duration                        = fields.Float(string="Durée de vie", tracking=True)
    rc_product_dest                    = fields.Char(string="Destination du produit", tracking=True)
    rc_cust_wait                       = fields.Char(string="Attentes de notre client et points particuliers", tracking=True)
    rc_done_study                      = fields.Selection([
        ("Oui", "Oui"),
        ("Non", "Non"),
    ], string="Étude pièce faite par PG", tracking=True)

    rc_cmd_date                        = fields.Date(string="Date de la commande", tracking=True)
    rc_cmd_date_semaine                = fields.Integer(string="Semaine de la commande", tracking=True)
    rc_cmd_date_nb                     = fields.Char(string="Nombre de pièces vendues", tracking=True)
    rc_dfn_ro_date                     = fields.Date(string="Date de la DFN RO", tracking=True)
    rc_dfn_ro_date_semaine             = fields.Integer(string="Semaine de la DFN RO", tracking=True)
    rc_dfn_ro_date_nb                  = fields.Char(string="Nombre de pièces vendues 1", tracking=True)
    rc_first_m_try                     = fields.Date(string="Date 1er essai moule (IOD) ", tracking=True)
    rc_first_m_try_semaine             = fields.Integer(string="Semaine 1er essai moule (IOD) ", tracking=True)
    rc_first_m_try_nb                  = fields.Char(string="Nombre de pièces vendues 2", tracking=True)
    rc_ei_pres                         = fields.Date(string="Date Présentation EI", tracking=True)
    rc_ei_pres_semaine                 = fields.Integer(string="Semaine Présentation EI", tracking=True)
    rc_ei_pres_nb                      = fields.Char(string="Nombre de pièces vendues 3", tracking=True)
    rc_dms_date                        = fields.Date(string="Date DMS", tracking=True)
    rc_dms_date_semaine                = fields.Integer(string="Semaine DMS", tracking=True)
    rc_dms_date_nb                     = fields.Char(string="Nombre de pièces vendues 4", tracking=True)
    rc_eop_date                        = fields.Date(string="Date EOP (Fin de vie)", tracking=True)
    rc_eop_date_semaine                = fields.Integer(string="Semaine EOP", tracking=True)

    rc_eop_date_nb                     = fields.Char(string="Nombre de pièces vendues 5", tracking=True)
    rc_nb_pce_p_jal                    = fields.Text(string="Commentaire spécifique (essais supplémentaire)", tracking=True)
    decomposition_prix_ids             = fields.One2many("is.revue.de.contrat.decomposition.prix", "is_revue_id", tracking=True)
    productivite_ids                   = fields.One2many("is.revue.de.contrat.decomposition.productivite", "is_revue_id", tracking=True)
    previsions_ids                     = fields.One2many("is.revue.de.contrat.decomposition.previsions", "is_revue_id", tracking=True)
    rc_eiv_moule                       = fields.Float(string="Moule ", tracking=True)
    rc_eiv_moule_cmt                   = fields.Char(string="Commentaire", tracking=True)
    rc_eiv_etude                       = fields.Float(string="Étude", tracking=True)
    rc_eiv_etude_cmt                   = fields.Char(string="Commentaire 1", tracking=True)
    rc_eiv_main_prehension             = fields.Float(string="Main de préhension", tracking=True)
    rc_eiv_main_prehension_cmt         = fields.Char(string="Commentaire 2", tracking=True)
    rc_eiv_barre_chaude                = fields.Float(string="Barre chaude", tracking=True)
    rc_eiv_barre_chaude_cmt            = fields.Char(string="Commentaire 3", tracking=True)
    rc_eiv_gab_controle                = fields.Float(string="Gabarit de contrôle", tracking=True)
    rc_eiv_gab_controle_cmt            = fields.Char(string="Commentaire 4", tracking=True)
    rc_eiv_mach_spec                   = fields.Float(string="Machine spéciale", tracking=True)
    rc_eiv_mach_spec_cmt               = fields.Char(string="Commentaire 5", tracking=True)
    rc_eiv_plan_valid                  = fields.Float(string="Plan de validation", tracking=True)
    rc_eiv_plan_valid_cmt              = fields.Char(string="Commentaire 6", tracking=True)
    rc_eiv_mis_point                   = fields.Float(string="Mise au point", tracking=True)
    rc_eiv_mis_point_cmt               = fields.Char(string="Commentaire 7", tracking=True)
    rc_eiv_pack                        = fields.Float(string="Packaging", tracking=True)
    rc_eiv_pack_cmt                    = fields.Char(string="Commentaire 8", tracking=True)
    rc_eiv_amort                       = fields.Float(string="Amortissement", tracking=True)
    rc_eiv_amort_cmt                   = fields.Char(string="Commentaire 9", tracking=True)
    rc_eiv_total                       = fields.Float(string="Total", compute="_compute_rc_eiv_total", store=True, readonly=True)
    rc_sp_type_piece                   = fields.Selection([
        ("PLS", "PLS"),
        ("POE", "POE"),
    ], string="Type de pièce", tracking=True)
    rc_sp_aspect                       = fields.Boolean(string="Type de pièce", tracking=True)
    rc_sp_aspect                       = fields.Boolean(string="Pièce d'aspect", tracking=True)
    rc_sp_piece_technique              = fields.Boolean(string="Pièce technique", tracking=True)
    rc_sp_piece_reglem                 = fields.Boolean(string="Pièce soumise à réglementation", tracking=True)
    rc_sp_piece_reglem_cmt             = fields.Text(string="Commentaire Pièce soumise à réglementation", tracking=True)
    rc_sp_piece_sec                    = fields.Boolean(string="Sécurité du produit", tracking=True)
    rc_sp_piece_sec_cmt                = fields.Text(string="Commentaire Sécurité du produit", tracking=True)
    rc_sp_piece_sec2                   = fields.Boolean(string="Pièce de sécurité", tracking=True)
    rc_sp_piece_sec2_cmt               = fields.Text(string="Commentaire pièce de sécurité", tracking=True)
    rc_sp_com_exig_part                = fields.Boolean(string="Exigences particulières ( légales, environnementales...)", tracking=True)
    rc_sp_com_exig_part_cmt            = fields.Text(string="Définition exigences particulières", tracking=True)
    rc_sp_crs                          = fields.Selection([
        ("analysee",  "Reçue et analysée"),
        ("recue",     "Reçue"),
        ("inchangee", "Inchangée"),
        ("non_recue", "Non reçue"),
    ], string="CSR ou Exigences spécifiques du client", tracking=True)
    rc_sp_crs_cmt                      = fields.Text(string="Commentaire CSR ou Exigences spécifiques du client", tracking=True)
    rc_sp_carac_spec                   = fields.Boolean(string="Caractéristiques spéciales définies", tracking=True)
    rc_sp_carac_spec_cmt               = fields.Text(string="Définition caractéristiques spéciales", tracking=True)
    rc_sp_mat_con_pg                   = fields.Boolean(string="Matière connue à PG", tracking=True)
    rc_sp_mat_con_pg_cmt               = fields.Text(string="Désignation matière connue à PG", tracking=True)
    rc_edl_at_n_ppm                    = fields.Char(string="Niveau ppm", tracking=True)
    rc_edl_at_eng_fais                 = fields.Boolean(string="Engagement de faisabilité", tracking=True)
    rc_edl_at_syn_am_proc              = fields.Boolean(string="Synthèse AMDEC Process", tracking=True)
    rc_edl_at_synop_fabr               = fields.Boolean(string="Synoptique de fabrication", tracking=True)
    rc_edl_at_plan_surv                = fields.Boolean(string="Plan de surveillance", tracking=True)
    rc_edl_at_car_spec                 = fields.Boolean(string="Caractéristiques spéciales", tracking=True)
    rc_edl_at_plan_piece               = fields.Boolean(string="Plan pièce", tracking=True)
    rc_edl_at_pres_util                = fields.Boolean(string="Préconisation d'utilisation", tracking=True)
    rc_edl_at_fiche_tech_mat           = fields.Boolean(string="Fiche technique matière", tracking=True)
    rc_edl_at_rapport_ctrl             = fields.Boolean(string="Rapport de contrôle", tracking=True)
    rc_edl_at_cap                      = fields.Boolean(string="Capabilité", tracking=True)
    rc_edl_at_plan_m_ctrl              = fields.Boolean(string="Plan du moyen de contrôle", tracking=True)
    rc_edl_at_moy_ctrl                 = fields.Boolean(string="R&amp;R Moyen de contrôle", tracking=True)
    rc_edl_at_ut_moy_ctrl              = fields.Boolean(string="Utilisation moyen de contrôle ", tracking=True)
    rc_edl_at_plan_valid               = fields.Boolean(string="Plan de validation ", tracking=True)
    rc_edl_at_rap_ess_lab              = fields.Boolean(string="Rapport essai laboratoire", tracking=True)
    rc_edl_at_acc_mont                 = fields.Boolean(string="Acceptation montabilité", tracking=True)
    rc_edl_at_acc_style                = fields.Boolean(string="Acceptation de style", tracking=True)
    rc_edl_at_fic_cond                 = fields.Boolean(string="Fiche de conditionnement", tracking=True)
    rc_edl_at_dec_idms                 = fields.Boolean(string="Déclaration IMDS", tracking=True)
    rc_edl_at_fic_cap                  = fields.Boolean(string="Fiche capacitaire", tracking=True)
    rc_edl_at_aud_proc                 = fields.Boolean(string="Audit process", tracking=True)
    rc_edl_at_acc_ei                   = fields.Boolean(string="Acceptation EI", tracking=True)
    rc_edl_n_at_n_ppm                  = fields.Boolean(string="Niveau ppm ", tracking=True)
    rc_edl_n_at_synt_amdec_proc        = fields.Boolean(string="Synthèse AMDEC Process ", tracking=True)
    rc_edl_n_at_syn_fab                = fields.Boolean(string="Synoptique de fabrication ", tracking=True)
    rc_edl_n_at_plan_surv              = fields.Boolean(string="Plan de surveillance ", tracking=True)
    rc_edl_n_at_carac_spec             = fields.Boolean(string="Caractéristiques spéciales ", tracking=True)
    rc_edl_n_at_plan_piece             = fields.Boolean(string="Plan pièce ", tracking=True)
    rc_edl_n_at_prec_ut                = fields.Boolean(string="Préconisation d'utilisation ", tracking=True)
    rc_edl_n_at_f_t_mat                = fields.Boolean(string="Fiche technique matière ", tracking=True)
    rc_edl_n_at_rprt_ctrl              = fields.Boolean(string="Rapport de contrôle ", tracking=True)
    rc_edl_n_at_cap                    = fields.Boolean(string="Capabilité ", tracking=True)
    rc_edl_n_at_fic_cond               = fields.Boolean(string="Fiche de conditionnement ", tracking=True)
    rc_edl_n_at_aud_proc               = fields.Boolean(string="Audit process ", tracking=True)
    rc_edl_n_at_acc_ei                 = fields.Boolean(string="Acceptation EI ", tracking=True)
    rc_synthese_amdec_process_choix    = fields.Selection([
        ("PG",     "Standard Plastigray"),
        ("CLIENT", "Standard Client"),
        ("AIAG",   "Standard AIAG"),
    ], string="Standard AMDEC Process", tracking=True)
    rc_num_plan                        = fields.Char(string="N°plan", tracking=True)
    rc_num_dfn                         = fields.Char(string="N°DFN", tracking=True)
    rc_num_cdc                         = fields.Char(string="N°CDC", tracking=True)
    rc_eqs_comment                     = fields.Text(string="Commentaire libre", tracking=True)
    rc_site_fabrication                = fields.Selection([
        ("1",      "1-Gray"),
        ("3",     "3-Plasti-ka"),
        ("4",     "4-St-Brice"),
        ("autre", "Autre"),
    ], string="Site de fabrication", tracking=True)
    rc_site_fabrication_autre          = fields.Char(string="Autre site de fabrication", tracking=True)
    rc_process_fabrication             = fields.Text(string="Process de fabrication", tracking=True)
    rc_nb_empreintes_moule             = fields.Char(string="Nombre d'empreintes du moule", tracking=True)
    rc_moulage_sur                     = fields.Char(string="Moulage sur (empreintes)", tracking=True)
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
    ], string="Tonnage presse vendu", tracking=True)
    rc_stock_securite                  = fields.Selection([
        ("Non", "Non"),
        ("Oui", "Oui"),
    ], string="Stock de sécurité", tracking=True)
    rc_stock_securite_commentaire      = fields.Char(string="Stock de sécurité commentaire", tracking=True)
    rc_dfi_process_fab                 = fields.Char(string="Process et site de fabrication vendu", tracking=True)
    rc_dfi_schema_lieu_fab             = fields.Text(string="Schéma de flux vendu (Logistique)", tracking=True)
    rc_dfi_classe_comrc                = fields.Selection([
        ("Classe 1", "Classe 1 : 50T - 75T"),
        ("Classe 2", "Classe 2 : 100T - 125T"),
        ("Classe 3", "Classe 3 : 150T - 250T"),
        ("Classe 4", "Classe 4 : 350T - 450T"),
        ("Classe 5", "Classe 5 : 600T - 700T"),
        ("Classe 6", "Classe 6 : 800T - 1000T"),
    ], string="Classe commerciale", tracking=True)
    version_ids                        = fields.One2many("is.revue.de.contrat.version", "is_revue_id", tracking=True)
    rc_dfi_temp_occ_pm                 = fields.Float(string="Temps occupation presse mensuelle", tracking=True)
    rc_dfe_desc_proc                   = fields.Text(string="Descriptif du process et site de fabrication vendu", tracking=True)
    rc_dfe_sch_lieu_fab                = fields.Text(string="Schéma de flux vendu (Logistique) ", tracking=True)
    rc_eqs_pj                          = fields.Many2many("ir.attachment", "is_rc_eqs_pj_rel"                         , "rc_eqs_pj"                         , "att_id", string="Pièce jointe")
    rc_df_engagement_faisabilite       = fields.Many2many("ir.attachment", "is_rc_df_engagement_faisabilite_rel"      , "rc_df_engagement_faisabilite"      , "att_id", string="PJ Engagement de faisabilité")
    rc_df_engagement_faisabilite_autre = fields.Many2many("ir.attachment", "is_rc_df_engagement_faisabilite_autre_rel", "rc_df_engagement_faisabilite_autre", "att_id", string="PJ Engagement de faisabilité (autres)")
    rc_df_fiche_capacitaire            = fields.Many2many("ir.attachment", "is_rc_df_fiche_capacitaire_rel"           , "rc_df_fiche_capacitaire"           , "att_id", string="PJ Fiche capacitaire")
    rc_ca_annuel                       = fields.Float(string="CA annuel", digits=(12, 2), tracking=True)
    rc_vac                             = fields.Float(string="VAC", digits=(12, 2), tracking=True)
    dfe_version_ids                    = fields.One2many("is.revue.de.contrat.dfe.version", "is_revue_id")
    dynacase_id = fields.Integer(string="Id Dynacase",index=True,copy=False)
    state = fields.Selection([
        ("brouillon", "Brouillon"),
        ("diffuse"  , "Diffusé"),
    ], string="État", default='brouillon', copy=False, tracking=True)
    active = fields.Boolean('Actif', default=True, tracking=True)


    def write(self,vals):
        res=super().write(vals)
        self._rc_unique()
        return res



    @api.constrains('rc_mouleid', 'rc_dossierfid', 'rc_indice')
    def _rc_unique(self):
        for obj in self:
            domain=[
                ('rc_mouleid'   , '=', obj.rc_mouleid.id), 
                ('rc_dossierfid', '=', obj.rc_dossierfid.id), 
                ('rc_indice'    , '=', obj.rc_indice), 
                #('active'       , 'in', (True,False)), 
            ]
            lines = self.env['is.revue.de.contrat'].search(domain)


            print('TEST 2 _rc_unique', domain, lines, len(lines))

            if len(lines) > 1:
                raise ValidationError("Cette revue de contrat existe déjà !")


    # def name_get(self):
    #     result = []
    #     for obj in self:
    #         name=""
    #         if obj.rc_mouleid:
    #             name = obj.rc_mouleid.name
    #         if obj.rc_dossierfid:
    #             name = obj.rc_dossierfid.name

    #         name='RC-%s-%s'%(name,obj.rc_indice)

    #         result.append((obj.id, name))
    #     return result


    # def _name_search(self, name='', args=None, operator='ilike', context=None, limit=100):
    #     if not args:
    #         args = []
    #     if name:
    #         ids = list(self._search(['|',('rc_mouleid','ilike', name),('rc_dossierfid','ilike', name)], limit=limit))
    #     else:
    #         ids = self._search(args, limit=limit)
    #     return ids



    def copy(self, default=None):
        for obj in self:
            default = dict(default or {})
            print(default)
            default['rc_indice']=obj.rc_indice+1
            res=super().copy(default=default)
            return res





    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
            

    def vers_diffuse_action(self):
        for obj in self:
            obj.state='diffuse'

            if obj.rc_mouleid:
                obj.rc_mouleid.revue_contrat_id = obj.id
            if obj.rc_dossierfid:
                obj.rc_dossierfid.revue_contrat_id = obj.id






    def vers_brouillon_action(self):
        for obj in self:
            obj.state='brouillon'



    def copie_assemblage_action(self):
        copie=[
            "rc_client",
            "rc_clientid",

            "rc_designation",

            "rc_num_outillage",
            "rc_num_outillageid",

            "rc_commercial",
            "rc_commercialid",

            "rc_year_quantity",
            "rc_duration",
            "rc_product_dest",
            "rc_cust_wait",
            "rc_done_study",

            "rc_cmd_date",
            "rc_dfn_ro_date",
            "rc_first_m_try",
            "rc_ei_pres",
            "rc_dms_date",
            "rc_nb_pce_p_jal",

            "rc_sp_type_piece",
            "rc_sp_aspect",
            "rc_sp_piece_technique",
            "rc_sp_piece_reglem",
            "rc_sp_piece_reglem_cmt",
            "rc_sp_piece_sec",
            "rc_sp_piece_sec_cmt",
            "rc_sp_com_exig_part",
            "rc_sp_com_exig_part_cmt",
            "rc_sp_carac_spec",
            "rc_sp_carac_spec_cmt",
            "rc_sp_mat_con_pg",
            "rc_sp_mat_con_pg_cmt",

            "rc_edl_at_n_ppm",
            "rc_edl_at_eng_fais",
            "rc_edl_at_syn_am_proc",
            "rc_edl_at_synop_fabr",
            "rc_edl_at_plan_surv",
            "rc_edl_at_car_spec",
            "rc_edl_at_plan_piece",
            "rc_edl_at_pres_util",
            "rc_edl_at_fiche_tech_mat",
            "rc_edl_at_rapport_ctrl",
            "rc_edl_at_cap",
            "rc_edl_at_plan_m_ctrl",
            "rc_edl_at_moy_ctrl",
            "rc_edl_at_ut_moy_ctrl",
            "rc_edl_at_plan_valid",
            "rc_edl_at_rap_ess_lab",
            "rc_edl_at_acc_mont",
            "rc_edl_at_acc_style",
            "rc_edl_at_fic_cond",
            "rc_edl_at_dec_idms",
            "rc_edl_at_fic_cap",
            "rc_edl_at_aud_proc",
            "rc_edl_at_acc_ei",

            "rc_edl_n_at_n_ppm",
            "rc_edl_n_at_synt_amdec_proc",
            "rc_edl_n_at_syn_fab",
            "rc_edl_n_at_plan_surv",
            "rc_edl_n_at_carac_spec",
            "rc_edl_n_at_plan_piece",
            "rc_edl_n_at_prec_ut",
            "rc_edl_n_at_f_t_mat",
            "rc_edl_n_at_rprt_ctrl",
            "rc_edl_n_at_cap",
            "rc_edl_n_at_fic_cond",
            "rc_edl_n_at_aud_proc",
            "rc_edl_n_at_acc_ei",

            "rc_eqs_comment",
        ]







        for obj in self:
            if obj.rc_doc_moule_assemblage=='c3':
                print('TEST', obj)
                dossierf = obj.rc_mouleid.dossierf_id
                if not dossierf:
                    raise ValidationError("Il n'y a pas de dossier F sur ce moule !")
                
                rc = dossierf.revue_contrat_id
                if not rc:
                    raise ValidationError("Il n'y a pas de revue de contrat sur le dossier %s"%dossierf.name)

                obj.rc_revue_contrat_assid = rc.id
                obj._compute_rc_ass_mouleid()
                for field_name in copie:                   
                    if hasattr(rc, field_name):
                        val = getattr(rc,field_name)
                        setattr(obj, field_name, val)



    # responsable = _RESPONSABLES.get(ppr_responsable)          
    #                 if hasattr(obj, responsable):
    #                     user = getattr(obj,responsable)
    #                     if user:
    #                         doc.idresp = user.id

#    field_name="rpj_%sid"%k
#                         setattr(obj, field_name, nomid)




class is_revue_de_contrat_decomposition_prix(models.Model):
    _name        = "is.revue.de.contrat.decomposition.prix"
    _description = "Revue de contrat Décomposition prix"
    _rec_name    = "rc_price_comp_article"


    is_revue_id                     = fields.Many2one("is.revue.de.contrat", string="Revue de contrat")

    rc_price_comp_article           = fields.Char(string="Désignation pièce")
    rc_reference_client             = fields.Char(string="Référence client")
    rc_year_quantity                = fields.Integer(string="Quantité annuelle")
    rc_price_clientid               = fields.Many2one("res.partner", string="Site de livraison client")

    rc_mat_part                     = fields.Float(string="Part matière"              , digits=(12, 6))
    rc_comp_part                    = fields.Float(string="Part composant"            , digits=(12, 6))
    rc_va_injection                 = fields.Float(string="VA injection"              , digits=(12, 6))
    rc_va_assembly                  = fields.Float(string="VA assemblage"             , digits=(12, 6))
    rc_emb_part                     = fields.Float(string="Part emballage"            , digits=(12, 6))
    rc_port_fee                     = fields.Float(string="Frais port"                , digits=(12, 6))
    rc_logistic                     = fields.Float(string="Logistique (Coût stockage)", digits=(12, 6))
    rc_moul_amort                   = fields.Float(string="Amortissement client"      , digits=(12, 6))
    rc_moul_amort_interne           = fields.Float(string="Amortissement interne"     , digits=(12, 6))
    rc_moul_cagnotage               = fields.Float(string="Cagnotage"                 , digits=(12, 6))
    rc_moul_amort_commentaire       = fields.Char(string="Amortissement Commentaire")
    rc_preserie_surcout             = fields.Float(string="Surcoût présérie"          , digits=(12, 6))
    rc_preserie_surcout_commentaire = fields.Char(string="Surcoût présérie Commentaire")
    rc_sell_price                   = fields.Float(string="Prix de vente"             , digits=(12, 6))
    rc_total                        = fields.Float(string="Total", digits=(12, 6), compute="_compute_rc_total", store=False, readonly=True)
    rc_ecart                        = fields.Float(string="Écart", digits=(12, 6), compute="_compute_rc_total", store=False, readonly=True)

    @api.depends("rc_mat_part","rc_comp_part","rc_va_injection","rc_va_assembly","rc_emb_part","rc_port_fee","rc_logistic",
                 "rc_moul_amort","rc_moul_amort_interne","rc_moul_cagnotage","rc_preserie_surcout","rc_sell_price")
    def _compute_rc_total(self):
        for obj in self:
            total = 0
            total += obj.rc_mat_part + obj.rc_comp_part + obj.rc_va_injection + obj.rc_va_assembly + obj.rc_emb_part + obj.rc_port_fee
            total += obj.rc_logistic + obj.rc_moul_amort + obj.rc_moul_amort_interne + obj.rc_moul_cagnotage + obj.rc_preserie_surcout
            obj.rc_total = total
            obj.rc_ecart = total - obj.rc_sell_price


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
