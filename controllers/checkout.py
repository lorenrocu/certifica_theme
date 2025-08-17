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

    @http.route(['/shop/address'], type='http', auth="public", website=True, sitemap=False)
    def address(self, **kw):
        """
        DESHABILITAR VALIDACIONES EN ADDRESS - SOLO LOGS
        """
        self._logger.info("=== ADDRESS ROUTE - VALIDACIONES DESHABILITADAS ===")
        self._logger.info(f"Method: {request.httprequest.method}")
        self._logger.info(f"KW recibidos: {kw}")
        
        # Obtener todos los valores del formulario
        all_form_values = request.httprequest.form.to_dict()
        self._logger.info(f"Todos los valores del formulario: {all_form_values}")
        
        # Verificar si es un envío de formulario (POST con datos)
        if request.httprequest.method == 'POST' and (all_form_values.get('submitted') or len(all_form_values) > 1):
            self._logger.info("=== PROCESANDO ENVÍO DE FORMULARIO SIN VALIDACIONES ===")
            
            # Obtener todos los valores para logging
            dni = all_form_values.get('dni', '').strip()
            ruc = all_form_values.get('ruc', '').strip()
            razon_social = all_form_values.get('razon_social', '').strip()
            invoice_type_checkbox = all_form_values.get('invoice_type_checkbox', '')
            shipping_option = all_form_values.get('shipping_option', 'pickup')
            name = all_form_values.get('name', '').strip()
            email = all_form_values.get('email', '').strip()
            phone = all_form_values.get('phone', '').strip()
            street = all_form_values.get('street', '').strip()
            city = all_form_values.get('city', '').strip()
            country_id = all_form_values.get('country_id', '')
            
            # LOGS DETALLADOS DE TODOS LOS VALORES
            self._logger.info("=== VALORES EXTRAÍDOS DEL FORMULARIO ===")
            self._logger.info(f"DNI: '{dni}' (longitud: {len(dni) if dni else 0})")
            self._logger.info(f"RUC: '{ruc}' (longitud: {len(ruc) if ruc else 0})")
            self._logger.info(f"Razón Social: '{razon_social}'")
            self._logger.info(f"Checkbox factura: '{invoice_type_checkbox}'")
            self._logger.info(f"Opción de envío: '{shipping_option}'")
            self._logger.info(f"Nombre: '{name}'")
            self._logger.info(f"Email: '{email}'")
            self._logger.info(f"Teléfono: '{phone}'")
            self._logger.info(f"Dirección: '{street}'")
            self._logger.info(f"Ciudad: '{city}'")
            self._logger.info(f"País ID: '{country_id}'")
            
            # LOGS DE VALIDACIONES IGNORADAS
            self._logger.info("=== VALIDACIONES IGNORADAS EN ADDRESS ===")
            
            is_invoice_requested = invoice_type_checkbox == '1'
            
            if is_invoice_requested:
                self._logger.info("MODO FACTURA - Validaciones ignoradas:")
                if not ruc:
                    self._logger.info("⚠️ RUC faltante - IGNORADO en address")
                elif len(ruc) != 11 or not ruc.isdigit():
                    self._logger.info(f"⚠️ RUC inválido '{ruc}' - IGNORADO en address")
                if not razon_social:
                    self._logger.info("⚠️ Razón Social faltante - IGNORADO en address")
            else:
                self._logger.info("MODO BOLETA - Validaciones ignoradas:")
                if dni and (len(dni) != 8 or not dni.isdigit()):
                    self._logger.info(f"⚠️ DNI inválido '{dni}' - IGNORADO en address")
            
            if shipping_option == 'pickup':
                self._logger.info("MODO PICKUP - Validaciones ignoradas:")
                if not name:
                    self._logger.info("⚠️ Nombre faltante - IGNORADO en address")
                if not email:
                    self._logger.info("⚠️ Email faltante - IGNORADO en address")
                if not phone:
                    self._logger.info("⚠️ Teléfono faltante - IGNORADO en address")
            else:
                self._logger.info("MODO DELIVERY - Validaciones ignoradas:")
                if not street:
                    self._logger.info("⚠️ Dirección faltante - IGNORADO en address")
                if not city:
                    self._logger.info("⚠️ Ciudad faltante - IGNORADO en address")
                if not country_id:
                    self._logger.info("⚠️ País faltante - IGNORADO en address")
            
            # PROCESAR DATOS SIN VALIDACIONES
            self._logger.info("=== PROCESANDO DATOS SIN VALIDACIONES ===")
            
            if is_invoice_requested:
                self._logger.info("MODO FACTURA - Procesando sin validaciones:")
                if ruc:
                    kw['vat'] = ruc
                    all_form_values['vat'] = ruc
                    self._logger.info(f"VAT establecido a RUC: '{ruc}' (sin validación)")
                if razon_social:
                    kw['name'] = razon_social
                    all_form_values['name'] = razon_social
                    kw['is_company'] = True
                    all_form_values['is_company'] = True
                    self._logger.info(f"Nombre establecido a razón social: '{razon_social}' (sin validación)")
            else:
                self._logger.info("MODO BOLETA - Procesando sin validaciones:")
                if dni:
                    kw['vat'] = dni
                    all_form_values['vat'] = dni
                    kw['is_company'] = False
                    all_form_values['is_company'] = False
                    self._logger.info(f"VAT establecido a DNI: '{dni}' (sin validación)")
            
            # Agregar todos los campos personalizados sin validar
            kw['dni'] = dni
            kw['ruc'] = ruc
            kw['razon_social'] = razon_social
            kw['invoice_type_checkbox'] = invoice_type_checkbox
            kw['shipping_option'] = shipping_option
            
            # Agregar campos básicos sin validar
            for field in ['name', 'email', 'phone', 'street', 'city', 'country_id']:
                if field in all_form_values and all_form_values[field]:
                    kw[field] = all_form_values[field]
                    self._logger.info(f"Campo '{field}' agregado: '{all_form_values[field]}' (sin validación)")
            
            self._logger.info(f"KW finales (sin validaciones): {kw}")
        
        # Llamar al método original con los datos procesados (sin validaciones)
        try:
            self._logger.info("=== LLAMANDO MÉTODO ORIGINAL SIN VALIDACIONES ===")
            result = super().address(**kw)
            self._logger.info("✅ Método super().address() ejecutado exitosamente sin validaciones")
            return result
        except Exception as e:
            self._logger.error(f"❌ Error en super().address(): {str(e)}")
            self._logger.info("⚠️ Error ignorado - continuando sin validaciones")
            # Retornar respuesta básica en caso de error
            return request.render('website_sale.address', {'error': str(e)})

    def _checkout_form_save(self, mode, checkout, all_values):
        """
        DESHABILITAR VALIDACIONES Y GUARDAR FORMULARIO - SOLO LOGS
        """
        self._logger.info("=== CHECKOUT FORM SAVE - VALIDACIONES DESHABILITADAS ===")
        self._logger.info(f"Mode: {mode}")
        self._logger.info(f"Checkout original: {checkout}")
        self._logger.info(f"All values: {all_values}")
        
        # Obtener todos los valores del formulario para logging
        dni = all_values.get('dni', '').strip()
        ruc = all_values.get('ruc', '').strip()
        razon_social = all_values.get('razon_social', '').strip()
        is_invoice_requested = all_values.get('invoice_type_checkbox') == '1'
        invoice_type = all_values.get('invoice_type', 'boleta')
        shipping_option = all_values.get('shipping_option', 'pickup')
        name = all_values.get('name', '').strip()
        email = all_values.get('email', '').strip()
        phone = all_values.get('phone', '').strip()
        street = all_values.get('street', '').strip()
        city = all_values.get('city', '').strip()
        country_id = all_values.get('country_id', '')
        
        # LOGS DETALLADOS DE TODOS LOS VALORES
        self._logger.info("=== VALORES EXTRAÍDOS DEL FORMULARIO ===")
        self._logger.info(f"DNI: '{dni}' (longitud: {len(dni) if dni else 0})")
        self._logger.info(f"RUC: '{ruc}' (longitud: {len(ruc) if ruc else 0})")
        self._logger.info(f"Razón Social: '{razon_social}'")
        self._logger.info(f"¿Solicita factura?: {is_invoice_requested}")
        self._logger.info(f"Tipo de comprobante: {invoice_type}")
        self._logger.info(f"Opción de envío: {shipping_option}")
        self._logger.info(f"Nombre: '{name}'")
        self._logger.info(f"Email: '{email}'")
        self._logger.info(f"Teléfono: '{phone}'")
        self._logger.info(f"Dirección: '{street}'")
        self._logger.info(f"Ciudad: '{city}'")
        self._logger.info(f"País ID: '{country_id}'")
        
        # LOGS DE VALIDACIONES IGNORADAS
        self._logger.info("=== VALIDACIONES IGNORADAS EN BACKEND ===")
        
        if is_invoice_requested:
            self._logger.info("MODO FACTURA - Validaciones ignoradas:")
            if not ruc:
                self._logger.info("⚠️ RUC faltante - IGNORADO, se procesará igual")
            elif len(ruc) != 11 or not ruc.isdigit():
                self._logger.info(f"⚠️ RUC inválido '{ruc}' - IGNORADO, se procesará igual")
            if not razon_social:
                self._logger.info("⚠️ Razón Social faltante - IGNORADO, se procesará igual")
        else:
            self._logger.info("MODO BOLETA - Validaciones ignoradas:")
            if dni and (len(dni) != 8 or not dni.isdigit()):
                self._logger.info(f"⚠️ DNI inválido '{dni}' - IGNORADO, se procesará igual")
        
        if shipping_option == 'pickup':
            self._logger.info("MODO PICKUP - Validaciones ignoradas:")
            if not name:
                self._logger.info("⚠️ Nombre faltante - IGNORADO, se procesará igual")
            if not email:
                self._logger.info("⚠️ Email faltante - IGNORADO, se procesará igual")
            if not phone:
                self._logger.info("⚠️ Teléfono faltante - IGNORADO, se procesará igual")
        else:
            self._logger.info("MODO DELIVERY - Validaciones ignoradas:")
            if not street:
                self._logger.info("⚠️ Dirección faltante - IGNORADO, se procesará igual")
            if not city:
                self._logger.info("⚠️ Ciudad faltante - IGNORADO, se procesará igual")
            if not country_id:
                self._logger.info("⚠️ País faltante - IGNORADO, se procesará igual")
        
        # PROCESAR DATOS SIN VALIDACIONES
        self._logger.info("=== PROCESANDO DATOS SIN VALIDACIONES ===")
        
        # Determinar qué número usar (sin validar formato)
        identification_type_id = None
        if is_invoice_requested and ruc:
            # Modo factura: usar RUC (sin validar formato)
            checkout['vat'] = ruc
            identification_type_id = self._detect_identification_type_id(ruc)
            self._logger.info(f"Modo factura: RUC '{ruc}' asignado (sin validación)")
            
            # Si hay razón social, usarla (sin validar)
            if razon_social:
                checkout['name'] = razon_social
                checkout['is_company'] = True
                self._logger.info(f"Empresa: '{razon_social}' (sin validación)")
        else:
            # Modo boleta: usar DNI (sin validar formato)
            checkout['vat'] = dni
            identification_type_id = self._detect_identification_type_id(dni)
            self._logger.info(f"Modo boleta: DNI '{dni}' asignado (sin validación)")
            checkout['is_company'] = False
        
        # Asignar valores por defecto si faltan (sin validar)
        if 'name' not in checkout or not checkout['name']:
            checkout['name'] = all_values.get('name', 'Sin nombre')
            self._logger.info(f"Nombre por defecto: '{checkout['name']}' (sin validación)")
        
        if 'email' not in checkout or not checkout['email']:
            checkout['email'] = all_values.get('email', '')
            self._logger.info(f"Email asignado: '{checkout['email']}' (sin validación)")
        
        if 'phone' not in checkout or not checkout['phone']:
            checkout['phone'] = all_values.get('phone', '')
            self._logger.info(f"Teléfono asignado: '{checkout['phone']}' (sin validación)")
        
        # Manejar dirección (sin validar campos requeridos)
        if shipping_option == 'delivery':
            self._logger.info("MODO DELIVERY - Asignando dirección sin validaciones:")
            checkout['street'] = all_values.get('street', 'Sin dirección')
            checkout['city'] = all_values.get('city', 'Sin ciudad')
            checkout['country_id'] = all_values.get('country_id', 173)  # Perú por defecto
            self._logger.info(f"Dirección: '{checkout['street']}' (sin validación)")
            self._logger.info(f"Ciudad: '{checkout['city']}' (sin validación)")
            self._logger.info(f"País: {checkout['country_id']} (sin validación)")
        else:
            # Recojo en tienda: valores por defecto
            checkout['street'] = 'Sin dirección'
            checkout['city'] = 'Sin dirección'
            checkout['country_id'] = 173  # Perú
            self._logger.info("Modo recogo: dirección por defecto (sin validación)")
        
        # Filtrar campos válidos (sin validar contenido)
        valid_fields = ['name', 'email', 'phone', 'street', 'city', 'country_id', 'vat', 'is_company']
        filtered_checkout = {k: v for k, v in checkout.items() if k in valid_fields and v is not None and v != ''}
        
        self._logger.info(f"Checkout filtrado (sin validaciones): {filtered_checkout}")
        
        # Crear o actualizar partner (sin validaciones)
        Partner = request.env['res.partner'].sudo()
        
        try:
            if mode[0] == 'edit':
                partner_id = int(mode[1])
                partner = Partner.browse(partner_id)
                partner.write(filtered_checkout)
                self._logger.info(f"✅ Partner actualizado sin validaciones: {partner_id}")
            else:
                partner_id = Partner.create(filtered_checkout).id
                self._logger.info(f"✅ Partner creado sin validaciones: {partner_id}")
        except Exception as e:
            self._logger.error(f"❌ Error al crear/actualizar partner: {str(e)}")
            # Intentar con valores mínimos si falla
            minimal_checkout = {'name': 'Cliente', 'email': 'cliente@example.com'}
            try:
                if mode[0] == 'edit':
                    partner_id = int(mode[1])
                    partner = Partner.browse(partner_id)
                    partner.write(minimal_checkout)
                    self._logger.info(f"✅ Partner actualizado con valores mínimos: {partner_id}")
                else:
                    partner_id = Partner.create(minimal_checkout).id
                    self._logger.info(f"✅ Partner creado con valores mínimos: {partner_id}")
            except Exception as e2:
                self._logger.error(f"❌ Error crítico al crear partner: {str(e2)}")
                raise
        
        # Actualizar campo de identificación (sin validar)
        if identification_type_id:
            success = self._update_partner_identification_type(partner_id, identification_type_id)
            if success:
                self._logger.info(f"✅ Campo de identificación actualizado: {partner_id}")
            else:
                self._logger.warning("⚠️ No se pudo actualizar campo de identificación")
        else:
            self._logger.warning("⚠️ No se detectó tipo de identificación")
        
        self._logger.info("=== PROCESAMIENTO COMPLETADO SIN VALIDACIONES ===")
        return partner_id

    def values_preprocess(self, order, mode, kw):
        """
        DESHABILITAR VALIDACIONES EN PREPROCESAMIENTO - SOLO LOGS
        """
        self._logger.info("=== VALUES PREPROCESS - VALIDACIONES DESHABILITADAS ===")
        self._logger.info(f"Order: {order}")
        self._logger.info(f"Mode: {mode}")
        self._logger.info(f"KW recibidos: {kw}")
        
        # Obtener todos los valores para logging
        dni = kw.get('dni', '').strip()
        ruc = kw.get('ruc', '').strip()
        is_invoice_requested = kw.get('invoice_type_checkbox') == '1'
        name = kw.get('name', '').strip()
        email = kw.get('email', '').strip()
        phone = kw.get('phone', '').strip()
        street = kw.get('street', '').strip()
        city = kw.get('city', '').strip()
        country_id = kw.get('country_id', '')
        
        # LOGS DETALLADOS DE VALORES RECIBIDOS
        self._logger.info("=== VALORES RECIBIDOS EN PREPROCESS ===")
        self._logger.info(f"DNI: '{dni}' (longitud: {len(dni) if dni else 0})")
        self._logger.info(f"RUC: '{ruc}' (longitud: {len(ruc) if ruc else 0})")
        self._logger.info(f"¿Solicita factura?: {is_invoice_requested}")
        self._logger.info(f"Nombre: '{name}'")
        self._logger.info(f"Email: '{email}'")
        self._logger.info(f"Teléfono: '{phone}'")
        self._logger.info(f"Dirección: '{street}'")
        self._logger.info(f"Ciudad: '{city}'")
        self._logger.info(f"País ID: '{country_id}'")
        
        # LOGS DE VALIDACIONES IGNORADAS
        self._logger.info("=== VALIDACIONES IGNORADAS EN PREPROCESS ===")
        
        if is_invoice_requested:
            self._logger.info("MODO FACTURA - Validaciones ignoradas:")
            if not ruc:
                self._logger.info("⚠️ RUC faltante - IGNORADO en preprocess")
            elif len(ruc) != 11 or not ruc.isdigit():
                self._logger.info(f"⚠️ RUC inválido '{ruc}' - IGNORADO en preprocess")
        else:
            self._logger.info("MODO BOLETA - Validaciones ignoradas:")
            if dni and (len(dni) != 8 or not dni.isdigit()):
                self._logger.info(f"⚠️ DNI inválido '{dni}' - IGNORADO en preprocess")
        
        # Crear diccionario de nuevos valores (sin validaciones)
        new_values = {}
        
        # Asignar valores sin validar formato
        if is_invoice_requested and ruc:
            # Modo factura: usar RUC (sin validar)
            new_values['vat'] = ruc
            identification_type_id = self._detect_identification_type_id(ruc)
            if identification_type_id:
                new_values['l10n_latam_identification_type_id'] = identification_type_id
            self._logger.info(f"Modo factura: RUC '{ruc}' asignado (sin validación)")
        else:
            # Modo boleta: usar DNI (sin validar)
            new_values['vat'] = dni
            identification_type_id = self._detect_identification_type_id(dni)
            if identification_type_id:
                new_values['l10n_latam_identification_type_id'] = identification_type_id
            self._logger.info(f"Modo boleta: DNI '{dni}' asignado (sin validación)")
        
        # Asignar otros campos sin validar
        if name:
            new_values['name'] = name
            self._logger.info(f"Nombre asignado: '{name}' (sin validación)")
        
        if email:
            new_values['email'] = email
            self._logger.info(f"Email asignado: '{email}' (sin validación)")
        
        if phone:
            new_values['phone'] = phone
            self._logger.info(f"Teléfono asignado: '{phone}' (sin validación)")
        
        if street:
            new_values['street'] = street
            self._logger.info(f"Dirección asignada: '{street}' (sin validación)")
        
        if city:
            new_values['city'] = city
            self._logger.info(f"Ciudad asignada: '{city}' (sin validación)")
        
        if country_id:
            new_values['country_id'] = country_id
            self._logger.info(f"País asignado: '{country_id}' (sin validación)")
        
        self._logger.info(f"Valores finales (sin validaciones): {new_values}")
        self._logger.info("=== PREPROCESS COMPLETADO SIN VALIDACIONES ===")
        return new_values

    def checkout_form_validate(self, mode, all_form_values, data_values):
        """
        DESHABILITAR TODAS LAS VALIDACIONES DEL BACKEND - SOLO LOGS
        """
        self._logger.info("=== CHECKOUT FORM VALIDATE - VALIDACIONES DESHABILITADAS ===")
        self._logger.info(f"Mode: {mode}")
        self._logger.info(f"All form values: {all_form_values}")
        self._logger.info(f"Data values: {data_values}")
        
        # Obtener todos los valores para logging
        shipping_option = all_form_values.get('shipping_option', 'pickup')
        invoice_type_checkbox = all_form_values.get('invoice_type_checkbox')
        dni = all_form_values.get('dni', '').strip()
        ruc = all_form_values.get('ruc', '').strip()
        razon_social = all_form_values.get('razon_social', '').strip()
        name = all_form_values.get('name', '').strip()
        email = all_form_values.get('email', '').strip()
        phone = all_form_values.get('phone', '').strip()
        street = all_form_values.get('street', '').strip()
        city = all_form_values.get('city', '').strip()
        country_id = all_form_values.get('country_id', '')
        
        # LOGS DETALLADOS DE TODOS LOS CAMPOS
        self._logger.info("=== VALORES RECIBIDOS EN EL FORMULARIO ===")
        self._logger.info(f"Opción de envío: {shipping_option}")
        self._logger.info(f"Checkbox factura: {invoice_type_checkbox}")
        self._logger.info(f"DNI: '{dni}' (longitud: {len(dni) if dni else 0})")
        self._logger.info(f"RUC: '{ruc}' (longitud: {len(ruc) if ruc else 0})")
        self._logger.info(f"Razón Social: '{razon_social}'")
        self._logger.info(f"Nombre: '{name}'")
        self._logger.info(f"Email: '{email}'")
        self._logger.info(f"Teléfono: '{phone}'")
        self._logger.info(f"Dirección: '{street}'")
        self._logger.info(f"Ciudad: '{city}'")
        self._logger.info(f"País ID: '{country_id}'")
        
        # LOGS DE VALIDACIONES QUE SE IGNORARÍAN EN BACKEND
        self._logger.info("=== VALIDACIONES IGNORADAS EN BACKEND ===")
        
        if is_invoice_requested:
            self._logger.info("MODO FACTURA - Validaciones que se ignorarían:")
            if not ruc:
                self._logger.info("⚠️ RUC faltante - IGNORADO en backend")
            elif len(ruc) != 11 or not ruc.isdigit():
                self._logger.info(f"⚠️ RUC inválido '{ruc}' - IGNORADO en backend")
            if not razon_social:
                self._logger.info("⚠️ Razón Social faltante - IGNORADO en backend")
        else:
            self._logger.info("MODO BOLETA - Validaciones que se ignorarían:")
            if dni and (len(dni) != 8 or not dni.isdigit()):
                self._logger.info(f"⚠️ DNI inválido '{dni}' - IGNORADO en backend")
        
        if shipping_option == 'pickup':
            self._logger.info("MODO PICKUP - Validaciones que se ignorarían:")
            if not name:
                self._logger.info("⚠️ Nombre faltante - IGNORADO en backend")
            if not email:
                self._logger.info("⚠️ Email faltante - IGNORADO en backend")
            if not phone:
                self._logger.info("⚠️ Teléfono faltante - IGNORADO en backend")
        else:
            self._logger.info("MODO DELIVERY - Validaciones que se ignorarían:")
            if not street:
                self._logger.info("⚠️ Dirección faltante - IGNORADO en backend")
            if not city:
                self._logger.info("⚠️ Ciudad faltante - IGNORADO en backend")
            if not country_id:
                self._logger.info("⚠️ País faltante - IGNORADO en backend")
        
        # DESHABILITAR TODAS LAS VALIDACIONES - RETORNAR SIN ERRORES
        self._logger.info("=== TODAS LAS VALIDACIONES DESHABILITADAS - RETORNANDO SIN ERRORES ===")
        self._logger.info("✅ El formulario será procesado sin validaciones en el backend")
        self._logger.info("✅ Las validaciones solo se realizan en el frontend")
        
        return {}, []