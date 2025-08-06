from odoo import models, fields, api
import math
from operator import itemgetter


class Products(models.Model):
    _inherit = 'product.product'

    def convert_to_uom_desc_for_transfer_report(self, rec, ref_qty):

        if not ref_qty:
            return ""

        is_negative = ref_qty < 0
        remaining_qty = abs(ref_qty)

        if not self.env.company.use_loose_uom:
            if not rec.uom_lines:
                return f"{int(ref_qty)} {rec.uom_id.name or 'PCs'}"

            uom_definitions = []
            for uom in rec.uom_lines:
                # 'smaller' type uom (e.g., Dozen = 12 PCs) အတွက် ratio ကိုမှန်ကန်အောင်တွက်သည်
                effective_ratio = uom.ratio if uom.uom_type != 'smaller' else (1 / uom.ratio if uom.ratio != 0 else 0)
                if effective_ratio > 0:
                    uom_definitions.append({
                        'name': uom.name,
                        'ratio': effective_ratio
                    })

            sorted_uoms = sorted(uom_definitions, key=itemgetter('ratio'), reverse=True)

            uom_parts = []
            for uom in sorted_uoms:
                if remaining_qty < uom['ratio']:
                    continue

                num_of_units = math.floor(remaining_qty / uom['ratio'])
                remaining_qty %= uom['ratio']

                if num_of_units > 0:
                    uom_parts.append(f"{int(num_of_units)} {uom['name']}")

            if remaining_qty > 0:
                base_uom_name = self.env['uom.uom'].search([('uom_type', '=', 'reference')], limit=1).name or 'PCs'
                uom_parts.append(f"{round(remaining_qty, 2)} {base_uom_name}")

            uom_desc = " ".join(uom_parts)

        else:
            box_ratio = rec.box_uom_id.ratio if rec.box_uom_id and rec.box_uom_id.ratio > 0 else 0
            loose_ratio = rec.loose_uom_id.ratio if rec.loose_uom_id and rec.loose_uom_id.ratio > 0 else 1

            if box_ratio > 0:
                box_qty, remainder = divmod(remaining_qty, box_ratio)
                loose_qty = remainder / loose_ratio
                uom_desc = f"{int(box_qty)}/{math.floor(loose_qty)}"
            else:
                loose_qty = remaining_qty / loose_ratio
                uom_desc = f"0/{math.floor(loose_qty)}"

        return f"-{uom_desc}" if is_negative else uom_desc