/* JavaScript personalizado para la página de producto individual */

$(document).ready(function() {
    
    // Funcionalidad del selector de cantidad
    $('.quantity-btn').on('click', function(e) {
        e.preventDefault();
        
        var $input = $(this).closest('.input-group').find('.quantity-input');
        var currentValue = parseInt($input.val()) || 1;
        var action = $(this).data('action');
        
        if (action === 'increase') {
            $input.val(currentValue + 1);
        } else if (action === 'decrease' && currentValue > 1) {
            $input.val(currentValue - 1);
        }
        
        // Trigger change event para validaciones
        $input.trigger('change');
    });
    
    // Validación del input de cantidad
    $('.quantity-input').on('change', function() {
        var value = parseInt($(this).val());
        if (isNaN(value) || value < 1) {
            $(this).val(1);
        }
    });
    
    // Funcionalidad de la galería de imágenes
    $('.gallery-thumb').on('click', function() {
        var newSrc = $(this).attr('src').replace('/image_128', '/image_1920');
        var $mainImage = $('.product-main-image img');
        
        // Efecto de fade para el cambio de imagen
        $mainImage.fadeOut(200, function() {
            $(this).attr('src', newSrc).fadeIn(200);
        });
        
        // Actualizar estado activo de las miniaturas
        $('.gallery-thumb').removeClass('active-thumb');
        $(this).addClass('active-thumb');
    });
    
    // Zoom en la imagen principal (opcional)
    $('.product-main-image img').on('mouseenter', function() {
        $(this).css('cursor', 'zoom-in');
    });
    
    // Funcionalidad de zoom modal (opcional)
    $('.product-main-image img').on('click', function() {
        var imageSrc = $(this).attr('src');
        var imageAlt = $(this).attr('alt');
        
        // Crear modal para zoom
        var modalHtml = `
            <div class="modal fade" id="imageZoomModal" tabindex="-1" role="dialog">
                <div class="modal-dialog modal-lg modal-dialog-centered" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${imageAlt}</h5>
                            <button type="button" class="close" data-dismiss="modal">
                                <span>&times;</span>
                            </button>
                        </div>
                        <div class="modal-body text-center">
                            <img src="${imageSrc}" class="img-fluid" alt="${imageAlt}">
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remover modal existente si existe
        $('#imageZoomModal').remove();
        
        // Agregar y mostrar el modal
        $('body').append(modalHtml);
        $('#imageZoomModal').modal('show');
    });
    
    // Animación suave para el scroll a las tabs
    $('.nav-link[data-toggle="tab"]').on('click', function(e) {
        e.preventDefault();
        
        var target = $(this).attr('href');
        
        // Activar la tab
        $(this).tab('show');
        
        // Scroll suave hacia las tabs
        $('html, body').animate({
            scrollTop: $('.product-tabs').offset().top - 100
        }, 500);
    });
    
    // Validación del formulario antes del envío
    $('.js_add_cart_variants').on('submit', function(e) {
        var quantity = parseInt($('.quantity-input').val());
        
        if (isNaN(quantity) || quantity < 1) {
            e.preventDefault();
            alert('Por favor, selecciona una cantidad válida.');
            return false;
        }
        
        // Mostrar indicador de carga en el botón
        var $submitBtn = $(this).find('.a-submit');
        var originalText = $submitBtn.html();
        
        $submitBtn.html('<i class="fa fa-spinner fa-spin mr-2"></i>Agregando...');
        $submitBtn.prop('disabled', true);
        
        // Restaurar el botón después de 3 segundos (por si hay error)
        setTimeout(function() {
            $submitBtn.html(originalText);
            $submitBtn.prop('disabled', false);
        }, 3000);
    });
    
    // Efecto parallax suave para la imagen principal (opcional)
    $(window).on('scroll', function() {
        var scrolled = $(window).scrollTop();
        var parallax = $('.product-main-image img');
        var speed = 0.5;
        
        if (parallax.length && $(window).width() > 768) {
            var yPos = -(scrolled * speed);
            parallax.css('transform', 'translateY(' + yPos + 'px)');
        }
    });
    
    // Lazy loading para imágenes de la galería
    $('.gallery-thumb').each(function() {
        var $img = $(this);
        var src = $img.data('src');
        
        if (src) {
            $img.attr('src', src).removeAttr('data-src');
        }
    });
    
    // Funcionalidad de favoritos (si se implementa en el futuro)
    $('.add-to-wishlist').on('click', function(e) {
        e.preventDefault();
        
        var $btn = $(this);
        var productId = $btn.data('product-id');
        
        // Aquí se puede agregar la lógica para añadir a favoritos
        $btn.toggleClass('active');
        
        if ($btn.hasClass('active')) {
            $btn.html('<i class="fa fa-heart"></i> En Favoritos');
        } else {
            $btn.html('<i class="fa fa-heart-o"></i> Añadir a Favoritos');
        }
    });
    
    // Smooth scroll para navegación interna
    $('a[href^="#"]').on('click', function(e) {
        var target = $(this.getAttribute('href'));
        
        if (target.length) {
            e.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 100
            }, 600);
        }
    });
    
    // Inicializar tooltips si Bootstrap está disponible
    if (typeof $().tooltip === 'function') {
        $('[data-toggle="tooltip"]').tooltip();
    }
    
    // Mejorar accesibilidad con navegación por teclado
    $('.gallery-thumb').on('keydown', function(e) {
        if (e.which === 13 || e.which === 32) { // Enter o Espacio
            e.preventDefault();
            $(this).click();
        }
    });
    
    // Agregar atributos de accesibilidad
    $('.gallery-thumb').attr({
        'role': 'button',
        'tabindex': '0',
        'aria-label': 'Ver imagen en tamaño completo'
    });
    
});

// Función para actualizar el precio dinámicamente (si hay variantes)
function updateProductPrice(newPrice, currency) {
    $('.product-price span').fadeOut(200, function() {
        $(this).text(currency + ' ' + newPrice).fadeIn(200);
    });
}

// Función para mostrar notificaciones
function showNotification(message, type = 'success') {
    var alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    var notification = `
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
            ${message}
            <button type="button" class="close" data-dismiss="alert">
                <span>&times;</span>
            </button>
        </div>
    `;
    
    $('body').append(notification);
    
    // Auto-remover después de 5 segundos
    setTimeout(function() {
        $('.alert').fadeOut(500, function() {
            $(this).remove();
        });
    }, 5000);
}