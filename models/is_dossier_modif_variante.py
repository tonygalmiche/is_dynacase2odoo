# -*- coding: utf-8 -*-
from odoo import models, fields, api, _      # type: ignore
from odoo.exceptions import ValidationError  # type: ignore
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class is_dossier_modif_variante(models.Model):
    _name        = "is.dossier.modif.variante"
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = "Dossier modif/variante"
    _rec_name    = "demao_num"
    _order = "demao_date desc"


    @api.depends("state")
    def _compute_vsb(self):
        for obj in self:
            vsb = False
            if obj.state in ["plascreate", "plastransbe"]:
                vsb = True
            obj.vers_analyse_vsb = vsb
            vsb = False
            if obj.state in ["plasanalysed", "Analyse_BE", "plasrelancecli", "plasdiffusedcli"]:
                vsb = True
            obj.vers_transmis_be_vsb = vsb
            vsb = False
            if obj.state in ["plastransbe", "plasvalidbe"]:
                vsb = True
            obj.vers_analyse_be_vsb = vsb
            vsb = False
            if obj.state in ["Analyse_BE"]:
                vsb = True
            obj.vers_vali_de_be_vsb = vsb
            vsb = False
            if obj.state in ["plasvalidbe"]:
                vsb = True
            obj.vers_vali_de_commercial_vsb = vsb
            vsb = False
            if obj.state in ["plasvalidcom", "plasanalysed", "plasloosed", "plaswinned", "plascancelled"]:
                vsb = True
            obj.vers_diffuse_client_vsb = vsb
            vsb = False
            if obj.state in ["plasdiffusedcli"]:
                vsb = True
            obj.vers_relance_client_vsb = vsb
            vsb = False
            if obj.state in ["plasrelancecli", "plasdiffusedcli"]:
                vsb = True
            obj.vers_perdu_vsb = vsb
            vsb = False
            if obj.state in ["plasrelancecli", "plasdiffusedcli"]:
                vsb = True
            obj.vers_gagne_vsb = vsb
            vsb = False
            if obj.state in ["plasrelancecli", "diffuse_client"]:
                vsb = True
            obj.vers_annule_vsb = vsb


    def vers_analyse_action(self):
        for obj in self:
            obj.sudo().state = "plasanalysed"

    def vers_transmis_be_action(self):
        for obj in self:
            obj.sudo().state = "plastransbe"

    def vers_vers_analyse_be_vsb_action(self):
        for obj in self:
            obj.sudo().state = "Analyse_BE"

    def vers_vali_de_be_vsb_action(self):
        for obj in self:
            obj.sudo().state = "plasvalidbe"

    def vers_vali_de_commercial_vsb_action(self):
        for obj in self:
            obj.sudo().state = "plasvalidcom"

    def vers_diffuse_client_vsb_action(self):
        for obj in self:
            obj.sudo().state = "plasdiffusedcli"

    def vers_relance_client_vsb_action(self):
        for obj in self:
            obj.sudo().state = "plasrelancecli"

    def vers_perdu_vsb_action(self):
        for obj in self:
            obj.sudo().state = "plasloosed"

    def vers_gagne_vsb_action(self):
        for obj in self:
            obj.sudo().state = "plaswinned"

    def vers_annule_vsb_action(self):
        for obj in self:
            obj.sudo().state = "plascancelled"


    @api.depends('demao_idmoule.is_database_id', 'dossierf_id.is_database_id')
    def _compute_site_id(self):
        for obj in self:
            site_id = False
            if obj.demao_idmoule.is_database_id:
                site_id = obj.demao_idmoule.is_database_id.id
            if obj.dossierf_id.is_database_id:
                site_id = obj.dossierf_id.is_database_id.id
            obj.site_id = site_id


    def compute_site_id(self):
        "for xml-rpc"
        self._compute_site_id()
        return True


    @api.depends('demao_idmoule.dossier_appel_offre_id', 'dossierf_id.dossier_appel_offre_id')
    def _compute_dossier_appel_offre_id(self):
        for obj in self:
            dossier_id = False
            if obj.demao_idmoule.dossier_appel_offre_id:
                dossier_id = obj.demao_idmoule.dossier_appel_offre_id.id
            if obj.dossierf_id.dossier_appel_offre_id:
                dossier_id = obj.dossierf_id.dossier_appel_offre_id.id
            obj.dossier_appel_offre_id = dossier_id


    @api.depends('demao_idmoule','dossierf_id', 'demao_idmoule.client_id.user_id', 'dossierf_id.client_id.user_id')
    def _compute_demao_idcommercial(self):
        for obj in self:
            client = client_id = user_id = desig = False
            if obj.demao_idmoule.designation:
                desig = obj.demao_idmoule.designation
            if obj.dossierf_id.designation:
                desig = obj.dossierf_id.designation
            if obj.demao_idmoule.client_id:
                client = obj.demao_idmoule.client_id
            if obj.dossierf_id.client_id:
                client = obj.dossierf_id.client_id
            if client:
                client_id = client.id
                user_id   = client.user_id.id
            obj.demao_idclient     = client_id
            obj.demao_idcommercial = user_id
            obj.demao_desig        = desig


    demao_type                  = fields.Selection([
        ("modification", "Modification"),
        ("variante",     "Variante"),
    ], string="Type", required=True, tracking=True)
    demao_num                   = fields.Char(string="N° ordre", required=True)
    demao_date                  = fields.Date(string="Date", default=fields.Date.context_today, required=False, tracking=True)
    demao_idmoule               = fields.Many2one("is.mold", string="Moule", tracking=True)
    dossierf_id                 = fields.Many2one("is.dossierf", string="Dossier F", tracking=True)
    dossier_appel_offre_id      = fields.Many2one("is.dossier.appel.offre", string="Dossier appel d'offre", tracking=True, compute='_compute_dossier_appel_offre_id', readonly=True, store=True)
    demao_idclient              = fields.Many2one("res.partner", string="Client"  , tracking=True, compute='_compute_demao_idcommercial', readonly=False, store=True, domain=[("is_company","=",True), ("customer","=",True)])
    demao_idcommercial          = fields.Many2one("res.users", string="Commercial", tracking=True, compute='_compute_demao_idcommercial', readonly=False, store=True)
    demao_desig                 = fields.Char(string="Désignation pièce"          , tracking=True, compute='_compute_demao_idcommercial', readonly=False, store=True)
    site_id                     = fields.Many2one('is.database', "Site", compute='_compute_site_id', readonly=True, store=True)
    demao_nature                = fields.Char(string="Nature", required=False, tracking=True)
    demao_ref                   = fields.Char(string="Référence", tracking=True)
    demao_daterep               = fields.Date(string="Date réponse", tracking=True)
    demao_datelanc              = fields.Date(string="Date lancement", tracking=True)
    demao_pxvente               = fields.Float(string="Prix de vente", tracking=True)
    demao_numcmd                = fields.Char(string="N° commande", tracking=True)
    demao_obs                   = fields.Char(string="Observation", tracking=True)
    demao_motif                 = fields.Selection([
        ("1", "abandon client"),
        ("2", "délai trop long"),
        ("3", "moule et pièce trop chers"),
        ("4", "moule trop cher"),
        ("5", "pièce trop chère"),
        ("6", "autre"),
        ("7", "abandon Plastigray"),
    ], string="Motif ", tracking=True)
    demao_idbe                  = fields.Many2one("res.users", string="BE", tracking=True)
    demao_annexcom              = fields.Many2many("ir.attachment", "is_dmv_annexcom_rel", "annexcom_id", "att_id", string="Fichiers commerciaux", tracking=True)
    demao_annex                 = fields.Many2many("ir.attachment", "is_dmv_annex_rel", "annex_id", "att_id", string="Fichiers BE", tracking=True)
    demao_cde_be                = fields.Many2many("ir.attachment", "is_dmv_cde_be_rel", "cde_be_id", "att_id", string="Commandes BE", tracking=True)
    state                       = fields.Selection([
        ("plascreate",      "Créé"),
        ("plasanalysed",    "Analysé"),
        ("plastransbe",     "Transmis BE"),
        ("Analyse_BE",      "Analysé BE"),
        ("plasvalidbe",     "Validé BE"),
        ("plasvalidcom",    "Validé Commercial"),
        ("plasdiffusedcli", "Diffusé Client"),
        ("plasrelancecli",  "Relance Client"),
        ("plasloosed",      "Perdu"),
        ("plaswinned",      "Gagné"),
        ("plascancelled",   "Annulé"),
    ], string="Etat", default="plascreate", tracking=True)
    vers_analyse_vsb            = fields.Boolean(string="Vers Cree", compute='_compute_vsb', readonly=True, store=False)
    vers_transmis_be_vsb        = fields.Boolean(string="Vers Transmis BE", compute='_compute_vsb', readonly=True, store=False)
    vers_analyse_be_vsb         = fields.Boolean(string="Vers Analyse BE", compute='_compute_vsb', readonly=True, store=False)
    vers_vali_de_be_vsb         = fields.Boolean(string="Vers Vali de BE", compute='_compute_vsb', readonly=True, store=False)
    vers_vali_de_commercial_vsb = fields.Boolean(string="Vers Vali de Commercial", compute='_compute_vsb', readonly=True, store=False)
    vers_diffuse_client_vsb     = fields.Boolean(string="Diffuse Client", compute='_compute_vsb', readonly=True, store=False)
    vers_relance_client_vsb     = fields.Boolean(string="Relance Client", compute='_compute_vsb', readonly=True, store=False)
    vers_perdu_vsb              = fields.Boolean(string="Perdu", compute='_compute_vsb', readonly=True, store=False)
    vers_gagne_vsb              = fields.Boolean(string="Gagne", compute='_compute_vsb', readonly=True, store=False)
    vers_annule_vsb             = fields.Boolean(string="Annule", compute='_compute_vsb', readonly=True, store=False)
    dynacase_id                 = fields.Integer(string="Id Dynacase",index=True,copy=False)
    solde                       = fields.Boolean(string="Soldé", default=False, copy=False, tracking=True)
    fermeture_id                = fields.Many2one("is.fermeture.gantt", string="Fermeture planning", tracking=True)
    fiche_codification_ids       = fields.One2many("is.fiche.codification", "dossier_modif_variante_id", readonly=True)
    active                      = fields.Boolean('Actif', default=True, tracking=True)


    @api.constrains('demao_idmoule', 'dossierf_id')
    def _demao_idmoule_dossierf_id(self):
        for obj in self:
            if obj.demao_idmoule.id and obj.dossierf_id.id:
                raise ValidationError("Il ne faut pas saisir un moule et un dossier F en même temps")


    def update_client_action(self):
        nb=len(self)
        ct=1
        for obj in self:
            _logger.info("update_client_action : %s/%s : %s"%(ct,nb,obj.demao_num))
            obj._compute_demao_idcommercial()
            #idclient = obj.demao_idmoule.client_id.id or obj.dossierf_id.client_id.id
            #if idclient:
            #    obj.demao_idclient=idclient
            ct+=1
        return []


    def gantt_action(self):
        for obj in self:
            # docs=self.env['is.doc.moule'].search([ ('dossier_modif_variante_id', '=', obj.id) ])
            # ids=[]
            # for doc in docs:
            #     ids.append(doc.id)
            domain=[('dossier_modif_variante_id', '=', obj.id)]
            tree_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_dossier_modif_variante_edit_tree_view').id
            gantt_id = self.env.ref('is_dynacase2odoo.is_doc_moule_moule_dhtmlxgantt_project_view').id
            ctx={
                'default_type_document': 'Dossier Modif Variante',
                'default_dossier_modif_variante_id'  : obj.id,
                'default_etat'          :'AF',
                'default_date_fin_gantt': datetime.today(),
                'default_idresp'        : self._uid,
            }
            return {
                'name': obj.demao_num,
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
            
    def action_creation_fiche_codification(self):
        for obj in self:
            project = obj.demao_idmoule.project
            vals = {'type_dossier': 'Dossier modification',
                    'client_id': obj.demao_idclient.id,
                    'project_id': project.id,
                    'chef_de_projet_id': project.chef_projet_id.id,
                    'dossier_modif_variante_id': obj.id,
                    #
                    'dossierf_id': obj.dossierf_id.id,
                    'mold_id': obj.demao_idmoule.id,
                    }
            doc = self.env['is.fiche.codification'].create(vals)
            res= {
                'name': 'Doc',
                'view_mode': 'form',
                'res_model': 'is.fiche.codification',
                'res_id': doc.id,
                'type': 'ir.actions.act_window',
            }
            return res
