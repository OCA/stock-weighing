# Copyright 2026 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import socket
import threading
import time

from odoo.tests import HttpCase, tagged

# F501 frame: [STX][stable flag][sign][weight][ETX]
F501_STABLE_FRAME = b"\x02 +001.250\x03"


class FakeScale:
    """Minimal TCP server answering every connection with a fixed frame."""

    def __init__(self, frame, delay=0):
        self.frame = frame
        self.delay = delay
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("127.0.0.1", 0))
        self.server.listen()
        self.server.settimeout(5)
        self.port = self.server.getsockname()[1]
        self.thread = threading.Thread(target=self._serve, daemon=True)

    def _serve(self):
        try:
            conn, _addr = self.server.accept()
        except OSError:
            return
        with conn:
            time.sleep(self.delay)
            conn.sendall(self.frame)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.server.close()
        self.thread.join(timeout=5)


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@tagged("post_install", "-at_install")
class TestRemoteMeasureTcp(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.device = cls.env["remote.measure.device"].create(
            {
                "name": "Test scale",
                "uom_id": cls.env.ref("uom.product_uom_kgm").id,
                "protocol": "f501",
                "connection_mode": "tcp",
                "host": "127.0.0.1:1",
            }
        )

    def test_tcp_connection_success(self):
        with FakeScale(F501_STABLE_FRAME) as scale:
            self.device.host = f"127.0.0.1:{scale.port}"
            action = self.device.test_tcp_connection()
        self.assertEqual(action["params"]["type"], "success")

    def test_tcp_connection_failure(self):
        self.device.host = f"127.0.0.1:{_free_port()}"
        action = self.device.test_tcp_connection()
        self.assertEqual(action["params"]["type"], "danger")

    def test_request_weight_route(self):
        """The widget reads the scale through this JSON-RPC route"""
        self.authenticate("admin", "admin")
        with FakeScale(F501_STABLE_FRAME) as scale:
            self.device.host = f"127.0.0.1:{scale.port}"
            response = self.make_jsonrpc_request(
                f"/remote_measure_device/{self.device.id}", {"command": False}
            )
        self.assertEqual(response, F501_STABLE_FRAME.decode())

    def test_request_weight_route_non_utf8_frame(self):
        """A byte that isn't valid UTF-8 (line noise) must not break the reply"""
        self.authenticate("admin", "admin")
        frame = b"\x02 +001.250\xb0\x03"
        with FakeScale(frame) as scale:
            self.device.host = f"127.0.0.1:{scale.port}"
            response = self.make_jsonrpc_request(
                f"/remote_measure_device/{self.device.id}", {"command": False}
            )
        self.assertEqual(response, frame.decode("latin-1"))

    def test_request_weight_route_timeout(self):
        """The timeout requested by the widget is the one used to read"""
        self.authenticate("admin", "admin")
        with FakeScale(F501_STABLE_FRAME, delay=1.5) as scale:
            self.device.host = f"127.0.0.1:{scale.port}"
            response = self.make_jsonrpc_request(
                f"/remote_measure_device/{self.device.id}",
                {"command": False, "timeout": 3},
            )
        self.assertEqual(response, F501_STABLE_FRAME.decode())

    def test_request_weight_route_unreachable_device(self):
        """A refused connection is reported to the widget instead of raising"""
        self.authenticate("admin", "admin")
        self.device.host = f"127.0.0.1:{_free_port()}"
        response = self.make_jsonrpc_request(
            f"/remote_measure_device/{self.device.id}", {"command": False}
        )
        self.assertIsInstance(response, dict)
        self.assertTrue(response.get("error"))
