import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-stock-weighing",
    description="Meta package for oca-stock-weighing Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-partner_delivery_zone_weighing>=15.0dev,<15.1dev',
        'odoo-addon-stock_weighing>=15.0dev,<15.1dev',
        'odoo-addon-web_widget_remote_measure>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
