from datetime import datetime
import math
import pytz
from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def get_current_datetime_myanmar(self):
        myanmar_tz = pytz.timezone('Asia/Yangon')
        now_utc = datetime.now(pytz.utc)
        now_myanmar = now_utc.astimezone(myanmar_tz)
        return now_myanmar.strftime('%d/%m/%Y %H:%M:%S')