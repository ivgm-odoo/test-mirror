from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    service_id = fields.Many2one(string="Field Service", comodel_name="project.task")
