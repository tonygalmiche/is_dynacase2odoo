from odoo import models, fields  # type: ignore


class is_liste_diffusion_mail(models.Model):
    _name        = "is.liste.diffusion.mail"
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = "Liste de diffusion  des mails"
    _order = "model_id,code"
    _rec_name = 'model_id'

    model_id          = fields.Many2one("ir.model", string="Modèle", tracking=True)
    code              = fields.Char("Code"                         , tracking=True)
    commentaire       = fields.Char("Commentaire"                  , tracking=True)
    user_ids          = fields.Many2many('res.users', string="Destinataires")
    active            = fields.Boolean('Actif', default=True       , tracking=True)

