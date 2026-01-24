from odoo import models, fields, api         # type: ignore


_TYPE = [
        ("", ""),
        ("B", "Bon"),
        ("M", "Mauvais"),
        ]


class is_oberthur(models.Model):
    _name='is.oberthur'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Oberthur"
#    _rec_name = "numero"
#    _order='create_date desc'

    active    = fields.Boolean("Actif", default=True, tracking=True)
    montage   = fields.Char("Montage 1ier Flux", tracking=True, required=True)
    coque     = fields.Char("Coque Interne", tracking=True, required=True)
    batterie  = fields.Char("K0008B27788", tracking=True)

    harnais   = fields.Char("Harnais CE-CI", tracking=True, default=lambda self: self._default_harnais())
    numof     = fields.Char("N° OF", tracking=True, default=lambda self: self._default_numof())
    
    
    continu1  = fields.Selection(_TYPE, "Continuité Maillage 1", tracking=True)
    tensiong  = fields.Float("Tension Batterie Gauche", digits=(5, 2), tracking=True)
    tensiond  = fields.Float("Tension Batterie Droite", digits=(5, 2), tracking=True)
    bransubd  = fields.Selection(_TYPE, "Branchement SubD25", tracking=True)
    blocvis   = fields.Selection(_TYPE, "Blocage 2 Vis 8059", tracking=True)
    soudure   = fields.Selection(_TYPE, "Aspect Soudure", tracking=True)
    continu2  = fields.Selection(_TYPE, "Continuité Maillage 2", tracking=True)
    ctrelect  = fields.Selection(_TYPE, "Contrôle Électrique Final", tracking=True)
    date      = fields.Char("Date saisie", tracking=True)
    heure     = fields.Char("Heure saisie", tracking=True)

    date_heure_saisie = fields.Integer("Date-Heure saisie", tracking=True)

    operateu  = fields.Char("Opérateur 1", tracking=True)
    operateu2 = fields.Char("Opérateur 2", tracking=True)
    controle  = fields.Char("Controleur", tracking=True)
    reprise   = fields.Char("Ordre Reprise", tracking=True)
    comment   = fields.Char("Commentaire", tracking=True)
    modif     = fields.Boolean(string="Modifier le harnais et numof", store=False)


    def _get_admin_user_id(self):
        """Récupère l'ID de l'utilisateur admin"""
        admin_user = self.env.ref('base.user_admin', raise_if_not_found=False)
        return admin_user.id if admin_user else 1


    def _default_harnais(self):
        """Récupère la valeur par défaut du harnais depuis is_mem_var"""
        admin_user_id = self._get_admin_user_id()
        mem_var = self.env['is.mem.var'].sudo()
        return mem_var.get(admin_user_id, 'oberthur_harnais') or ''


    def _default_numof(self):
        """Récupère la valeur par défaut du numof depuis is_mem_var"""
        admin_user_id = self._get_admin_user_id()
        mem_var = self.env['is.mem.var'].sudo()
        return mem_var.get(admin_user_id, 'oberthur_numof') or ''


    def _memoriser_harnais_numof(self, vals):
        """Mémorise les valeurs de harnais et numof dans is_mem_var pour l'admin"""
        admin_user_id = self._get_admin_user_id()
        mem_var = self.env['is.mem.var'].sudo()
        
        if 'harnais' in vals and vals['harnais']:
            mem_var.set(admin_user_id, 'oberthur_harnais', vals['harnais'])
        
        if 'numof' in vals and vals['numof']:
            mem_var.set(admin_user_id, 'oberthur_numof', vals['numof'])


    def write(self, vals):
        """Enregistre les valeurs de harnais et numof dans is_mem_var en tant qu'admin"""
        res = super(is_oberthur, self).write(vals)
        self._memoriser_harnais_numof(vals)
        return res


    @api.model_create_multi
    def create(self, vals_list):
        """Enregistre les valeurs de harnais et numof dans is_mem_var en tant qu'admin lors de la création"""
        res = super(is_oberthur, self).create(vals_list)
        
        for vals in vals_list:
            self._memoriser_harnais_numof(vals)
        
        return res
