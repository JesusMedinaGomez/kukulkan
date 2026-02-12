from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, EmailValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.contrib.auth.models import User
import os
from tinymce.models import HTMLField

# ============================================
# CONFIGURACIÓN GENERAL DEL SITIO 
# ============================================

class ConfiguracionSitio(models.Model):
    """Configuración global del sitio web"""
    nombre_sitio = models.CharField(max_length=100, default='Logia Kukulkan #41')
    lema_principal = models.CharField(max_length=200, blank=True, 
                                      default='"Pulir la piedra bruta para construir el templo interior"')
    logo_tipo = models.CharField(max_length=50, default='∴', 
                                help_text='Símbolo principal del logo')
    logo_texto = models.CharField(max_length=100, default='Logia Kukulkan #41 · Mérida')
    
    color_primario = models.CharField(max_length=7, default='#7b1e3a', 
                                     help_text='Color Borgoña - HEX')
    color_secundario = models.CharField(max_length=7, default='#FFD700', 
                                       help_text='Color Dorado - HEX')
    
    url_moodle = models.URLField(
        max_length=200, 
        blank=True, 
        null=True,  
        default='https://moodle.kukulkan41.org',
        verbose_name='URL de Moodle',
        help_text='URL de la plataforma educativa Moodle'
    )
    url_moodle_login = models.URLField(
        max_length=200, 
        blank=True, 
        null=True,  
        default='https://moodle.kukulkan41.org/login',
        verbose_name='URL de login de Moodle',
        help_text='URL para iniciar sesión en Moodle'
    )
    texto_boton_moodle = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,  
        default='Ir a Moodle',
        verbose_name='Texto del botón Moodle'
    )
    
    # SEO
    meta_descripcion = models.TextField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)
    google_analytics_id = models.CharField(max_length=50, blank=True)
    
    # Redes sociales
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    
    # Pie de página
    copyright_text = models.CharField(max_length=200, default='Todos los derechos reservados')
    ano_fundacion = models.IntegerField(default=1980)
    
    activo = models.BooleanField(default=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Configuración del sitio'
        verbose_name_plural = 'Configuración del sitio'
    
    def save(self, *args, **kwargs):
        if not self.pk and ConfiguracionSitio.objects.exists():
            raise ValidationError('Solo puede existir una configuración del sitio')
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Configuración: {self.nombre_sitio}"
    
# ============================================
# NAVEGACIÓN
# ============================================

class ItemMenu(models.Model):
    """Items del menú de navegación"""
    TIPO_ENLACE = [
        ('url_named', 'URL nombrada (Django)'),
        ('url_externa', 'URL externa'),
        ('pagina', 'Página interna'),
    ]
    
    titulo = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    tipo_enlace = models.CharField(max_length=20, choices=TIPO_ENLACE, default='url_named')
    url_name = models.CharField(max_length=100, blank=True)
    url_externa = models.URLField(blank=True)
    pagina = models.ForeignKey('Pagina', on_delete=models.SET_NULL, null=True, blank=True)
    orden = models.PositiveIntegerField(default=0)
    es_activo = models.BooleanField(default=True)
    padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subitems')
    icono = models.CharField(max_length=50, blank=True)
    solo_miembros = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['orden', 'titulo']
        verbose_name = 'Item del menú'
        verbose_name_plural = 'Items del menú'
    
    def __str__(self):
        prefix = '→ ' * self.nivel if self.padre else ''
        return f"{prefix}{self.titulo}"
    
    @property
    def nivel(self):
        nivel = 0
        p = self.padre
        while p:
            nivel += 1
            p = p.padre
        return nivel


# ============================================
# PÁGINAS Y CONTENIDO ESTÁTICO
# ============================================

class Pagina(models.Model):
    """Páginas de contenido estático"""
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    subtitulo = models.CharField(max_length=300, blank=True)
    contenido = models.TextField()
    contenido_resumido = models.TextField(max_length=500, blank=True)
    
    imagen_destacada = models.ImageField(upload_to='paginas/', blank=True, null=True)
    imagen_descripcion = models.CharField(max_length=200, blank=True)
    
    meta_titulo = models.CharField(max_length=200, blank=True)
    meta_descripcion = models.TextField(max_length=300, blank=True)
    palabras_clave = models.CharField(max_length=200, blank=True)
    
    fecha_publicacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    es_activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)
    solo_miembros = models.BooleanField(default=False)
    requiere_autenticacion = models.BooleanField(default=False)
    plantilla = models.CharField(max_length=100, default='default')
    
    class Meta:
        ordering = ['-destacado', 'orden', '-fecha_publicacion']
        verbose_name = 'Página'
        verbose_name_plural = 'Páginas'
    
    def __str__(self):
        return self.titulo
    
    @property
    def get_meta_titulo(self):
        return self.meta_titulo or self.titulo


class SeccionPagina(models.Model):
    """Secciones modulares dentro de una página"""
    TIPO_SECCION = [
        ('texto', 'Texto completo'),
        ('texto_imagen', 'Texto con imagen'),
        ('galeria', 'Galería'),
        ('cards', 'Tarjetas'),
        ('timeline', 'Línea de tiempo'),
        ('citas', 'Citas'),
        ('formulario', 'Formulario'),
    ]
    
    pagina = models.ForeignKey(Pagina, on_delete=models.CASCADE, related_name='secciones')
    titulo = models.CharField(max_length=200)
    subtitulo = models.CharField(max_length=300, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_SECCION, default='texto')
    contenido = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=0)
    fondo_oscuro = models.BooleanField(default=False)
    ancho_completo = models.BooleanField(default=False)
    padding_vertical = models.CharField(max_length=20, default='py-12')
    
    class Meta:
        ordering = ['pagina', 'orden']
        verbose_name = 'Sección de página'
        verbose_name_plural = 'Secciones de página'
    
    def __str__(self):
        return f"{self.pagina.titulo} - {self.titulo}"


# ============================================
# PRINCIPIOS Y VALORES
# ============================================


class Principio(models.Model):
    """Principios y valores masónicos"""
    titulo = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    descripcion_corta = models.CharField(max_length=200)
    descripcion_larga = models.TextField()
    
    simbolo = models.CharField(max_length=50, default='∴')
    simbolo_descripcion = models.CharField(max_length=100, blank=True)
    
    COLUMNA = [
        ('norte', 'Columna del Norte'),
        ('sur', 'Columna del Sur'),
        ('central', 'Central'),
    ]
    columna = models.CharField(max_length=20, choices=COLUMNA, default='norte')
    
    frase = models.CharField(max_length=200, blank=True)
    autor_frase = models.CharField(max_length=100, blank=True)
    
    orden = models.PositiveIntegerField(default=0)
    destacado = models.BooleanField(default=False)
    
    es_activo = models.BooleanField(default=True, verbose_name='Activo')
    
    imagen = models.ImageField(upload_to='principios/', blank=True, null=True)
    
    class Meta:
        ordering = ['columna', 'orden']
        verbose_name = 'Principio'
        verbose_name_plural = 'Principios'
    
    def __str__(self):
        return self.titulo

# ============================================
# HISTORIA Y LÍNEA DE TIEMPO
# ============================================

class EventoHistorico(models.Model):
    """Eventos en la línea de tiempo histórica"""
    titulo = models.CharField(max_length=200)
    fecha = models.DateField()
    fecha_texto = models.CharField(max_length=50, blank=True)
    descripcion = models.TextField()
    descripcion_corta = models.CharField(max_length=200, blank=True)
    
    imagen = models.ImageField(upload_to='historia/eventos/', blank=True, null=True)
    video_url = models.URLField(blank=True)
    
    orden = models.PositiveIntegerField(default=0)
    es_hito = models.BooleanField(default=False)
    
    CATEGORIA = [
        ('fundacion', 'Fundación'),
        ('expansion', 'Expansión'),
        ('renovacion', 'Renovación'),
        ('educacion', 'Educación'),
        ('social', 'Social'),
        ('otros', 'Otros'),
    ]
    categoria = models.CharField(max_length=20, choices=CATEGORIA, default='otros')
    
    protagonistas = models.ManyToManyField('Miembro', blank=True, related_name='eventos_historicos')
    
    class Meta:
        ordering = ['-fecha', 'orden']
        verbose_name = 'Evento histórico'
        verbose_name_plural = 'Eventos históricos'
    
    def __str__(self):
        return f"{self.fecha.year} - {self.titulo}"


class ImagenHistorica(models.Model):
    """Galería de imágenes históricas"""
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='historia/galeria/')
    fecha = models.DateField(null=True, blank=True)
    
    CATEGORIA = [
        ('fundacion', 'Fundación'),
        ('eventos', 'Eventos'),
        ('templo', 'Templo'),
        ('miembros', 'Miembros'),
        ('rituales', 'Rituales'),
        ('documentos', 'Documentos'),
    ]
    categoria = models.CharField(max_length=20, choices=CATEGORIA, default='eventos')
    
    evento_relacionado = models.ForeignKey(EventoHistorico, on_delete=models.SET_NULL, 
                                          null=True, blank=True, related_name='imagenes')
    
    destacado = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)
    
    subido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha', 'orden']
        verbose_name = 'Imagen histórica'
        verbose_name_plural = 'Imágenes históricas'
    
    def __str__(self):
        return self.titulo


class DocumentoHistorico(models.Model):
    """Documentos del archivo histórico"""
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to='historia/documentos/')
    fecha = models.DateField(null=True, blank=True)
    
    TIPO = [
        ('acta', 'Acta de fundación'),
        ('ritual', 'Ritual'),
        ('plancha', 'Plancha'),
        ('fotografia', 'Fotografía'),
        ('correspondencia', 'Correspondencia'),
        ('otros', 'Otros'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO, default='otros')
    
    evento_relacionado = models.ForeignKey(EventoHistorico, on_delete=models.SET_NULL, 
                                          null=True, blank=True)
    
    solo_miembros = models.BooleanField(default=True)
    descargable = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Documento histórico'
        verbose_name_plural = 'Documentos históricos'
    
    def __str__(self):
        return self.titulo


# ============================================
# MIEMBROS Y OFICIALES
# ============================================

class Grado(models.Model):
    """Grados masónicos"""
    nombre = models.CharField(max_length=100)
    numero = models.PositiveIntegerField(unique=True)
    descripcion = models.TextField(blank=True)
    simbolo = models.CharField(max_length=50, blank=True)
    orden = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['numero']
        verbose_name = 'Grado'
        verbose_name_plural = 'Grados'
    
    def __str__(self):
        return f"{self.numero}° - {self.nombre}"


class Cargo(models.Model):
    """Cargos oficiales dentro de la logia"""
    nombre = models.CharField(max_length=100)
    abreviatura = models.CharField(max_length=20, blank=True)
    descripcion = models.TextField(blank=True)
    
    JERARQUIA = [
        ('venerable', 'Venerable Maestro'),
        ('oficial', 'Oficial'),
        ('comision', 'Comisión'),
        ('honorario', 'Honorario'),
    ]
    jerarquia = models.CharField(max_length=20, choices=JERARQUIA, default='oficial')
    
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['jerarquia', 'orden']
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'
    
    def __str__(self):
        return self.nombre


class Miembro(models.Model):
    """Miembros de la logia"""
    nombre_completo = models.CharField(max_length=200)
    nombre_masonico = models.CharField(max_length=200, blank=True)
    
    ESTATUS = [
        ('activo', 'Activo'),
        ('pasivo', 'Pasivo'),
        ('honorario', 'Honorario'),
        ('ausente', 'Ausente'),
        ('retirado', 'Retirado'),
        ('fallecido', 'Fallecido'),
    ]
    estatus = models.CharField(max_length=20, choices=ESTATUS, default='activo')
    
    grado_actual = models.ForeignKey(Grado, on_delete=models.PROTECT, related_name='miembros')
    fecha_iniciacion = models.DateField(null=True, blank=True)
    fecha_ascenso = models.DateField(null=True, blank=True)
    
    cargo_actual = models.ForeignKey(Cargo, on_delete=models.SET_NULL, 
                                    null=True, blank=True, related_name='titulares')
    fecha_inicio_cargo = models.DateField(null=True, blank=True)
    fecha_fin_cargo = models.DateField(null=True, blank=True)
    
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    
    foto = models.ImageField(upload_to='miembros/', blank=True, null=True)
    firma = models.ImageField(upload_to='firmas/', blank=True, null=True)
    
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    fecha_ultima_tenida = models.DateField(null=True, blank=True)
    
    usuario = models.OneToOneField(User, on_delete=models.SET_NULL, 
                                  null=True, blank=True, related_name='miembro')
    es_publico = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)
    
    notas = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-estatus', 'orden', 'nombre_completo']
        verbose_name = 'Miembro'
        verbose_name_plural = 'Miembros'
    
    def __str__(self):
        return self.nombre_masonico or self.nombre_completo
    
    @property
    def antiguedad_anios(self):
        """Calcula la antigüedad en años del miembro"""
        if not self.fecha_ingreso:  
            return 0  
        
        hoy = timezone.now().date()
        return hoy.year - self.fecha_ingreso.year


# ============================================
# EDUCACIÓN Y CURSOS
# ============================================

class Curso(models.Model):
    """Cursos educativos"""
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    descripcion_corta = models.CharField(max_length=300)
    descripcion_larga = models.TextField()
    
    GRADO = [
        ('aprendiz', 'Aprendiz'),
        ('companero', 'Compañero'),
        ('maestro', 'Maestro'),
        ('todos', 'Todos los grados'),
    ]
    grado_destinatario = models.CharField(max_length=20, choices=GRADO, default='todos')
    
    instructor = models.ForeignKey(Miembro, on_delete=models.SET_NULL, 
                                  null=True, blank=True, related_name='cursos_impartidos')
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    
    lecciones = models.PositiveIntegerField(default=0)
    duracion_horas = models.PositiveIntegerField(default=0)
    
    url_moodle = models.URLField(blank=True)
    url_recurso = models.URLField(blank=True)
    
    imagen_portada = models.ImageField(upload_to='cursos/', blank=True, null=True)
    
    es_activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)
    
    cupo_maximo = models.PositiveIntegerField(default=0, blank=True)
    inscritos = models.ManyToManyField(Miembro, blank=True, related_name='cursos_inscritos')
    
    class Meta:
        ordering = ['-destacado', 'orden', 'titulo']
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
    
    def __str__(self):
        return self.titulo


class MaterialEducativo(models.Model):
    """Materiales de estudio"""
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    
    TIPO = [
        ('documento', 'Documento PDF'),
        ('video', 'Video'),
        ('presentacion', 'Presentación'),
        ('audio', 'Audio'),
        ('enlace', 'Enlace externo'),
        ('libro', 'Libro digital'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO, default='documento')
    
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, 
                             related_name='materiales', null=True, blank=True)
    
    archivo = models.FileField(upload_to='educacion/materiales/', blank=True)
    url_externa = models.URLField(blank=True)
    
    autor = models.CharField(max_length=200, blank=True)
    fecha_publicacion = models.DateField(null=True, blank=True)
    
    solo_miembros = models.BooleanField(default=True)
    descargable = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['curso', 'orden', 'titulo']
        verbose_name = 'Material educativo'
        verbose_name_plural = 'Materiales educativos'
    
    def __str__(self):
        return self.titulo


class BibliotecaDigital(models.Model):
    """Recursos de biblioteca"""
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    
    CATEGORIA = [
        ('clasico', 'Clásico masónico'),
        ('historia', 'Historia'),
        ('filosofia', 'Filosofía'),
        ('simbolismo', 'Simbolismo'),
        ('ritual', 'Ritual'),
        ('biografia', 'Biografía'),
    ]
    categoria = models.CharField(max_length=20, choices=CATEGORIA, default='clasico')
    
    año_publicacion = models.IntegerField(null=True, blank=True)
    editorial = models.CharField(max_length=200, blank=True)
    
    archivo_pdf = models.FileField(upload_to='biblioteca/', blank=True)
    url_externa = models.URLField(blank=True)
    
    portada = models.ImageField(upload_to='biblioteca/portadas/', blank=True, null=True)
    
    disponible = models.BooleanField(default=True)
    solo_miembros = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['categoria', 'titulo']
        verbose_name = 'Recurso biblioteca'
        verbose_name_plural = 'Biblioteca digital'
    
    def __str__(self):
        return f"{self.titulo} - {self.autor}"


# ============================================
# EVENTOS Y TENIDAS
# ============================================

class Evento(models.Model):
    """Eventos y tenidas"""
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    
    TIPO = [
        ('tenida_regular', 'Tenida Regular'),
        ('tenida_extraordinaria', 'Tenida Extraordinaria'),
        ('grado', 'Ceremonia de Grado'),
        ('conferencia', 'Conferencia'),
        ('taller', 'Taller'),
        ('social', 'Evento Social'),
        ('filantropico', 'Evento Filantrópico'),
    ]
    tipo = models.CharField(max_length=30, choices=TIPO, default='tenida_regular')
    
    descripcion = models.TextField()
    descripcion_corta = models.CharField(max_length=300, blank=True)
    
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    lugar = models.CharField(max_length=200)
    direccion = models.TextField(blank=True)
    
    organizador = models.ForeignKey(Miembro, on_delete=models.SET_NULL, 
                                   null=True, blank=True, related_name='eventos_organizados')
    
    cupo_maximo = models.PositiveIntegerField(default=0, blank=True)
    asistentes = models.ManyToManyField(Miembro, blank=True, related_name='eventos_asistidos')
    
    imagen = models.ImageField(upload_to='eventos/', blank=True, null=True)
    
    es_publico = models.BooleanField(default=False)
    es_activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    
    enviar_recordatorio = models.BooleanField(default=False)
    dias_recordatorio = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
    
    def __str__(self):
        return f"{self.fecha_inicio.strftime('%d/%m/%Y')} - {self.titulo}"
    
    @property
    def esta_proximo(self):
        hoy = timezone.now()
        return self.fecha_inicio > hoy


class Tenida(models.Model):
    """Tenidas regulares (semanal)"""
    dia_semana = models.PositiveIntegerField(choices=[
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'),
        (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo'),
    ], default=0)
    
    hora = models.TimeField(default='19:30')
    
    GRADO = [
        ('aprendiz', 'Aprendiz'),
        ('companero', 'Compañero'),
        ('maestro', 'Maestro'),
        ('todos', 'Todos los grados'),
    ]
    grado = models.CharField(max_length=20, choices=GRADO, default='todos')
    
    lugar = models.CharField(max_length=200, default='Templo Masónico "Renacimiento"')
    direccion = models.TextField(default='Calle 60 No. 487 x 57, Centro, Mérida, Yucatán')
    
    es_activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Configuración de tenida'
        verbose_name_plural = 'Configuración de tenidas'
    
    def __str__(self):
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        return f"Tenida {dias[self.dia_semana]} - {self.hora.strftime('%H:%M')}"
    
    @property
    def dia_semana_display(self):
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        return dias[self.dia_semana] if self.dia_semana < len(dias) else 'Desconocido'


# ============================================
# CONTACTO Y FORMULARIOS
# ============================================

class MedioContacto(models.Model):
    """Medios de contacto (dinámicos)"""
    TIPO = [
        ('email', 'Correo electrónico'),
        ('telefono', 'Teléfono'),
        ('whatsapp', 'WhatsApp'),
        ('direccion', 'Dirección física'),
        ('horario', 'Horario'),
        ('red_social', 'Red social'),
        ('otro', 'Otro'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPO)
    titulo = models.CharField(max_length=100)
    valor = models.CharField(max_length=500)
    icono = models.CharField(max_length=50, blank=True)
    
    orden = models.PositiveIntegerField(default=0)
    es_activo = models.BooleanField(default=True)
    es_principal = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-es_principal', 'orden']
        verbose_name = 'Medio de contacto'
        verbose_name_plural = 'Medios de contacto'
    
    def __str__(self):
        return f"{self.get_tipo_display()}: {self.titulo}"


class HorarioAtencion(models.Model):
    """Horarios de atención"""
    DIA = [
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'),
        (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo'),
    ]
    
    dia = models.PositiveIntegerField(choices=DIA)
    hora_apertura = models.TimeField()
    hora_cierre = models.TimeField()
    cerrado = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['dia']
        verbose_name = 'Horario de atención'
        verbose_name_plural = 'Horarios de atención'
    
    def __str__(self):
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        if self.cerrado:
            return f"{dias[self.dia]} - Cerrado"
        return f"{dias[self.dia]}: {self.hora_apertura.strftime('%H:%M')} - {self.hora_cierre.strftime('%H:%M')}"
    
    @property
    def dia_display(self):
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        return dias[self.dia] if self.dia < len(dias) else 'Desconocido'


class MensajeContacto(models.Model):
    """Mensajes recibidos del formulario"""
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    
    ASUNTO = [
        ('informacion', 'Solicitar información'),
        ('visita', 'Solicitar visita'),
        ('historia', 'Consulta histórica'),
        ('educacion', 'Información educativa'),
        ('otro', 'Otro asunto'),
    ]
    asunto = models.CharField(max_length=20, choices=ASUNTO, default='informacion')
    asunto_personalizado = models.CharField(max_length=200, blank=True)
    
    mensaje = models.TextField()
    
    fecha_envio = models.DateTimeField(auto_now_add=True)
    ip_origen = models.GenericIPAddressField(blank=True, null=True)
    
    leido = models.BooleanField(default=False)
    respondido = models.BooleanField(default=False)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    respuesta = models.TextField(blank=True)
    
    asignado_a = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                  null=True, blank=True, related_name='mensajes_asignados')
    
    class Meta:
        ordering = ['-fecha_envio']
        verbose_name = 'Mensaje de contacto'
        verbose_name_plural = 'Mensajes de contacto'
    
    def __str__(self):
        return f"{self.fecha_envio.strftime('%d/%m/%Y %H:%M')} - {self.nombre}"


# ============================================
# PUBLICACIONES Y BLOG
# ============================================

class CategoriaPublicacion(models.Model):
    """Categorías para publicaciones"""
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    descripcion = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
    
    def __str__(self):
        return self.nombre


class Publicacion(models.Model):
    """Publicaciones y noticias"""
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    subtitulo = models.CharField(max_length=300, blank=True)
    contenido = HTMLField()
    resumen = models.TextField(max_length=500, blank=True)
    
    imagen_destacada = models.ImageField(upload_to='publicaciones/', blank=True, null=True)
    video_url = models.URLField(blank=True)
    
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, 
                             null=True, blank=True, related_name='publicaciones')
    fecha_publicacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    categorias = models.ManyToManyField(CategoriaPublicacion, blank=True)
    etiquetas = models.CharField(max_length=200, blank=True)
    
    es_activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    importante = models.BooleanField(default=False)
    solo_miembros = models.BooleanField(default=False)
    
    visitas = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-fecha_publicacion']
        verbose_name = 'Publicación'
        verbose_name_plural = 'Publicaciones'
    
    def __str__(self):
        return self.titulo


# ============================================
# CONFIGURACIÓN VISUAL
# ============================================

class Carrusel(models.Model):
    """Slides para el carrusel principal"""
    titulo = models.CharField(max_length=200)
    subtitulo = models.CharField(max_length=300, blank=True)
    imagen = models.ImageField(upload_to='carrusel/')
    enlace = models.URLField(blank=True)
    texto_boton = models.CharField(max_length=50, default='Conocer más')
    
    orden = models.PositiveIntegerField(default=0)
    es_activo = models.BooleanField(default=True)
    
    POSICION = [
        ('left', 'Izquierda'),
        ('center', 'Centro'),
        ('right', 'Derecha'),
    ]
    posicion_texto = models.CharField(max_length=20, choices=POSICION, default='center')
    
    class Meta:
        ordering = ['orden']
        verbose_name = 'Slide de carrusel'
        verbose_name_plural = 'Carrusel'
    
    def __str__(self):
        return self.titulo


class Testimonial(models.Model):
    """Testimonios de miembros"""
    autor = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100, blank=True)
    contenido = models.TextField(max_length=500)
    foto = models.ImageField(upload_to='testimonios/', blank=True, null=True)
    
    fecha = models.DateField(default=timezone.now)
    orden = models.PositiveIntegerField(default=0)
    destacado = models.BooleanField(default=False)
    es_activo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-destacado', 'orden', '-fecha']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonios'
    
    def __str__(self):
        return f"Testimonio de {self.autor}"


# ============================================
# FRASES Y CITAS
# ============================================

class FraseCelebre(models.Model):
    """Citas y frases célebres masónicas"""
    contenido = models.TextField(max_length=500)
    autor = models.CharField(max_length=100)
    
    CATEGORIA = [
        ('masonica', 'Masónica'),
        ('filosofica', 'Filosófica'),
        ('historica', 'Histórica'),
        ('ritual', 'Ritual'),
    ]
    categoria = models.CharField(max_length=20, choices=CATEGORIA, default='masonica')
    
    activo = models.BooleanField(default=True)
    mostrada = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Frase célebre'
        verbose_name_plural = 'Frases célebres'
    
    def __str__(self):
        return f"{self.autor}: {self.contenido[:50]}..."
    
# ============================================
# ESTADÍSTICAS Y CONTADORES DINÁMICOS
# ============================================

class Estadistica(models.Model):
    """Estadísticas dinámicas para mostrar en el sitio"""
    titulo = models.CharField(max_length=100)
    valor = models.CharField(max_length=50, help_text='Puede ser número o texto (ej: "32", "15°", "4")')
    subtitulo = models.CharField(max_length=200, blank=True)
    icono = models.CharField(max_length=50, default='∴', help_text='Emoji o símbolo')
    
    CATEGORIA = [
        ('general', 'Generales'),
        ('miembros', 'Miembros'),
        ('educacion', 'Educación'),
        ('eventos', 'Eventos'),
        ('historia', 'Historia'),
        ('personalizado', 'Personalizado'),
    ]
    categoria = models.CharField(max_length=20, choices=CATEGORIA, default='general')
    
    # Para estadísticas calculadas automáticamente
    es_automatica = models.BooleanField(default=False, help_text='Si está activo, el valor se calcula automáticamente')
    tipo_automatico = models.CharField(
        max_length=50,
        choices=[
            ('total_miembros', 'Total de miembros activos'),
            ('total_cursos', 'Total de cursos activos'),
            ('total_eventos', 'Total de eventos próximos'),
            ('total_publicaciones', 'Total de publicaciones'),
            ('total_grados', 'Total de grados'),
            ('total_logia', 'Años de la logia'),
            ('total_tenidas', 'Tenidas en el año'),
            ('total_hermanos_nuevos', 'Hermanos nuevos este año'),
        ],
        blank=True
    )

    
    orden = models.PositiveIntegerField(default=0)
    es_activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['categoria', 'orden', 'titulo']
        verbose_name = 'Estadística'
        verbose_name_plural = 'Estadísticas'
    
    def __str__(self):
        return f"{self.titulo}: {self.valor}"
    
    def get_valor_calculado(self):
        """Calcula el valor automático si corresponde"""
        if not self.es_automatica:
            return self.valor
            
        from django.utils import timezone
        from .models import Miembro, Curso, Evento, Publicacion, Grado, Tenida, ConfiguracionSitio
        
        hoy = timezone.now()
        
        if self.tipo_automatico == 'total_miembros':
            return Miembro.objects.filter(estatus='activo').count()
        elif self.tipo_automatico == 'total_cursos':
            return Curso.objects.filter(es_activo=True).count()
        elif self.tipo_automatico == 'total_eventos':
            return Evento.objects.filter(es_activo=True, fecha_inicio__gte=hoy).count()
        elif self.tipo_automatico == 'total_publicaciones':
            return Publicacion.objects.filter(es_activo=True).count()
        elif self.tipo_automatico == 'total_grados':
            return Grado.objects.count()
        elif self.tipo_automatico == 'total_logia':
            config = ConfiguracionSitio.objects.first()
            if config:
                return hoy.year - config.ano_fundacion
            return 0
        elif self.tipo_automatico == 'total_tenidas':
            return Tenida.objects.filter(es_activo=True).count()
        elif self.tipo_automatico == 'total_hermanos_nuevos':
            return Miembro.objects.filter(estatus='activo', fecha_ingreso__year=hoy.year).count()
        
        return self.valor

# ============================================
# LOGIAS DEL MUNDO
# ============================================

class Logia(models.Model):
    """Logias masónicas alrededor del mundo"""
    
    CATEGORIA = [
        ('mundo', '🌍 Logias del Mundo'),
        ('mexico', '🇲🇽 Logias de México'),
        ('yucatan', '🌴 Logias de Yucatán'),
    ]
    
    nombre = models.CharField(max_length=200, verbose_name='Nombre de la Logia')
    ubicacion = models.CharField(max_length=200, verbose_name='Ubicación')
    fundacion = models.IntegerField(null=True, blank=True, verbose_name='Año de fundación')
    descripcion = models.TextField(max_length=300, verbose_name='Descripción')
    bandera = models.CharField(max_length=10, default='🏛️', verbose_name='Bandera/Emoji')
    categoria = models.CharField(max_length=20, choices=CATEGORIA, verbose_name='Categoría')
    
    # Orden y visibilidad
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden')
    es_activo = models.BooleanField(default=True, verbose_name='Activo')
    destacado = models.BooleanField(default=False, verbose_name='Destacado')
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['categoria', 'orden', 'nombre']
        verbose_name = 'Logia'
        verbose_name_plural = 'Logias'
    
    def __str__(self):
        return f"{self.nombre} - {self.get_categoria_display()}"
    
    @property
    def fundacion_display(self):
        """Muestra el año de fundación o 'Desconocido'"""
        return str(self.fundacion) if self.fundacion else '—'
    

# ============================================
# ACTIVIDADES HUMANÍSTICAS
# ============================================

class Actividad(models.Model):
    """Actividades humanísticas de la Logia Kukulkan"""
    titulo = models.CharField(max_length=200, verbose_name='Actividad')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    icono = models.CharField(max_length=50, default='→', verbose_name='Icono')
    
    # Orden y visibilidad
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden')
    es_activo = models.BooleanField(default=True, verbose_name='Activo')
    destacado = models.BooleanField(default=False, verbose_name='Destacado')
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['orden', 'titulo']
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'
    
    def __str__(self):
        return self.titulo