# -*- coding: utf-8 -*-
from odoo import models,fields,api  # type: ignore
from datetime import datetime, timedelta, date


_DAO_RSPLAST=([
    ('A', 'A=Acceptée'),
    ('D', 'D=Déclinée'),
])


_DAO_MOTIF=([
    ('P01', 'Perdu - Prix moule & pièce'),
    ('P02', 'Perdu - Prix moule'),
    ('P03', 'Perdu - Prix pièce'),
    ('P04', 'Perdu - Délai trop long'),
    ('P05', 'Perdu - Projet client annulé'),
    ('P06', 'Perdu - Pas de retour client'),
    ('P07', 'Perdu - Choix stratégique client'),
    ('D01', 'Décliné - Motif technique (process ou techno)'),
    ('D02', 'Décliné - Capacitaire PG'),
    ('D03', 'Décliné - Volume faible'),
    ('D04', 'Décliné - Stratégique'),
])


_DAO_AVANCEMENT=([
    ('Développement', 'Développement'),
    ('Série'        , 'Série'),
])


_STATE=([
    ('plascreate'     , 'Créé'),
    ('plasanalysed'   , 'Analysé'),
    ('plastransbe'    , 'Transmis BE'),
    ('Analyse_BE'     , 'Analysé BE'),
    ('plasvalidbe'    , 'Validé BE'),
    ('plasvalidcom'   , 'Validé commercial'),
    ('plasdiffusedcli', 'Diffusé client'),
    ('plasrelancecli' , 'Relance client'),
    ('plaswinned'     , 'Gagné'),
    ('plasloosed'     , 'Perdu'),
    ('plascancelled'  , 'Annulé'),
])


_OFFRE_DECROCHEE=([
    ('oui', 'Oui'),
    ('non', 'Non'),
])


class is_dossier_appel_offre(models.Model):
    _name = "is.dossier.appel.offre"
    _inherit=['mail.thread']
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="is_dossier_appel_offre"
    _order = "dao_date desc"
    _rec_name = 'dao_num'


    @api.depends('dao_date')
    def _compute_dao_annee(self):
        for obj in self:
            annee = False
            if obj.dao_date:
                annee = obj.dao_date.year
            obj.dao_annee = annee


    @api.depends('client_id','prospect')
    def _compute_dao_typeclient(self):
        for obj in self:
            type_client=False

            if obj.prospect:
                type_client='Prospect'   
            if obj.client_id:
                type_client='Client'
            obj.dao_typeclient = type_client


    @api.depends('client_id')
    def _compute_secteur_activite(self):
        for obj in self:
            obj.secteur_activite = obj.client_id.is_secteur_activite.id
            obj.commercial_id    = obj.client_id.user_id.id


    @api.depends('dao_ca','dao_vacom')
    def _compute_dao_pourcentva(self):
        for obj in self:
            val=False
            if obj.dao_ca>0:
                val = round(100 * obj.dao_vacom / obj.dao_ca)
            obj.dao_pourcentva = val


    @api.model
    def default_get(self, default_fields):
        user    = self.env["res.users"].browse(self._uid)
        company = user.company_id
        user_id = company.is_directeur_technique_id.id

        res = super(is_dossier_appel_offre, self).default_get(default_fields)
        res.update({
            'chef_projet_id'        : user_id,
            'directeur_technique_id': user_id,
        })
        return res


    dao_num          = fields.Char("Numéro"                           , tracking=True, readonly=True, copy=False)
    dao_date         = fields.Date("Date consultation"                , tracking=True, default=fields.Date.context_today,required=True, copy=False)
    dao_annee        = fields.Char("Année consultation"               , tracking=True, compute="_compute_dao_annee",store=True, readonly=True)
    client_id        = fields.Many2one("res.partner", string="Client" , tracking=True, domain=[("is_company","=",True), ("customer","=",True)])
    prospect         = fields.Char("Prospect / Suspect"               , tracking=True)
    dao_typeclient   = fields.Char("Type client"                      , tracking=True, compute="_compute_dao_typeclient",store=True, readonly=True)
    #dao_sectclient  = fields.Char("Section client"                   , tracking=True)
    secteur_activite = fields.Many2one('is.secteur.activite', "Secteur d'activité", tracking=True, compute="_compute_secteur_activite",store=True, readonly=False)
    commercial_id    = fields.Many2one("res.users", string="Commercial"           , tracking=True, compute="_compute_secteur_activite",store=True, readonly=False)
    #dao_commercial  = fields.Char("Commercial"                       , tracking=True)
    dao_desig        = fields.Char("Désignation"                      , tracking=True)
    dao_ref          = fields.Char("Référence"                        , tracking=True)
    dao_datedms      = fields.Date("Date DMS"                         , tracking=True)
    dao_ca           = fields.Float("Chiffre d'affaire"               , tracking=True)
    dao_vacom        = fields.Float("VA commerciale"                  , tracking=True)
    dao_pourcentva   = fields.Integer("% VA"                          , tracking=True, compute="_compute_dao_pourcentva",store=True, readonly=True)
    dao_camoule      = fields.Float("CA Moule"                        , tracking=True)
    #dao_be                = fields.Char("Chef de projet"                   , tracking=True)
    #dao_dirbe             = fields.Char("Directeur technique"              , tracking=True)
    chef_projet_id         = fields.Many2one("res.users", string="Chef de projet"     , tracking=True)
    directeur_technique_id = fields.Many2one("res.users", string="Directeur technique", tracking=True)
    dao_daterepbe          = fields.Date("Date réponse BE souhaitée"        , tracking=True)
    dao_daterepplast       = fields.Date("Date réponse Plastigray"          , tracking=True)
    dao_daterepcli         = fields.Date("Date réponse client"              , tracking=True)
    dao_date_relance       = fields.Date("Date de relance"                , tracking=True)
    dao_comment            = fields.Char("Commentaire"                      , tracking=True)
    dao_offre_decrochee    = fields.Selection(_OFFRE_DECROCHEE, "Offre décrochée", tracking=True)
    dao_rsplast            = fields.Selection(_DAO_RSPLAST, "Rsp Plastigray", tracking=True)
    dao_motif              = fields.Selection(_DAO_MOTIF, "Motif"           , tracking=True)
    dao_avancement         = fields.Selection(_DAO_AVANCEMENT, "Avancement" , tracking=True)
    state                  = fields.Selection(_STATE, "Etat"                , tracking=True, default='plascreate')
    dao_consult_initial    = fields.Many2many("ir.attachment", "is_dao_consult_initial_rel"  , "consult_initial_id"  , "att_id", string="Consultation initiale client")
    dao_annexcom           = fields.Many2many("ir.attachment", "is_dao_annexcom_rel"         , "annexcom_id"         , "att_id", string="Fichiers commerciaux")
    dao_annex              = fields.Many2many("ir.attachment", "is_dao_annex_rel"            , "annex_id"            , "att_id", string="Fiches de devis du BE")
    dao_offre_validee      = fields.Many2many("ir.attachment", "is_dao_offre_validee_rel"    , "offre_validee_id"    , "att_id", string="Dernière offre validée par le client")
    dao_commande_client    = fields.Many2many("ir.attachment", "is_dao_commande_client_rel"  , "commande_client_id"  , "att_id", string="Commande client")
    dao_lettre_nomination  = fields.Many2many("ir.attachment", "is_dao_lettre_nomination_rel", "lettre_nomination_id", "att_id", string="Lettre de nomination et contrats")
    dao_devis_achat        = fields.Many2many("ir.attachment", "is_dao_devis_achat_rel"      , "devis_achat_id"      , "att_id", string="Fichier de devis des achats")
    fermeture_id           = fields.Many2one("is.fermeture.gantt", string="Fermeture planning", tracking=True)
    active                 = fields.Boolean('Actif', default=True, tracking=True)
    dynacase_id            = fields.Integer("id Dynacase",index=True,copy=False)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            dao_date = vals.get("dao_date") or date.today()
            annee = str(dao_date)[0:4]
            domain = [('dao_annee', '=', annee),('dao_num','!=',False)]
            lines=self.env['is.dossier.appel.offre'].search(domain,order='dao_num desc', limit=1)
            for line in lines:
                aa = annee[-2:]
                num=int(line.dao_num[0:3])+1
                num = ("000%s"%num)[-3:]
                dao_num="%s.%s"%(num,aa)
                vals['dao_num'] = dao_num
        return super().create(vals_list)


    def gantt_action(self):
        for obj in self:
            # docs=self.env['is.doc.moule'].search([ ('dossier_appel_offre_id', '=', obj.id) ])
            # ids=[]
            # for doc in docs:
            #     ids.append(doc.id)
            domain = [('dossier_appel_offre_id', '=', obj.id)]
            tree_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_dossier_appel_offre_edit_tree_view').id
            gantt_id = self.env.ref('is_dynacase2odoo.is_doc_moule_moule_dhtmlxgantt_project_view').id
            ctx={
                'default_type_document': 'dossier_appel_offre',
                'default_dossier_appel_offre_id'  : obj.id,
                'default_etat'          :'AF',
                'default_date_fin_gantt': datetime.today(),
                'default_idresp'        : self._uid,
            }
            return {
                'name': obj.dao_num,
                'view_mode': 'dhtmlxgantt_project,tree,form,kanban,calendar,pivot,graph',
                "views"    : [
                    (gantt_id, "dhtmlxgantt_project"),
                    (tree_id, "tree"),
                    (False, "form"),(False, "kanban"),(False, "calendar"),(False, "pivot"),(False, "graph")],
                'res_model': 'is.doc.moule',
                # 'domain': [
                #     ('id','in',ids),
                # ],
                'domain': domain,
                'type': 'ir.actions.act_window',
                "context": ctx,
                'limit': 1000,
            }



    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
            
            
