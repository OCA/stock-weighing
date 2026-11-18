# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_add_move_line(self):
        action = super().action_add_move_line()
        if self.secondary_uom_id:
            extra_info = (
                f"[{self.secondary_uom_id.display_name} - {self.secondary_uom_qty}]"
            )
            action["name"] = f'{action["name"]} {extra_info}'
        return action
