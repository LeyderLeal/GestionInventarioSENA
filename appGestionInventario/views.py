from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate
from django.contrib import auth
from django.conf import settings
import urllib
from django.contrib.auth.models import Group
import json, string, random
from django.db import transaction, Error
from appGestionInventario.models import *
from django.http import JsonResponse

#enviar correo
from django.core.mail import EmailMultiAlternatives
import threading #hilos envio de correo
from smtplib import SMTPException
from django.template.loader import get_template

from django.views.decorators.csrf import csrf_exempt
# Create your views here.

#Formulario inicial
#Inicio de la pagina
def vistaInicio(request):
    return render(request, "frmIniciarSesion.html")
    # template=loader.get_template('frmIniciarSesion.html')
    # return HttpResponse(template.render())


def inicioAsistente(request):
    # if request.user.is_authenticated:
        return render(request, "asistente/inicioAsis.html")
    # else:
        retorno={"mensaje":"Debe ingresar con sus credenciales"}
        return render(request, "frmIniciarSesion.html", retorno)


def inicioInstructor(request):
    # if request.user.is_authenticated:
        return render(request, "Instructor/inicioIns.html")
    # else:
        retorno={"mensaje":"Debe ingresar con sus credenciales"}
        return render(request, "frmIniciarSesion.html", retorno)

      
#Parte del Administrador del menu principal
def inicioAdmin(request):
    # if request.user.is_authenticated:
        return render(request, "administrador/inicioAdmin.html")
    # else:
        retorno={"mensaje":"debe ingresar con sus credenciales"}
        return render(request, "frmIniciarSesion.html", retorno)


#Salir del modo adminsitrador
def salida(request):
    return render(request, "inicio.html")


#formulario administrador para registrar el usuario
def vistaRegistrarUsuario(request):
    roles = Group.objects.all()
    retorno={"tipoUsuario":tipoUsuario, "roles":roles}
    return render(request, "administrador/frmRegistrarUsuarioAd.html", retorno)


#Registrar usuario a la base de datos
def registrarUsuario(request):
    try:
        nombre= request.POST["txtNombre"]
        apellidos=request.POST["txtApellido"]
        correo=request.POST["txtEmail"]
        tipo=request.POST["cbTipoUser"]
        foto=request.FILES.get("fileFoto", False)
        idRol=int(request.POST["cbRol"])
        with transaction.atomic():
            user=User(username=correo, first_name=nombre, last_name=apellidos, email=correo, userTipo=tipo, userFoto=foto)
            user.save()
            
            rol=Group.objects.get(pk=idRol)
            
            user.groups.add(rol)
            
            if(rol.name=="Administrador"):user.is_staff=True
            
            user.save()
            
            passwordGenerado= generarPassword()
            print(f"password{passwordGenerado}")
            
            user.set_password(passwordGenerado)
            
            user.save()
            
            mensaje="Usuario Agregado Correctamente"
            retorno={"mensaje":mensaje}
            
            asunto='Registro Sistema Inventario CIES-NEIVA'
            mensaje=f'Cordial Saludo,<b>{user.first_name}{user.last_name}</b>, nos permitimos \
                informarle que usted ha sido registrado en el sistema de Gestion de Inventario \
                del centro de la industria, la Empresa y los servicios CIES de la ciudad de Neiva. \
                Nos permitimos enviarle las credenciales de Ingreso a nuestro sistema.<br>\
                <br><b>Username:</b>{user.username}\
                <br><b>Password:</b>{passwordGenerado}\
                <br><b>Lo invitamos a ingresar a nuestro sistema en la url:\
                http://gestioninventario.sena.edu.co </b>'
            thread=threading.Thread(target=enviarCorreo, args=(asunto, mensaje, user.email))
            thread.start()
            
            return redirect("/vistaGestionarUsuarios/", retorno)
    except Error as error:
        transaction.rollback()
        mensaje=f"{error}"
    retorno={"mensaje":mensaje, "user":user}
    return render(request, "administrador/frmRegistrarUsuarioAd.html", retorno)


#Lista de los usuraios agregados
def vistaGestionarUsuarios(request):
    lista_usuarios = User.objects.all()
    return render(request, "administrador/listaUsuarios.html", {"lista_usuarios": lista_usuarios})


#para generar la contraseña
def generarPassword():
    longitud=10
    caracteres=string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    password=''
    for i in range(longitud):
        password += ''.join(random.choice(caracteres))
    return password


def enviarCorreo(asunto=None, mensaje=None, destinatario=None):
    remitente=settings.EMAIL_HOST_USER
    template=get_template('enviarCorreo.html')
    contenido=template.render({
        'destinatario': destinatario,
        'mensaje': mensaje,
        'asunto':asunto,
        'remitente': "leyder.leal2005@gmail.com",
    })
    try:
        correo=EmailMultiAlternatives(asunto, mensaje, remitente, [destinatario])
        correo.attach_alternative(contenido, 'text/html')
        correo.send(fail_silently=True)
    except SMTPException as error:
        print(error)
            

#Formulario inicial
# def vistaLogin(request):
#     # template=loader.get_template('frmIniciarSesion.html')
#     # return HttpResponse(template.render())
#     return render(request, "frmIniciarSesion.html")

    
#METODO LOGIN
@csrf_exempt
def login(request):
    
    recaptcha_response = request.POST.get('g-recaptcha-response')
    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = { 
        'secret':settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        'response':recaptcha_response
    }
    data = urllib.parse.urlencode(values).encode()
    req = urllib.request.Request(url,data=data)
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode())
    print(result)
    
    if result['success']:
        username = request.POST["txtUsername"]
        password = request.POST["txtPassword"]
        user = authenticate(username=username, password=password)
        if user is not None:
            #registar la variable de sesión
            auth.login(request, user)
            if user.groups.filter(name='Administrador').exists():
                return redirect('/inicioAdmin')
            elif user.groups.filter(name='Asistente').exists():
                return redirect('/inicioAsis')
            else:
                return redirect('/inicioInst')
        else:
            mensaje = "Usuario o Contraseña Incorrectas"
            return render(request, "frmIniciarSesion.html", {"mensaje":mensaje})
    else:
        mensaje="Debe Validar primero el recaptcha"
        return render(request, "frmIniciarSesion.html", {"mensaje":mensaje})
    
    
def vistaGestionarDevolutivos(request):
    # if request.user.is_authenticated:
        elementosDevolutivos= Devolutivo.objects.all()
        retorno = {"listaElementosDevolutivos": elementosDevolutivos}
        print(elementosDevolutivos)
        return render(request, "asistente/vistaGestionarElementos.html", retorno)
    # else:
        mensaje="Debe iniciar sesion"
        return render(request, "frmIniciarSesion.html", {"mensaje":mensaje})


def vistaRegistrarDevolutivo(request):
    retorno = {"tipoElementos":tipoElemento, "estados":estadosElementos}
    print(retorno)
    return render(request, "asistente//frmRegistrarDevolutivos.html", retorno)


def registrarDevolutivo(request):
    estado=False
    try:
        placaSena=request.POST["txtPlaca"]
        fechaInventarioSena=request.POST["txtFecha"]
        tipoElemento=request.POST["cbTipoElementos"]
        serial=request.POST.get("txtSerial", False)
        marca=request.POST.get("txtMarca", False)
        valorUnitario=request.POST["txtValorUnitario"]
        estado=request.POST["cbEstado"]
        nombre=request.POST["txtNombre"]
        descripcion=request.POST["txtDescripcion"]
        deposito=request.POST["cbDeposito"]
        estante=request.POST.get("txtEstante", False)
        entrepano=request.POST.get("txtEntrepano", False)
        locker=request.POST.get("txtLocker", False)
        archivo=request.FILES.get("fileFoto", False)
        with transaction.atomic():
            
            cantidad=Elemento.objects.all().count()
            
            codigoElemento = tipoElemento.upper() + str(cantidad+1).rjust(6, '0')
            
            elemento=Elemento(eleCodigo=codigoElemento, eleNombre=nombre, eleTipo=tipoElemento, eleEstado=estado)
            
            elemento.save()
            
            ubicacion=UbicacionFisica(ubiDeposito=deposito, ubiEstante=estante, ubiEntrepano=entrepano, ubiLocker=locker, ubiElemento=elemento)
            
            ubicacion.save()
            
            elementoDevolutivo = Devolutivo(devPlacaSena=placaSena, devSerial=serial, devDescripcion=descripcion, devMarca=marca, devFechaIngresoSENA=fechaInventarioSena,
                                          devValor=valorUnitario, devFoto=archivo, devElemento=elemento)
            
            elementoDevolutivo.save()
            estado=True
            mensaje=f"Elemento devolutivo registrado satisfectoriamente con el codigo {codigoElemento}"
    except Error as error:
        transaction.rollback()
        mensaje=f"{error}"
    retorno={"mensaje":mensaje, "devolutivo":elementoDevolutivo, "estado":estado}
    return render(request, "asistente/frmRegistrarDevolutivos.html", retorno)




def vistaRegistrarMaterial(request):
    unidadesMedida = UnidadMedida.objects.all()
    retorno = {"unidadesMedida": unidadesMedida, "estados": estadosElementos}
    return render(request,"asistente/frmRegistrarMaterial.html", retorno)

  
def registrarMaterial(request):
    estado=False

    try:
        nombre = request.POST["txtNombre"]
        marca = request.POST.get("txtMarca",None)
        descripcion = request.POST.get("txtDescripcion",None)
        estado = request.POST["cbEstado"]
        deposito = request.POST["cbDeposito"]
        estante = request.POST.get("txtEstante",False)
        entrepano =request.POST.get("txtEntrepano",False)
        locker = request.POST.get("txtLocker",False)
        
        with transaction.atomic():
            cantidad = Elemento.objects.all().filter(eleTipo="MAT").count()
            codigoElemento = "MAT" + str(cantidad+1).rjust(6, '0')
            # crear el elemento
            elemento = Elemento(eleCodigo = codigoElemento, eleNombre = nombre,
                                eleTipo = "MAT", eleEstado = estado )
            # salvar el elemento en la base de datos
            elemento.save()
            # crear el material
            material = Material (matReferencia = descripcion,matMarca=marca,
                                matElemento = elemento)

            material.save()

            #crear objeto ubicación física del elemeto"

            ubicacion = UbicacionFisica(ubiDeposito = deposito,ubiEstante = estante,
                            ubiEntrepano = entrepano, ubiLocker = locker, ubiElemento = elemento)

            # registrar en la base de datos la ubicación física del elemento

            ubicacion.save()
            estado=True
            mensaje=f"Material registrado Satisfactoriamente con el codigo {codigoElemento}"
    except Error as error:
        transaction.rollback()
        mensaje=f"{error}"
    retorno = {"mensaje":mensaje, "material": material, "estado":estado}
    return render(request,"asistente/frmRegistrarMaterial.html", retorno)
    
    

def vistaEntradaMaterial(request):
    proveedores = Proveedor.objects.all()
    usuarios = User.objects.all()
    materiales = Material.objects.all()
    unidadesMedida = UnidadMedida.objects.all()
    
    retorno = {"proveedores":proveedores, "usuarios":usuarios,
               "materiales":materiales, "unidadesMedida": unidadesMedida}
    return render(request,"asistente/frmRegistrarEntradaMaterial.html", retorno)


def registrarEntradaMaterial(request):
    if request.method == "POST":
        estado = False
        try:
            with transaction.atomic():
                
                codigoFactura = request.POST.get('codigoFactura')
                entregadoPor = request.POST.get('entregadoPor')
                idProveedor = int(request.POST.get('proveedor'))
                recibidoPor = int(request.POST.get('recibidoPor'))
                fechaHora = request.POST.get('fechaHora',None)
                observaciones = request.POST.get('observaciones')
                userRecibe = User.objects.get(pk=recibidoPor)
                proveedor = Proveedor.objects.get(pk=idProveedor)
                entradaMaterial = EntradaMaterial(entNumeroFactura = codigoFactura, entFechaHora = fechaHora,
                                                  entUsuarioRecibe= userRecibe, entEntregadoPor = entregadoPor,
                                                  entProveedor = proveedor, entObservaciones=observaciones)
                entradaMaterial.save()
                detalleMateriales = json.loads(request.POST.get('detalle'))
                for detalle in detalleMateriales:
                    material = Material.objects.get(pk=int(detalle['idMaterial'])) 
                    cantidad = int(detalle['cantidad'])
                    precio = int(detalle['precio'])
                    estado = detalle['estado']
                    unidadMedida = UnidadMedida.objects.get(pk=int(detalle['idUnidadMedida']))
                    detalleEntradaMaterial = DetalleEntradaMaterial(detEntradaMaterial = entradaMaterial,
                    detMaterial = material, detUnidadMedida = unidadMedida,
                    detCantidad=cantidad, detPrecioUnitario = precio, devEstado=estado)
                    detalleEntradaMaterial.save()
                estado = True
                mensaje = "Se ha registrado la entrada de Materiales correctamente" 
        except Error as error:
            transaction.rollback()
            mensaje = f"{error}"
        retorno={"estado":estado, "mensaje":mensaje}
        return JsonResponse(retorno)
        

def solicitudesInstructor(request):
    # se obtienen las solicitudes de acuerdo al usuario en sesión
    solicitudes = SolicitudElemento.objects.filter(solUsuario=request.user)
    detalleSolicitudes=[]
    for solicitud in solicitudes:
        detalle = DetalleSolicitud.objects.filter(detSolicitud = solicitud)
        detalleSolicitudes.append(detalle)
    retorno = {"solicitudes":solicitudes,"detalleSolicitudes":detalleSolicitudes}
    return render(request,"instructor/misSolicitudes.html",retorno)

def vistaRegistrarSolicitud(request):
    usuarios = User.objects.all()
    elementos = Elemento.objects.all()
    unidadesMedida = UnidadMedida.objects.all()
    fichas = Ficha.objects.all()
    
    retorno = {"usuarios": usuarios, "elementos":elementos,
               "unidadesMedida":unidadesMedida, "ficha":fichas}
    return render(request, "instructor/frmRegistrarSolicitud.html", retorno)




