# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class QuickStartScreenAction(models.Model):
    _inherit = "quick.start.screen.action"

    def run_action(self):
        # We need call super to get the action and check if it is the one we want
        # to modify, in that case we will call action_stock_batch_picking_weighing
        # and show only the MO kanban/list views
        self.ensure_one()
        res = super().run_action()
        target_action = self.env.ref(
            "stock_picking_batch_weighing.quick_start_screen_action_batch_picking_any_operations",
            raise_if_not_found=False,
        )
        if not target_action or self != target_action:
            return res
        any_operation_actions = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("stock_weighing.any_operation_actions")
        )
        res = self.env["stock.move"].action_stock_batch_picking_weighing()
        base_domain = res.get("domain") or []
        if isinstance(base_domain, str):
            base_domain = safe_eval(base_domain)
        if not any_operation_actions:
            res["domain"] = expression.AND(
                [base_domain, [("has_weighing_operations", "=", True)]]
            )
        return res
