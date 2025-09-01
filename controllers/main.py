# -*- coding: utf-8 -*-

import json
from odoo import http
from odoo.http import request, Response
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.controllers.main import Website


class WebsiteSaleCustom(WebsiteSale):
    def _prepare_page_values(self, values=None):
        values = super(WebsiteSaleCustom, self)._prepare_page_values(values)
        if values:
            values['website_sale_order'] = request.website.sale_get_order()
        return values
    """
    Extensión del controlador de la tienda para personalizar funcionalidades
    """
    
    def _get_search_domain(self, *args, **kwargs):
        """Extiende el dominio de búsqueda sin alterar la firma del método padre"""
        return super(WebsiteSaleCustom, self)._get_search_domain(*args, **kwargs)
    
    def _get_products_domain(self, search, category, attrib_values):
        """Delegamos al método original sin modificaciones para mantener la búsqueda nativa."""
        return super(WebsiteSaleCustom, self)._get_products_domain(search, category, attrib_values)
    
    def _get_products(self, search, category, attrib_values, **post):
        """Usamos la lógica original para respetar completamente los filtros de búsqueda."""
        return super(WebsiteSaleCustom, self)._get_products(search, category, attrib_values, **post)
    
    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>',
        '/shop/filter_products',
    ], type='http', auth="public", website=True, csrf=False)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        """
        Sobrescribimos el método shop para manejar peticiones AJAX y pricelist específico
        """
        # Forzamos 18 productos por página
        ppg = 18
        
        pricelist = request.env['product.pricelist'].sudo().browse(1573)
        if pricelist.exists():
            request.session['website_sale_pricelist'] = pricelist.id
        
        # Obtener los IDs de productos con reglas en el pricelist 1573
        item_products = request.env['product.pricelist.item'].sudo().search([('pricelist_id', '=', 1573)]).mapped('product_tmpl_id')
        # Si no hay productos en la lista, forzar un dominio vacío
        if item_products:
            product_filter_domain = [('id', 'in', item_products.ids)]
        else:
            product_filter_domain = [('id', '=', 0)]
        
        # Si es una petición AJAX, solo devolvemos los productos
        if request.httprequest.headers.get('X-Requested-With') == 'XMLHttpRequest':
            response = super(WebsiteSaleCustom, self).shop(
                page=page, category=category, search=search, ppg=ppg, **post)
            # Filtrar productos en el contexto de respuesta combinando búsqueda con pricelist
            if hasattr(response, 'qcontext') and response.qcontext:
                products = response.qcontext.get('products')
                if products:
                    # Intersección entre productos de la búsqueda y productos del pricelist
                    pricelist_products = item_products if item_products else request.env['product.template'].sudo().browse([])
                    products = products & pricelist_products
                    products = products.with_context(pricelist=pricelist.id if pricelist.exists() else None)
                    response.qcontext['products'] = products
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
        
        # Para peticiones normales, llamamos al método padre
        response = super(WebsiteSaleCustom, self).shop(
            page=page, category=category, search=search, ppg=ppg, **post)
        # Filtrar productos en el contexto de respuesta combinando búsqueda con pricelist
        if hasattr(response, 'qcontext') and response.qcontext:
            products = response.qcontext.get('products')
            if products:
                # Intersección entre productos de la búsqueda y productos del pricelist
                pricelist_products = item_products if item_products else request.env['product.template'].sudo().browse([])
                products = products & pricelist_products
                products = products.with_context(pricelist=pricelist.id if pricelist.exists() else None)
                response.qcontext['products'] = products
        return response

    @http.route(['/shop/cart/quantity'], type='json', auth="public", website=True)
    def cart_quantity(self):
        """Devuelve la cantidad de artículos en el carrito como JSON."""
        return request.website.sale_get_order().cart_quantity or 0

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        """
        Sobrescribimos el método cart_update para asegurar que use el pricelist correcto
        """
        # Asegurar que el website use el pricelist correcto
        pricelist = request.env['product.pricelist'].sudo().browse(1573)
        if pricelist.exists():
            request.session['website_sale_pricelist'] = pricelist.id
        
        # Llamar al método padre
        return super(WebsiteSaleCustom, self).cart_update(
            product_id=product_id, add_qty=add_qty, set_qty=set_qty, **kw)

    @http.route(['/shop/test_pricelist'], type='http', auth="public", website=True)
    def test_pricelist(self):
        """
        Método de prueba para verificar que el pricelist funciona correctamente
        """
        pricelist = request.env['product.pricelist'].sudo().browse(1573)
        if not pricelist.exists():
            return "Error: El pricelist con ID 1573 no existe"
        
        # Obtener algunos productos para probar
        products = request.env['product.template'].sudo().search([('sale_ok', '=', True)], limit=5)
        
        result = f"Pricelist encontrado: {pricelist.name}<br><br>"
        result += "Productos de prueba:<br>"
        
        for product in products:
            price_with_pricelist = product.with_context(pricelist=pricelist.id).price
            list_price = product.list_price
            result += f"- {product.name}: Lista: {list_price}, Pricelist: {price_with_pricelist}<br>"
        
        return result
