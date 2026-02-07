from odoo import models, fields, api         # type: ignore
from odoo.exceptions import ValidationError  # type: ignore
from datetime import datetime
import pytz


_TYPE = [
        ("", ""),
        ("B", "Bon"),
        ("M", "Mauvais"),
        ]

_OPERATEURS = [
        ("", ""),
        ("116", "116"),
        ("131", "131"),
        ("147", "147"),
        ("241", "241"),
        ("288", "288"),
        ("338", "338"),
        ("354", "354"),
        ("399", "399"),
        ("412", "412"),
        ("453", "453"),
        ("477", "477"),
        ("484", "484"),
        ("537", "537"),
        ("INT", "INT"),
        ]

_CONTROLEURS = [
        ("", ""),
        ("CF", "CF"),
        ("CT", "CT"),
        ("267", "267"),
        ("416", "416"),
        ("524", "524"),
        ]


class is_oberthur(models.Model):
    _name='is.oberthur'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Oberthur"
    _rec_name = "id"
    _order='date_heure_saisie desc'

    active    = fields.Boolean("Actif", default=True, tracking=True)
    montage   = fields.Char("Montage 1ier Flux", tracking=True, required=True)
    coque     = fields.Char("Coque Interne", tracking=True, required=True)
    batterie  = fields.Char("Batterie", tracking=True, default='1031000000000')

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
    date      = fields.Char("Date saisie", tracking=True, default=lambda self: datetime.now(pytz.timezone('Europe/Paris')).strftime('%Y%m%d'))
    heure     = fields.Char("Heure saisie", tracking=True, default=lambda self: datetime.now(pytz.timezone('Europe/Paris')).strftime('%H%M'))

    date_heure_saisie = fields.Datetime("Date-Heure saisie", default=fields.Datetime.now, readonly=True, tracking=True)

    operateu  = fields.Selection(_OPERATEURS, "Opérateur 1", tracking=True)
    operateu2 = fields.Selection(_OPERATEURS, "Opérateur 2", tracking=True)
    controle  = fields.Selection(_CONTROLEURS, "Controleur", tracking=True)
    reprise   = fields.Char("Ordre Reprise", tracking=True)
    comment   = fields.Char("Commentaire", tracking=True)
    modif     = fields.Boolean(string="Modifier le harnais et numof", store=False)

    @api.constrains('montage', 'coque')
    def _check_montage_coque(self):
        """Vérifie que la combinaison montage/coque est autorisée"""
        combinaisons_7 = [
            ('K0123AB', 'K0081AA'),
            ('K0109AA', 'K0108AA'),
            ('K0029BC', 'K0008AA'),
            ('K0126AB', 'K0008AA'),
            ('K0110AA', 'K0081AA'),
            ('K0128AB', 'K0108AA'),
            ('J0007B0', 'K0008B'),
            ('J0049A0', 'K0008B'),
            ('K0301A',  'K0081B'),
            ('K0301A',  'K0008B'),
        ]
        combinaisons_6 = [
            ('K0278C', 'K0008B'),
            ('J0007B', 'K0008B'),
            ('J0031A', 'K00810'),
            ('K0295A', 'K0008B'),
            ('J0049A', 'K0008B'),
            ('K0301A', 'K0081B'),
            ('K0301A', 'K0008B'),
        ]
        for rec in self:
            if rec.montage and rec.coque:
                test = False
                montage7 = rec.montage[:7].upper()
                coque7   = rec.coque[:7].upper()
                for m, c in combinaisons_7:
                    if montage7 == m and coque7 == c:
                        test = True
                        break
                if not test:
                    montage6 = rec.montage[:6].upper()
                    coque6   = rec.coque[:6].upper()
                    for m, c in combinaisons_6:
                        if montage6 == m and coque6 == c:
                            test = True
                            break
                if not test:
                    raise ValidationError(
                        "Montage '%s' non concordant avec Coque '%s'" % (rec.montage, rec.coque)
                    )

    @api.constrains('harnais')
    def _check_harnais(self):
        for rec in self:
            if rec.harnais:
                if len(rec.harnais) != 13 or not rec.harnais.isdigit():
                    raise ValidationError("La référence de l'harnais doit être un nombre à 13 chiffres.")
                #val = int(rec.harnais)
                #if val < 1032000000000 or val >= 1033000000000:
                #    raise ValidationError("La référence de l'harnais doit être comprise entre 1032000000000 et 1032999999999.")

    @api.constrains('batterie')
    def _check_batterie(self):
        for rec in self:
            if rec.batterie:
                if len(rec.batterie) != 13 or not rec.batterie.isdigit():
                    raise ValidationError("La référence de la batterie doit être un nombre à 13 chiffres commençant par 1031.")
                val = int(rec.batterie)
                if val < 1031000000000 or val >= 1032000000000:
                    raise ValidationError("La référence de la batterie doit être un nombre à 13 chiffres commençant par 1031.")

    @api.constrains('tensiong', 'tensiond')
    def _check_tensions(self):
        for rec in self:

            print(rec,rec.tensiong, rec.tensiond)

            if rec.tensiong <= 0:
                raise ValidationError("La Tension Batterie Gauche doit être supérieure à 0.")
            if rec.tensiond <= 0:
                raise ValidationError("La Tension Batterie Droite doit être supérieure à 0.")

    @api.constrains('numof')
    def _check_numof(self):
        for rec in self:
            if rec.numof:
                if not rec.numof.isdigit():
                    raise ValidationError("Le N° de l'OF doit être un nombre.")
                val = int(rec.numof)
                if val < 200 or val > 500000:
                    raise ValidationError("Le N° de l'OF doit être compris entre 200 et 500000.")


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


    def _check_montage_unique(self, montage, exclude_id=False):
        """Vérifie que le montage n'existe pas déjà (hors enregistrement courant)"""
        if montage:
            domain = [('montage', '=', montage)]
            if exclude_id:
                domain.append(('id', '!=', exclude_id))
            existing = self.search(domain, limit=1)

            print('TEST', domain,existing)


            if existing:
                raise ValidationError("Ce montage '%s' existe déjà !" % montage)


    def write(self, vals):
        """Enregistre les valeurs de harnais et numof dans is_mem_var en tant qu'admin"""
        if 'montage' in vals:
            for rec in self:
                self._check_montage_unique(vals['montage'], exclude_id=rec.id)
        res = super(is_oberthur, self).write(vals)
        self._memoriser_harnais_numof(vals)
        return res


    @api.model_create_multi
    def create(self, vals_list):
        """Enregistre les valeurs de harnais et numof dans is_mem_var en tant qu'admin lors de la création"""
        for vals in vals_list:
            self._check_montage_unique(vals.get('montage'))

        res = super(is_oberthur, self).create(vals_list)
        
        for vals in vals_list:
            self._memoriser_harnais_numof(vals)
        
        return res
