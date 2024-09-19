from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "project.task", "to_supervisor", "is_supervised")
    util.rename_xmlid(cr, "easyred_field_service.field_service_form_inherit_easyred", "easyred_field_service.view_task_form2_inherit")
