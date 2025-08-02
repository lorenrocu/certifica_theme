{
    'name': 'Certifica Theme',
    'description': 'Theme minimalista con header y footer para Odoo 13',
    'category': 'Theme/Creative',
    'version': '13.0.1.0.0',
    'author': 'Lorenzo Romero.',
    'website': 'https://helydev.com',
    'depends': ['website', 'website_sale'],
    'data': [
        'views/assets.xml',
        'views/layout.xml',
        'views/shop_layout.xml',
        'views/product_page_custom.xml',
        # 'views/checkout_custom.xml',  # Formulario heredado (comentado)
        'views/checkout_custom_form.xml',  # Nuevo formulario personalizado
        'views/payment_confirmation.xml',  # Template de confirmación de pago
    ],
    'installable': True,
    'application': False,
}