# mi_app/paypal_utils.py

import requests
import base64
from django.conf import settings
from django.urls import reverse # Usaremos reverse para las URLs de retorno

# --- Obtener Token de Acceso de PayPal ---
def get_paypal_access_token():
    """
    Obtiene un token de acceso de la API de PayPal.
    """
    client_id = settings.PAYPAL_CLIENT_ID
    client_secret = settings.PAYPAL_SECRET

    auth = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US",
        "Authorization": f"Basic {auth}",
    }
    data = {
        "grant_type": "client_credentials",
    }
    token_url = f"{settings.PAYPAL_API_BASE_URL}/v1/oauth2/token"

    try:
        response = requests.post(token_url, headers=headers, data=data, timeout=10)
        response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
        token_data = response.json()
        return token_data.get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener token de PayPal: {e}")
        if response is not None:
            print(f"Respuesta de PayPal: {response.text}")
        return None

# --- Crear Orden en PayPal ---
def create_paypal_order(product_name, product_sku, quantity, unit_amount_value, currency_code="USD"):
    """
    Crea una orden en PayPal.
    https://developer.paypal.com/docs/api/orders/v2/#orders_create
    """
    access_token = get_paypal_access_token()
    if not access_token:
        return None

    order_url = f"{settings.PAYPAL_API_BASE_URL}/v2/checkout/orders"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        # "PayPal-Request-Id": "opcional_unique_id_para_idempotencia"
    }

    # Usamos reverse para obtener las URLs de forma dinámica
    # Asumimos que tienes nombres de URL 'pago_exitoso' y 'pago_fallido' definidos en tu urls.py
    try:
        return_url = settings.BASE_URL + reverse('pago_exitoso')
        cancel_url = settings.BASE_URL + reverse('pago_fallido')
    except Exception as e:
        # Fallback a las URLs definidas en settings si reverse falla (ej. urls no cargadas aún)
        # Esto es menos ideal, pero una salvaguarda. Asegúrate de que tus URLs estén nombradas.
        print(f"Advertencia: No se pudieron resolver las URLs con reverse. Usando URLs de settings. Error: {e}")
        return_url = settings.PAYPAL_RETURN_URL
        cancel_url = settings.PAYPAL_CANCEL_URL


    # Estructura de la orden. Puedes personalizarla mucho más.
    # Ver documentación de PayPal para más detalles sobre ítems, desglose, etc.
    order_data = {
        "intent": "CAPTURE", # CAPTURE para capturar el pago inmediatamente. AUTHORIZE para autorizar y capturar luego.
        "purchase_units": [
            {
                "reference_id": f"PUHF_{product_sku}", # Un ID de referencia tuyo
                "description": f"Compra de {product_name}",
                "custom_id": f"CUST_{product_sku}", # Otro ID personalizado
                "items": [
                    {
                        "name": product_name,
                        "sku": product_sku, # Opcional, pero bueno para seguimiento
                        "quantity": str(quantity), # Debe ser string
                        "unit_amount": {
                            "currency_code": currency_code,
                            "value": str(unit_amount_value), # Debe ser string
                        }
                    }
                ],
                "amount": {
                    "currency_code": currency_code,
                    "value": str(float(unit_amount_value) * int(quantity)), # Calcula el total
                    "breakdown": { # Desglose del monto
                        "item_total": {
                            "currency_code": currency_code,
                            "value": str(float(unit_amount_value) * int(quantity)),
                        }
                        # Aquí podrías añadir shipping, tax_total, etc.
                    }
                }
            }
        ],
        "application_context": {
            "brand_name": "Tu Tienda Increíble", # Nombre de tu tienda que aparece en PayPal
            "locale": "es-ES", # Opcional: para la experiencia de PayPal
            "landing_page": "LOGIN", # O "GUEST_CHECKOUT" o "NO_PREFERENCE"
            "shipping_preference": "NO_SHIPPING", # O "GET_FROM_FILE", "SET_PROVIDED_ADDRESS"
            "user_action": "PAY_NOW", # Texto del botón final en PayPal
            "return_url": return_url,
            "cancel_url": cancel_url,
        }
    }

    try:
        response = requests.post(order_url, headers=headers, json=order_data, timeout=20)
        response.raise_for_status()
        order_response = response.json()
        # Devolvemos el ID de la orden y los links de aprobación para el SDK de JS
        # El SDK de JS usará el ID, pero es bueno tener los links si se necesitaran para otros flujos
        return {
            "id": order_response.get("id"),
            "approve_url": next((link["href"] for link in order_response.get("links", []) if link["rel"] == "approve"), None)
        }
    except requests.exceptions.RequestException as e:
        print(f"Error al crear orden en PayPal: {e}")
        if response is not None:
            print(f"Respuesta de PayPal: {response.text}")
            try:
                print(f"Detalles del error de PayPal: {response.json()}")
            except ValueError:
                pass # No es JSON
        return None

# --- Capturar Orden en PayPal ---
def capture_paypal_order(order_id):
    """
    Captura el pago para una orden previamente aprobada.
    https://developer.paypal.com/docs/api/orders/v2/#orders_capture
    """
    access_token = get_paypal_access_token()
    if not access_token:
        return {"status": "ERROR", "message": "No se pudo obtener token de acceso"}

    capture_url = f"{settings.PAYPAL_API_BASE_URL}/v2/checkout/orders/{order_id}/capture"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        # "PayPal-Request-Id": "opcional_unique_id_para_idempotencia"
    }

    try:
        response = requests.post(capture_url, headers=headers, timeout=30) # No hay 'data' o 'json' body para una captura simple
        response.raise_for_status()
        capture_data = response.json()
        
        # Verificar el estado de la captura
        if capture_data.get("status") == "COMPLETED":
            return {
                "status": "SUCCESS",
                "id": capture_data.get("id"), # ID de la orden de PayPal
                "paypal_capture_id": capture_data.get("purchase_units")[0].get("payments").get("captures")[0].get("id"), # ID específico de la captura
                "payer_email": capture_data.get("payer", {}).get("email_address"),
                "payer_name": f"{capture_data.get('payer', {}).get('name', {}).get('given_name', '')} {capture_data.get('payer', {}).get('name', {}).get('surname', '')}".strip(),
                "details": capture_data
            }
        else:
            # Podría haber otros estados como PENDING, DENIED, etc.
            return {"status": "ERROR", "message": f"Estado de captura no completado: {capture_data.get('status')}", "details": capture_data}

    except requests.exceptions.RequestException as e:
        print(f"Error al capturar orden en PayPal ({order_id}): {e}")
        error_details = {"status": "ERROR", "message": str(e)}
        if response is not None:
            print(f"Respuesta de PayPal: {response.text}")
            try:
                error_details["paypal_response"] = response.json()
            except ValueError:
                error_details["paypal_response_text"] = response.text
        return error_details