# Copyright 2026 Tecnativa - Andrii Kompaniiets
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env, "mrp_weighing", "migrations/18.0.1.0.0/noupdate_changes.xml"
    )
