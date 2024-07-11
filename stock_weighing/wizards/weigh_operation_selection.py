# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models


class WeightOperationSelection(models.TransientModel):
    _name = "weigh.operation.selection"
    _description = "weigh operation selection screen"

    @api.model
    def _get_weighing_start_screen_actions(self):
        """Extend to add more options to the start screen"""
        any_operation_actions = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("stock_weighing.any_operation_actions")
        )
        actions = []
        actions.append(
            {
                "title": _("Incoming (weighing)"),
                "description": _("Incoming weighing operations"),
                "icon": "fa-arrow-down text-success",
                "method": "action_incoming_weighing_operations",
            }
        )
        if any_operation_actions:
            actions.append(
                {
                    "title": _("Incoming (any)"),
                    "description": _("Any incoming operation"),
                    "icon": "fa-arrow-down text-info",
                    "method": "action_incoming_any_operations",
                }
            )
        actions.append(
            {
                "title": _("Outgoing (weighing)"),
                "description": _("Outgoing weighing operations"),
                "icon": "fa-arrow-right text-success",
                "method": "action_outgoing_weighing_operations",
            }
        )
        if any_operation_actions:
            actions.append(
                {
                    "title": _("Outgoing (any)"),
                    "description": _("Any outgoing operation"),
                    "icon": "fa-arrow-right text-info",
                    "method": "action_outgoing_any_operations",
                }
            )
        return actions
