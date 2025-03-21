from odoo import fields, models


class ResUsersSettings(models.Model):
    _inherit = "res.users.settings"

    remote_measure_device_id = fields.Many2one(
        comodel_name="remote.measure.device",
        help="Default remote measure device for this user",
    )
