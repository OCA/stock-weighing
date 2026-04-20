# Copyright 2026 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE stock_move ADD COLUMN IF NOT EXISTS picking_partner_id INTEGER",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move sm
        SET picking_partner_id = sp.partner_id
        FROM stock_picking sp
        WHERE sm.picking_id = sp.id
        """,
    )
