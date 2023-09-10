$(document).ready(function() {
    $("#ver_contrasena").change(function() {
        if ($("#ver_contrasena").is(":checked")) {
            $("#contrasena").attr("type", "text");
            $("#icono_contrasena").show();
        } else {
            $("#contrasena").attr("type", "password");
            $("#icono_contrasena").hide();
        }
    });
});