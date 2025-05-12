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


    def get_users(self,model,code):
        users=False
        lines = self.env['ir.model'].search([('model','=',model)],limit=1)
        for line in lines:
            res = self.env['is.liste.diffusion.mail'].search([('model_id','=',line.id),('code','=',code)],limit=1)
            if len(res)>0:
                users=[]
                for l in res:
                    for user in l.user_ids:
                        if user.email:
                            users.append(user)
            return users
       

    def get_users_ids(self,users=False):
        ids=[]
        if users:
            for user in users:
                if user.email:
                    if user.id not in ids:
                        ids.append(user.id)
        return ids


    def get_partners_ids(self,model,code):
        partners_ids=False
        users = self.get_users(model,code)
        if users:
            partners_ids=[]
            for user in users:
                partners_ids.append(user.partner_id.id)
        return partners_ids
    

    def get_destinataires_name(self,model,code):
        destinataires_name=False
        users = self.get_users(model,code)
        if users:
            mydict=[]
            for user in users:
                if user.email:
                    #name='%s <%s>'%(user.name,user.email)
                    name=user.email
                    mydict.append(name)
            destinataires_name=', '.join(mydict)
        return destinataires_name


    def users2mail(self,users):
        name=False
        liste=[]
        for user in users:
            if user.email and user.email not in liste:
                liste.append(user.email)
            name=', '.join(liste)
        return name


    def users2partner_ids(self,users):
        ids=[]
        for user in users:
            if user.email and user.partner_id.id not in ids:
                ids.append(user.partner_id.id)
        return ids
