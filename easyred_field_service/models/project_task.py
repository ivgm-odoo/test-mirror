from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    is_saleorder = fields.Boolean(string="Require Saleorder")
    is_supervised = fields.Boolean(string="To supervisor")
    picking_count = fields.Integer(string="Stock Count", compute="_compute_picking_count")
    material_ids = fields.One2many(string="Materials", comodel_name="fsm.material", inverse_name="task_id")
    picking_ids = fields.One2many(string="Delivery Order", comodel_name="stock.picking", inverse_name="service_id")

    @api.depends("picking_ids", "picking_ids.state")
    def _compute_picking_count(self):
        for task in self:
            task.picking_count = len(task.picking_ids.filtered(lambda pick: pick.state != "cancel"))

    def action_send_to_supervisor(self):
        self.is_supervised = True
        self.env["mail.activity"].create([
            {
                "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                "note": "Approve materials",
                "date_deadline": fields.Date.today(),
                "user_id": user.employee_parent_id.user_id.id,
                "res_model_id": self.env.ref("project.model_project_task").id,
                "res_id": self.id,
            }
            for user in self.user_ids
            if user.employee_parent_id.user_id
            and user.employee_parent_id.user_id.has_group("easyred_field_service.group_task_approval")
        ])

    def action_approve_by_admin(self):
        if self.user_has_groups("!easyred_field_service.group_task_approval") or not self.is_supervised:
            return False

        picking_type = self.env["stock.picking.type"].search([("code", "=", "outgoing")], limit=1)
        cust_location = self.env["stock.location"].search([("usage", "=", "customer")], limit=1)

        picking_id = self.env["stock.picking"].create({
            "partner_id": self.partner_id.id,
            "location_id": picking_type.default_location_src_id.id,
            "picking_type_id": picking_type.id,
            "origin": self.name,
            "service_id": self.id,
        })

        self.env["stock.move"].create([
            {
                "product_id": material.product_id.id,
                "name": material.product_id.name,
                "product_uom_qty": material.quantity,
                "product_uom": material.uom_id.id,
                "picking_id": picking_id.id,
                "location_id": picking_type.default_location_src_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id or cust_location.id,
            }
            for material in self.material_ids
        ])

        return True

    def action_reject(self):
        self.ensure_one()
        self.is_supervised = False

        self.env["mail.activity"].create([
            {
                "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                "note": "Review materials and send to validate",
                "date_deadline": fields.Date.today(),
                "user_id": user.id,
                "res_model_id": self.env.ref("project.model_project_task").id,
                "res_id": self.id,
            }
            for user in self.user_ids
        ])

        return True
