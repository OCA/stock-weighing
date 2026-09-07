# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase


class TestWebWidgetRemoteMeasure(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.device = cls.env["remote.measure.device"].create(
            {
                "name": "Test scale",
                "uom_id": cls.env.ref("uom.product_uom_kgm").id,
                "protocol": "f501",
                "connection_mode": "tcp",
                "host": "127.0.0.1:1234",
            }
        )
        cls.user = cls.env["res.users"].create(
            {
                "name": "Plain warehouse user",
                "login": "plain_warehouse_user",
                "groups_id": [(6, 0, [cls.env.ref("base.group_user").id])],
            }
        )

    def test_non_admin_user_can_pick_own_device(self):
        """A plain internal user (no Settings access) must be able to set
        their own preferred remote device through the systray self-service
        selector - without remote_measure_device_id in SELF_WRITEABLE_FIELDS,
        this raises AccessError since res.users.settings is otherwise not
        writeable by a non-admin.
        """
        self.user.with_user(self.user).write(
            {"remote_measure_device_id": self.device.id}
        )
        self.assertEqual(self.user.remote_measure_device_id, self.device)
