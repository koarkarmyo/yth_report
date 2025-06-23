import math

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"


    test_field = fields.Char("My field")

    def get_current_page(self, order_lines):
        return math.ceil(len(order_lines) / 13)