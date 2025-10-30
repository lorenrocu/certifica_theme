# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """
    Post-migración para desactivar vistas QWeb en BD que heredan de `web.login_layout`
    pero intentan modificar elementos del layout del Website (por ejemplo,
    //div[@id='wrapwrap']/header/nav), lo que causa errores de XPath al renderizar
    la plantilla de login.

    Caso reportado:
      ValueError: El elemento "//div[@id='wrapwrap']/header/nav" no puede ser localizado en la vista padre
      Contexto: Vista `preHeader` [view_id: 7371] Template: web.login_layout
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    View = env['ir.ui.view']

    # Localizar la vista padre web.login_layout
    parent_login = View.search([('key', '=', 'web.login_layout')], limit=1)

    # Acumular vistas a desactivar
    to_disable = View.browse([])

    # Heurística: todas las vistas que hereden de web.login_layout
    candidates = View.search([('inherit_id', '=', parent_login.id)]) if parent_login else View.search([])

    patterns = [
        'wrapwrap',
        '/header',
        'header/nav',
        "/div[@id='wrapwrap']/header/nav",
        'o_footer_copyright',
    ]

    for v in candidates:
        arch = (v.arch_db or '').lower()
        if any(p.lower() in arch for p in patterns):
            to_disable |= v

    # Añadir explícitamente la vista reportada por ID (si existe en esta BD)
    direct = View.browse(7371)
    if direct.exists():
        to_disable |= direct

    # Desactivar vistas problemáticas
    if to_disable:
        to_disable.write({'active': False})
        for v in to_disable:
            try:
                print(
                    "[certifica_theme] Desactivada vista problematica id=%s name=%s inherit=%s"
                    % (v.id, v.name, v.inherit_id.key if v.inherit_id else None)
                )
            except Exception:
                pass
    else:
        print("[certifica_theme] No se encontraron vistas adicionales para desactivar en 13.0.1.0.2.")