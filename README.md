# Certifica Theme - Tema Personalizado para Odoo 13

## Descripción

Tema minimalista y moderno para Odoo 13 con diseño personalizado para el sitio web de Certifica. Incluye header personalizado, footer, diseño de tienda optimizado y página de producto individual completamente rediseñada.

## Características Principales

### 🎨 Diseño General
- Header personalizado con navegación responsive
- Footer corporativo con información de contacto
- Diseño minimalista y profesional
- Totalmente responsive para dispositivos móviles

### 🛍️ Tienda Online
- Diseño de tienda con sidebar de filtros
- Filtros jerárquicos por categorías
- Filtros por atributos con checkboxes
- Grid de productos optimizado
- Paginación mejorada

### 📱 Página de Producto Individual (NUEVO)
- **Diseño de dos columnas (50% cada una)**:
  - **Columna izquierda**: Imagen principal del producto con galería de miniaturas
  - **Columna derecha**: Título, precio, descripción, selector de cantidad y botón de añadir al carrito
- Galería de imágenes interactiva con zoom
- Selector de cantidad con botones +/-
- Información de stock en tiempo real
- Descarga de ficha técnica PDF
- Tabs para descripción y especificaciones
- Diseño completamente responsive

## Archivos Principales

### Vistas (XML)
- `views/layout.xml` - Header y footer personalizados
- `views/shop_layout.xml` - Diseño de la tienda con filtros
- `views/product_page_custom.xml` - **NUEVO**: Página de producto individual
- `views/assets.xml` - Inclusión de archivos CSS y JS

### Estilos (CSS)
- `static/src/custom_header.css` - Estilos del header
- `static/src/css/shop_custom.css` - Estilos de la tienda
- `static/src/css/product_custom.css` - **NUEVO**: Estilos del producto individual

### JavaScript
- `static/src/js/menu_simple.js` - Funcionalidad del menú
- `static/src/js/category_hierarchy.js` - Filtros de categorías
- `static/src/js/product_custom.js` - **NUEVO**: Funcionalidad del producto individual

## Funcionalidades del Producto Individual

### 🖼️ Galería de Imágenes
- Imagen principal con efecto hover
- Miniaturas clickeables para cambiar la imagen principal
- Modal de zoom para ver imágenes en tamaño completo
- Transiciones suaves entre imágenes

### 🛒 Selector de Cantidad
- Botones +/- para incrementar/decrementar
- Validación de cantidad mínima
- Input numérico editable
- Integración con el formulario de Odoo

### 📋 Información del Producto
- Título prominente y legible
- Precio destacado con formato monetario
- Descripción corta del producto
- Indicador de stock disponible
- Información de envío

### 📄 Tabs de Contenido
- Tab de descripción detallada
- Tab de especificaciones técnicas
- Navegación suave entre tabs
- Contenido dinámico basado en datos del producto

### 📱 Diseño Responsive
- Adaptación automática a dispositivos móviles
- Reorganización de columnas en pantallas pequeñas
- Botones y elementos táctiles optimizados
- Imágenes responsive con lazy loading

## Instalación y Requisitos para usar como Theme Web en Odoo

### Requisitos mínimos
- Odoo 13
- Módulo `website` instalado
- Módulo `website_sale` instalado (si quieres tienda online)
- (Opcional) Módulo `stock` instalado si quieres lógica de inventario real

### Instalación
1. Copia la carpeta `certifica_theme` en tu carpeta de `addons` de Odoo.
2. Ve a **Apps** en Odoo, actualiza la lista de aplicaciones.
3. Busca "Certifica Theme" e instálalo.
4. Ve a **Sitio Web > Configuración > Temas** y selecciona "Certifica Theme" como tema activo.

### Notas importantes
- El theme personaliza header, footer, página de producto, tienda y checkout.
- El contador de carrito funciona en todas las páginas si la ruta `/shop/cart/count` está disponible (requiere `website_sale` correctamente instalado y sin conflictos).
- El stock mostrado en la página de producto es **simulado** por defecto. Si quieres mostrar el stock real, deberás dar permisos de lectura al usuario público sobre el campo `qty_available` del modelo `product.product` (no recomendado en la mayoría de los casos por seguridad).
- Si tienes módulos personalizados que sobrescriben rutas de `/shop`, pueden interferir con la funcionalidad del theme.

### Personalización
- Puedes modificar los colores y estilos en los archivos CSS del theme.
- Si quieres mostrar información adicional (como stock real), revisa la sección correspondiente en este README y los comentarios en los archivos XML.

### Soporte
Si tienes problemas con la instalación o el funcionamiento del theme, revisa primero los requisitos y dependencias. Si el problema persiste, revisa los logs de Odoo y asegúrate de que no hay conflictos con otros módulos personalizados.

## Dependencias

- `website` - Módulo base de sitio web de Odoo
- `website_sale` - Módulo de tienda online de Odoo

## Compatibilidad

- Odoo 13.0
- Bootstrap 4
- Font Awesome 5.15.4
- jQuery (incluido en Odoo)

## Personalización

### Colores y Estilos
Los colores principales se pueden modificar en los archivos CSS:
- Color primario: `#87465C` (color corporativo Certifica)
- Color secundario: `#6c757d` (gris)
- Color de éxito: `#28a745` (verde)

### Funcionalidades Adicionales
El JavaScript está modularizado para facilitar la adición de nuevas funcionalidades:
- Sistema de favoritos (preparado para implementar)
- Notificaciones personalizadas
- Validaciones de formulario
- Efectos de animación

## Soporte

Para soporte técnico o personalizaciones adicionales, contactar al desarrollador:
- **Autor**: Lorenzo Romero
- **Website**: https://helydev.com

## Changelog

### v13.0.1.0.0
- ✅ Header y footer personalizados
- ✅ Diseño de tienda con filtros
- ✅ **NUEVO**: Página de producto individual con diseño de dos columnas
- ✅ **NUEVO**: Galería de imágenes interactiva
- ✅ **NUEVO**: Selector de cantidad mejorado
- ✅ **NUEVO**: Tabs de contenido dinámico
- ✅ **NUEVO**: Diseño completamente responsive
- ✅ **NUEVO**: JavaScript modular y extensible

## Licencia

Este tema está desarrollado específicamente para Certifica y su uso está restringido según los términos acordados.

### Pricelist Específico (ID 4)

El módulo está configurado para usar automáticamente el pricelist con ID 4 en toda la tienda web. Esto incluye:

- **Página de productos**: Los precios mostrados corresponden al pricelist 4
- **Página individual de producto**: El precio mostrado es del pricelist 4
- **Carrito de compras**: Los productos se añaden con precios del pricelist 4
- **Checkout**: Los precios finales corresponden al pricelist 4

#### Verificación

Para verificar que el pricelist funciona correctamente, puedes acceder a:
```
/shop/test_pricelist
```

Esta URL mostrará:
- Si el pricelist con ID 4 existe
- Comparación entre precios de lista y precios del pricelist para algunos productos

#### Configuración

Si necesitas cambiar el ID del pricelist, modifica los siguientes archivos:

1. **controllers/main.py**: Cambia el número `4` en las líneas donde se referencia el pricelist
2. **views/shop_layout.xml**: Cambia `pricelist=4` por el nuevo ID
3. **views/product_page_custom.xml**: Cambia `pricelist=4` por el nuevo ID