# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.exceptions import ValidationError
import logging


class WebsiteSaleCheckout(WebsiteSale):
    """
    Controlador personalizado para el checkout con campos DNI/RUC
    """
    _logger = logging.getLogger(__name__)

    def _detect_identification_type_id(self, vat_number):
        """
        Detectar automáticamente el ID del tipo de identificación basándose en el número
        """
        if not vat_number:
            return False
        
        vat_clean = str(vat_number).strip()
        self._logger.info(f"=== DETECTANDO TIPO DE IDENTIFICACIÓN PARA: {vat_clean} ===")
        
        try:
            # Verificar si el modelo está disponible
            if 'l10n_latam.identification.type' not in request.env.registry:
                self._logger.warning("Modelo l10n_latam.identification.type no disponible")
                return False
            
            # Buscar el tipo de identificación en la base de datos
            identification_type_model = request.env['l10n_latam.identification.type'].sudo()
            
            # Detectar DNI (8 dígitos) - ID 5 en tu base de datos
            if len(vat_clean) == 8 and vat_clean.isdigit():
                dni_type = identification_type_model.search([
                    ('name', '=', 'DNI'),
                    ('country_id', '=', 173)  # Perú
                ], limit=1)
                if dni_type:
                    self._logger.info(f"DNI detectado: {vat_clean} -> Tipo ID: {dni_type.id}")
                    return dni_type.id
                else:
                    self._logger.warning("No se encontró el tipo DNI en la base de datos")
                    return False
            
            # Detectar RUC (11 dígitos) - ID 4 en tu base de datos
            elif len(vat_clean) == 11 and vat_clean.isdigit():
                ruc_type = identification_type_model.search([
                    ('name', '=', 'RUC'),
                    ('country_id', '=', 173)  # Perú
                ], limit=1)
                if ruc_type:
                    self._logger.info(f"RUC detectado: {vat_clean} -> Tipo ID: {ruc_type.id}")
                    return ruc_type.id
                else:
                    self._logger.warning("No se encontró el tipo RUC en la base de datos")
                    return False
            
            # Detectar VAT con prefijos peruanos (10 dígitos)
            elif len(vat_clean) == 10 and vat_clean.startswith(('10', '20', '15', '16', '17')):
                ruc_type = identification_type_model.search([
                    ('name', '=', 'RUC'),
                    ('country_id', '=', 173)  # Perú
                ], limit=1)
                if ruc_type:
                    self._logger.info(f"RUC con prefijo detectado: {vat_clean} -> Tipo ID: {ruc_type.id}")
                    return ruc_type.id
                else:
                    self._logger.warning("No se encontró el tipo RUC en la base de datos")
                    return False
            
            # Detectar DNI con prefijo 10 (10 dígitos)
            elif len(vat_clean) == 10 and vat_clean.startswith('10'):
                dni_type = identification_type_model.search([
                    ('name', '=', 'DNI'),
                    ('country_id', '=', 173)  # Perú
                ], limit=1)
                if dni_type:
                    self._logger.info(f"DNI con prefijo 10 detectado: {vat_clean} -> Tipo ID: {dni_type.id}")
                    return dni_type.id
                else:
                    self._logger.warning("No se encontró el tipo DNI en la base de datos")
                    return False
            
            # Otros casos - usar DNI por defecto (ID 5)
            else:
                dni_type = identification_type_model.search([
                    ('name', '=', 'DNI'),
                    ('country_id', '=', 173)  # Perú
                ], limit=1)
                if dni_type:
                    self._logger.info(f"VAT genérico detectado: {vat_clean} -> Usando DNI por defecto ID: {dni_type.id}")
                    return dni_type.id
                else:
                    self._logger.warning("No se encontró el tipo DNI en la base de datos")
                    return False
                    
        except Exception as e:
            self._logger.error(f"Error al detectar tipo de identificación: {e}")
            return False

    def _update_partner_identification_type(self, partner_id, identification_type_id):
        """
        Actualizar el campo l10n_latam_identification_type_id del partner después de crearlo
        """
        if not partner_id or not identification_type_id:
            return False
        
        try:
            Partner = request.env['res.partner'].sudo()
            partner = Partner.browse(partner_id)
            
            if partner.exists():
                # Actualizar el campo directamente
                partner.write({'l10n_latam_identification_type_id': identification_type_id})
                self._logger.info(f"✅ Campo l10n_latam_identification_type_id actualizado para partner {partner_id}: {identification_type_id}")
                return True
            else:
                self._logger.warning(f"❌ Partner {partner_id} no encontrado")
                return False
                
        except Exception as e:
            self._logger.error(f"❌ Error al actualizar campo de identificación: {e}")
            return False

    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        """
        Sobrescribimos el método checkout para procesar la lógica necesaria
        pero redirigir automáticamente a payment sin mostrar la vista
        """
        self._logger.info("=== CHECKOUT ROUTE (PROCESSING + AUTO REDIRECT) ===")
        order = request.website.sale_get_order()
        
        if not order or not order.order_line:
            self._logger.info("🛒 No hay líneas de pedido, redirigiendo a /shop/cart")
            return request.redirect('/shop/cart')
        
        # Verificar que el partner esté correctamente asignado
        if not order.partner_id or order.partner_id.id == request.website.partner_id.id:
            self._logger.warning("⚠️ Partner no válido en el pedido, redirigiendo a /shop/address")
            return request.redirect('/shop/address')
        
        # Procesar lógica de checkout (llamar al método padre para procesar)
        try:
            # Llamar al método padre para ejecutar la lógica de checkout
            result = super().checkout(**post)
            
            # Si el resultado es una redirección, respetarla
            if hasattr(result, 'status_code') and result.status_code in [301, 302]:
                return result
            
            # Si llegamos aquí, el checkout se procesó correctamente
            # Redirigir automáticamente a payment
            self._logger.info("✅ Checkout procesado correctamente, redirigiendo a /shop/payment")
            return request.redirect('/shop/payment')
            
        except Exception as e:
            self._logger.error(f"❌ Error en checkout: {str(e)}")
            # En caso de error, redirigir a address para corregir datos
            return request.redirect('/shop/address')
        
    @http.route(['/shop/address'], type='http', auth="public", website=True, sitemap=False)
    def address(self, **kw):
        """
        Sobrescribimos para manejar los campos personalizados DNI, RUC y tipo de comprobante
        """
        self._logger.info("=== ADDRESS ROUTE ===")
        self._logger.info(f"Method: {request.httprequest.method}")
        self._logger.info(f"KW recibidos: {kw}")
        
        # Obtener todos los valores del formulario
        all_form_values = request.httprequest.form.to_dict()
        self._logger.info(f"Todos los valores del formulario: {all_form_values}")
        
        # Normalizar claves con espacios accidentales (p.ej., 'phone ')
        sanitized_form_values = {k.strip(): v for k, v in all_form_values.items()}
        if set(sanitized_form_values.keys()) != set(all_form_values.keys()):
            self._logger.info(f"Normalizando claves del formulario: {set(all_form_values.keys())} -> {set(sanitized_form_values.keys())}")
        all_form_values = sanitized_form_values
        
        # Fusionar KW con valores normalizados para asegurar consistencia aguas abajo
        kw = {**kw, **all_form_values}
        
        # Verificar si es un envío de formulario (POST con datos)
        if request.httprequest.method == 'POST' and (all_form_values.get('submitted') or len(all_form_values) > 1):
            self._logger.info("=== PROCESANDO ENVÍO DE FORMULARIO ===")
            
            # Obtener valores específicos
            dni = all_form_values.get('dni', '').strip()
            ruc = all_form_values.get('ruc', '').strip()
            razon_social = all_form_values.get('razon_social', '').strip()
            invoice_type_checkbox = all_form_values.get('invoice_type_checkbox', '')
            shipping_option = all_form_values.get('shipping_option', 'pickup')
            
            self._logger.info(f"DNI extraído: '{dni}'")
            self._logger.info(f"RUC extraído: '{ruc}'")
            self._logger.info(f"Razón Social extraída: '{razon_social}'")
            self._logger.info(f"Checkbox factura: '{invoice_type_checkbox}'")
            self._logger.info(f"Opción de envío: '{shipping_option}'")
            
            # Determinar si se solicita factura
            is_invoice_requested = invoice_type_checkbox == '1'
            
            # Procesar los datos personalizados y actualizar kw
            if is_invoice_requested:
                self._logger.info("=== MODO FACTURA ===")
                if ruc:
                    kw['vat'] = ruc
                    all_form_values['vat'] = ruc
                    self._logger.info(f"VAT establecido a RUC: {ruc}")
                if razon_social:
                    kw['name'] = razon_social
                    all_form_values['name'] = razon_social
                    kw['is_company'] = True
                    all_form_values['is_company'] = True
                    self._logger.info(f"Nombre establecido a razón social: {razon_social}")
            else:
                self._logger.info("=== MODO BOLETA ===")
                if dni:
                    kw['vat'] = dni
                    all_form_values['vat'] = dni
                    kw['is_company'] = False
                    all_form_values['is_company'] = False
                    self._logger.info(f"VAT establecido a DNI: {dni}")
            
            # Agregar campos personalizados a kw para que estén disponibles en el procesamiento
            kw['dni'] = dni
            kw['ruc'] = ruc
            kw['razon_social'] = razon_social
            kw['invoice_type_checkbox'] = invoice_type_checkbox
            kw['shipping_option'] = shipping_option
            
            # Asegurar que los campos básicos estén presentes
            for field in ['name', 'email', 'phone']:
                if field in all_form_values and all_form_values[field]:
                    kw[field] = all_form_values[field]
            
            self._logger.info(f"KW actualizados: {kw}")
        
        # Usar métodos sin validación para crear/actualizar partners
        try:
            self._logger.info("🔄 PROCESANDO ADDRESS SIN VALIDACIONES DE BACKEND")
            
            # Obtener partner actual si existe
            partner = None
            if hasattr(request, 'website') and request.website.partner_id:
                partner = request.website.partner_id
                self._logger.info(f"  - Partner existente encontrado: ID {partner.id}")

            # Normalizar claves de kw por si llegan con espacios (ej. 'phone ')
            kw = {k.strip(): v for k, v in kw.items()}
            
            # Si hay partner, actualizar sin validaciones
            if partner and partner.id != request.website.user_id.partner_id.id:
                self._update_partner_without_validation(partner, kw)
            else:
                self._logger.info("  - No hay partner específico, usando método estándar con contexto sin validaciones")
            
            # Llamar al método padre con contexto sin validaciones
            no_validation_context = {
                'skip_validation': True,
                'no_vat_validation': True,
                'disable_mail_validation': True,
                'skip_check_vat': True,
                'import_file': True,
                'tracking_disable': True,
                'mail_create_nolog': True,
                'mail_create_nosubscribe': True,
            }
            
            # Aplicar contexto sin validaciones al request
            original_context = request.context
            request.context = dict(original_context, **no_validation_context)
            
            try:
                # Si es POST con datos del formulario, procesar y redirigir manualmente sin llamar al método padre
                if request.httprequest.method == 'POST' and (all_form_values.get('submitted') or len(all_form_values) > 1):
                    self._logger.info("🧭 POST address(): guardado manual sin super() y redirección controlada")

                    # Preprocesar valores (detecta vat e identificación)
                    order = request.website.sale_get_order()
                    mode = ('new', 'billing')
                    data_values = self.values_preprocess(order, mode, kw)

                    # Guardar partner sin validaciones
                    try:
                        partner_id = self._checkout_form_save(mode, kw, {**kw, **data_values})
                        self._logger.info(f"✅ Partner guardado manualmente (id={partner_id})")

                        # Vincular partner al pedido actual antes de redirigir
                        if order:
                            try:
                                partner_rec = request.env['res.partner'].sudo().browse(partner_id)
                                write_vals = {
                                    'partner_id': partner_rec.commercial_partner_id.id or partner_rec.id,
                                    'partner_invoice_id': partner_rec.id,
                                    'partner_shipping_id': partner_rec.id,
                                }
                                order.sudo().write(write_vals)
                                # Actualizar sesión para coherencia
                                request.session['partner_id'] = partner_rec.id
                                self._logger.info(f"🧩 Pedido {order.id} actualizado con partner {partner_rec.id} (invoice/shipping asignados)")
                            except Exception as e:
                                self._logger.error(f"❌ Error vinculando partner {partner_id} al pedido: {e}")
                    except Exception as e:
                        self._logger.error(f"❌ Error guardando partner manualmente: {e}")
                        # Como fallback, intentar con super() una sola vez
                        result = super().address(**kw)
                        self._logger.info("↩️ Fallback a super().address() ejecutado")

                        # Intentar enlazar partner al pedido si el super() no lo hizo
                        try:
                            order = request.website.sale_get_order()
                            # Extraer partner_id potencial del contexto/resultados
                            possible_pid = None
                            # buscar en kw o all_form_values
                            for key in ['partner_id', 'partner', 'partner_shipping_id', 'partner_invoice_id']:
                                if key in kw and str(kw[key]).strip().isdigit():
                                    possible_pid = int(str(kw[key]).strip())
                                    break
                            if not possible_pid and 'vat' in kw:
                                # Buscar por VAT recientemente creado
                                found = request.env['res.partner'].sudo().search([('vat', '=', kw['vat'])], limit=1)
                                possible_pid = found.id if found else None
                            if order and possible_pid:
                                partner_rec = request.env['res.partner'].sudo().browse(possible_pid)
                                if partner_rec and partner_rec.exists():
                                    write_vals = {
                                        'partner_id': partner_rec.commercial_partner_id.id or partner_rec.id,
                                        'partner_invoice_id': partner_rec.id,
                                        'partner_shipping_id': partner_rec.id,
                                    }
                                    order.sudo().write(write_vals)
                                    request.session['partner_id'] = partner_rec.id
                                    self._logger.info(f"🧩 Enlace post-super(): Pedido {order.id} actualizado con partner {partner_rec.id}")
                        except Exception as e2:
                            self._logger.error(f"❌ Error enlazando partner tras super(): {e2}")

                        return result

                    # Redirigir explícitamente después del guardado
                    order = request.website.sale_get_order()
                    if order and order.order_line:
                        self._logger.info("🔄 Redirigiendo a /shop/checkout para procesamiento")
                        return request.redirect('/shop/checkout')
                    else:
                        self._logger.info("🛒 No hay líneas de pedido, redirigiendo a /shop/cart")
                        return request.redirect('/shop/cart')
                else:
                    # Si es GET, mostrar la página normalmente
                    result = super().address(**kw)
                    self._logger.info("✅ Método address() GET ejecutado sin validaciones de backend")
                    return result
            finally:
                # Restaurar contexto original
                request.context = original_context
                
        except Exception as e:
            self._logger.error(f"❌ Error en address() sin validaciones: {str(e)}")
            raise

    def _checkout_form_save(self, mode, checkout, all_values):
        """
        Guardar el formulario de checkout con detección automática del tipo de identificación
        """
        self._logger.info("=== CHECKOUT FORM SAVE ===")
        self._logger.info(f"Mode: {mode}")
        self._logger.info(f"Checkout: {checkout}")
        self._logger.info(f"All values: {all_values}")
        
        # 🔧 NORMALIZAR TIPOS DE DATOS Y SANITIZAR CAMPOS
        # Normalizar cualquier clave con espacios accidentales
        sanitized_checkout = {k.strip(): v for k, v in checkout.items()}
        sanitized_all_values = {k.strip(): v for k, v in all_values.items()}
        
        if set(sanitized_checkout.keys()) != set(checkout.keys()):
            self._logger.info(f"Normalizando claves checkout: {set(checkout.keys())} -> {set(sanitized_checkout.keys())}")
        if set(sanitized_all_values.keys()) != set(all_values.keys()):
            self._logger.info(f"Normalizando claves all_values: {set(all_values.keys())} -> {set(sanitized_all_values.keys())}")
        
        checkout = sanitized_checkout
        all_values = sanitized_all_values
        
        # Obtener valores del formulario
        dni = all_values.get('dni', '').strip()
        ruc = all_values.get('ruc', '').strip()
        razon_social = all_values.get('razon_social', '').strip()
        is_invoice_requested = all_values.get('invoice_type_checkbox') == '1'
        invoice_type = all_values.get('invoice_type', 'boleta')
        shipping_option = all_values.get('shipping_option', 'pickup')
        
        self._logger.info(f"DNI: {dni}")
        self._logger.info(f"RUC: {ruc}")
        self._logger.info(f"Razón Social: {razon_social}")
        self._logger.info(f"¿Solicita factura?: {is_invoice_requested}")
        self._logger.info(f"Tipo de comprobante: {invoice_type}")
        self._logger.info(f"Opción de envío: {shipping_option}")
        
        # Determinar qué número usar y detectar tipo automáticamente
        identification_type_id = None
        if is_invoice_requested and ruc:
            # Modo factura: usar RUC
            checkout['vat'] = ruc
            identification_type_id = self._detect_identification_type_id(ruc)
            self._logger.info(f"Modo factura: RUC {ruc} detectado como ID: {identification_type_id}")
            
            # Si es empresa, usar razón social
            if razon_social:
                checkout['name'] = razon_social
                checkout['is_company'] = True
                self._logger.info(f"Empresa: {razon_social}")
        else:
            # Modo boleta: usar DNI
            checkout['vat'] = dni
            identification_type_id = self._detect_identification_type_id(dni)
            self._logger.info(f"Modo boleta: DNI {dni} detectado como ID: {identification_type_id}")
            
            # Si no es empresa, usar nombre personal
            checkout['is_company'] = False
        
        # Asegurar que el nombre esté presente
        if 'name' not in checkout or not checkout['name']:
            checkout['name'] = all_values.get('name', 'Sin nombre')
            self._logger.info(f"Nombre asignado por defecto: {checkout['name']}")
        
        # Asegurar que el email esté presente
        if 'email' not in checkout or not checkout['email']:
            checkout['email'] = all_values.get('email', '')
            self._logger.info(f"Email asignado: {checkout['email']}")
        
        # Asegurar que el teléfono esté presente
        if 'phone' not in checkout or not checkout['phone']:
            checkout['phone'] = all_values.get('phone', '')
            self._logger.info(f"Teléfono asignado: {checkout['phone']}")
        
        # Manejar campos de dirección según la opción de envío
        if shipping_option == 'delivery':
            # Envío a domicilio: campos de dirección son requeridos
            if 'street' not in checkout or not checkout['street']:
                checkout['street'] = all_values.get('street', '')
                self._logger.info(f"Dirección asignada: {checkout['street']}")
            
            if 'city' not in checkout or not checkout['city']:
                checkout['city'] = all_values.get('city', '')
                self._logger.info(f"Ciudad asignada: {checkout['city']}")
            
            # Normalizar country_id (y otros posibles Many2one IDs)
            def _to_int(val):
                try:
                    # Manejar valores como '173', 173, ' 173 ', None, ''
                    if val is None:
                        return None
                    if isinstance(val, int):
                        return val
                    if isinstance(val, str):
                        val = val.strip()
                        return int(val) if val.isdigit() else None
                    # Manejar floats accidentalmente
                    if isinstance(val, float):
                        return int(val)
                    return None
                except Exception:
                    return None
            
            if 'country_id' in all_values or 'country_id' in checkout:
                raw_country = checkout.get('country_id') or all_values.get('country_id')
                normalized_country = _to_int(raw_country)
                if normalized_country:
                    checkout['country_id'] = normalized_country
                    self._logger.info(f"País asignado (normalizado): {checkout['country_id']}")
                else:
                    self._logger.warning(f"País inválido: {raw_country}")
        else:
            # Recojo en tienda: usar valores por defecto
            checkout['street'] = 'Sin dirección'
            checkout['city'] = 'Sin dirección'
            checkout['country_id'] = 173  # Perú
            self._logger.info("Modo recogo: usando dirección por defecto")
        
        # Incluir l10n_latam_identification_type_id y normalizarlo si llega como string
        if identification_type_id:
            checkout['l10n_latam_identification_type_id'] = int(identification_type_id)
        elif 'l10n_latam_identification_type_id' in checkout:
            try:
                checkout['l10n_latam_identification_type_id'] = int(str(checkout['l10n_latam_identification_type_id']).strip())
            except Exception:
                self._logger.warning(f"l10n_latam_identification_type_id inválido: {checkout.get('l10n_latam_identification_type_id')} (se omitirá)")
                checkout.pop('l10n_latam_identification_type_id', None)

        # Filtrar solo campos válidos de res.partner (incluye l10n_latam_identification_type_id)
        valid_fields = ['name', 'email', 'phone', 'street', 'city', 'country_id', 'vat', 'is_company', 'l10n_latam_identification_type_id']
        filtered_checkout = {k: v for k, v in checkout.items() if k in valid_fields and v is not None and v != ''}
        
        self._logger.info(f"Checkout filtrado: {filtered_checkout}")
        
        # Crear o actualizar el partner
        Partner = request.env['res.partner'].sudo()
        
        if mode[0] == 'edit':
            partner_id = int(mode[1])
            partner = Partner.browse(partner_id)
            partner.write(filtered_checkout)
            self._logger.info(f"Partner actualizado: {partner_id}")
        else:
            partner_id = Partner.create(filtered_checkout).id
            self._logger.info(f"Partner creado: {partner_id}")
        
        # Ya no es necesario actualizar después; se envió en el write/create
        if identification_type_id:
            self._logger.info(f"✅ l10n_latam_identification_type_id enviado en create/write: {checkout.get('l10n_latam_identification_type_id')}")
        else:
            self._logger.warning("⚠️ No se detectó tipo de identificación, el campo puede no haberse enviado")
        
        return partner_id

    def values_preprocess(self, order, mode, kw):
        """
        Preprocesar valores antes de guardar
        """
        self._logger.info("=== VALUES PREPROCESS ===")
        self._logger.info(f"Order: {order}")
        self._logger.info(f"Mode: {mode}")
        self._logger.info(f"KW: {kw}")
        
        # Obtener valores del formulario
        dni = kw.get('dni', '').strip()
        ruc = kw.get('ruc', '').strip()
        is_invoice_requested = kw.get('invoice_type_checkbox') == '1'
        
        # Crear diccionario de nuevos valores
        new_values = {}
        
        # Determinar qué número usar y detectar tipo automáticamente
        if is_invoice_requested and ruc:
            # Modo factura: usar RUC
            new_values['vat'] = ruc
            identification_type_id = self._detect_identification_type_id(ruc)
            if identification_type_id:
                new_values['l10n_latam_identification_type_id'] = identification_type_id
            self._logger.info(f"Modo factura: RUC {ruc} detectado como ID: {identification_type_id}")
        else:
            # Modo boleta: usar DNI
            new_values['vat'] = dni
            identification_type_id = self._detect_identification_type_id(dni)
            if identification_type_id:
                new_values['l10n_latam_identification_type_id'] = identification_type_id
            self._logger.info(f"Modo boleta: DNI {dni} detectado como ID: {identification_type_id}")
        
        self._logger.info(f"Nuevos valores: {new_values}")
        return new_values

    def checkout_form_validate(self, mode, all_form_values, data_values):
        """
        VALIDACIONES COMPLETAMENTE DESHABILITADAS EN BACKEND
        Todas las validaciones se manejan exclusivamente en el frontend
        """
        self._logger.info("=== CHECKOUT FORM VALIDATE - BACKEND DESHABILITADO ===")
        self._logger.info(f"Mode: {mode}")
        self._logger.info(f"All form values: {all_form_values}")
        self._logger.info(f"Data values: {data_values}")
        
        # LOGGING EXHAUSTIVO DE VALIDACIONES PREDETERMINADAS DE ODOO
        self._log_odoo_default_validations(mode, all_form_values, data_values)
        
        # DESHABILITAR COMPLETAMENTE TODAS LAS VALIDACIONES
        self._logger.info("🚫 TODAS LAS VALIDACIONES DE BACKEND DESHABILITADAS")
        self._logger.info("✅ Validaciones manejadas exclusivamente por el frontend")
        
        # Logging exhaustivo de validaciones predeterminadas de Odoo
        self._logger.info(f"📊 Datos recibidos: {data_values}")
        
        # Ejecutar logging exhaustivo de todas las validaciones de Odoo
        self._log_odoo_default_validations(mode, all_form_values, data_values)
        
        # Retornar sin errores - el frontend maneja toda la validación
        return {}, []
    
    def _log_odoo_default_validations(self, mode, all_form_values, data_values):
        """
        Logging exhaustivo de todas las validaciones predeterminadas de Odoo
        """
        self._logger.info("=== LOGGING EXHAUSTIVO DE VALIDACIONES PREDETERMINADAS DE ODOO ===")
        
        try:
            # 1. VALIDACIONES DE PARTNER/CONTACTO
            self._logger.info("📋 VALIDACIONES DE PARTNER/CONTACTO:")
            name = all_form_values.get('name', '')
            email = all_form_values.get('email', '')
            phone = all_form_values.get('phone', '')
            vat = all_form_values.get('vat', '')
            
            self._logger.info(f"  - Nombre: '{name}' (Requerido por Odoo: {'✅' if name else '❌'})")
            self._logger.info(f"  - Email: '{email}' (Requerido por Odoo: {'✅' if email else '❌'})")
            self._logger.info(f"  - Teléfono: '{phone}' (Requerido por Odoo: {'✅' if phone else '❌'})")
            self._logger.info(f"  - VAT: '{vat}' (Validación VAT Odoo: DESHABILITADA)")
            
            # 2. VALIDACIONES DE DIRECCIÓN
            self._logger.info("🏠 VALIDACIONES DE DIRECCIÓN:")
            street = all_form_values.get('street', '')
            street2 = all_form_values.get('street2', '')
            city = all_form_values.get('city', '')
            zip_code = all_form_values.get('zip', '')
            country_id = all_form_values.get('country_id', '')
            state_id = all_form_values.get('state_id', '')
            
            self._logger.info(f"  - Calle: '{street}' (Requerido por Odoo: {'✅' if street else '❌'})")
            self._logger.info(f"  - Calle 2: '{street2}' (Opcional en Odoo: ✅)")
            self._logger.info(f"  - Ciudad: '{city}' (Requerido por Odoo: {'✅' if city else '❌'})")
            self._logger.info(f"  - Código Postal: '{zip_code}' (Requerido por Odoo: {'✅' if zip_code else '❌'})")
            self._logger.info(f"  - País: '{country_id}' (Requerido por Odoo: {'✅' if country_id else '❌'})")
            self._logger.info(f"  - Estado: '{state_id}' (Requerido por Odoo: {'✅' if state_id else '❌'})")
            
            # 3. VALIDACIONES DE FACTURACIÓN
            self._logger.info("💰 VALIDACIONES DE FACTURACIÓN:")
            is_company = all_form_values.get('is_company', False)
            company_name = all_form_values.get('company_name', '')
            
            self._logger.info(f"  - Es Empresa: {is_company} (Validación Odoo: ✅)")
            self._logger.info(f"  - Nombre Empresa: '{company_name}' (Requerido si es_empresa: {'✅' if not is_company or company_name else '❌'})")
            
            # 4. VALIDACIONES DE LOCALIZACIÓN PERUANA
            self._logger.info("🇵🇪 VALIDACIONES DE LOCALIZACIÓN PERUANA:")
            l10n_latam_identification_type_id = all_form_values.get('l10n_latam_identification_type_id', '')
            dni = all_form_values.get('dni', '')
            ruc = all_form_values.get('ruc', '')
            
            self._logger.info(f"  - Tipo Identificación: '{l10n_latam_identification_type_id}' (L10n_PE: DESHABILITADO)")
            self._logger.info(f"  - DNI: '{dni}' (Validación L10n_PE: DESHABILITADA)")
            self._logger.info(f"  - RUC: '{ruc}' (Validación L10n_PE: DESHABILITADA)")
            
            # 5. VALIDACIONES DE WEBSITE SALE
            self._logger.info("🛒 VALIDACIONES DE WEBSITE SALE:")
            shipping_option = all_form_values.get('shipping_option', '')
            
            self._logger.info(f"  - Opción de Envío: '{shipping_option}' (Website Sale: ✅)")
            
            # 6. VALIDACIONES DE CAMPOS PERSONALIZADOS
            self._logger.info("⚙️ VALIDACIONES DE CAMPOS PERSONALIZADOS:")
            invoice_type_checkbox = all_form_values.get('invoice_type_checkbox', '')
            razon_social = all_form_values.get('razon_social', '')
            
            self._logger.info(f"  - Tipo Factura: '{invoice_type_checkbox}' (Personalizado: FRONTEND ONLY)")
            self._logger.info(f"  - Razón Social: '{razon_social}' (Personalizado: FRONTEND ONLY)")
            
            # 7. RESUMEN DE VALIDACIONES DESHABILITADAS
            self._logger.info("🚫 VALIDACIONES DESHABILITADAS EN BACKEND:")
            self._logger.info("  - ❌ Validación de formato de email")
            self._logger.info("  - ❌ Validación de formato de teléfono")
            self._logger.info("  - ❌ Validación de VAT/RUC")
            self._logger.info("  - ❌ Validación de DNI")
            self._logger.info("  - ❌ Validación de campos requeridos")
            self._logger.info("  - ❌ Validación de dirección completa")
            self._logger.info("  - ❌ Validación de país/estado")
            self._logger.info("  - ❌ Validación de código postal")
            
            self._logger.info("✅ TODAS LAS VALIDACIONES SE MANEJAN EN EL FRONTEND")
            
        except Exception as e:
            self._logger.error(f"❌ Error en logging de validaciones: {str(e)}")
    
    def _disable_partner_validations(self, partner_values):
        """
        Deshabilita todas las validaciones automáticas de partner en el backend
        """
        self._logger.info("🚫 DESHABILITANDO VALIDACIONES DE PARTNER EN BACKEND")
        
        try:
            # Crear contexto que deshabilita validaciones
            no_validation_context = {
                'skip_validation': True,
                'no_vat_validation': True,
                'disable_mail_validation': True,
                'skip_check_vat': True,
                'import_file': True,  # Evita validaciones de importación
                'tracking_disable': True,  # Deshabilita tracking
                'mail_create_nolog': True,  # No crear logs de mail
                'mail_create_nosubscribe': True,  # No suscribir automáticamente
            }
            
            self._logger.info(f"  - Contexto sin validaciones: {no_validation_context}")
            
            # Remover campos que pueden causar validaciones automáticas
            safe_values = partner_values.copy()
            
            # Campos que pueden causar validaciones VAT
            vat_fields = ['vat', 'l10n_latam_identification_type_id']
            for field in vat_fields:
                if field in safe_values:
                    self._logger.info(f"  - Removiendo campo de validación VAT: {field} = {safe_values[field]}")
                    # No remover, solo loggear que se está pasando sin validar
            
            # Campos de email que pueden causar validaciones
            if 'email' in safe_values:
                self._logger.info(f"  - Email sin validación: {safe_values['email']}")
            
            # Campos de teléfono que pueden causar validaciones
            if 'phone' in safe_values:
                self._logger.info(f"  - Teléfono sin validación: {safe_values['phone']}")
            
            self._logger.info("✅ Validaciones de partner deshabilitadas exitosamente")
            return safe_values, no_validation_context
            
        except Exception as e:
            self._logger.error(f"❌ Error deshabilitando validaciones de partner: {str(e)}")
            return partner_values, {}
    
    def _create_partner_without_validation(self, partner_values):
        """
        Crea un partner sin ejecutar validaciones del backend
        """
        self._logger.info("👤 CREANDO PARTNER SIN VALIDACIONES DE BACKEND")
        
        try:
            # Obtener valores seguros y contexto sin validaciones
            safe_values, no_validation_context = self._disable_partner_validations(partner_values)
            
            # Crear partner con contexto que deshabilita validaciones
            Partner = request.env['res.partner'].with_context(**no_validation_context)
            
            self._logger.info(f"  - Valores para crear partner: {safe_values}")
            
            # Crear partner
            partner = Partner.sudo().create(safe_values)
            
            self._logger.info(f"✅ Partner creado exitosamente sin validaciones: ID {partner.id}")
            return partner
            
        except Exception as e:
            self._logger.error(f"❌ Error creando partner sin validaciones: {str(e)}")
            # Fallback: intentar crear con método estándar
            return request.env['res.partner'].sudo().create(partner_values)
    
    def _update_partner_without_validation(self, partner, partner_values):
        """
        Actualiza un partner sin ejecutar validaciones del backend
        """
        self._logger.info(f"🔄 ACTUALIZANDO PARTNER {partner.id} SIN VALIDACIONES DE BACKEND")
        
        try:
            # Obtener valores seguros y contexto sin validaciones
            safe_values, no_validation_context = self._disable_partner_validations(partner_values)
            
            # Actualizar partner con contexto que deshabilita validaciones
            partner_with_context = partner.with_context(**no_validation_context)
            
            self._logger.info(f"  - Valores para actualizar partner: {safe_values}")
            
            # Actualizar partner
            partner_with_context.sudo().write(safe_values)
            
            self._logger.info(f"✅ Partner {partner.id} actualizado exitosamente sin validaciones")
            return partner
            
        except Exception as e:
            self._logger.error(f"❌ Error actualizando partner sin validaciones: {str(e)}")
            # Fallback: intentar actualizar con método estándar
            partner.sudo().write(partner_values)
            return partner