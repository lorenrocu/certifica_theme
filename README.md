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

## Instalación

1. Copiar el módulo en la carpeta `addons` de Odoo
2. Actualizar la lista de aplicaciones
3. Instalar el módulo "Certifica Theme"
4. Activar el tema desde Configuración > Sitio Web > Temas

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