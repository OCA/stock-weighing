# Copyright 2023 Tecnativa - David Vidal
# Copyright 2025 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    remote_measure_device_id = fields.Many2one(
        comodel_name="remote.measure.device",
        help="Default remote measure device for this user",
    )

    def action_close_remote_device_wizard(self):
        return {
            "type": "ir.actions.act_window_close",
        }

    # Allow users without setting security group read and write the remote device
    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ["remote_measure_device_id"]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + [
            "remote_measure_device_id",
        ]
