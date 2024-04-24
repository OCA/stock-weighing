# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import threading

from odoo import _, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def action_print_weight_record_label(self):
        """Speedup label printing"""
        ICP = self.env["ir.config_parameter"].sudo()
        if ICP.get_param(
            "stock_weighing_threaded_print.print_in_new_thread"
        ) and not self.env.context.get("skip_threaded_printing"):
            return self._launch_print_weighing_label_thread()
        return super().action_print_weight_record_label()

    def action_print_weighing_label_threaded(self):
        with self.pool.cursor() as new_cr:
            self = self.with_env(self.env(cr=new_cr))
            report = self.picking_type_id.weighing_label_report_id
            try:
                report.print_document(self.ids)
                self.env.user.notify_success(message="Succesfully printed")
            except Exception:
                action = self.with_context(
                    skip_threaded_printing=True
                ).action_print_weight_record_label()
                action["context"].setdefault("params", {})
                action["context"]["params"]["button_name"] = "Print"
                action["context"]["params"]["button_icon"] = "fa-print"
                self.env.user.notify_warning(
                    title=_("Direct print issue"),
                    message=_(
                        "The label(s) for <ul><b>%(operations_name)s</b></ul> "
                        "couldn't be printed. Click below to download it.",
                        operations_name=(
                            "".join(
                                [
                                    (f"<li>{sml._get_action_weighing_name()}</li>")
                                    for sml in self
                                ]
                            )
                        ),
                    ),
                    sticky=True,
                    html=True,
                    action=action,
                )

    def _launch_print_weighing_label_thread(self):
        threaded_calculation = threading.Thread(
            target=self.action_print_weighing_label_threaded,
            args=(),
        )
        threaded_calculation.start()
