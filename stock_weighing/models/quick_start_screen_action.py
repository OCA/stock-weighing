# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models
from odoo.osv import expression


class QuickStartScreenAction(models.Model):
    _inherit = "quick.start.screen.action"

    def run_action(self):
        # We override the action so that when it involves actions of the
        # type `weighing_operation_action` and the context key
        # `any_operation_actions` does not exist, the domain is extended
        # and the context is modified to activate the `to_weigh` header
        # button.
        res = super().run_action()
        if res.get("xml_id", "") == "stock_weighing.weighing_operation_action":
            any_operation_actions = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("stock_weighing.any_operation_actions")
            )
            if not any_operation_actions:
                res["domain"] = expression.AND(
                    [res["domain"], [("has_weight", "=", True)]]
                )
                res["context"].pop("show_weight_detail_buttons", None)
                res["context"] = dict(search_default_to_weigh=1, **res["context"])
        return res
