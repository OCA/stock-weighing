# Copyright 2023 Tecnativa - David Vidal
# Copyright 2025 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import socket
from contextlib import closing
from urllib.parse import urlparse

from odoo import _, fields, models


class RemoteMeasureDevice(models.Model):
    _name = "remote.measure.device"
    _description = "Remote measure device"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    uom_id = fields.Many2one(
        string="Unit of measure",
        comodel_name="uom.uom",
        required=True,
    )
    uom_category_id = fields.Many2one(related="uom_id.category_id")
    uom_factor = fields.Float(related="uom_id.factor")
    protocol = fields.Selection(
        selection=[("f501", "Scale F501")],
        help="Operating protocol",
        required=True,
    )
    connection_mode = fields.Selection(
        selection=[
            ("websockets", "Web Sockets"),
            ("webservices", "Web Services"),
            ("tcp", "Direct connection"),
        ],
        required=True,
    )
    host = fields.Char(required=True)
    instant_read = fields.Boolean(help="Read right on as the widget gets rendered")
    non_stop_read = fields.Boolean(
        help="Don't stop reading until the widget is disposed"
    )
    read_interval = fields.Integer(
        help="(0 for no sleep between reads) Miliseconds to wait between device reads"
    )
    test_measure = fields.Float(default=0.0)

    def test_tcp_connection(self):
        """
        Verify the TCP connection with the remote device
        """
        parsed_address = urlparse(f"//{self.host}")
        host = parsed_address.hostname
        port = parsed_address.port
        timeout = 2.0
        try:
            with closing(socket.create_connection((host, port), timeout)):
                return self.test_connection_notification("success", host, port)
        except (socket.timeout, socket.error):
            return self.test_connection_notification("danger", host, port)

    def test_connection_notification(self, notification_type, host, port):
        if notification_type == "success":
            message = _(
                "Successfully connected to %(host)s:%(port)s", host=host, port=port
            )
        else:
            message = _("Connection failure to %(host)s:%(port)s", host=host, port=port)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Test connection"),
                "message": message,
                "sticky": False,
                "type": notification_type,
            },
        }
