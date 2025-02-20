# -*- coding: utf-8 -*-
from odoo import models, fields, api # type: ignore
from odoo.addons.is_dynacase2odoo.models.is_param_project import DOCUMENT_ACTION, DOCUMENT_ETAT # type: ignore
from odoo.exceptions import AccessError, ValidationError, UserError  # type: ignore
from datetime import datetime, timedelta, date


#TODO : 
#- Le champ rpj_total_vente_moule va lire des infos dans les investissement achat moule => Pas dispo dans Odoo


class is_revue_projet_jalon(models.Model):
    _name        = "is.revue.projet.jalon"
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = "Compte-rendu revue de projet jalon"
    _rec_name    = "rpj_chrono"
    _order = "create_date desc"


    @api.depends("state")
    def _compute_vsb(self):
        for obj in self:
            uid = self._uid

            vsb = False
            if obj.state in ["rpj_directeur_technique"]:
                vsb = True
            obj.vers_brouillon_vsb = vsb
            
            vsb = False
            if obj.state in ["rpj_brouillon"] and obj.rpj_j in ['J4','J5']:
                if  uid in [obj.rpj_chef_projetid.id, obj.rpj_directeur_techniqueid.id]:
                    vsb = True
            obj.vers_directeur_technique_vsb = vsb

            vsb = False
            if obj.state in ["rpj_directeur_technique"]:
                if  uid in [obj.rpj_directeur_techniqueid.id]:
                    vsb = True
            obj.vers_direceeur_de_site_vsb = vsb

            vsb = False
            if obj.state in ["rpj_brouillon"]:
                vsb = True
            obj.vers_diffuse_vsb = vsb

            vsb = False
            if obj.state=="rpj_directeur_site":
                if  uid in [obj.rpj_directeur_siteid.id]:
                    vsb = True
            #En J4 et J5, il faut passer par la validation du directeur de technique"
            if obj.state=="rpj_brouillon":
                if obj.rpj_j not in ['J4','J5']:
                    vsb = True
            obj.vers_valide_vsb = vsb

            vsb = False
            if obj.state in ["rpj_directeur_technique", "rpj_directeur_site"]:
                vsb = True
            obj.vers_refuse_vsb = vsb

            vsb = False
            if obj.state=='rpj_valide':                                   # Etat Validé uniquement
                if obj.rpj_j!='J6':                                       # Pas en J6
                    if obj.rpj_note>=80:                                  # Note >= 80
                        if obj.rpj_point_bloquant==0:                     # Pas de point bloquant
                            if obj.rpj_j==(obj.rpj_mouleid.j_actuelle or obj.dossierf_id.j_actuelle):     # Uniquement si J moule = J CR
                                if  uid in [obj.rpj_chef_projetid.id, obj.rpj_directeur_techniqueid.id]:
                                    vsb=True
            obj.vers_j_suivante_vsb = vsb


    def envoi_mail(self, users=[]):
        for obj in self:
            partner_ids = []
            destinataires_name = []
            for user in users:
                if user.id:
                    destinataires_name.append(user.name)
                    partner_ids.append(user.partner_id.id)
            if len(partner_ids)>0:
                etat = dict(self._fields['state'].get_description(self.env).get('selection')).get(self.state)
                user          = self.env['res.users'].browse(self._uid)
                nom           = user.name
                subject       = "[CR Jalon] %s état '%s'"%(obj.rpj_chrono, etat)
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                url = base_url + '/web#id=%s' '&view_type=form&model=%s'%(obj.id,self._name)
                destinataires_name = ', '.join(destinataires_name)
                body = """ 
                    <p>Bonjour,</p> 
                    <p>%s vient de passer le 'CR revue projet jalon'  
                    <a href='%s'>%s</a> à l'état '%s'.</p> 
                    <p>Merci d'en prendre connaissance.</p> 
                    <p><i>(Destinataires : %s)</i></p>
                """%(nom, url,obj.rpj_chrono,etat,destinataires_name)
                vals={
                    "model"         : self._name,
                    "subject"       : subject,
                    "body"          : body,
                    "partner_ids"   : partner_ids,
                }
                ctx = dict(
                    default_model=self._name,
                    default_res_id=obj.id,
                    default_composition_mode='comment',
                    custom_layout='mail.mail_notification_light', # Permet de définir la mise en page du mail
                )
                wizard = self.env['mail.compose.message'].with_context(ctx).create(vals)
                wizard.action_send_mail()
 

    def vers_brouillon_action(self):
        for obj in self:
            obj.sudo().state = "rpj_brouillon"
            users = [obj.rpj_chef_projetid]
            self.envoi_mail(users)


    def vers_directeur_technique_action(self):
        for obj in self:
            if not obj.rpj_rrid:
                raise ValidationError("Il est obligatoire d'avoir une revue des risques pour valider ce document!")
            J = obj.rpj_j
            if J!='J4' and J!='J5':
                raise ValidationError("En J0, J1, J2 et J3, il ne faut pas passer par la validation du directeur de technique!")
            if J=='J5':
                for line in obj.revue_de_projet_jalon_ids:
                    if not line.rpj_de2_cycle or not line.rpj_de2_nb_emp or not line.rpj_de2_mod or not line.rpj_de2_taux_rebut or not line.rpj_de2_poids_piece or not line.rpj_de2_poids_carotte:
                        err="Ces champs sont obligatoires en J5 : 'Cycle par pièce', 'Nb empreintes', 'MOD', 'Tx rebut vendu', 'Poids pièce (en g)', 'Poids carotte (en g)'"
                        raise ValidationError(err)
            obj.sudo().state = "rpj_directeur_technique"
            users = [obj.rpj_directeur_techniqueid]
            self.envoi_mail(users)


    def vers_direceeur_de_site_action(self):
        for obj in self:
            obj.sudo().state = "rpj_directeur_site"
            users = [obj.rpj_directeur_siteid]
            self.envoi_mail(users)


    def vers_diffuse_action(self):
        for obj in self:
            obj.sudo().state = "rpj_diffuse"
            users = [
                obj.rpj_chef_projetid,
                obj.rpj_expert_injectionid,
                obj.rpj_methode_injectionid,
                obj.rpj_methode_assemblageid,
                obj.rpj_qualite_devid,
                obj.rpj_qualite_usineid,
                obj.rpj_achatsid,
                obj.rpj_logistiqueid,
                obj.rpj_logistique_usineid,
                obj.rpj_commercial2id,
                obj.rpj_responsable_outillageid,
                obj.rpj_responsable_projetid,
                obj.rpj_directeur_siteid,
                obj.rpj_directeur_techniqueid,
            ]
            self.envoi_mail(users)


    def vers_valide_action(self):
        for obj in self:
            J=obj.rpj_j.lower()
            field_name="rpj_avancement_%s"%J
            setattr(obj, field_name, obj.rpj_note)
            field_name="rpj_date_valide_%s"%J
            setattr(obj, field_name, date.today())
            obj.sudo().state = "rpj_valide"
            if not obj.rpj_rcid or obj.rpj_rcid.state!='diffuse' or obj.rpj_rcid.active==False:
                raise ValidationError("Une revue de contrat diffusée est obligatoire !")
            if not obj.rpj_rlid or obj.rpj_rlid.state!='rl_diffuse' or obj.rpj_rlid.active==False:
                raise ValidationError("Une revue de lancement diffusée est obligatoire !")
            if not obj.rpj_rrid or obj.rpj_rrid.state!='rr_diffuse' or obj.rpj_rrid.active==False:
                raise ValidationError("Une revue des risques diffusée est obligatoire !")


    def vers_refuse_action(self):
        for obj in self:
            if not obj.rpj_motif_refus:
                raise ValidationError("Le motif du refus est obligatoire!")
            obj.sudo().state = "rpj_refus"

    def vers_j_suivante_action(self):
        for obj in self:
            if obj.vers_j_suivante_vsb:
                j = int(obj.rpj_j[-1:])
                j_suivante = j+1
                if obj.rpj_mouleid:
                    obj.rpj_mouleid.j_actuelle = "J%s"%j_suivante
                if obj.dossierf_id:
                    obj.dossierf_id.j_actuelle = "J%s"%j_suivante


    rpj_mouleid                  = fields.Many2one("is.mold"    , string="Moule", tracking=True)
    dossierf_id                  = fields.Many2one("is.dossierf", string="Dossier F", tracking=True)
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
    rpj_date_planning_j          = fields.Date(string="Date planning J", tracking=True)
    rpj_date_creation            = fields.Date(string="Date de réalisation", default=fields.Date.context_today, copy=False, tracking=True)
    rpj_plan_action              = fields.Char(string="Plan d'action associé", tracking=True)
    rpj_niveau_ppm               = fields.Char(string="Niveau ppm revue de contrat", tracking=True)
    rpj_commentaire              = fields.Text(string="Commentaire", tracking=True)
    rpj_motif_refus              = fields.Text(string="Motif du refus", tracking=True)
    rpj_photo                    = fields.Image(string="Photo de la pièce", related='rpj_mouleid.image')
    rpj_lieu_production          = fields.Selection([
        ("g", "Gray"),
        ("sb", "St-Brice"),
        ("pl", "Plasti-ka"),
        ("st", "Sous-Traitant"),
    ], string="Lieu de production (Revue de lancement)", tracking=True)
    rpj_affectation_presse       = fields.Char(string="Affectation presse (Revue de lancement)", tracking=True)
    rpj_lieu_production2         = fields.Selection([
        ("g",  "Gray"),
        ("sb", "St-Brice"),
        ("pl", "Plasti-ka"),
        ("st", "Sous-Traitant"),
    ], string="Lieu de production actuel", tracking=True)
    rpj_affectation_presse2      = fields.Char(string="Affectation presse actuelle", tracking=True)
    rpj_clientid                 = fields.Many2one("res.partner", string="Client", domain=[("is_company","=",True), ("customer","=",True)], tracking=True)
    rpj_rcid                     = fields.Many2one("is.revue.de.contrat", string="Revue de contrat", tracking=True)
    rpj_rlid                     = fields.Many2one("is.revue.lancement", string="Revue de lancement", tracking=True)
    rpj_rrid                     = fields.Many2one("is.revue.risque", string="Revue des risques", tracking=True)
    bilan_ids                    = fields.One2many("is.revue.projet.jalon.bilan", "is_revue_project_jalon_id", tracking=True)
    rpj_piece_jointe             = fields.Many2many("ir.attachment", "is_jalon_rpj_jointe_rel", "rpj_jointe_id", "att_id", string="Pièces jointes")
    equipe_projet_ids            = fields.One2many("is.revue.projet.jalon.equipe.projet", "is_revue_project_jalon_id", copy=True)
    rpj_chef_projetid            = fields.Many2one("res.users", string="Chef de projet", tracking=True)
    rpj_expert_injectionid       = fields.Many2one("res.users", string="Expert injection", tracking=True)
    rpj_methode_injectionid      = fields.Many2one("res.users", string="Méthode injection", tracking=True)
    rpj_methode_assemblageid     = fields.Many2one("res.users", string="Méthode assemblage", tracking=True)
    rpj_qualite_devid            = fields.Many2one("res.users", string="Métrologie", tracking=True)
    rpj_qualite_usineid          = fields.Many2one("res.users", string="Qualité développement", tracking=True)
    rpj_achatsid                 = fields.Many2one("res.users", string="Achats", tracking=True)
    rpj_logistiqueid             = fields.Many2one("res.users", string="Logistique", tracking=True)
    rpj_logistique_usineid       = fields.Many2one("res.users", string="Logistique Usine", tracking=True)
    rpj_commercial2id            = fields.Many2one("res.users", string="Commercial", tracking=True)
    rpj_responsable_outillageid  = fields.Many2one("res.users", string="Responsable outillage", tracking=True)
    rpj_responsable_projetid     = fields.Many2one("res.users", string="Responsable projets", tracking=True)
    rpj_directeur_siteid         = fields.Many2one("res.users", string="Directeur site de production", tracking=True)
    rpj_directeur_techniqueid    = fields.Many2one("res.users", string="Directeur technique", tracking=True)
    rpj_critere_a_risque         = fields.Text(string="Critères à risque", tracking=True)
    rpj_date_j0                  = fields.Date(string="J0", tracking=True)
    rpj_date_j1                  = fields.Date(string="J1", tracking=True)
    rpj_date_j2                  = fields.Date(string="J2", tracking=True)
    rpj_date_j3                  = fields.Date(string="J3", tracking=True)
    rpj_date_j4                  = fields.Date(string="J4", tracking=True)
    rpj_date_j5                  = fields.Date(string="J5", tracking=True)
    rpj_avancement_j0            = fields.Integer(string="Avancement J0", tracking=True)
    rpj_avancement_j1            = fields.Integer(string="Avancement J1", tracking=True)
    rpj_avancement_j2            = fields.Integer(string="Avancement J2", tracking=True)
    rpj_avancement_j3            = fields.Integer(string="Avancement J3", tracking=True)
    rpj_avancement_j4            = fields.Integer(string="Avancement J4", tracking=True)
    rpj_avancement_j5            = fields.Integer(string="Avancement J5", tracking=True)
    rpj_date_valide_j0           = fields.Date(string="Date validation J0", tracking=True)
    rpj_date_valide_j1           = fields.Date(string="Date validation J1", tracking=True)
    rpj_date_valide_j2           = fields.Date(string="Date validation J2", tracking=True)
    rpj_date_valide_j3           = fields.Date(string="Date validation J3", tracking=True)
    rpj_date_valide_j4           = fields.Date(string="Date validation J4", tracking=True)
    rpj_date_valide_j5           = fields.Date(string="Date validation J5", tracking=True)
    documents_ids                = fields.One2many("is.revue.projet.jalon.documents", "is_revue_project_jalon_id")
    rpj_point_bloquant           = fields.Integer(string="Nombre de points bloquants", tracking=True)
    rpj_point_bloquant_liste     = fields.Text(string="Liste des points bloquants", tracking=True)
    rpj_note                     = fields.Integer(string="Note finale (%)", tracking=True)
    revue_de_contrat_ids         = fields.One2many("is.revue.projet.jalon.revue.de.contrat", "is_revue_project_jalon_id")
    revue_de_projet_jalon_ids    = fields.One2many("is.revue.projet.jalon.revue.de.projet.jalon", "is_revue_project_jalon_id")
    rpj_total_vente_moule        = fields.Float(string="Total vente moule", tracking=True)
    rpj_total_achat_moule        = fields.Float(string="Total achat moule", tracking=True)
    rp_marge_brute_moule         = fields.Float(string="Marge brute moule (%)", compute='_compute_rp_marge_brute_moule', readonly=True, store=True, copy=False)
    decomposition_prix_ids       = fields.One2many("is.revue.projet.jalon.decomposition.prix", "is_revue_project_jalon_id")
    rpj_dp_ca_annuel             = fields.Float(string="CA Annuel", tracking=True)
    rpj_dp_vac                   = fields.Float(string="VAC", tracking=True)
    rpj_dp_eiv_total             = fields.Float(string="Total investissement", tracking=True)
    rpj_dp_schema_flux_vendu     = fields.Char(string="Schéma de flux vendu", tracking=True)
    dynacase_id                  = fields.Integer(string="Id Dynacase",index=True,copy=False)
    state = fields.Selection([
        ("rpj_brouillon",           "Brouillon"),
        ("rpj_directeur_technique", "Directeur Technique"),
        ("rpj_directeur_site",      "DIRECTEUR de Site"),
        ("rpj_diffuse",             "Pour Information"),
        ("rpj_valide",              "Validé"),
        ("rpj_refus",               "Refusé"),
    ], default="rpj_brouillon", string="État", tracking=True, copy=False)
    vers_brouillon_vsb           = fields.Boolean(string="Brouillon"          , compute='_compute_vsb', readonly=True, store=False)
    vers_directeur_technique_vsb = fields.Boolean(string="Directeur Technique", compute='_compute_vsb', readonly=True, store=False)
    vers_direceeur_de_site_vsb   = fields.Boolean(string="Direceeur de Site"  , compute='_compute_vsb', readonly=True, store=False)
    vers_diffuse_vsb             = fields.Boolean(string="Pour Information"   , compute='_compute_vsb', readonly=True, store=False)
    vers_valide_vsb              = fields.Boolean(string="Validé"             , compute='_compute_vsb', readonly=True, store=False)
    vers_refuse_vsb              = fields.Boolean(string="Refusé"             , compute='_compute_vsb', readonly=True, store=False)
    vers_j_suivante_vsb          = fields.Boolean(string="J suivante"         , compute='_compute_vsb', readonly=True, store=False)
    logo_rs                      = fields.Char(string="Logo RS"               , compute='_compute_logo_rs', readonly=True, store=False)
    active                       = fields.Boolean('Actif', default=True, tracking=True)



    @api.constrains('rpj_total_achat_moule')
    def rpj_total_achat_moule_constrain(self):
        for obj in self:
            if obj.rpj_total_achat_moule <= 0 and obj.state=='rpj_brouillon':
                raise ValidationError("Le champ 'Total achat moule' est obligatoire !")


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


    @api.depends('rpj_mouleid','dossierf_id')
    def _compute_rpj_chrono(self):
        for obj in self:
            rpj_indice=0
            rpj_chrono = "?"
            rpj_j = ''
            if obj.rpj_mouleid.j_actuelle or obj.dossierf_id.j_actuelle:
                rpj_j = obj.rpj_mouleid.j_actuelle or obj.dossierf_id.j_actuelle
                domain=[
                    ('rpj_mouleid','=', obj.rpj_mouleid.id),
                    ('dossierf_id','=', obj.dossierf_id.id),
                    ('rpj_j'      ,'=', rpj_j),
                ]
                docs=self.env['is.revue.projet.jalon'].search(domain, limit=1, order="rpj_indice desc")
                for doc in docs:
                    rpj_indice = int(doc.rpj_indice)
                rpj_indice+=1
                indice = ("00%s"%rpj_indice)[-2:]
                rpj_chrono = "%s-%s-%s"%(obj.rpj_mouleid.name or obj.dossierf_id.name,rpj_j, indice)
            obj.rpj_j      = rpj_j
            obj.rpj_indice = rpj_indice
            obj.rpj_chrono = rpj_chrono

  
    def actualiser_action(self):
        for obj in self:
            obj._compute_logo_rs()
            obj._compute_rp_marge_brute_moule()
            if obj.rpj_mouleid:
                if not obj.rpj_mouleid.j_actuelle:
                    obj.rpj_mouleid.j_actuelle='J0'
                if not obj.rpj_j:
                    obj.rpj_j = obj.rpj_mouleid.j_actuelle
                obj.rpj_clientid = obj.rpj_mouleid.client_id.id
                obj.rpj_rcid     = obj.rpj_mouleid.revue_contrat_id.id
                obj.rpj_rlid     = obj.rpj_mouleid.revue_lancement_id.id
                obj.rpj_rrid     = obj.rpj_mouleid.revue_risque_id.id
            if obj.dossierf_id:
                if not obj.dossierf_id.j_actuelle:
                    obj.dossierf_id.j_actuelle='J0'
                if not obj.rpj_j:
                    obj.rpj_j = obj.dossierf_id.j_actuelle
                obj.rpj_clientid = obj.dossierf_id.client_id.id
                obj.rpj_rcid     = obj.dossierf_id.revue_contrat_id.id
                obj.rpj_rlid     = obj.dossierf_id.revue_lancement_id.id
                obj.rpj_rrid     = obj.dossierf_id.revue_risque_id.id
            #obj._compute_rpj_chrono()



            #** Equipe projet *************************************************
            if not obj.equipe_projet_ids:
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
                        vals={
                            'rpj_equipe_projet_fonction': equipe_projet_fonction[k],
                            'rpj_equipe_projet_nomid'   : nomid,
                        }
                        equipe_projet_ids.append([0,False,vals])
                    obj.equipe_projet_ids=equipe_projet_ids
            #******************************************************************

            #** Planning ******************************************************
            if obj.rpj_rlid:
                obj.rpj_date_j0 = obj.rpj_rlid.rl_date_j0
                obj.rpj_date_j1 = obj.rpj_rlid.rl_date_j1
                obj.rpj_date_j2 = obj.rpj_rlid.rl_date_j2
                obj.rpj_date_j3 = obj.rpj_rlid.rl_date_j3
                obj.rpj_date_j4 = obj.rpj_rlid.rl_date_j4
                obj.rpj_date_j5 = obj.rpj_rlid.rl_date_j5
            #******************************************************************

            #** Recherche des documents du modèle de la J**********************
            obj.documents_ids=False
            line_ids={}
            J = obj.rpj_j
            if J:
                domain=[
                    ('mb_titre','=' , J),
                ]
                modeles=self.env['is.modele.bilan'].search(domain,limit=1)
                for modele in modeles:
                    for line in modele.line_ids:
                        domain=[
                            ('idmoule'         ,'=', obj.rpj_mouleid.id),
                            ('dossierf_id'     ,'=', obj.dossierf_id.id),
                            ('param_project_id','=', line.param_project_id.id),
                            ('suivi_projet'    ,'=', True),
                        ]
                        docs=self.env['is.doc.moule'].search(domain,limit=1)
                        doc=False
                        for d in docs:
                            doc=d
                        line_ids[line.param_project_id]=doc

            #** Recherche de tous les documents à faire ***********************
            domain=[
                ('idmoule'     ,'=' , obj.rpj_mouleid.id),
                ('dossierf_id' ,'=' , obj.dossierf_id.id),
                ('etat'        ,'in', ['AF','D']),
                ('action'      ,'!=', False),
                ('suivi_projet','=' , True),
            ]
            docs=self.env['is.doc.moule'].search(domain)
            for doc in docs:
                line_ids[doc.param_project_id]=doc
            #******************************************************************

            documents_ids=[]
            rpj_point_bloquant=coefficient=note=rpj_note=0
            rpj_point_bloquant_liste=[]
            for param_project_id in line_ids:
                doc = line_ids[param_project_id]
                if doc:
                    coefficient+=doc.coefficient
                    note+=doc.note
                    if doc.bloquant and doc.etat!='F':
                        rpj_point_bloquant+=1
                        rpj_point_bloquant_liste.append(param_project_id.ppr_famille)
                vals={
                    'rpj_doc_document'  : param_project_id.ppr_famille,
                    'rpj_doc_documentid': doc and doc.id,
                    'rpj_doc_action'    : doc and doc.action,
                    'rpj_doc_bloquant'  : doc and doc.bloquant,
                    'rpj_doc_respid'    : doc and doc.idresp.id,
                    'rpj_doc_etat'      : doc and doc.etat,
                    'rpj_doc_coeff'     : doc and doc.coefficient,
                    'rpj_doc_note'      : doc and doc.note,
                }
                documents_ids.append([0,False,vals])     
            rpj_note
            if coefficient>0:
                rpj_note = round(100*note/coefficient)
            obj.documents_ids      = documents_ids
            obj.rpj_point_bloquant = rpj_point_bloquant
            obj.rpj_point_bloquant_liste = '\n'.join(rpj_point_bloquant_liste)
            obj.rpj_note           = rpj_note
            #******************************************************************

            #** Date Planning J ***********************************************
            if obj.rpj_rlid:
                j_actuelle=(obj.rpj_j or '').lower()
                name =  'rl_date_%s'%j_actuelle
                date_planning_j = getattr(obj.rpj_rlid,name)
                obj.rpj_date_planning_j = date_planning_j
            #******************************************************************

            #** Niveau de PPM *************************************************
            rpj_niveau_ppm=0
            if obj.rpj_rcid:
                if obj.rpj_rcid.rc_type_automobile=='Oui':
                    rpj_niveau_ppm = obj.rpj_rcid.rc_edl_at_n_ppm
                else:
                    rpj_niveau_ppm = obj.rpj_rcid.rc_edl_n_at_n_ppm
            obj.rpj_niveau_ppm = rpj_niveau_ppm
            #******************************************************************

            #** Revue de contrat - Suivi des données économiques **************
            obj.revue_de_contrat_ids=False
            revue_de_contrat_ids=[]
            if obj.rpj_rcid:
                for line in obj.rpj_rcid.version_ids:
                    vals={
                        'rpj_de1_article': line.rc_dfi_article,
                        'rpj_de1_cycle': line.rc_dfi_cycle,
                        'rpj_de1_nb_emp': line.rc_dfi_nb_emp,
                        'rpj_de1_mod': line.rc_dfi_mod,
                        'rpj_de1_taux_rebut': line.rc_dfi_taux_rebut,
                        'rpj_de1_poids_piece': line.rc_dfi_poids_piece,
                        'rpj_de1_poids_carotte': line.rc_dfi_poids_carotte,
                    }
                    revue_de_contrat_ids.append([0,False,vals])     
            obj.revue_de_contrat_ids = revue_de_contrat_ids
            if obj.rpj_rcid and not obj.revue_de_projet_jalon_ids:
                revue_de_projet_jalon_ids=[]
                for line in obj.rpj_rcid.version_ids:
                    vals={
                        'rpj_de2_article': line.rc_dfi_article,
                    }
                    revue_de_projet_jalon_ids.append([0,False,vals])     
                obj.revue_de_projet_jalon_ids = revue_de_projet_jalon_ids
            #******************************************************************

            #** Decomposition prix revue de contrat ***************************
            obj.decomposition_prix_ids=False
            decomposition_prix_ids=[]
            rpj_dp_ca_annuel = rpj_dp_vac = rpj_dp_eiv_total = rpj_dp_schema_flux_vendu = False
            if obj.rpj_rcid:
                rpj_dp_ca_annuel         = obj.rpj_rcid.rc_ca_annuel
                rpj_dp_vac               = obj.rpj_rcid.rc_vac
                rpj_dp_eiv_total         = obj.rpj_rcid.rc_eiv_total
                rpj_dp_schema_flux_vendu = obj.rpj_rcid.rc_dfi_schema_lieu_fab
                for line in obj.rpj_rcid.decomposition_prix_ids:
                    prix_piece = line.rc_sell_price - line.rc_preserie_surcout
                    vals={
                        'rpj_dp_article': line.rc_price_comp_article,
                        'rpj_dp_qt_annuelle': line.rc_year_quantity,
                        'rpj_dp_part_matiere': line.rc_mat_part,
                        'rpj_dp_part_composant': line.rc_comp_part,
                        'rpj_dp_part_emballage': line.rc_emb_part,
                        'rpj_dp_va_injection': line.rc_va_injection,
                        'rpj_dp_va_assemblage': line.rc_va_assembly,
                        'rpj_dp_frais_port': line.rc_port_fee,
                        'rpj_dp_logistique': line.rc_logistic,
                        'rpj_dp_amt_moule': line.rc_moul_amort,
                        'rpj_dp_prix_piece': prix_piece,
                     }
                    decomposition_prix_ids.append([0,False,vals])     
            obj.decomposition_prix_ids   = decomposition_prix_ids
            obj.rpj_dp_ca_annuel         = rpj_dp_ca_annuel
            obj.rpj_dp_vac               = rpj_dp_vac
            obj.rpj_dp_eiv_total         = rpj_dp_eiv_total
            obj.rpj_dp_schema_flux_vendu = rpj_dp_schema_flux_vendu
            #******************************************************************

            #** Revue de lancement ********************************************
            rl_lieu_production = rl_affectation_presse = False
            if  obj.rpj_rlid:
                rl_lieu_production = obj.rpj_rlid.rl_lieu_production
                rl_affectation_presse = obj.rpj_rlid.rl_affectation_presse
            obj.rpj_lieu_production = rl_lieu_production
            obj.rpj_affectation_presse = rl_affectation_presse
            #******************************************************************

            #** Revue des risquee *********************************************
            obj.bilan_ids=False
            bilan_ids=[]
            rpj_dp_ca_annuel = rpj_dp_vac = rpj_dp_eiv_total = rpj_dp_schema_flux_vendu = False
            if obj.rpj_rrid:
                for line in obj.rpj_rrid.rr_bilan_ar:
                    vals={
                        'rpj_bilan_risque_j': line.rr_bilan_risque_j,
                        'rpj_bilan_risque_design': line.rr_bilan_risque_design,
                        'rpj_bilan_risque_supply_chain': line.rr_bilan_risque_supply_chain,
                        'rpj_bilan_risque_qualite': line.rr_bilan_risque_qualite,
                        'rpj_bilan_risque_leadership': line.rr_bilan_risque_leadership,
                     }
                    bilan_ids.append([0,False,vals])     
            obj.bilan_ids   = bilan_ids
            #******************************************************************

            #** Recherche des investissements *********************************
            rpj_total_vente_moule = 0
            if obj.rpj_mouleid.id:
                domain=[
                    ('num_mouleid','=' , obj.rpj_mouleid.id),
                ]
                docs=self.env['is.inv.achat.moule'].search(domain)
                for doc in docs:
                    rpj_total_vente_moule+=doc.montant_vendu
            obj.rpj_total_vente_moule = rpj_total_vente_moule
            #******************************************************************


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
    ], string="Présence", copy=False)
    is_revue_project_jalon_id  = fields.Many2one("is.revue.projet.jalon")


class is_revue_projet_jalon_documents(models.Model):
    _name        = "is.revue.projet.jalon.documents"
    _description = "Compte-rendu revue de projet jalon Bilan - Documents"
    _rec_name    = "rpj_doc_documentid"

    rpj_doc_document          = fields.Char(string="Document")
    rpj_doc_documentid        = fields.Many2one("is.doc.moule", string="Famille Document")
    rpj_doc_action            = fields.Selection(DOCUMENT_ACTION, string="Action")
    rpj_doc_etat              = fields.Selection(DOCUMENT_ETAT, string="État")
    rpj_doc_bloquant          = fields.Boolean(string="Point bloquant", default=False)
    rpj_doc_respid            = fields.Many2one("res.users", string="Responsable")
    rpj_doc_coeff             = fields.Integer(string="Coefficient")
    rpj_doc_note              = fields.Integer(string="Note")
    is_revue_project_jalon_id = fields.Many2one("is.revue.projet.jalon")


    def acceder_doc_action(self):
        for obj in self:
            form_id = obj.rpj_doc_documentid.get_form_view_id()
            res= {
                'name': 'Doc',
                'view_mode': 'form',
                "views"    : [
                    (form_id, "form")
                ],
                'res_model': 'is.doc.moule',
                'res_id': obj.rpj_doc_documentid.id,
                'type': 'ir.actions.act_window',
            }
            return res




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
    rpj_dp_part_matiere       = fields.Float(string="Part matière"       , digits=(12, 6))
    rpj_dp_part_composant     = fields.Float(string="Part composant"     , digits=(12, 6))
    rpj_dp_part_emballage     = fields.Float(string="Part emballage"     , digits=(12, 6))
    rpj_dp_va_injection       = fields.Float(string="VA injection"       , digits=(12, 6))
    rpj_dp_va_assemblage      = fields.Float(string="VA assemblage"      , digits=(12, 6))
    rpj_dp_frais_port         = fields.Float(string="Frais port"         , digits=(12, 6))
    rpj_dp_logistique         = fields.Float(string="Logistique"         , digits=(12, 6))
    rpj_dp_amt_moule          = fields.Float(string="Amortissement moule", digits=(12, 6))
    rpj_dp_prix_piece         = fields.Float(string="Prix pièce"         , digits=(12, 6))
    is_revue_project_jalon_id = fields.Many2one("is.revue.projet.jalon")
