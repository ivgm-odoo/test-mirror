{
    "name": "Easyred field service",
    "author": "Odoo PS",
    "website": "https://www.odoo.com",
    "category": "Custom Developments",
    "version": "17.0.1.0.1",
    "license": "OEEL-1",
    "depends": ["industry_fsm_sale", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "security/approval_group.xml",
        "views/field_service_form.xml",
        "views/stock_picking_form_view.xml",
    ],
    "assets": {
        "web.assets_tests": [
            "easyred_field_service/static/tests/tours/*",
        ],
    },
}
