from django.http import HttpResponse, JsonResponse, HttpResponseServerError, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Registro, Paciente, Camilla, TransaccionPaypal, Producto, Pedido
import random
from django.utils.decorators import method_decorator
from django.conf import settings
import json
from django.urls import reverse
from . import paypal_utils
from django.views import View



def index(request):
    list(messages.get_messages(request))

    return render (request, 'index.html')

def compra(request):
    list(messages.get_messages(request))
    return render (request, 'compra.html')
#-----------------------------------------------------------------------------        
def register(request):
    list(messages.get_messages(request))
    if request.method == 'POST':
        username = request.POST.get('username', None)
        email = request.POST.get('email', None)
        telefono = request.POST.get('telefono', None)
        password = request.POST.get('password', None)
        confirm_password = request.POST.get('confirm_password', None)

        if not email:
            messages.error(request, 'El campo email es obligatorio.')
            return render(request, 'register.html', {'form_data': request.POST})

        if Registro.objects.filter(usuario=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return render(request, 'register.html', {'form_data': request.POST})
        
        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'register.html', {'form_data': request.POST})

        # Crear el nuevo registro
        nuevo_registro = Registro(usuario=username, email=email, telefono=telefono, contraseña=password)
        nuevo_registro.save()
        
        messages.success(request, 'Registro exitoso.')
        return render(request, 'login.html')
    return render(request, 'register.html')
#-----------------------------------------------------------------------------

def login(request):
    list(messages.get_messages(request))
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
            
        try:
            user = Registro.objects.get(usuario=username, contraseña=password)
            messages.success(request, 'Inicio de sesión exitoso.')
            request.session['registrado_id'] = user.id_registro
            request.session['registrado_usuario'] = user.usuario
            return redirect('inicio')
        except Registro.DoesNotExist:
            messages.error(request, 'Credenciales incorrectas.')
            return render(request, 'login.html', {'form_data': request.POST})
    return render (request, 'login.html')
#-----------------------------------------------------------------------------

def cerrar_sesion(request):
    if 'registrado_id' in request.session:
        del request.session['registrado_id']
    if 'registrado_usuario' in request.session:
        del request.session['registrado_usuario']
    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('login')
#-----------------------------------------------------------------------------
    
def inicio(request):
    list(messages.get_messages(request))
    context = {}
    registrado_id = request.session.get('registrado_id', None)
    print(f"ID en sesión: {request.session.get('registrado_id')}")
    if registrado_id:
        try:
            usuario_logueado = Registro.objects.get(id_registro = registrado_id)
            context['usuario_actual'] = usuario_logueado
        except Registro.DoesNotExist:
            del request.session['registrado_id']
            if 'registrado_usuario' in request.session:
                del request.session['registrado_usuario']
            print(f"Contexto FINAL enviado a la plantilla: {context}")

        # Renderiza la plantilla pasándole el contexto
    return render(request, 'inicio.html', context)
#-----------------------------------------------------------------------------


def asignar(request):    
    list(messages.get_messages(request))
    if request.method == 'POST':
        print("--- DEBUG VISTA ASIGNAR ---")
        print(f'Datos recibidos: {request.POST}')
        print(f'Datos recibidos: {request.POST['motivo_consulta']}')
        nombre_pac = request.POST['nombre_pac']
        apellido_pac = request.POST['apellido_pac']
        rut = request.POST['rut'] 
        email = request.POST['email']
        fecha_nacimiento = request.POST['fecha_nacimiento']
        telefono = request.POST['telefono']
        sexo = request.POST['sexo']
        motivo_consulta = request.POST['motivo_consulta']
        
        if Paciente.objects.filter(rut=rut).exists():
            messages.error(request, 'El RUT ya existe.')
            return render(request, 'asignar.html', {'form_data': request.POST})
        
        nuevo_paciente = Paciente(
        nombre_pac=nombre_pac, apellido_pac=apellido_pac, rut=rut, 
        email=email, telefono=telefono,
        fecha_nacimiento=fecha_nacimiento,sexo=sexo, motivo_consulta=motivo_consulta
        ) 
        nuevo_paciente.save()
        messages.success(request, 'Datos guardados correctamente.') 
        return redirect('asignar')  
    return render(request, 'asignar.html')

    
#-----------------------------------------------------------------------------




def camilla(request):
    list(messages.get_messages(request))
    pacientes = Paciente.objects.all()
    # enviar la informacion de los pacientes a la plantilla
    context = {'pacientes': pacientes}
        
    return render(request, 'camilla.html', context)

#-----------------------------------------------------------------------------


def buscarpac(request):
    list(messages.get_messages(request))
    #Extraer todos los pacientes de la base de datos
    pacientes = Paciente.objects.all()
    # enviar la informacion de los pacientes a la plantilla
    context = {'pacientes': pacientes}
    
    
    if request.method == 'POST':
        rut = request.POST.get('rut')
        nombre_pac = request.POST.get('nombre_pac')
        if rut or nombre_pac:
            pacientes = pacientes.filter(rut=rut) or pacientes.filter(nombre_pac=nombre_pac)
            if pacientes.exists(): 
                context['pacientes'] = pacientes
            else:
                messages.error(request, 'No se encontraron resultados.')
        else:
            messages.error(request, 'Por favor, ingrese un RUT válido.')
                
    return render(request, 'buscarpac.html', context)

#-----------------------------------------------------------------------------


def mensaje(request):
    
    return render(request, 'mensaje.html')

#-----------------------------------------------------------------------------

def asignar_camilla(request, paciente_id):
    list(messages.get_messages(request))
    if request.method == 'POST':
        paciente = Paciente.objects.get(id_paciente=paciente_id)
        if paciente.id_camilla_id:
            return redirect('buscarpac')

        # Obtener todas las camillas disponibles con IDs entre 1 y 100
        camillas_disponibles = Camilla.objects.filter(estado='libre', id_camilla__gte=1, id_camilla__lte=100)

        if not camillas_disponibles.exists():
            messages.error(request, 'No hay camillas disponibles.')
            return redirect('buscarpac')

        camilla_disponible = random.choice(camillas_disponibles)

        # Asignar la camilla al paciente
        paciente.id_camilla_id = camilla_disponible
        paciente.save()

        # Cambiar el estado de la camilla a "ocupada"
        camilla_disponible.estado = 'ocupada'
        camilla_disponible.save()

        messages.success(request, 'Camilla asignada correctamente.')
        return redirect('buscarpac')

    return redirect('buscarpac')
#-----------------------------------------------------------------------------


def liberar_camilla(request, paciente_id):
    list(messages.get_messages(request))
    if request.method == 'POST':
        paciente = Paciente.objects.get(id_paciente=paciente_id)
        if paciente.id_camilla_id:
            camilla = Camilla.objects.get(id_camilla=paciente.id_camilla_id)
            camilla.estado = 'libre'
            camilla.save()

            # Limpiar la relación de la camilla en el paciente
            paciente.id_camilla_id = None
            paciente.save()

        return redirect('buscarpac')

    return redirect('buscarpac')

#-----------------------------------------------------------------------------

def eliminar_paciente(request, paciente_id):
    if request.method == 'POST':
        paciente = Paciente.objects.get(id_paciente=paciente_id)
        if paciente.id_camilla_id:
            messages.success(request, 'Paciente en camilla, no se puede eliminar.')
            return redirect('camilla')        
        else:
            print("entro")
            paciente.delete()
            messages.success(request, 'Paciente eliminado correctamente.')
            return redirect('camilla')

    return redirect('camilla')

#-----------------------------------------------------------------------------

def editar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id_paciente=paciente_id)
    
    if request.method == 'POST':
        
        
        paciente.nombre_pac = request.POST.get('nombre_pac', paciente.nombre_pac)
        paciente.apellido_pac = request.POST.get('apellido_pac', paciente.apellido_pac)
        paciente.rut = request.POST.get('rut', paciente.rut)
        paciente.email = request.POST.get('email', paciente.email)
        paciente.telefono = request.POST.get('telefono', paciente.telefono)
        paciente.fecha_nacimiento = request.POST.get('fecha_nacimiento', paciente.fecha_nacimiento)
        paciente.sexo = request.POST.get('sexo', paciente.sexo)
        paciente.motivo_consulta = request.POST.get('motivo_consulta', paciente.motivo_consulta)

        # Guardar los cambios en la base de datos
        paciente.save()
        
        messages.success(request, 'Paciente editado correctamente.')
        return redirect('buscarpac')
    
    return render(request, 'editar_paciente.html', {'paciente': paciente})
#------------------------------------------------------------------------------

class CheckoutView(View):
    def get(self, request, product_id):
        producto = get_object_or_404(Producto, pk=product_id)
        context = {
            'producto': producto,
            'paypal_client_id': settings.PAYPAL_CLIENT_ID,
            # Pasamos el product_id para que el JS lo pueda usar al llamar a create-order
            'product_id_for_js': product_id,
            # Pasamos las URLs para que el JS sepa a dónde llamar y a dónde redirigir
            'paypal_create_order_url': reverse('paypal_create_order', args=[product_id]),
            'paypal_capture_order_url': reverse('paypal_capture_order'),
            'payment_success_url': reverse('pago_exitoso'),
            'payment_failed_url': reverse('pago_fallido'),
        }
        print(settings.PAYPAL_CLIENT_ID)
        return render(request, 'Pagos/checkout_page.html', context)

#-----------------------------------------------------------------------------

class PaymentSuccessView(View):
    def get(self, request):
        # Aquí podrías obtener información de la sesión o de la query string si PayPal la añade
        # por ejemplo, request.GET.get('token'), request.GET.get('PayerID') si usaras otro flujo.
        # Con el flujo actual de JS SDK, la redirección la hacemos nosotros.
        # Podrías pasar un ID de pedido si lo guardaste en la sesión en CapturePayPalOrderView
        # order_id = request.session.get('last_order_id')
        # if order_id:
        #     # Obtener detalles del pedido para mostrar
        #     pass
        return render(request, 'Pagos/pago_exitoso.html')



class PaymentFailedView(View):
    def get(self, request):
        # Aquí podrías obtener información de error de la sesión o query string
        return render(request, 'Pagos/pago_fallido.html')


@method_decorator(csrf_exempt, name='dispatch')
class CreatePayPalOrderView(View):
    def post(self, request, product_id):
        try:
            producto = get_object_or_404(Producto, pk=product_id)

            # --- NUEVO: Guardar product_id en la sesión ---
            request.session['paypal_pending_product_id'] = producto.id_producto
            # También podrías guardar el monto esperado aquí para una verificación extra al capturar
            # request.session['paypal_pending_amount'] = str(producto.monto)

            order_payload = paypal_utils.create_paypal_order(
                product_name=producto.nombre,
                product_sku=str(producto.id_producto),
                quantity=1,
                unit_amount_value=producto.monto,
                currency_code="USD" # O la moneda de tu producto/tienda
            )

            if order_payload and order_payload.get("id"):
                # --- NUEVO: Guardar el paypal_order_id en sesión para referencia ---
                request.session['paypal_pending_order_id'] = order_payload["id"]
                return JsonResponse({"orderID": order_payload["id"]})
            else:
                # Limpiar la sesión si la creación de la orden falla
                if 'paypal_pending_product_id' in request.session:
                    del request.session['paypal_pending_product_id']
                if 'paypal_pending_order_id' in request.session:
                    del request.session['paypal_pending_order_id']

                error_message = "No se pudo crear la orden en PayPal."
                # ... (tu manejo de errores existente) ...
                return JsonResponse({"error": error_message}, status=500)

        except Producto.DoesNotExist:
            return JsonResponse({"error": "Producto no encontrado."}, status=404)
        except Exception as e:
            print(f"Excepción en CreatePayPalOrderView: {e}")
            # Limpiar la sesión en caso de excepción también
            if 'paypal_pending_product_id' in request.session:
                del request.session['paypal_pending_product_id']
            if 'paypal_pending_order_id' in request.session:
                del request.session['paypal_pending_order_id']
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CapturePayPalOrderView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            paypal_order_id_from_js = data.get('orderID')

            if not paypal_order_id_from_js:
                return JsonResponse({"error": "orderID no proporcionado por JS."}, status=400)

            # --- Recuperar datos de la sesión para el producto y la orden de PayPal ---
            pending_product_id = request.session.get('paypal_pending_product_id')
            session_paypal_order_id = request.session.get('paypal_pending_order_id')

            # Opcional: Verificación de consistencia del OrderID
            if not session_paypal_order_id or session_paypal_order_id != paypal_order_id_from_js:
                print(f"ADVERTENCIA: Discrepancia de OrderID. JS: {paypal_order_id_from_js}, Sesión: {session_paypal_order_id}")
                # Decide si quieres ser estricto y abortar. Por ahora, continuamos.
                pass

            if not pending_product_id:
                return JsonResponse({"error": "No se encontró el ID del producto pendiente en la sesión."}, status=400)

            # --- Capturar el pago en PayPal ---
            capture_response = paypal_utils.capture_paypal_order(paypal_order_id_from_js)

            if capture_response and capture_response.get("status") == "SUCCESS":
                # ÉXITO EN LA CAPTURA DE PAYPAL

                # Obtener el producto comprado
                try:
                    producto_comprado = Producto.objects.get(pk=pending_product_id)
                except Producto.DoesNotExist:
                    print(f"Error CRÍTICO: Producto con ID {pending_product_id} no encontrado después del pago.")
                    producto_comprado = None # O manejar de otra forma, el pago ya está hecho

                # --- Obtener usuario de 'Registro' usando el ID de la sesión ---
                registro_usuario_actual = None
                logged_user_id_registro = request.session.get('registrado_id') # Usamos la clave de sesión de tu función login

                if logged_user_id_registro:
                    try:
                        registro_usuario_actual = Registro.objects.get(pk=logged_user_id_registro)
                        print(f"Pedido asociado al usuario de Registro: {registro_usuario_actual.usuario}")
                    except Registro.DoesNotExist:
                        print(f"Usuario de Registro con ID {logged_user_id_registro} (de sesión) no encontrado en BD.")
                        # El usuario pudo haber sido eliminado mientras la sesión estaba activa.
                        # El pedido se creará como invitado.
                        pass
                else:
                    print("No hay usuario de Registro logueado (sesión 'registrado_id' no encontrada). Pedido como invitado.")


                # Extraer detalles de la respuesta de PayPal para el Pedido
                paypal_capture_details = capture_response.get("details", {})
                purchase_unit = paypal_capture_details.get("purchase_units", [{}])[0]
                amount_details = purchase_unit.get("amount", {})
                payer_details = paypal_capture_details.get("payer", {})
                payer_name_details = payer_details.get("name", {})
                payments = purchase_unit.get("payments", {})
                captures_list = payments.get("captures", [{}]) # Renombrado a captures_list para evitar colisión
                capture_id_from_paypal = captures_list[0].get("id") if captures_list else None


                # --- Crear el objeto Pedido en la base de datos ---
                try:
                    nuevo_pedido = Pedido.objects.create(
                        registro_usuario=registro_usuario_actual, # Puede ser None si es invitado
                        producto=producto_comprado, # Puede ser None si el producto fue borrado (raro pero posible)
                        paypal_order_id=paypal_capture_details.get("id"),
                        paypal_capture_id=capture_id_from_paypal,
                        monto_total=amount_details.get("value", "0.00"), # Asegúrate de que sea un string para DecimalField si es necesario
                        moneda=amount_details.get("currency_code", "USD"),
                        estado='COMPLETADO',
                        payer_email=payer_details.get("email_address"),
                        payer_id_paypal=payer_details.get("payer_id"),
                        payer_nombre=f"{payer_name_details.get('given_name', '')} {payer_name_details.get('surname', '')}".strip()
                    )
                    print(f"Pedido #{nuevo_pedido.id} creado exitosamente para el producto '{producto_comprado.nombre if producto_comprado else 'N/A'}'.")
                    # request.session['last_order_db_id'] = nuevo_pedido.id # Opcional, para usar en página de éxito

                except Exception as e:
                    print(f"Error CRÍTICO al guardar el pedido en la BD después del pago exitoso en PayPal: {e}")
                    # Aquí deberías tener un sistema de alerta para administradores.
                    # El pago está hecho, pero el pedido no se registró.

                # --- Limpiar variables de sesión relacionadas con este pago ---
                keys_to_delete_from_session = ['paypal_pending_product_id', 'paypal_pending_order_id']
                for key in keys_to_delete_from_session:
                    if key in request.session:
                        del request.session[key]
                print("Variables de sesión de PayPal limpiadas.")

                return JsonResponse({
                    "status": "success",
                    "orderID": capture_response.get("id"),
                    "captureID": capture_id_from_paypal,
                })
            else: # La captura en PayPal no fue "SUCCESS"
                # Limpiar variables de sesión también si la captura falla
                keys_to_delete_from_session = ['paypal_pending_product_id', 'paypal_pending_order_id']
                for key in keys_to_delete_from_session:
                    if key in request.session:
                        del request.session[key]
                
                error_message = "No se pudo capturar el pago en PayPal."
                if capture_response and capture_response.get('message'):
                     error_message = capture_response.get('message')
                # ... (tu lógica de mensajes de error)
                print(f"Fallo en la captura de PayPal: {error_message}, Detalles: {capture_response}")
                return JsonResponse({"error": error_message, "details": capture_response}, status=400)

        except json.JSONDecodeError:
            print("Error: JSON inválido en el cuerpo de la solicitud de captura.")
            return JsonResponse({"error": "JSON inválido en el cuerpo de la solicitud."}, status=400)
        except Exception as e:
            print(f"Excepción general en CapturePayPalOrderView: {e}")
            # Limpiar variables de sesión en caso de excepción inesperada
            keys_to_delete_from_session = ['paypal_pending_product_id', 'paypal_pending_order_id']
            for key in keys_to_delete_from_session:
                if key in request.session:
                    del request.session[key]
            return JsonResponse({"error": str(e)}, status=500)
