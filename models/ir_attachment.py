from odoo import api, fields, models, tools, _  # type: ignore

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
  
    is_dynacase_id = fields.Integer(string="Id Dynacase",index=True, readonly=True,copy=False)


    # is_doc_moule_id = fields.Many2one("is.doc.moule", string="is.doc.moule", compute='_compute_is_doc_moule_id', store=True, readonly=True)

    # @api.depends('res_model','res_id')
    # def _compute_is_doc_moule_id(self):
    #     for obj in self:
    #         doc_id = False
    #         if obj.res_model=='is.doc.moule':
    #             doc_id = obj.res_id
    #             doc = self.env['is.doc.moule'].browse(doc_id)
    #             doc._compute_rsp_pj()
    #         obj.is_doc_moule_id = doc_id
           


    # #TODO : Pour ajouter une piece jointe par glisser / déposer => Fonctionne, mais le document n'est pas rafraichi automatiquement
    # @api.model_create_multi
    # def create(self, vals_list):
    #     line_id=False
    #     if len(vals_list)==1:
    #         vals = vals_list[0]
    #         if vals.get('res_model')=='is.doc.moule':
    #             res_id=vals.get('res_id')
    #             lines=self.env['is.doc.moule.array'].search([ ('is_doc_id', '=', res_id) ], limit=1)
    #             for line in lines:
    #                 vals_list[0]['res_id']=line.id
    #                 vals_list[0]['res_model']='is.doc.moule.array'
    #                 line_id = line.id
    #     res = super().create(vals_list)
    #     if line_id:
    #         cr=self._cr
    #         SQL="""
    #             INSERT INTO attach_annex_rel(
    #                 annex_id, attachment_id)
    #             VALUES (%s, %s)
    #         """%(line_id,res.id)

    #         r = cr.execute(SQL)
    #         cr.commit()
    #     return res
    
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'reload',
    #     }
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'soft_reload'
    #     }