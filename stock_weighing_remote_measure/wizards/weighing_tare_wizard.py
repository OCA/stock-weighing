# Copyright 2026 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class WeighingTareWizard(models.TransientModel):
    _name = "weighing.tare.wizard"
    _description = "Weighing tares configuration wizard"

    def _default_tare_ids(self):
        return self.env["weighing.tare"].with_context(active_test=False).search([])

    tare_ids = fields.Many2many(
        comodel_name="weighing.tare",
        relation="weighing_tare_wizard_tare_rel",
        default=lambda self: self._default_tare_ids(),
        context={"active_test": False},
    )
    # Tares loaded when the wizard was opened, so we only remove the ones the
    # user actually dropped from the list
    origin_tare_ids = fields.Many2many(
        comodel_name="weighing.tare",
        relation="weighing_tare_wizard_origin_tare_rel",
        default=lambda self: self._default_tare_ids(),
        context={"active_test": False},
    )

    def action_apply(self):
        """Inline edits are saved along with the wizard. Remove the dropped ones"""
        for wizard in self:
            (wizard.origin_tare_ids - wizard.tare_ids).unlink()
        return True
