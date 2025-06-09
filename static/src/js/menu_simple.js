// JavaScript básico sin dependencias
document.addEventListener("DOMContentLoaded", function() {
    console.log("Menu simple inicializado");
    
    // Botón para abrir el menú
    var btnMenu = document.getElementById("menu-btn");
    // Menú lateral
    var menuLateral = document.getElementById("menu-movil");
    // Overlay de fondo
    var menuOverlay = document.getElementById("menu-overlay");
    // Botón para cerrar
    var btnCerrar = document.getElementById("menu-cerrar");
    
    // Función para abrir el menú
    function abrirMenu() {
        console.log("Abriendo menú");
        menuLateral.style.left = "0px";
        menuOverlay.style.display = "block";
    }
    
    // Función para cerrar el menú
    function cerrarMenu() {
        console.log("Cerrando menú");
        menuLateral.style.left = "-250px";
        menuOverlay.style.display = "none";
    }
    
    // Asignar eventos si los elementos existen
    if (btnMenu) {
        btnMenu.onclick = function(e) {
            e.preventDefault();
            abrirMenu();
        };
    } else {
        console.error("Botón de menú no encontrado");
    }
    
    if (btnCerrar) {
        btnCerrar.onclick = function(e) {
            e.preventDefault();
            cerrarMenu();
        };
    }
    
    if (menuOverlay) {
        menuOverlay.onclick = function() {
            cerrarMenu();
        };
    }
    
    // También cerrar con ESC
    document.onkeydown = function(e) {
        if (e.key === "Escape") {
            cerrarMenu();
        }
    };
});
