from odoo import Command

from odoo.addons.industry_fsm_sale.tests.test_industry_fsm_sale_products import TestFsmSaleProducts


setUpClass = TestFsmSaleProducts.setUpClass.__func__


def patched_setupclass(cls):
    setUpClass(cls)
    cls.task.is_saleorder = True


def test_industry_fsm_sale_products_from_fsm_tour(self):
    """
    Checks that the catalogs associated to field services tasks generated from the same main SO
    do not share their catalogs.
    """
    self.partner_1.name = "fsm tester"
    admin = self.env.ref("base.user_admin")
    field_service = self.env.ref("industry_fsm_sale.field_service_product")
    main_so = (
        self.env["sale.order"]
        .with_context(default_user_id=admin.id)
        .create({
            "partner_id": self.partner_1.id,
            "order_line": [
                Command.create({
                    "name": "task 1",
                    "product_id": field_service.id,
                }),
                Command.create({
                    "name": "task 2",
                    "product_id": field_service.id,
                }),
                Command.create({
                    "name": "task 3",
                    "product_id": field_service.id,
                }),
            ],
        })
    )
    main_so.action_confirm()
    super_product = self.env["product.product"].create({
        "name": "Super Product",
        "invoice_policy": "delivery",
        "list_price": 100.0,
        "priority": "1",
    })
    ### BEGIN PATCH ###
    for task in main_so.tasks_ids:
        task.is_saleorder = True
    ### END PATCH ###
    self.start_tour("/web", "industry_fsm_sale_products_compute_catalog_tour", login="admin")
    self.assertTrue(
        main_so.order_line.filtered(lambda sol: "task 1" in sol.task_id.name and sol.product_id == super_product)
    )
    self.assertTrue(
        main_so.order_line.filtered(lambda sol: "task 2" in sol.task_id.name and sol.product_id == super_product)
    )
    self.assertTrue(
        main_so.order_line.filtered(lambda sol: "task 3" in sol.task_id.name and sol.product_id == super_product)
    )


TestFsmSaleProducts.setUpClass = classmethod(patched_setupclass)
TestFsmSaleProducts.test_industry_fsm_sale_products_from_fsm_tour = test_industry_fsm_sale_products_from_fsm_tour
