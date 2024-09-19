from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "project.task", "to_supervisor", "is_supervised")
