from odoo import models, fields, api         # type: ignore
from odoo.exceptions import ValidationError  # type: ignore
from datetime import datetime



class is_plan_amelioration_continu_pj(models.Model):
    _name        = "is.plan.amelioration.continu.pj"
    _description = "Pièce-jointe des PAC"
    _order='lig,id'

    lig            = fields.Integer(string="Lig",index=True,copy=False, help="Permet de faire le lien avec la ligne du tableau dans Dynacase")
    attachment_ids = fields.Many2many("ir.attachment", "is_plan_amelioration_continu_attachment_rel", "pac_line_id", "attachment_id", string="Fichiers")
    pac_id         = fields.Many2one("is.plan.amelioration.continu")


class is_plan_amelioration_continu(models.Model):
    _name='is.plan.amelioration.continu'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Plan d'amélioration continu"
    _rec_name = "numero"
    _order='numero desc'

    numero              = fields.Integer('Numéro', tracking=True, copy=False)
    active              = fields.Boolean('Actif', default=True, tracking=True)
    type                = fields.Selection([('pac', 'PAC'), ('revue', 'Revue')], "Type", required=True, tracking=True)
    createur_id         = fields.Many2one('res.users', 'Créateur', required=True, copy=False, default=lambda self: self.env.uid, tracking=True)
    site_id             = fields.Many2one('is.database', "Site", tracking=True)
    service_id          = fields.Many2one('is.service', "Service", tracking=True)
    #service_id          = fields.Many2one(related="createur_id.is_service_id")
    processus_id        = fields.Many2one('is.processus', "Processus", tracking=True)
    annee               = fields.Char('Année', default=lambda self: datetime.now().year, store=True, tracking=True)
    mois                = fields.Char('Mois', default=lambda self: str(datetime.now().month) if datetime.now().month > 9 else '0' + str(datetime.now().month), tracking=True)
    groupe_acces_id     = fields.Many2one('res.groups', "Groupe d'accès en consultation", tracking=True, readonly=True)
    plan_action_ids     = fields.Many2many('is.plan.action','is_plan_amelioration_continu_plan_action_rel','plan_amelioration_continu_id','plan_action_id', string="Plan d'actions", tracking=True)
    dynacase_id         = fields.Integer(string="Id Dynacase", index=True, copy=False)
    pj_ids              = fields.One2many("is.plan.amelioration.continu.pj", "pac_id", string="Pièce jointe")
    pj_noms             = fields.Text(string="Noms des pièces jointes", tracking=True, compute="_compute_pj_noms", store=True, readonly=True,copy=False)
    
    # Champ calculé pour détecter si l'utilisateur peut modifier
    readonly_all        = fields.Boolean(string="Lecture seule", compute="_compute_readonly_all", store=False)




    @api.onchange('site_id')
    def _onchange_site_id_set_groupe_acces(self):
        """Si le site est "Siège", renseigne automatiquement le groupe d'accès
        en consultation avec le groupe nommé 'CODIR'. Sinon, vide le champ.

        Implémenté à la demande: mise à jour via onchange uniquement.
        """
        for rec in self:
            groupe = False
            # On teste sur le libellé du site
            if rec.site_id and (rec.site_id.name or '').strip().lower() == 'siège':
                groupe = rec.env['res.groups'].search([('name', '=', 'CODIR')], limit=1)
            rec.groupe_acces_id = groupe.id if groupe else False


    @api.depends('createur_id')
    def _compute_readonly_all(self):
        """Détermine si l'utilisateur courant peut modifier cet enregistrement"""
        for record in self:
            readonly = True
            try:
                # Vérifier si l'utilisateur peut écrire sur cet enregistrement
                record.check_access_rights('write')
                record.check_access_rule('write')
                readonly = False
            except Exception:
                # Si une exception est levée, l'utilisateur n'a pas le droit d'écriture
                readonly = True
            
            record.readonly_all = readonly


    @api.depends('pj_ids', 'pj_ids.attachment_ids', 'pj_ids.attachment_ids.name')
    def _compute_pj_noms(self):
        """Calcule la liste des noms des pièces jointes"""
        for record in self:
            noms = []
            for pj in record.pj_ids:
                for attachment in pj.attachment_ids:
                    if attachment.name:
                        noms.append(attachment.name)
            record.pj_noms = '\n'.join(noms) if noms else ''


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'numero' not in vals:
                last = self.env[self._name].search([('numero', '!=', None)], order="numero desc", limit=1)
                if last:
                    vals['numero'] = last.numero + 1
                else:
                    vals['numero'] = 0
        return super().create(vals_list)


    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
