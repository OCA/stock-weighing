# Copyright 2024 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, models


class WeightOperationSelection(models.TransientModel):
    _inherit = "weigh.operation.selection"

    @api.model
    def _get_weighing_start_screen_actions(self):
        actions = super()._get_weighing_start_screen_actions()
        actions.append(
            {
                "title": _("Production Orders"),
                "description": _("Weighing Production Orders"),
                "icon": "fa-wrench",
                "method": "action_mrp_production_weighing",
            }
        )
        return actions
