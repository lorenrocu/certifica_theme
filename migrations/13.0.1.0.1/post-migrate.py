# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """
    Desactiva vistas QWeb en base de datos que heredan indebidamente de `web.login_layout`
    y contienen XPaths dirigidos al footer del website (por ejemplo, o_footer_copyright),
    lo que provoca errores de XPath durante la carga del template.

    Ejemplo de error:
      ValueError: El elemento "//div[hasclass('o_footer_copyright')]//div[hasclass('row')]/div[1]" no puede ser localizado en la vista padre
      Contexto: Vista `add_footer_arrow` heredando de `web.login_layout`
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    View = env['ir.ui.view']

    # 1) Filtro principal: heredando de web.login_layout y con referencia a o_footer_copyright
    parent_login = View.search([('key', '=', 'web.login_layout')], limit=1)
    views = env['ir.ui.view']
    to_disable = env['ir.ui.view']
    if parent_login:
        to_disable = View.search([
            ('inherit_id', '=', parent_login.id),
            ('arch_db', 'ilike', "o_footer_copyright"),
        ])

    # 2) Heurística adicional: nombre parecido a add_footer_arrow
    if not to_disable:
        to_disable = View.search([
            ('name', 'ilike', 'add_footer_arrow'),
            ('inherit_id', '=', parent_login.id) if parent_login else ('inherit_id', '!=', False),
        ])

    # 3) Intento directo por ID reportado en logs (7357) si existiese en esta BD
    direct = View.browse(7357)
    if direct.exists():
        to_disable |= direct

    if to_disable:
        to_disable.write({'active': False})
        for v in to_disable:
            try:
                print("[certifica_theme] Desactivada vista problemática id=%s name=%s inherit=%s" % (v.id, v.name, v.inherit_id.key if v.inherit_id else None))
            except Exception:
                # Evitar cualquier bloqueo por acceso a campos computados en logs
                pass
    else:
        print("[certifica_theme] No se encontraron vistas problemáticas para desactivar.")