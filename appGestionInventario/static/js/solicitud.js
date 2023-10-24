/**
 * 
 * @param {*} id
 * @param {*} estado
 */
function cargarSolicitudes(id,estado){
    const solicitud = {
        "id":id,
        "estado":estado
    }
    solicitudes.push(solicitud);
}

/**
 * Obtiene los elementos registrados en el 
 * sistema con los datos necesarios. Los recibe 
 * de la vista y los almacena en un arreglo
 * @param {*} idElemento
 * @param {*} codigo
 * @param {*} nombre
 */

function cargarElementos(idElemento, codigo, nombre){
    const elemento = {
        "idElemento": idElemento,
        "codigo":codigo,
        "nombre":nombre,
    }
    elementos.push(elemento);
}



/**
 * Obtiene las unidades de Medida y los
 * almacena en un arreglo
 * @param {*} id
 * @param {*} nombre
 */
function cargarUnidadesMedida(id, nombre){
    const unidadMedida = {
        "id":id,
        "nombre":nombre,
    }
    unidadesMedida.push(unidadMedida);
}

$("#btnAgregarElementoDetalle").click(function(){
    agregarElementoADetalle();
})

/**
 * Agrega cada material al arreglo de entradaMateriales,
 * primero valida que no se haya agregado previamente
 */
function agregarElementoADetalle(){
    //averiguar si ya se ha agregado el material
    const m = detalleSolicitudElementos.find(elemento=>elemento.idElemento == $("#cbElemento").val());
    if(m==null){
        const elemento = {
            "idElemento":$("#cbElemento").val(),
            "cantidad":$("#txtCantidad").val(),
            "idUnidadMedida":$("#cbUnidadMedida").val(),
        }
        detalleSolicitudElementos.push(elemento);
        frmDetalleSolicitudElemento.reset();
        mostrarDatosTabla();
    }else{
        Swal.fire("Solicitud Elementos",
        "El elemento seleccionado ya se ha agregado en el Detalle. Verifique","info");
    }
}

/**
 * Agrega los materiales del arreglo entradaMateriales
 * en la tabla html
 */
function mostrarDatosTabla(){
    datos = "";
    detalleSolicitudElementos.forEach(entrada => {
        //obtiene la posición del material en el arreglo materiales de acuerdo al idMaterial
        //del arreglo entradaMateriales, para poder obtener codigo y nombre del material
        posE = elementos.findIndex(elemento=>elemento.idElemento==entrada.idElemento);
        //obtiene la posición de la unidad de medida en el arreglo UnidadesMedida de acuerdo
        //al idUnidadMedida en arreglo entradaMateriales para poder obtener el nombre
        posU = unidadesMedida.findIndex(unidad=>unidad.id == entrada.idUnidadMedida);
        datos += "<tr>";
        datos += "<td class='text-center'>" + elementos[posE].codigo + "</td>";
        datos += "<td>" + elementos[posE].nombre + "</td>";
        datos += "<td class='text-center'>" + entrada.cantidad + "</td>";
        datos += "<td>" + unidadesMedida[posU].nombre + "</td>";
        datos += "</tr>";
    });
    //agregar a la tabla con id datosTablaMateriales
    datosTablaElementos.innerHTML = datos;
}