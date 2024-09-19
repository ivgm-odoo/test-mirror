from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    material_ids = fields.One2many(comodel_name="fsm.material", inverse_name="task_id", string="Materials")

    is_saleorder = fields.Boolean(string="Require Saleorder")

    to_supervisor = fields.Boolean(string="To supervisor", default=False)
    picking_ids = fields.One2many(comodel_name="stock.picking", inverse_name="service_id", string="Delivery Order")
    picking_count = fields.Integer(string="Stock Count", compute="_compute_delivery_count")

    @api.depends("picking_ids", "picking_ids.state")
    def _compute_delivery_count(self):
        for task in self:
            task.picking_count = len(task.picking_ids.filtered(lambda pick: pick.state != "cancel"))

    def action_send_to_supervisor(self):
        for rec in self:
            rec.to_supervisor = True

        for user in self.user_ids:
            manager_id = user.employee_parent_id.user_id if user.employee_parent_id.user_id else None
            if manager_id and manager_id.user_has_groups("easyred_field_service.group_task_approval"):
                self.env["mail.activity"].create({
                    "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                    "note": "Approve materials",
                    "date_deadline": fields.Date.today(),
                    "user_id": manager_id.id,
                    "res_model_id": self.env.ref("project.model_project_task").id,
                    "res_id": self.id,
                })

    def action_approve_by_admin(self):
        if not self.user_has_groups("easyred_field_service.group_task_approval") or not self.to_supervisor:
            return False

        picking = self.env["stock.picking"]
        move = self.env["stock.move"]
        picking_type = self.env["stock.picking.type"].search([("code", "=", "outgoing")])
        cust_location = self.env["stock.location"].search([("usage", "=", "customer")])
        if len(picking_type) > 1:
            picking_type = picking_type[0]
        vals = {
            "partner_id": self.partner_id.id,
            "location_id": picking_type.default_location_src_id.id,
            "picking_type_id": picking_type.id,
            "origin": self.name,
            "service_id": self.id,
        }
        picking_id = picking.create(vals)

        for material in self.material_ids:
            move.create({
                "product_id": material.product_id.id,
                "name": material.product_id.name,
                "product_uom_qty": material.quantity,
                "product_uom": material.uom_id.id,
                "picking_id": picking_id.id,
                "location_id": picking_type.default_location_src_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id or cust_location.id,
            })
        # look into how sale.order creates stock.picking
        return True

    def action_reject(self):
        self.ensure_one()
        self.to_supervisor = False

        for user in self.user_ids:
            self.env["mail.activity"].create({
                "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                "note": "Review materials and send to validate",
                "date_deadline": fields.Date.today(),
                "user_id": user.id,
                "res_model_id": self.env.ref("project.model_project_task").id,
                "res_id": self.id,
            })
        return True
