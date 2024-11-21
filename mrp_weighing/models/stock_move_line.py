# Copyright 2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def action_reset_weights(self):
        res = super().action_reset_weights()
        for move in self.move_id.filtered(
            lambda sm: sm.product_id == sm.production_id.product_id
        ):
            move.production_id.qty_producing = move.quantity_done
        return res
