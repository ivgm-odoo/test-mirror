from odoo.addons.industry_fsm_stock.tests.test_fsm_stock_ui import TestFsmStockUI


setUpClass = TestFsmStockUI.setUpClass.__func__


def patched_setupclass(cls):
    setUpClass(cls)
    cls.task.is_saleorder = True


TestFsmStockUI.setUpClass = classmethod(patched_setupclass)
