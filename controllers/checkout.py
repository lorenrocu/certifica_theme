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
        Sobrescribimos para manejar los campos personalizados DNI, RUC y tipo de comprobante
        """
        self._logger.info("=== ADDRESS ROUTE ===")
        self._logger.info(f"Method: {request.httprequest.method}")
        self._logger.info(f"KW recibidos: {kw}")
        
        # Obtener todos los valores del formulario
        all_form_values = request.httprequest.form.to_dict()
        self._logger.info(f"Todos los valores del formulario: {all_form_values}")
        
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
        
        # Llamar al método original con los datos procesados
        try:
            result = super().address(**kw)
            self._logger.info("Método super().address() ejecutado exitosamente")
            
            # Si es un POST exitoso, forzar redirección a payment
            if request.httprequest.method == 'POST' and (all_form_values.get('submitted') or len(all_form_values) > 1):
                self._logger.info("=== FORZANDO REDIRECCIÓN A PAYMENT ===")
                return request.redirect('/shop/payment')
            
            return result
        except Exception as e:
            self._logger.error(f"Error en super().address(): {str(e)}")
            raise

    def _checkout_form_save(self, mode, checkout, all_values):
        """
        Guardar el formulario de checkout con detección automática del tipo de identificación
        """
        self._logger.info("=== CHECKOUT FORM SAVE ===")
        self._logger.info(f"Mode: {mode}")
        self._logger.info(f"Checkout: {checkout}")
        self._logger.info(f"All values: {all_values}")
        
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
            
            if 'country_id' not in checkout or not checkout['country_id']:
                country_id = all_values.get('country_id', '')
                if country_id and country_id.isdigit():
                    checkout['country_id'] = int(country_id)
                    self._logger.info(f"País asignado: {checkout['country_id']}")
                else:
                    self._logger.warning(f"País inválido: {country_id}")
        else:
            # Recojo en tienda: usar valores por defecto
            checkout['street'] = 'Sin dirección'
            checkout['city'] = 'Sin dirección'
            checkout['country_id'] = 173  # Perú
            self._logger.info("Modo recogo: usando dirección por defecto")
        
        # Filtrar solo campos válidos de res.partner (EXCLUIR l10n_latam_identification_type_id)
        valid_fields = ['name', 'email', 'phone', 'street', 'city', 'country_id', 'vat', 'is_company']
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
        
        # ACTUALIZAR EL CAMPO DE IDENTIFICACIÓN DESPUÉS DE CREAR/ACTUALIZAR
        if identification_type_id:
            success = self._update_partner_identification_type(partner_id, identification_type_id)
            if success:
                self._logger.info(f"✅ Campo de identificación actualizado exitosamente para partner {partner_id}")
            else:
                self._logger.error(f"❌ No se pudo actualizar el campo de identificación para partner {partner_id}")
        else:
            self._logger.warning("⚠️ No se detectó tipo de identificación, no se actualizará el campo")
        
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
        Validar el formulario de checkout con lógica personalizada
        """
        self._logger.info("=== CHECKOUT FORM VALIDATE ===")
        self._logger.info(f"Mode: {mode}")
        self._logger.info(f"All form values: {all_form_values}")
        self._logger.info(f"Data values: {data_values}")
        
        shipping_option = all_form_values.get('shipping_option', 'pickup')
        
        # Inicializar errores
        error = {}
        error_message = []
        
        try:
            # Validaciones personalizadas (DNI, RUC, razón social)
            invoice_type_checkbox = all_form_values.get('invoice_type_checkbox')
            dni = all_form_values.get('dni', '').strip()
            ruc = all_form_values.get('ruc', '').strip()
            razon_social = all_form_values.get('razon_social', '').strip()
            is_invoice_requested = invoice_type_checkbox == '1'
            
            self._logger.info(f"Validando - DNI: '{dni}', RUC: '{ruc}', Razón Social: '{razon_social}', Factura: {is_invoice_requested}")

            if is_invoice_requested:
                self._logger.info("Validando modo factura")
                if not ruc:
                    error['ruc'] = 'missing'
                    error_message.append('RUC es requerido para factura')
                    self._logger.warning("Error: RUC faltante")
                elif len(ruc) != 11 or not ruc.isdigit():
                    error['ruc'] = 'invalid'
                    error_message.append('RUC debe tener exactamente 11 dígitos')
                    self._logger.warning(f"Error: RUC inválido - {ruc}")
                if not razon_social:
                    error['razon_social'] = 'missing'
                    error_message.append('Razón Social es requerida para factura')
                    self._logger.warning("Error: Razón Social faltante")
            else:
                self._logger.info("Validando modo boleta")
                if dni and (len(dni) != 8 or not dni.isdigit()):
                    error['dni'] = 'invalid'
                    error_message.append('DNI debe tener exactamente 8 dígitos')
                    self._logger.warning(f"Error: DNI inválido - {dni}")
            
            # Validar campos básicos requeridos solo para pickup
            if shipping_option == 'pickup':
                name = all_form_values.get('name', '').strip()
                email = all_form_values.get('email', '').strip()
                phone = all_form_values.get('phone', '').strip()
                
                if not name:
                    error['name'] = 'missing'
                    error_message.append('Nombre es requerido')
                    self._logger.warning("Error: Nombre faltante")
                
                if not email:
                    error['email'] = 'missing'
                    error_message.append('Email es requerido')
                    self._logger.warning("Error: Email faltante")
                
                if not phone:
                    error['phone'] = 'missing'
                    error_message.append('Teléfono es requerido')
                    self._logger.warning("Error: Teléfono faltante")
            
            self._logger.info(f"Errores encontrados: {error}")
            self._logger.info(f"Mensajes de error: {error_message}")
            
            # Si hay errores personalizados, retornarlos
            if error:
                return error, error_message
            
            # Si no hay errores personalizados y no es pickup, usar validación estándar
            if shipping_option != 'pickup':
                self._logger.info("Usando validación estándar (no pickup)")
                return super(WebsiteSaleCheckout, self).checkout_form_validate(mode, all_form_values, data_values)
            
            # Si es pickup y no hay errores, retornar sin errores
            self._logger.info("Validación exitosa para pickup")
            return {}, []
            
        except Exception as e:
            self._logger.error(f"Error en checkout_form_validate: {str(e)}")
            # En caso de error, usar validación estándar como fallback
            return super(WebsiteSaleCheckout, self).checkout_form_validate(mode, all_form_values, data_values)