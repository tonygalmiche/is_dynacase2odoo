from odoo import api, fields, models, tools, _

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
  
    is_dynacase_id = fields.Integer(string="Id Dynacase",index=True, readonly=True)

