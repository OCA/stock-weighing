# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class WeighingWizard(models.TransientModel):
    _inherit = "weighing.wizard"

    def record_weight(self):
        """Print in background if needed so we can handle exceptions"""
        print_in_new_thread = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("stock_weighing_threaded_print.print_in_new_thread")
        )
        if (
            self.print_label
            and print_in_new_thread
            and not self.env.context.get("skip_threaded_printing")
        ):
            self.print_label = False
            super().record_weight()
            self._cr.postcommit.add(
                self.selected_move_line_id.action_print_weight_record_label
            )
            return {"type": "ir.actions.act_window_close"}
        return super().record_weight()
