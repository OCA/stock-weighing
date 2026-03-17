# Copyright 2026 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Weighing assistant configure lots on creations",
    "summary": "Allow to configure the lots created",
    "version": "15.0.1.0.0",
    "development_status": "Beta",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-weighing",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["stock_weighing_auto_create_lot"],
    "data": ["wizards/weighing_wizard_views.xml"],
    "maintainers": ["CarlosRoca13"],
    "assets": {
        "web.assets_backend": [
            "/stock_weighing_auto_create_lot_config/static/src/js/*.js"
        ],
        "web.assets_qweb": [
            "/stock_weighing_auto_create_lot_config/static/src/xml/quick_create_lot.xml",
        ],
    },
}
