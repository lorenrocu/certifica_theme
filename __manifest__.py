# -*- coding: utf-8 -*-
{
    'name': 'Certifica Theme',
    'version': '13.0.1.0.0',
    'category': 'Website',
    'summary': 'Tema personalizado para Certifica',
    'description': """
        Tema personalizado para el sitio web de Certifica.
        Incluye:
        - Formulario de checkout personalizado
        - Campos DNI y RUC
        - Validación automática de tipos de identificación
        - Diseño responsivo
    """,
    'author': 'Certifica',
    'website': 'https://www.certifica.com.pe',
    'depends': [
        'base',
        'website',
        'website_sale',
        'base_vat',
        'l10n_latam_base',
        'l10n_pe',
    ],
    'data': [
        'data/ir_config_parameter.xml',
        'views/res_partner_form.xml',
        'views/assets.xml',
        'views/layout.xml',
        'views/shop_layout.xml',
        'views/product_page_custom.xml',
        'views/checkout_custom_form.xml',
        'views/payment_confirmation.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}