from odoo import models, fields  # type: ignore

class is_modif_donnee_technique(models.Model):
    _name='is.modif.donnee.technique'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Fiche information prospect"
#    _rec_name = "nom_prospect"
#    _order='nom_prospect'

    num_demande                   = fields.Integer("N° Demande", tracking=True)
    active                        = fields.Boolean('Actif', default=True, tracking=True)
    moule_id                      = fields.Many2one('is.mold', 'Moule', tracking=True)
    dossierf_id                   = fields.Many2one("is.dossierf", string="Dossier F", tracking=True)
    codepg                        = fields.Char("Code PG", tracking=True)
    designation                   = fields.Char("Désignation", tracking=True)
    demandeur                     = fields.Many2one("res.users", "Demandeur", default=lambda self: self.env.uid, tracking=True)
    date_demande                  = fields.Date("Date demande", tracking=True, default=lambda *a: fields.datetime.now())
    responsable_action            = fields.Many2one("res.users", "Responsable de l'action", tracking=True, required=True)

    article                       = fields.Boolean("Modification Article", tracking=True)
    article_commentaire           = fields.Text("Commentaire article", tracking=True)
    article_piece_jointe          = fields.Many2one("ir.attachment", "Pièce jointe article", tracking=True)
    article_piece_jointe_ids      = fields.Many2many("ir.attachment", "is_article_piece_jointe_rel", "piece_jointe", "att_id", string="Pièce jointe article")

    nomenclature                  = fields.Boolean("Modification Nomenclature", tracking=True)
    nomenclature_commentaire      = fields.Text("Commentaire nomenclature", tracking=True)
    nomenclature_piece_jointe_ids = fields.Many2many("ir.attachment", "is_nomenclature_piece_jointe_rel", "piece_jointe", "att_id", string="Pièce jointe nomenclature")

    gamme_article                 = fields.Boolean("Modification Gamme", tracking=True)
    gamme_commentaire             = fields.Text("Commentaire", tracking=True)

    dynacase_id                   = fields.Integer(string="Id Dynacase", index=True, copy=False)

    def lien_vers_dynacase_action(self):
        for obj in self:
            url="https://dynacase-rp/?sole=Y&app=FDL&action=FDL_CARD&latest=Y&id=%s"%obj.dynacase_id
            return {
                'type' : 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
