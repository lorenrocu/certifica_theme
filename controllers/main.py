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
            # Obtener orden de venta con manejo robusto de errores
            try:
                order = request.website.sale_get_order(force_create=True)
                
                # Si la orden no tiene pricelist_id, asignar uno por defecto
                if order and not order.pricelist_id:
                    default_pricelist = request.env['product.pricelist'].sudo().search([
                        ('active', '=', True)
                    ], limit=1)
                    
                    if not default_pricelist:
                        # Crear pricelist por defecto si no existe
                        default_pricelist = request.env['product.pricelist'].sudo().create({
                            'name': 'Lista de Precios por Defecto',
                            'active': True,
                            'currency_id': request.env.ref('base.PEN').id if request.env.ref('base.PEN') else 1,
                        })
                    
                    order.pricelist_id = default_pricelist.id
                
                # Si aún no hay orden, crear una de emergencia
                if not order:
                    order = self._create_emergency_order()
                
                values['website_sale_order'] = order
                
            except Exception as e:
                # En caso de error, crear orden de emergencia
                import logging
                _logger = logging.getLogger(__name__)
                _logger.error(f"Error al obtener website_sale_order: {str(e)}")
                values['website_sale_order'] = self._create_emergency_order()
        
        return values
    
    def _create_emergency_order(self):
        """Crear orden de emergencia para evitar errores de template"""
        try:
            # Obtener valores por defecto
            default_pricelist = request.env['product.pricelist'].sudo().search([
                ('active', '=', True)
            ], limit=1)
            
            if not default_pricelist:
                default_pricelist = request.env['product.pricelist'].sudo().create({
                    'name': 'Lista de Precios de Emergencia',
                    'active': True,
                    'currency_id': request.env.ref('base.PEN').id if request.env.ref('base.PEN') else 1,
                })
            
            default_partner = request.env['res.partner'].sudo().search([
                ('customer', '=', True)
            ], limit=1)
            
            if not default_partner:
                default_partner = request.env['res.partner'].sudo().create({
                    'name': 'Cliente por Defecto',
                    'customer': True,
                    'is_company': False,
                })
            
            # Crear orden de emergencia
            emergency_order = request.env['sale.order'].sudo().create({
                'name': 'Orden de Emergencia',
                'partner_id': default_partner.id,
                'pricelist_id': default_pricelist.id,
                'currency_id': default_pricelist.currency_id.id,
                'state': 'draft',
            })
            
            return emergency_order
            
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Error al crear orden de emergencia: {str(e)}")
            return None
    
    @http.route(['/shop/cart_summary'], type='json', auth="public", website=True)
    def get_cart_summary_data(self):
        """Endpoint específico para obtener datos seguros del cart_summary"""
        try:
            # Obtener orden con manejo robusto
            order = request.website.sale_get_order(force_create=True)
            
            # Si no hay orden, crear una de emergencia
            if not order:
                order = self._create_emergency_order()
            
            # Verificar que la orden tenga pricelist_id
            if order and not order.pricelist_id:
                default_pricelist = request.env['product.pricelist'].sudo().search([
                    ('active', '=', True)
                ], limit=1)
                
                if not default_pricelist:
                    default_pricelist = request.env['product.pricelist'].sudo().create({
                        'name': 'Lista de Precios Cart Summary',
                        'active': True,
                        'currency_id': request.env.ref('base.PEN').id if request.env.ref('base.PEN') else 1,
                    })
                
                order.pricelist_id = default_pricelist.id
            
            # Preparar datos seguros
            cart_data = {
                'order_id': order.id if order else None,
                'amount_total': order.amount_total if order else 0.0,
                'currency_symbol': order.pricelist_id.currency_id.symbol if (order and order.pricelist_id and order.pricelist_id.currency_id) else 'S/',
                'cart_quantity': order.cart_quantity if order else 0,
                'has_valid_pricelist': bool(order and order.pricelist_id and order.pricelist_id.currency_id),
            }
            
            return cart_data
            
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f"Error en get_cart_summary_data: {str(e)}")
            
            # Retornar datos de emergencia
            return {
                'order_id': None,
                'amount_total': 0.0,
                'currency_symbol': 'S/',
                'cart_quantity': 0,
                'has_valid_pricelist': False,
            }
    
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
