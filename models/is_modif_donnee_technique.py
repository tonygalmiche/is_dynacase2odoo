from odoo import models, fields, api  # type: ignore

class is_modif_donnee_technique(models.Model):
    _name='is.modif.donnee.technique'
    _inherit     = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description="Demande modification données techniques"
    _rec_name = "num_demande"
    _order='num_demande'

    num_demande                   = fields.Integer("N° Demande", readonly=True)
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
    article_piece_jointe_ids      = fields.Many2many("ir.attachment", "is_modif_donnee_technique_article_piece_jointe_rel", "piece_jointe", "att_id", string="Pièce jointe article")

    nomenclature                  = fields.Boolean("Modification Nomenclature", tracking=True)
    nomenclature_commentaire      = fields.Text("Commentaire nomenclature", tracking=True)
    nomenclature_piece_jointe_ids = fields.Many2many("ir.attachment", "is_modif_donnee_technique_nomenclature_piece_jointe_rel", "piece_jointe", "att_id", string="Pièce jointe nomenclature")

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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "num_demande" not in vals:
                last_codif = self.env["is.modif.donnee.technique"].search([('num_demande', '!=', None)], order="num_demande desc", limit=1)
                if last_codif:
                    num_demande = last_codif.num_demande
                else:
                    num_demande = -1
                vals["num_demande"] = num_demande + 1
        return super().create(vals_list)
