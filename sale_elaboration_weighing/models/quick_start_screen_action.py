# Copyright 2026 Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, models


class QuickStartScreenAction(models.Model):
    _inherit = "quick.start.screen.action"

    def run_action(self):
        # We need call super to get the action and check if it is the one
        # we want to modify, in that case we will call action_mrp_production_weighing
        # and show only the MO kanban/list views
        self.ensure_one()
        res = super().run_action()
        target_action = self.env.ref(
            "sale_elaboration_weighing.quick_start_screen_action_elaborations",
            raise_if_not_found=False,
        )
        if not target_action or self != target_action:
            return res
        res["display_name"] = _("Weigh elaborations")
        return res
