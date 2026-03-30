# Copyright 2026 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class WeighingWizard(models.TransientModel):
    _inherit = "weighing.wizard"

    def record_weight(self):
        action = super().record_weight()
        if self.show_auto_lot_info and not self.lot_id:
            return {
                "type": "ir.actions.act_window",
                "res_model": "stock.production.lot",
                "view_mode": "form",
                "res_id": self.selected_move_line_id.lot_id.id,
                "views": [[False, "form"]],
                "target": "new",
                "context": {
                    "action_weighing_wizard": self.reload_action_wizard()
                    if self.env.context.get("reload_wizard_action")
                    else False,
                },
            }
        return action

    def reload_action_wizard(self):
        res = super().reload_action_wizard()
        res["views"] = [[False, "form"]]
        return res
