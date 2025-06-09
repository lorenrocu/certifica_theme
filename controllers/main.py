# -*- coding: utf-8 -*-

import json
from odoo import http
from odoo.http import request, Response
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import QueryURL


class WebsiteSaleCustom(WebsiteSale):
    """
    Extensión del controlador de la tienda para personalizar funcionalidades
    """
    
    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        """
        Heredamos el método original para mantener la funcionalidad de búsqueda
        """
        return super(WebsiteSaleCustom, self)._get_search_domain(
            search, category, attrib_values, search_in_description)
    
    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>',
        '/shop/filter_products',
    ], type='http', auth="public", website=True, csrf=False)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        """
        Sobrescribimos el método shop para manejar peticiones AJAX
        """
        # Forzamos 18 productos por página
        ppg = 18
        
        # Si es una petición AJAX, solo devolvemos los productos
        if request.httprequest.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Obtenemos los atributos seleccionados
            attrib_list = request.httprequest.args.getlist('attrib')
            
            # Llamamos al método original para obtener los productos
            response = super(WebsiteSaleCustom, self).shop(
                page=page, category=category, search=search, ppg=ppg, **post)
            
            # Renderizamos solo el template de productos
            products_html = request.env['ir.ui.view']._render_template(
                'website_sale.products',
                response.qcontext
            )
            
            return Response(
                json.dumps({
                    'products_html': products_html,
                    'filters': response.qcontext.get('filters', {})
                }),
                headers={'Content-Type': 'application/json'}
            )
        
        # Para peticiones normales, comportamiento estándar
        return super(WebsiteSaleCustom, self).shop(
            page=page, category=category, search=search, ppg=ppg, **post)
