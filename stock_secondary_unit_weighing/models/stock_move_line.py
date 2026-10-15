# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_action_weighing_name(self):
        """Add secondary unit info"""
        action_name = super()._get_action_weighing_name()
        if self.secondary_uom_id:
            extra_info = (
                f"[{self.secondary_uom_id.display_name} - {self.secondary_uom_qty}]"
            )
            action_name = f"{action_name} {extra_info}"
        return action_name
