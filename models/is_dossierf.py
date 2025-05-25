from odoo import models, fields, api # type: ignore
from odoo.addons.is_dynacase2odoo.models.is_param_project import GESTION_J, TYPE_DOCUMENT # type: ignore
from datetime import datetime, timedelta, date


class is_dossierf(models.Model):
    _inherit = 'is.dossierf'

    image                  = fields.Binary('Image')
    dossier_appel_offre_id = fields.Many2one("is.dossier.appel.offre", string="Dossier appel d'offre", copy=False, tracking=True)
    revue_contrat_id       = fields.Many2one("is.revue.de.contrat"   , string="Revue de contrat"     , copy=False, tracking=True)
    revue_lancement_id     = fields.Many2one("is.revue.lancement"    , string="Revue de lancement"   , copy=False, tracking=True)
    revue_risque_id        = fields.Many2one("is.revue.risque"       , string="Revue des risques"    , copy=False, tracking=True)
    j_actuelle             = fields.Selection(GESTION_J              , string="J Actuelle"           , copy=False, tracking=True, default='J0')
    j_avancement           = fields.Integer(string="Avancement J (%)"                                , copy=False, tracking=True)
    date_fin_be            = fields.Date(string="Date fin BE"                                        , copy=False, tracking=True)
    article_ids            = fields.One2many('is.mold.dossierf.article', 'dossierf_id'               , copy=False)
    fermeture_id           = fields.Many2one("is.fermeture.gantt", string="Fermeture planning")
    j_actuelle_rw          = fields.Boolean(string="J Actuelle rw", compute='_compute_j_actuelle_rw', store=False, readonly=True)


    @api.model_create_multi
    def create(self, vals_list):
        res=super().create(vals_list)
        company = self.env.user.company_id
        if company.is_base_principale:
            res.envoi_mail()
        return res


    def envoi_mail(self):
        template = self.env.ref('is_dynacase2odoo.is_dossierf_mail_template').sudo()     
        email_values = {
            'email_to'      : self.get_email_to(),
            'auto_delete'   : False,
            'scheduled_date': False,
        }
        template.send_mail(self.id, force_send=True, raise_exception=False, email_values=email_values)


    def get_users(self):
        for obj in self:
            users=[]
            users.append(self.env.user)
            if obj.chef_projet_id:
                users.append(obj.chef_projet_id)
            if obj.client_id.user_id:
                users.append(obj.client_id.user_id)
            return users


    def get_email_to(self):
        for obj in self:
            email_to=False
            users = obj.get_users()
            if users:
                email_to=[]
                for user in users:
                    email_to.append(user.partner_id.email)
                email_to = ', '.join(email_to)
            return email_to


    def get_doc_url(self):
        for obj in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = base_url + '/web#id=%s' '&view_type=form&model=%s'%(obj.id,self._name)
            return url














    @api.depends('j_actuelle')
    def _compute_j_actuelle_rw(self):
        admin = self.env.user.has_group('base.group_system')
        for obj in self:
            rw = False
            if admin:
                rw=True
            obj.j_actuelle_rw = rw


    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }

    def gantt_action(self):
        for obj in self:
            domain=[ ('dossierf_id', '=', obj.id) ]

            tree_id  = self.env.ref('is_dynacase2odoo.is_doc_moule_dossierf_edit_tree_view').id
            gantt_id = self.env.ref('is_dynacase2odoo.is_doc_moule_moule_dhtmlxgantt_project_view').id
            ctx={
                'default_type_document' : 'Dossier F',
                'default_dossierf_id'   : obj.id,
                'default_etat'          :'AF',
                'default_date_fin_gantt': datetime.today(),
                'default_idresp'        : self._uid,
            }
            return {
                'name': obj.name,
                'view_mode': 'dhtmlxgantt_project,tree,form,kanban,calendar,pivot,graph',
                "views"    : [
                    (gantt_id, "dhtmlxgantt_project"),
                    (tree_id, "tree"),
                    (False, "form"),(False, "kanban"),(False, "calendar"),(False, "pivot"),(False, "graph")],
                'res_model': 'is.doc.moule',
               'domain': domain,
                'type': 'ir.actions.act_window',
                "context": ctx,
                'limit': 1000,
            }


    def archiver_documents_action(self):
        for obj in self:
            domain=[
                ('dossierf_id'     ,'=', obj.id),
            ]
            docs=self.env['is.doc.moule'].search(domain)
            for doc in docs:
                doc.active = False

