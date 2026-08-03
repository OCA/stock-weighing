# Copyright 2026 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Weighing Owner Restriction",
    "summary": "Apply the owner restriction rules to the weighing wizard "
    "quant and lot selection",
    "version": "18.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-weighing",
    "license": "AGPL-3",
    "category": "Inventory",
    "depends": [
        "stock_weighing",
        "stock_owner_restriction",
    ],
    "data": ["wizards/weighing_wizard_views.xml"],
    "auto_install": True,
    "maintainers": ["sergio-teruel"],
}
