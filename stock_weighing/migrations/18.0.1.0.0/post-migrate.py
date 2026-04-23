# Copyright 2026 Tecnativa - Andrii Kompaniiets
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _update_qty_picked(env):
    """
    It needs to sync the new qty_picked field with the quantity when the
    state is done or when a weight is recorded on stock.move / stock.move.line
    """
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE stock_move
            SET qty_picked=quantity
            WHERE weighing_state='weighed' OR state='done'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE stock_move_line
            SET qty_picked=quantity
            WHERE has_recorded_weight=true OR state='done'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _update_qty_picked(env)
