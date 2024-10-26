# -*- coding: utf-8 -*-
from odoo import models, fields, api # type: ignore


#TODO : 
#- Manque lien Revue de lancement, revue de contrat, revue de projet, revue des risuqes
#- Lignes en trop dans tableaux Revue de contrat et Revue de projet jalon
#- Manque le lien avec les documents des moules dans le tableau des docuements
#- Le champ rpj_total_vente_moule valire des infos dans les investissement achat moule => Pas dispo dans Odoo



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


    rpj_mouleid                  = fields.Many2one("is.mold", string="Moule", required=True)
    rpj_chrono                   = fields.Char(string="Chrono"   , copy=False, compute='_compute_rpj_chrono',store=True, readonly=True)
    rpj_indice                   = fields.Integer(string="Indice", copy=False, compute='_compute_rpj_chrono',store=True, readonly=True)
    rpj_j = fields.Selection([
        ("J0", "Préparation J0"),
        ("J1", "Préparation J1"),
        ("J2", "Préparation J2"),
        ("J3", "Préparation J3"),
        ("J4", "Préparation J4"),
        ("J5", "Préparation J5"),
        ("J6", "J5 validé"),
    ], string="J actuelle", copy=False, compute='_compute_rpj_chrono',store=True, readonly=True)
    rpj_date_planning_j          = fields.Date(string="Date planning J")
    rpj_date_creation            = fields.Date(string="Date de réalisation", default=fields.Date.context_today, copy=False)
    rpj_plan_action              = fields.Char(string="Plan d'action associé")
    rpj_niveau_ppm               = fields.Char(string="Niveau ppm revue de contrat")
    rpj_commentaire              = fields.Text(string="Commentaire")
    rpj_motif_refus              = fields.Text(string="Motif du refus")
    rpj_photo                    = fields.Image(string="Photo de la pièce", related='rpj_mouleid.image')
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
    rp_marge_brute_moule         = fields.Float(string="Marge brute moule (%)", compute='_compute_rp_marge_brute_moule', readonly=True, store=True, copy=False)
    decomposition_prix_ids       = fields.One2many("is.revue.projet.jalon.decomposition.prix", "is_revue_project_jalon_id")
    rpj_dp_ca_annuel             = fields.Float(string="CA Annuel")
    rpj_dp_vac                   = fields.Float(string="VAC")
    rpj_dp_eiv_total             = fields.Float(string="Total investissement")
    rpj_dp_schema_flux_vendu     = fields.Char(string="Schéma de flux vendu")
    dynacase_id                  = fields.Integer(string="Id Dynacase",index=True,copy=False)
    state = fields.Selection([
        ("rpj_brouillon",           "Brouillon"),
        ("rpj_directeur_technique", "Directeur Technique"),
        ("rpj_directeur_site",      "DIRECTEUR de Site"),
        ("rpj_pour_information",    "Pour Information"),
        ("rpj_valide",              "Validé"),
        ("rpj_refus",               "Refusé"),
    ], default="rpj_brouillon", string="State", tracking=True, copy=False)
    vers_brouillon_vsb           = fields.Boolean(string="Brouillon"          , compute='_compute_vsb', readonly=True, store=False)
    vers_directeur_technique_vsb = fields.Boolean(string="Directeur Technique", compute='_compute_vsb', readonly=True, store=False)
    vers_direceeur_de_site_vsb   = fields.Boolean(string="Direceeur de Site"  , compute='_compute_vsb', readonly=True, store=False)
    vers_pour_information_vsb    = fields.Boolean(string="Pour Information"   , compute='_compute_vsb', readonly=True, store=False)
    vers_valide_vsb              = fields.Boolean(string="Validé"             , compute='_compute_vsb', readonly=True, store=False)
    vers_refuse_vsb              = fields.Boolean(string="Refusé"             , compute='_compute_vsb', readonly=True, store=False)
    logo_rs                      = fields.Char(string="Logo RS"               , compute='_compute_logo_rs', readonly=True, store=False)


    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }


    @api.depends('rpj_rcid','rpj_total_achat_moule')
    def _compute_logo_rs(self):
        for obj in self:
            logo_rs = False
            if obj.rpj_rcid:
                if obj.rpj_rcid.rc_sp_piece_reglem:
                    logo_rs='R'
                if obj.rpj_rcid.rc_sp_piece_sec:
                    logo_rs='S'
                if obj.rpj_rcid.rc_sp_piece_reglem and obj.rpj_rcid.rc_sp_piece_sec:
                    logo_rs='RS'
            obj.logo_rs = logo_rs


    @api.depends('rpj_total_vente_moule','rpj_total_achat_moule')
    def _compute_rp_marge_brute_moule(self):
        for obj in self:
            vente_moule = obj.rpj_total_vente_moule
            achat_moule = obj.rpj_total_achat_moule
            marge_brute_moule = 0
            if vente_moule>0:
                marge_brute_moule = round(100*(1 - (achat_moule / vente_moule)),2)
            obj.rp_marge_brute_moule = marge_brute_moule



    # rpj_total_vente_moule        = fields.Float(string="Total vente moule")
    # rpj_total_achat_moule        = fields.Float(string="Total achat moule")


#   //** Marge brute **************************************************
#   $vente_moule=$this->getValue("rpj_total_vente_moule");
#   $achat_moule=$this->getValue("rpj_total_achat_moule");
#   //Marge en % =1-(Achat/ Vente)*100 = (1-(14104/32402))*100= 56.47 % 
#   $marge_brute_moule = round(100*(1 - ($achat_moule / $vente_moule)),2);
#   $this->setValue("rp_marge_brute_moule",$marge_brute_moule);
#   //*****************************************************************



    @api.depends('rpj_mouleid')
    def _compute_rpj_chrono(self):
        for obj in self:
            rpj_indice=0
            rpj_chrono = "?"
            rpj_j = ''
            if obj.rpj_mouleid.j_actuelle:
                rpj_j = obj.rpj_mouleid.j_actuelle
                domain=[
                    ('rpj_mouleid','=', obj.rpj_mouleid.id),
                    ('rpj_j'      ,'=', rpj_j),
                ]
                docs=self.env['is.revue.projet.jalon'].search(domain, limit=1, order="rpj_indice desc")
                for doc in docs:
                    rpj_indice = int(doc.rpj_indice)
                    print(doc, doc.rpj_indice)
                rpj_indice+=1
                indice = ("00%s"%rpj_indice)[-2:]
                rpj_chrono = "%s-%s-%s"%(obj.rpj_mouleid.name,rpj_j, indice)
            obj.rpj_j      = rpj_j
            obj.rpj_indice = rpj_indice
            obj.rpj_chrono = rpj_chrono




    @api.onchange('rpj_mouleid')
    def onchange_rpj_mouleid(self):
        for obj in self:
            obj.rpj_clientid = obj.rpj_mouleid.client_id.id
            obj.rpj_rcid     = obj.rpj_mouleid.revue_contrat_id.id
            obj.rpj_rlid     = obj.rpj_mouleid.revue_lancement_id.id
            obj.rpj_rr       = obj.rpj_mouleid.revue_risque_id.id
            
            #** Equipe projet *************************************************
            obj.equipe_projet_ids=False
            equipe_projet_ids=[]
            if obj.rpj_rlid:
                equipe_projet_fonction={
                    "chef_projet"          : "Chef de projet",
                    "expert_injection"     : "Expert injection",
                    "methode_injection"    : "Méthode injection",
                    "methode_assemblage"   : "Méthode assemblage",
                    "qualite_dev"          : "Métrologie",
                    "qualite_usine"        : "Qualité développement",
                    "achats"               : "Achats",
                    "logistique"           : "Logistique",
                    "logistique_usine"     : "Logistique Usine",
                    "commercial2"          : "Commercial",
                    "responsable_outillage": "Responsable outillage",
                    "responsable_projet"   : "Responsable projets",
                    "directeur_site"       : "Directeur site de production",
                    "directeur_technique"  : "Directeur technique",
                }
                for k in equipe_projet_fonction:
                    field_name="rl_%sid"%k
                    nomid = getattr(obj.rpj_rlid,field_name).id              
                    field_name="rpj_%sid"%k
                    setattr(obj, field_name, nomid)



                    print(field_name,nomid)
                    vals={
                        'rpj_equipe_projet_fonction': equipe_projet_fonction[k],
                        'rpj_equipe_projet_nomid'   : nomid,
                    }
                    equipe_projet_ids.append([0,False,vals])
                obj.equipe_projet_ids=equipe_projet_ids



                                # setattr(copie, name_field, dst_dossier_id)
                    # doc = getattr(obj,name_field)                





 
            #            workorders_values += [{
            #                 'sequence': operation.sequence,
            #                 'name': operation.name,
            #                 'production_id': production.id,
            #                 'workcenter_id': operation.workcenter_id.id,
            #                 'product_uom_id': production.product_uom_id.id,
            #                 'operation_id': operation.id,
            #                 'state': 'pending',
            #             }]
            #     workorders_dict = {wo.operation_id.id: wo for wo in production.workorder_ids.filtered(lambda wo: wo.operation_id)}
            #     for workorder_values in workorders_values:
            #         if workorder_values['operation_id'] in workorders_dict:
            #             # update existing entries
            #             workorders_list += [Command.update(workorders_dict[workorder_values['operation_id']].id, workorder_values)]
            #         else:
            #             # add new entries
            #             workorders_list += [Command.create(workorder_values)]                    
            #     production.workorder_ids = workorders_list
            # else:
            #     production.workorder_ids = [Command.delete(wo.id) for wo in production.workorder_ids.filtered(lambda wo: wo.operation_id)]






    # //** Equipe projet ************************************************
    # if (is_object($rl) and $this->getValue("rpj_equipe_projet_fonction")=="") {
    #   $equipe_projet_fonction="Chef de projet\nExpert injection\nMéthode injection\nMéthode assemblage\nMétrologie\nQualité développement\nAchats\nLogistique\nLogistique Usine\nCommercial\nResponsable outillage\nResponsable projets\nDirecteur site de production\nDirecteur technique";
    #   $tab=array(
    #     "chef_projet",
    #     "expert_injection",
    #     "methode_injection",
    #     "methode_assemblage",
    #     "qualite_dev",
    #     "qualite_usine",
    #     "achats",
    #     "logistique",
    #     "logistique_usine",
    #     "commercial2",
    #     "responsable_outillage",
    #     "responsable_projet",
    #     "directeur_site",
    #     "directeur_technique"
    #   );

    #   $noms=array(); $nomsid=array();
    #   foreach($tab as $v) {
    #     $title = $rl->getValue("rl_".$v);
    #     $id    = $rl->getValue("rl_".$v."id");
    #     $this->setValue("rpj_".$v,$title);
    #     $this->setValue("rpj_".$v."id",$id);
    #     $noms[]=$title;
    #     $nomsid[]=$id;
    #   }

    #   $this->setValue("rpj_equipe_projet_fonction", $equipe_projet_fonction);
    #   $this->setValue("rpj_equipe_projet_nom"     , $noms);
    #   $this->setValue("rpj_equipe_projet_nomid"   , $nomsid);
    # }
    # //*****************************************************************







    # rpj_rcid                     = fields.Many2one("is.revue.de.contrat", string="Revue de contrat")
    # rpj_rlid                     = fields.Many2one("is.revue.lancement", string="Revue de lancement")
    # rpj_rp                       = fields.Char(string="Revue de projet")
    # rpj_rr                       = fields.Char(string="Revue des risques")



    # revue_contrat_id   = fields.Many2one("is.revue.de.contrat", string="Revue de contrat"  , copy=False)
    # revue_lancement_id = fields.Many2one("is.revue.lancement" , string="Revue de lancement", copy=False)
    # revue_risque_id    = fields.Many2one("is.revue.risque"    , string="Revue des risques" , copy=False)


            # type_demande = obj.param_project_id.ppr_type_demande
            # print('onchange_etat',obj, type_demande)
            # if type_demande in ['DATE','PJ_DATE']:
            #     if obj.etat=='F':
            #         obj.rsp_date = date.today()
            #     else:
            #         obj.rsp_date=False












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
    rpj_bilan_risque_design       = fields.Integer(string="Design/Industrialisation ")
    rpj_bilan_risque_supply_chain = fields.Integer(string="Supply chain/Achat")
    rpj_bilan_risque_qualite      = fields.Integer(string="Qualite")
    rpj_bilan_risque_leadership   = fields.Integer(string="Leadership/Finances")
    is_revue_project_jalon_id     = fields.Many2one("is.revue.projet.jalon")


class is_revue_projet_jalon_equipe_projet(models.Model):
    _name        = "is.revue.projet.jalon.equipe.projet"
    _description = "Compte-rendu revue de projet jalon Bilan - Équipe projet"
    _rec_name    = "rpj_equipe_projet_fonction"

    rpj_equipe_projet_fonction = fields.Char(string="Fonction")
    rpj_equipe_projet_nomid    = fields.Many2one("res.users", string="Nom")
    rpj_equipe_projet_presence = fields.Selection([
        ("A", "Absent"),
        ("P", "Présent"),
        ("E", "Excusé"),
        ("N", "Non convoqué"),
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
        ("0.25", "0.25"),
        ("0.5",  "0.5"),
        ("0.75", "0.75"),
        ("1",    "1"),
        ("1.5",  "1.5"),
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
        ("0.25", "0.25"),
        ("0.5", "0.5"),
        ("0.75", "0.75"),
        ("1", "1"),
        ("1.5", "1.5"),
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

    rpj_dp_article            = fields.Char(string="Article")
    rpj_dp_qt_annuelle        = fields.Integer(string="Quantité annuelle")
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
