# Copyright 2026 Tecnativa - Andrii Kompaniiets
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

from odoo.addons.stock_move_line_qty_picked.hooks import initialize_picked_quantities


def _update_qty_picked(env):
    """
    The recorded weights are the picked quantities of the move lines, so pick
    them before filling the shared picked quantities. The picked quantity of
    the moves is computed from their lines.
    """
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE stock_move_line
            SET picked = TRUE
            WHERE has_recorded_weight AND state NOT IN ('done', 'cancel')
        """,
    )
    initialize_picked_quantities(env.cr)


@openupgrade.migrate()
def migrate(env, version):
    _update_qty_picked(env)
