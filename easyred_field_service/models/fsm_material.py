from odoo import fields, models


class FsmMaterial(models.Model):
    _name = "fsm.material"
    _description = "FSM Material"

    quantity = fields.Float()
    qty_on_hand = fields.Float(string="Quantity on Hand", related="product_id.qty_available")
    product_id = fields.Many2one(string="Product", comodel_name="product.product")
    task_id = fields.Many2one(string="Task", comodel_name="project.task")
    uom_id = fields.Many2one(string="UOM", comodel_name="uom.uom", related="product_id.uom_id")
