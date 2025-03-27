# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    _logger.info("Pre-creating weighing state column to avoid computing everyone...")
    env.cr.execute(
        "ALTER TABLE stock_move ADD COLUMN IF NOT EXISTS weighing_state VARCHAR"
    )


def post_init_hook(env):
    """Recompute weighing_state only in pending moves"""
    _logger.info("Computing weighing state on pending moves...")
    env["stock.move"].search(
        [
            ("has_weight", "=", True),
            ("state", "in", ("assigned", "confirmed", "waiting")),
        ]
    )._compute_weighing_state()
