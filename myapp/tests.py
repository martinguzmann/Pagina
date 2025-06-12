from django.test import TestCase, Client
from django.db.utils import IntegrityError
from .models import Registro, Paciente
from django.urls import reverse
from django.contrib.messages import get_messages


class RegistroModelTest(TestCase):
    
    def setUp(self):
        
        self.registro_prueba = Registro.objects.create(
            usuario=Registro.usuario.field.get_default(),
            email=Registro.email.field.get_default(),
            telefono=Registro.telefono.field.get_default(),
            contraseña=Registro.contraseña.field.get_default()
        )
        
    def test_registro_exitoso(self):
        registro = self.registro_prueba
        self.assertEqual(registro.usuario, Registro.usuario.field.get_default())
        self.assertEqual(registro.email, Registro.email.field.get_default())
        
    def test_usuario_unico(self):
        with self.assertRaises(IntegrityError):
            Registro.objects.create(
                usuario=self.registro_prueba.usuario,
            )
            
            
            
class PacienteModelTest(TestCase):
        
    def setUp(self):

        self.client = Client()
        self.asignar_url = reverse('asignar')        
        self.paciente_existente = Paciente.objects.create(
            nombre_pac='Juan',
            apellido_pac='Pérez',
            rut='12345678-9',
            email='juan@perez.com',
            fecha_nacimiento='1990-01-01',
            telefono='987654321',
            sexo='M',
            motivo_consulta='Dolor de cabeza'
        )
        
    def test_creacion_exitosa_de_paciente_con_POST(self):

        datos_formulario = {
            'nombre_pac': 'Ana',
            'apellido_pac': 'García',
            'rut': '11223344-5',
            'email': 'ana@garcia.com',
            'fecha_nacimiento': '1995-05-10',
            'telefono': '123456789',
            'sexo': 'F',
            'motivo_consulta': 'Chequeo general'
        }
        response = self.client.post(self.asignar_url, data=datos_formulario)
        self.assertEqual(Paciente.objects.count(), 2)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.asignar_url) 
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Datos guardados correctamente.')
        
    def test_error_al_crear_paciente_con_RUT_duplicado(self):

        datos_formulario_duplicado = {
            'nombre_pac': 'Pedro',
            'apellido_pac': 'Soto',
            'rut': '12345678-9', 
            'email': 'pedro@soto.com',
            'fecha_nacimiento': '1988-03-15',
            'telefono': '555666777',
            'sexo': 'M',
            'motivo_consulta': 'Dolor de espalda'
        }
        
        response = self.client.post(self.asignar_url, data=datos_formulario_duplicado)

        self.assertEqual(Paciente.objects.count(), 1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'asignar.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'El RUT ya existe.')
