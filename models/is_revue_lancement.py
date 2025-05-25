# -*- coding: utf-8 -*-
from odoo import models, fields, api, _       # type: ignore
from odoo.exceptions import ValidationError   # type: ignore


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
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = "Revue de lancement"


    def compute_xml_rpc(self):
        for obj in self:
            obj._compute_rl_be_total()
            obj._compute_rc()
            obj._compute_name()
        return True


    @api.depends("rl_be01", "rl_be01b", "rl_be01c", "rl_be02", "rl_be03", "rl_be04", "rl_be05", "rl_be06", "rl_be07",
                "rl_be09", "rl_be10", "rl_be11", "rl_be12", "rl_be13", "rl_be14", "rl_be15", "rl_be16", "rl_be17")
    def _compute_rl_be_total(self):
        for record in self:
            total = record.rl_be01 + record.rl_be01b +  record.rl_be01c + record.rl_be02 + record.rl_be03 + \
                                record.rl_be04 + record.rl_be05 + record.rl_be06 + record.rl_be07 + record.rl_be09 + \
                                record.rl_be10 + record.rl_be11 + record.rl_be12 + record.rl_be13 + record.rl_be14 + \
                                record.rl_be15 + record.rl_be16 + record.rl_be17
            record.rl_be_total = total
            record.ecart = record.rl_pgrc_total - total


    @api.depends("rl_num_rcid","rl_num_rcid.rc_designation","rl_num_rcid.rc_client","rl_num_rcid.rc_projetid","rl_num_rcid.rc_commercial","dossierf_id")
    def _compute_rc(self):
        for obj in self:
            obj.rl_designation_rc  = obj.rl_num_rcid.rc_designation
            obj.rl_client_rcid     = obj.rl_num_rcid.rc_client     or obj.dossierf_id.client_id.id
            obj.rl_projet_rcid     = obj.rl_num_rcid.rc_projetid   or obj.dossierf_id.project.id
            obj.rl_commercial_rcid = obj.rl_num_rcid.rc_commercial or obj.dossierf_id.client_id.user_id.id


    @api.depends("rl_mouleid","rl_dossierfid","rl_indice","dossierf_id")
    def _compute_name(self):
        for obj in self:
            name="x"
            if obj.rl_mouleid:
                name = obj.rl_mouleid.name
            if obj.rl_dossierfid:
                name = obj.rl_dossierfid.name
            if obj.dossierf_id:
                name = obj.dossierf_id.name
            obj.name='RL-%s-%s'%(name,obj.rl_indice)


    name                              = fields.Char(string="N°", compute="_compute_name", store=True, readonly=True)
    rl_num_rcid                       = fields.Many2one("is.revue.de.contrat", string="Revue de contrat", required=False, tracking=True)
    dossierf_id                       = fields.Many2one("is.dossierf", string="Dossier F", tracking=True)
    rl_mouleid                        = fields.Many2one(related='rl_num_rcid.rc_mouleid')
    rl_dossierfid                     = fields.Many2one(related='rl_num_rcid.rc_dossierfid', string="Dossier F RC")
    rl_title                          = fields.Char(string="Revue de lancement (champ à supprimer)", tracking=True)
    rl_indice                         = fields.Integer(string="Indice", tracking=True, readonly=True, default=0, required=True)
    rl_designation_rc                 = fields.Char(string="Désignation"                  , tracking=True, compute="_compute_rc", store=True, readonly=True)
    rl_client_rcid                    = fields.Many2one("res.partner", string="Client"    , tracking=True, compute="_compute_rc", store=True, readonly=True)
    rl_projet_rcid                    = fields.Many2one("is.mold.project", string="Projet", tracking=True, compute="_compute_rc", store=True, readonly=True)
    rl_commercial_rcid                = fields.Many2one("res.users", string="Commercial"  , tracking=True, compute="_compute_rc", store=True, readonly=True)
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

    cmd_date                          = fields.Date(string="Date de la commande"        , tracking=True, readonly=True)
    dfn_ro_date                       = fields.Date(string="Date de la DFN RO"          , tracking=True, readonly=True)
    first_m_try                       = fields.Date(string="Date 1er essai moule (IOD) ", tracking=True, readonly=True)
    ei_pres                           = fields.Date(string="Date Présentation EI"       , tracking=True, readonly=True)
    dms_date                          = fields.Date(string="Date DMS"                   , tracking=True, readonly=True)
    eop_date                          = fields.Date(string="Date EOP (Fin de vie)"      , tracking=True, readonly=True)

    rl_date_j0                        = fields.Date(string="Date J0", tracking=True)
    rl_date_j1                        = fields.Date(string="Date J1", tracking=True)
    rl_date_j2                        = fields.Date(string="Date J2", tracking=True)
    rl_date_j3                        = fields.Date(string="Date J3", tracking=True)
    rl_date_j4                        = fields.Date(string="Date J4", tracking=True)
    rl_date_j5                        = fields.Date(string="Date J5", tracking=True)

    rl_pgrc_moule_mnt                 = fields.Float(string="Moule.", readonly=True)
    rl_pgrc_moule_cmt                 = fields.Char(string="Commentaire", readonly=True)
    rl_pgrc_etude_mnt                 = fields.Float(string="Etude", readonly=True)
    rl_pgrc_etude_cmt                 = fields.Char(string="Commentaire 1", readonly=True)
    rl_pgrc_main_prehension_mnt       = fields.Float(string="Main de préhension", readonly=True)
    rl_pgrc_main_prehension_cmt       = fields.Char(string="Commentaire  2", readonly=True)
    rl_pgrc_barre_chaude_mnt          = fields.Float(string="Barre chaude", readonly=True)
    rl_pgrc_barre_chaude_cmt          = fields.Char(string="Commentaire 3", readonly=True)
    rl_pgrc_gabarit_controle_mnt      = fields.Float(string="Gabarit de contrôle", readonly=True)
    rl_pgrc_gabarit_controle_cmt      = fields.Char(string="Commentaire 4", readonly=True)
    rl_pgrc_machine_speciale_mnt      = fields.Float(string="Machine spéciale", readonly=True)
    rl_pgrc_machine_speciale_cmt      = fields.Char(string="Commentaire 5", readonly=True)
    rl_pgrc_plan_validation_mnt       = fields.Float(string="Plan de validation", readonly=True)
    rl_pgrc_plan_validation_cmt       = fields.Char(string="Commentaire 6", readonly=True)
    rl_pgrc_mise_point_mnt            = fields.Float(string="Mise au point", readonly=True)
    rl_pgrc_mise_point_cmt            = fields.Char(string="Commentaire 7", readonly=True)
    rl_pgrc_packaging_mnt             = fields.Float(string="Packaging", readonly=True)
    rl_pgrc_packaging_cmt             = fields.Char(string="Commentaire 8", readonly=True)
    rl_pgrc_amort_mnt                 = fields.Float(string="Amortissement", readonly=True)
    rl_pgrc_amort_cmt                 = fields.Char(string="Commentaire 9", readonly=True)
    rl_pgrc_total                     = fields.Float(string="Total RC", readonly=True)


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
    rl_be_total                       = fields.Float(string="Total RL", compute="_compute_rl_be_total", store=True)
    ecart                             = fields.Float(string="Ecart"   , compute="_compute_rl_be_total", store=True)
    rl_annee_inv                      = fields.Char(string="Année d'enregistrement des investissements", size=4, tracking=True)


    rl_be01_id   = fields.Many2one("is.inv.achat.moule", string="BE01a: Nouveau moule/ Moule transféré", tracking=True,copy=False,readonly=True)
    rl_be01b_id  = fields.Many2one("is.inv.achat.moule", string="BE01b: Grainage", tracking=True,copy=False,readonly=True)
    rl_be01c_id  = fields.Many2one("is.inv.achat.moule", string="BE01c: Barre chaude", tracking=True,copy=False,readonly=True)
    rl_be02_id   = fields.Many2one("is.inv.achat.moule", string="BE02: Etude, CAO, Rhéologie" , tracking=True,copy=False,readonly=True)
    rl_be03_id   = fields.Many2one("is.inv.achat.moule", string="BE03: Prototype" , tracking=True,copy=False,readonly=True)
    rl_be04_id   = fields.Many2one("is.inv.achat.moule", string="BE04: Main de préhension" , tracking=True,copy=False,readonly=True)
    rl_be05_id   = fields.Many2one("is.inv.achat.moule", string="BE05: Gabarit de contrôle" , tracking=True,copy=False,readonly=True)
    rl_be06_id   = fields.Many2one("is.inv.achat.moule", string="BE06: Mise au point" , tracking=True,copy=False,readonly=True)
    rl_be07_id   = fields.Many2one("is.inv.achat.moule", string="BE07: Test" , tracking=True,copy=False,readonly=True)
    rl_be09_id   = fields.Many2one("is.inv.achat.moule", string="BE09: Essais + divers" , tracking=True,copy=False,readonly=True)
    rl_be10_id   = fields.Many2one("is.inv.achat.moule", string="BE10: Métrologie" , tracking=True,copy=False,readonly=True)
    rl_be11_id   = fields.Many2one("is.inv.achat.moule", string="BE11: Transports" , tracking=True,copy=False,readonly=True)
    rl_be12_id   = fields.Many2one("is.inv.achat.moule", string="BE12: Etude/Developpement Packaging" , tracking=True,copy=False,readonly=True)
    rl_be13_id   = fields.Many2one("is.inv.achat.moule", string="BE13: Poste d'assemblage" , tracking=True,copy=False,readonly=True)
    rl_be14_id   = fields.Many2one("is.inv.achat.moule", string="BE14: Developpement outillages divers ( découpe...)" , tracking=True,copy=False,readonly=True)
    rl_be15_id   = fields.Many2one("is.inv.achat.moule", string="BE15: Achat matière" , tracking=True,copy=False,readonly=True)
    rl_be16_id   = fields.Many2one("is.inv.achat.moule", string="BE16: Achat composants" , tracking=True,copy=False,readonly=True)
    rl_be17_id   = fields.Many2one("is.inv.achat.moule", string="BE17: Essai injection" , tracking=True,copy=False,readonly=True)



    state                             = fields.Selection([
        ("rl_brouillon",  "Brouillon"),
        ("rl_diffuse",    "Diffusé"),
    ], string="État", tracking=True, default="rl_brouillon")
    dynacase_id = fields.Integer(string="Id Dynacase",index=True,copy=False)
    active      = fields.Boolean('Actif', default=True, tracking=True)


    @api.constrains('rl_num_rcid', 'dossierf_id')
    def _rl_num_rcid_dossierf_id_constrain(self):
        for obj in self:
            if obj.rl_num_rcid.id and obj.dossierf_id.id:
                raise ValidationError("Il ne faut pas saisir une revue de contrat et un dossier F en même temps")


    # def write(self,vals):
    #     res=super().write(vals)
    #     self._rl_unique()
    #     # for obj in self:
    #     #     if obj.rl_pgrc_total != obj.rl_be_total:
    #     #         raise ValidationError("Total moule et revue de lancement différent !")
    #     return res


    def dupliquer_rl_action(self):
        for obj in self:
            copy=obj.copy()
            res= {
                'name': 'Copie',
                'view_mode': 'form',
                'res_model': 'is.revue.lancement',
                'res_id': copy.id,
                'type': 'ir.actions.act_window',
            }
            return res


    def copy(self, default=None):
        for obj in self:
            default = dict(default or {})
            default['rl_indice']=obj.rl_indice+1
            #** Recherche de la dernière revue de contrat validée *************
            domain=[
                ('rc_mouleid'   , '=', obj.rl_mouleid.id), 
                ('rc_dossierfid', '=', obj.rl_dossierfid.id), 
                ('state'        , '=', 'diffuse'), 
            ]
            lines = self.env['is.revue.de.contrat'].search(domain,order='rc_indice desc',limit=1)
            for line in lines:
                default['rl_num_rcid']=line.id
            #******************************************************************
            res=super().copy(default=default)
            return res


    @api.constrains('rl_num_rcid', 'rl_indice')
    def _rl_unique(self):
        for obj in self:
            domain=[
                ('rl_mouleid'   , '=', obj.rl_mouleid.id), 
                ('rl_dossierfid', '=', obj.rl_dossierfid.id), 
                ('rl_indice'    , '=', obj.rl_indice), 
            ]
            lines = self.env['is.revue.lancement'].search(domain)
            if len(lines) > 1:
                raise ValidationError("Cette revue de lancement existe déjà %s %s indice %s !"%( obj.rl_mouleid.name or '', obj.rl_dossierfid.name or '',obj.rl_indice))


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
            dossierf_id = obj.rl_num_rcid.rc_dossierfid.id or obj.dossierf_id.id
            domain=False
            if moule_id:
                domain=[('idmoule', '=', moule_id)]
            if dossierf_id:
                domain=[('dossierf_id', '=', dossierf_id)]
            if domain:
                docs = self.env['is.doc.moule'].search(domain)
                for doc in docs:
                    ppr_responsable = doc.param_project_id.ppr_responsable
                    if ppr_responsable:
                        responsable = _RESPONSABLES.get(ppr_responsable)          
                        if hasattr(obj, responsable):
                            user = getattr(obj,responsable)
                            if user:
                                doc.idresp = user.id



    def voir_investissements_action(self):
        for obj in self:
            res = {
                'name': 'RL',
                'view_mode': 'tree,form',
                'res_model': 'is.inv.achat.moule',
                'domain': [
                    ('revue_lancementid','=',obj.id),
                ],
                'type': 'ir.actions.act_window',
                'limit': 1000,
            }
            return res
        

    def copie_rc_action(self):
        for obj in self:
            rc = obj.rl_num_rcid
            obj.rl_pgrc_moule_mnt  = rc.rc_eiv_moule
            obj.rl_pgrc_moule_cmt  = rc.rc_eiv_moule_cmt
            obj.rl_pgrc_etude_mnt  = rc.rc_eiv_etude
            obj.rl_pgrc_etude_cmt  = rc.rc_eiv_etude_cmt
            obj.rl_pgrc_main_prehension_mnt  = rc.rc_eiv_main_prehension
            obj.rl_pgrc_main_prehension_cmt  = rc.rc_eiv_main_prehension_cmt
            obj.rl_pgrc_barre_chaude_mnt     = rc.rc_eiv_barre_chaude
            obj.rl_pgrc_barre_chaude_cmt     = rc.rc_eiv_barre_chaude_cmt
            obj.rl_pgrc_gabarit_controle_mnt = rc.rc_eiv_gab_controle
            obj.rl_pgrc_gabarit_controle_cmt = rc.rc_eiv_gab_controle_cmt
            obj.rl_pgrc_machine_speciale_mnt = rc.rc_eiv_mach_spec
            obj.rl_pgrc_machine_speciale_cmt = rc.rc_eiv_mach_spec_cmt
            obj.rl_pgrc_plan_validation_mnt  = rc.rc_eiv_plan_valid
            obj.rl_pgrc_plan_validation_cmt  = rc.rc_eiv_plan_valid_cmt
            obj.rl_pgrc_mise_point_mnt       = rc.rc_eiv_mis_point
            obj.rl_pgrc_mise_point_cmt       = rc.rc_eiv_mis_point_cmt
            obj.rl_pgrc_packaging_mnt        = rc.rc_eiv_pack
            obj.rl_pgrc_packaging_cmt        = rc.rc_eiv_pack_cmt
            obj.rl_pgrc_amort_mnt            = rc.rc_eiv_amort
            obj.rl_pgrc_amort_cmt            = rc.rc_eiv_amort_cmt
            obj.rl_pgrc_total                = rc.rc_eiv_total
            obj.copie_dates_rc_action()


    def creation_inv_achat_moule(self):
        tab=[
            "be01",
            "be01b",
            "be01c",
            "be02",
            "be03",
            "be04",
            "be05",
            "be06",
            "be07",
            "be09",
            "be10",
            "be11",
            "be12",
            "be13",
            "be14",
            "be15",
            "be16",
            "be17"
        ] 
        for obj in self:
            for key in tab:
                field_name="rl_%s"%key
                val = getattr(obj,field_name)
                vals={
                    'num_mouleid': obj.rl_mouleid.id,
                    'revue_lancementid': obj.id,
                    'clientid': obj.rl_client_rcid.id,
                    'projetid': obj.rl_projet_rcid.id,
                    'chef_projetid': obj.rl_chef_projetid.id,
                    'annee_enregistre': obj.rl_annee_inv,
                    'code_imputation': key,
                    'montant_vendu': val,
                }
                field_name = "rl_%s_id"%key
                doc = getattr(obj,field_name)
                if doc:
                    doc.write(vals) 
                else:
                    if val>0:
                        doc = self.env['is.inv.achat.moule'].create(vals)
                        setattr(obj, field_name, doc.id)


    def compute_project_prev(self):
        "for xml-rpc"
        self.update_j_prevue_action()
        self._compute_project_prev()
        self._compute_idproject_moule_dossierf()
        self._compute_site_id()
        self._compute_demao_nature()
        self._compute_solde()
        self._compute_actuelle()
        self._compute_rsp_pj()
        self._compute_coefficient_bloquant_note()
        self._compute_color()
        self._compute_indicateur()
        return True


    def copie_dates_rc_action(self):
        for obj in self:
            rc = obj.rl_num_rcid
            if rc:
               obj.cmd_date    = rc.rc_cmd_date
               obj.dfn_ro_date = rc.rc_dfn_ro_date
               obj.first_m_try = rc.rc_first_m_try
               obj.ei_pres     = rc.rc_ei_pres
               obj.dms_date    = rc.rc_dms_date
               obj.eop_date    = rc.rc_eop_date


    def action_vers_brouillon(self):
        for obj in self:
            obj.state = "rl_brouillon"


    def action_vers_diffuse(self):
        self.creation_inv_achat_moule()
        for obj in self:
            if obj.rl_pgrc_total != obj.rl_be_total:
                raise ValidationError("Le total des données du moule et de la revue de lancement n'est pas le même !")
            obj.state = "rl_diffuse"            
            obj.envoi_mail()
            if obj.rl_mouleid:
                obj.sudo().rl_mouleid.revue_lancement_id = obj.id
            if obj.rl_dossierfid:
                obj.sudo().rl_dossierfid.revue_lancement_id = obj.id


    def get_state_name(self):
        for obj in self:
            return dict(self._fields['state'].selection).get(self.state)


    def get_doc_url(self):
        for obj in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = base_url + '/web#id=%s' '&view_type=form&model=%s'%(obj.id,self._name)
            return url


    def get_users(self):
        for obj in self:
            equipe=[
                "rl_chef_projetid", 
                "rl_methode_injectionid", 
                "rl_methode_assemblageid", 
                "rl_qualite_devid", 
                "rl_qualite_usineid", 
                "rl_achatsid", 
                "rl_logistiqueid", 
                "rl_commercial2id",
                "rl_responsable_outillageid",
                "rl_directeur_siteid",
                "rl_directeur_techniqueid",
            ]
            users=[]
            for key in equipe:
                user = getattr(obj,key)
                if user and user not in users:
                    users.append(user)
            return users

   
    def get_destinataires_name(self):
        for obj in self:
            users = obj.get_users()
            if users:
                mydict=[]
                for user in users:
                    if user.email and user.email not in mydict:
                        name=user.email
                        mydict.append(name)
                destinataires_name=', '.join(mydict)
            return destinataires_name


    def get_partners_ids(self):
        for obj in self:
            partners_ids=False
            users = obj.get_users()
            if users:
                partners_ids=[]
                for user in users:
                    partners_ids.append(user.partner_id.id)
            return partners_ids


    def get_copie(self):
        return self.env['is.liste.diffusion.mail'].get_destinataires_name('is.revue.lancement','cc')


    def envoi_mail(self):
        template = self.env.ref('is_dynacase2odoo.is_revue_lancement_mail_template').sudo()     
        email_values = {
            'email_cc'      : self.get_copie(),
            'auto_delete'   : False,
            'recipient_ids' : self.get_partners_ids(),
            'scheduled_date': False,
        }
        template.send_mail(self.id, force_send=True, raise_exception=False, email_values=email_values)

