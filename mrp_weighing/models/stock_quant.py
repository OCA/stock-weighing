from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def name_get(self):
        if not self.env.context.get("show_lot_product"):
            return super().name_get()

        result = []
        for rec in self:
            name = (
                f"{rec.lot_id.name or ''} - "
                f"{rec.location_id.display_name}/{rec.product_id.display_name} "
                f"({rec.quantity} {rec.product_uom_id.name})"
            )
            result.append((rec.id, name))
        return result
