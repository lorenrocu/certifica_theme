// JavaScript simple para cambiar el texto del encabezado de precio en el carrito
$(document).ready(function() {
    // Verificar que estamos en la página del carrito
    if (window.location.pathname === '/shop/cart') {
        // Función para actualizar el encabezado de precio
        function updatePriceHeader() {
            // Buscar el encabezado de precio con diferentes selectores
            var $priceHeader = $('th.text-center.td-price');
            
            if ($priceHeader.length > 0) {
                $priceHeader.text('Precio Unitario');
                console.log('Encabezado actualizado: Precio Unitario');
                return;
            }
            
            // Selector alternativo
            $priceHeader = $('th.td-price');
            if ($priceHeader.length > 0) {
                $priceHeader.text('Precio Unitario');
                console.log('Encabezado actualizado: Precio Unitario (selector alternativo)');
                return;
            }
            
            // Buscar por contenido de texto
            $('th').each(function() {
                if ($(this).text().trim() === 'Precio') {
                    $(this).text('Precio Unitario');
                    console.log('Encabezado actualizado: Precio Unitario (por contenido)');
                    return false; // Salir del each
                }
            });
        }
        
        // Ejecutar inmediatamente
        updatePriceHeader();
        
        // También ejecutar después de un pequeño delay por si la página se carga dinámicamente
        setTimeout(updatePriceHeader, 500);
        setTimeout(updatePriceHeader, 1000);
    }
});