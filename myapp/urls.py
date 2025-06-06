from django.urls import path
from . import views


urlpatterns = [
    path('', views.index),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('inicio/', views.inicio, name = 'inicio'),
    path('asignar/', views.asignar, name = 'asignar'),
    path('camilla/', views.camilla, name = 'camilla'),
    path('buscarpac/', views.buscarpac, name = 'buscarpac'),
    path('mensaje/', views.mensaje, name = 'mensaje'),
    path('asignar-camilla/<int:paciente_id>/', views.asignar_camilla, name='asignar_camilla'),
    path('liberar-camilla/<int:paciente_id>/', views.liberar_camilla, name='liberar_camilla'),
    path('eliminar-paciente/<int:paciente_id>/', views.eliminar_paciente, name='eliminar_paciente'),
    path('editar-paciente/<int:paciente_id>/', views.editar_paciente, name='editar_paciente'),
    path('compra/', views.compra, name='compra'),
    path('payment/success/', views.PaymentSuccessView.as_view(), name='pago_exitoso'),
    path('payment/failed/', views.PaymentFailedView.as_view(), name='pago_fallido'),
    path('checkout/<int:product_id>/', views.CheckoutView.as_view(), name='checkout_page'),
    path('paypal/create-order/<int:product_id>/', views.CreatePayPalOrderView.as_view(), name='paypal_create_order'),
    path('paypal/capture-order/', views.CapturePayPalOrderView.as_view(), name='paypal_capture_order'),

  
    ]