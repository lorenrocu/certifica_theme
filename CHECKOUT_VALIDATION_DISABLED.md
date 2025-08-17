# CHECKOUT VALIDATION DISABLED - BACKEND

## Descripción

Este módulo ha sido configurado para **DESHABILITAR COMPLETAMENTE** todas las validaciones del checkout en el backend de Odoo. Solo se mantienen las validaciones en el frontend (JavaScript).

## Archivos Modificados

### 1. `controllers/checkout.py`
- **`checkout_form_validate`**: Deshabilitado - retorna siempre `{}, []` (sin errores)
- **`_checkout_form_save`**: Deshabilitado - procesa datos sin validaciones
- **`values_preprocess`**: Deshabilitado - procesa valores sin validaciones
- **`address`**: Deshabilitado - procesa direcciones sin validaciones

### 2. `models/website_sale_validation_override.py` (NUEVO)
- Deshabilita todas las validaciones del módulo `website_sale`
- Incluye métodos para validación de checkout, guardado, dirección, pago, envío, carrito y orden

### 3. `models/payment_validation_override.py` (NUEVO)
- Deshabilita todas las validaciones del módulo `payment`
- Incluye métodos para validación de datos de pago, transacciones, métodos de pago, tarjetas, bancos, montos, monedas, partners y referencias

### 4. `models/sale_validation_override.py` (NUEVO)
- Deshabilita todas las validaciones del módulo `sale`
- Incluye métodos para validación de checkout, guardado, datos de orden, líneas de orden, partners y montos

### 5. Archivos Existentes de VAT (ya deshabilitados)
- `models/base_vat_override.py`
- `models/l10n_latam_override.py`
- `models/vat_validation_override.py`
- `models/vat_monkey_patch.py`

## Funcionalidad

### ✅ LO QUE ESTÁ DESHABILITADO (BACKEND)
- **Validación de DNI/RUC**: No se valida formato, longitud ni contenido
- **Validación de Razón Social**: No se valida si está presente o es válida
- **Validación de Email**: No se valida formato ni si está presente
- **Validación de Teléfono**: No se valida formato ni si está presente
- **Validación de Dirección**: No se valida si está presente o es válida
- **Validación de Ciudad**: No se valida si está presente o es válida
- **Validación de País**: No se valida si está presente o es válido
- **Validación de Código Postal**: No se valida formato ni si está presente
- **Validación de VAT**: No se valida formato ni contenido
- **Validación de Montos**: No se valida si son positivos o válidos
- **Validación de Partners**: No se valida si existen o son válidos
- **Validación de Pagos**: No se valida método, datos de tarjeta, etc.
- **Validación de Envíos**: No se valida opción de envío ni datos de entrega

### ✅ LO QUE SE MANTIENE (FRONTEND)
- **Validaciones JavaScript**: Se mantienen todas las validaciones del frontend
- **Validaciones de Formulario**: Se mantienen las validaciones visuales
- **Mensajes de Error**: Se muestran errores en el frontend
- **Bloqueo de Envío**: Se bloquea el envío si hay errores en el frontend

## Logs Detallados

### 📝 LOGS DE VALIDACIONES IGNORADAS
Cada método registra en el log:
- **Valores recibidos**: Todos los datos del formulario
- **Validaciones ignoradas**: Qué validaciones se saltan
- **Procesamiento**: Cómo se procesan los datos sin validar
- **Resultado**: Confirmación de que se procesó sin validaciones

### 🔍 EJEMPLO DE LOG
```
=== CHECKOUT FORM VALIDATE - VALIDACIONES DESHABILITADAS ===
=== VALORES RECIBIDOS EN EL FORMULARIO ===
DNI: '123' (longitud: 3)
RUC: '45678901234' (longitud: 11)
Email: 'test@' (longitud: 5)
=== VALIDACIONES IGNORADAS EN BACKEND ===
⚠️ DNI inválido '123' - IGNORADO en backend
⚠️ Email inválido - IGNORADO en backend
=== TODAS LAS VALIDACIONES DESHABILITADAS - RETORNANDO SIN ERRORES ===
✅ El formulario será procesado sin validaciones en el backend
```

## Configuración

### 📋 ARCHIVOS INCLUIDOS
El archivo `models/__init__.py` incluye todos los nuevos modelos:
```python
from . import website_sale_validation_override
from . import payment_validation_override
from . import sale_validation_override
```

### 🔧 INSTALACIÓN
1. Reiniciar el servidor Odoo
2. Actualizar el módulo `certifica_theme`
3. Verificar en los logs que aparezcan los mensajes de validación deshabilitada

## Uso

### 🚀 PROCESAMIENTO SIN VALIDACIONES
- **Frontend**: Valida y muestra errores al usuario
- **Backend**: Procesa cualquier dato sin restricciones
- **Logs**: Registra todas las validaciones ignoradas
- **Resultado**: El checkout se completa independientemente de la calidad de los datos

### ⚠️ CONSIDERACIONES
- **Seguridad**: No hay validación de datos en el backend
- **Integridad**: Los datos pueden ser incorrectos o malformados
- **Auditoría**: Todos los datos se registran en logs para revisión posterior
- **Frontend**: Las validaciones del frontend siguen funcionando normalmente

## Monitoreo

### 📊 LOGS A REVISAR
- **Checkout**: `controllers/checkout.py`
- **Website Sale**: `models/website_sale_validation_override.py`
- **Payment**: `models/payment_validation_override.py`
- **Sale**: `models/sale_validation_override.py`

### 🔍 BÚSQUEDA EN LOGS
Buscar en los logs de Odoo:
- `VALIDACIONES DESHABILITADAS`
- `IGNORADO en backend`
- `sin validación`
- `VALIDACIÓN DESHABILITADA`

## Resumen

Este módulo **DESHABILITA COMPLETAMENTE** todas las validaciones del checkout en el backend de Odoo, manteniendo solo las validaciones del frontend. Esto permite que cualquier dato sea procesado sin restricciones, mientras se mantiene un registro detallado de todas las validaciones que se ignoran.
