from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import *
from django.contrib.admin import AdminSite

# ============================================
# CONFIGURACIÓN GENERAL DEL ADMIN
# ============================================

admin.site.site_header = 'Administración Logia Kukulkan #41'
admin.site.site_title = 'Panel Masónico'
admin.site.index_title = 'Bienvenido, Venerable Maestro'

class SitioAdminSite(AdminSite):
    site_header = 'Administración Logia Kukulkan #41'
    site_title = 'Panel Masónico'
    index_title = 'Panel de Control Masónico'

# ============================================
# MIXINS Y CLASES BASE
# ============================================

class ActivoFilter(admin.SimpleListFilter):
    title = 'estado'
    parameter_name = 'activo'
    
    def lookups(self, request, model_admin):
        return (
            ('activo', 'Activo'),
            ('inactivo', 'Inactivo'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'activo':
            return queryset.filter(es_activo=True)
        if self.value() == 'inactivo':
            return queryset.filter(es_activo=False)
        return queryset

class OrdenableAdmin(admin.ModelAdmin):
    list_editable = ['orden']
    list_display = ['__str__', 'orden']


# ============================================
# CONFIGURACIÓN DEL SITIO
# ============================================

@admin.register(ConfiguracionSitio)
class ConfiguracionSitioAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Identidad', {
            'fields': ('nombre_sitio', 'lema_principal', 'logo_tipo', 'logo_texto')
        }),
        ('Colores institucionales', {
            'fields': ('color_primario', 'color_secundario'),
            'classes': ('wide',),
            'description': 'Colores en formato HEX (ej: #7b1e3a)'
        }),
        # ✅ NUEVA SECCIÓN PARA MOODLE
        ('Plataforma Educativa', {
            'fields': ('url_moodle', 'url_moodle_login', 'texto_boton_moodle'),
            'classes': ('wide',),
            'description': 'Configuración de la plataforma Moodle'
        }),
        ('SEO y Analytics', {
            'fields': ('meta_descripcion', 'meta_keywords', 'google_analytics_id'),
            'classes': ('collapse',),
        }),
        ('Redes sociales', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url', 'youtube_url'),
            'classes': ('collapse',),
        }),
        ('Pie de página', {
            'fields': ('copyright_text', 'ano_fundacion'),
        }),
    )
    
    def has_add_permission(self, request):
        return not ConfiguracionSitio.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

# ============================================
# NAVEGACIÓN
# ============================================

@admin.register(ItemMenu)
class ItemMenuAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'slug', 'tipo_enlace', 'orden', 'es_activo', 'solo_miembros']
    list_filter = ['tipo_enlace', 'es_activo', 'solo_miembros', 'padre']
    list_editable = ['orden', 'es_activo']
    search_fields = ['titulo', 'slug']
    prepopulated_fields = {'slug': ('titulo',)}
    
    fieldsets = (
        ('Información básica', {
            'fields': ('titulo', 'slug', 'padre', 'tipo_enlace', 'orden')
        }),
        ('Destino del enlace', {
            'fields': ('url_name', 'url_externa', 'pagina'),
            'description': 'Completa según el tipo de enlace seleccionado'
        }),
        ('Configuración', {
            'fields': ('icono', 'es_activo', 'solo_miembros')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('padre')


# ============================================
# PÁGINAS Y CONTENIDO
# ============================================

class SeccionPaginaInline(admin.TabularInline):
    model = SeccionPagina
    extra = 1
    fields = ['titulo', 'tipo', 'orden', 'contenido']
    classes = ['collapse']


@admin.register(Pagina)
class PaginaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'slug', 'fecha_publicacion', 'es_activo', 'destacado', 'solo_miembros']
    list_filter = ['es_activo', 'destacado', 'solo_miembros', 'autor']
    search_fields = ['titulo', 'contenido']
    prepopulated_fields = {'slug': ('titulo',)}
    inlines = [SeccionPaginaInline]
    
    fieldsets = (
        ('Contenido principal', {
            'fields': ('titulo', 'slug', 'subtitulo', 'contenido', 'contenido_resumido')
        }),
        ('Multimedia', {
            'fields': ('imagen_destacada', 'imagen_descripcion'),
            'classes': ('collapse',),
        }),
        ('SEO', {
            'fields': ('meta_titulo', 'meta_descripcion', 'palabras_clave'),
            'classes': ('collapse',),
        }),
        ('Configuración', {
            'fields': ('autor', 'fecha_publicacion', 'es_activo', 'destacado', 'orden')
        }),
        ('Visibilidad', {
            'fields': ('solo_miembros', 'requiere_autenticacion'),
            'classes': ('wide',),
        }),
        ('Plantilla', {
            'fields': ('plantilla',),
            'classes': ('collapse',),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.autor_id:
            obj.autor = request.user
        super().save_model(request, obj, form, change)


@admin.register(SeccionPagina)
class SeccionPaginaAdmin(admin.ModelAdmin):
    list_display = ['pagina', 'titulo', 'tipo', 'orden']
    list_filter = ['tipo', 'fondo_oscuro', 'pagina']
    search_fields = ['titulo', 'contenido']
    list_editable = ['orden']


# ============================================
# PRINCIPIOS
# ============================================

@admin.register(Principio)
class PrincipioAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'columna', 'orden', 'destacado']
    list_filter = ['columna', 'destacado']
    list_editable = ['orden', 'destacado']
    search_fields = ['titulo', 'descripcion_corta']
    prepopulated_fields = {'slug': ('titulo',)}
    
    fieldsets = (
        ('Información básica', {
            'fields': ('titulo', 'slug', 'columna', 'orden', 'destacado')
        }),
        ('Descripción', {
            'fields': ('descripcion_corta', 'descripcion_larga')
        }),
        ('Simbología', {
            'fields': ('simbolo', 'simbolo_descripcion', 'imagen')
        }),
        ('Frase asociada', {
            'fields': ('frase', 'autor_frase')
        }),
    )


# ============================================
# HISTORIA
# ============================================

class ImagenHistoricaInline(admin.TabularInline):
    model = ImagenHistorica
    extra = 1
    fields = ['titulo', 'imagen', 'fecha', 'destacado']
    classes = ['collapse']


@admin.register(EventoHistorico)
class EventoHistoricoAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'titulo', 'categoria', 'es_hito']
    list_filter = ['categoria', 'es_hito']
    search_fields = ['titulo', 'descripcion']
    date_hierarchy = 'fecha'
    inlines = [ImagenHistoricaInline]
    
    fieldsets = (
        ('Evento', {
            'fields': ('titulo', 'fecha', 'fecha_texto', 'categoria', 'es_hito')
        }),
        ('Descripción', {
            'fields': ('descripcion', 'descripcion_corta')
        }),
        ('Multimedia', {
            'fields': ('imagen', 'video_url')
        }),
        ('Protagonistas', {
            'fields': ('protagonistas',)
        }),
    )
    
    filter_horizontal = ['protagonistas']


@admin.register(ImagenHistorica)
class ImagenHistoricaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'fecha', 'destacado', 'imagen_preview']
    list_filter = ['categoria', 'destacado', 'evento_relacionado']
    search_fields = ['titulo', 'descripcion']
    list_editable = ['destacado']
    
    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', 
                             obj.imagen.url)
        return 'Sin imagen'
    imagen_preview.short_description = 'Vista previa'


@admin.register(DocumentoHistorico)
class DocumentoHistoricoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'fecha', 'solo_miembros', 'descargable']
    list_filter = ['tipo', 'solo_miembros', 'evento_relacionado']
    search_fields = ['titulo', 'descripcion']


# ============================================
# MIEMBROS
# ============================================

@admin.register(Grado)
class GradoAdmin(OrdenableAdmin):
    list_display = ['numero', 'nombre', 'simbolo', 'orden']
    list_editable = ['orden']


@admin.register(Cargo)
class CargoAdmin(OrdenableAdmin):
    list_display = ['nombre', 'abreviatura', 'jerarquia', 'activo', 'orden']
    list_filter = ['jerarquia', 'activo']
    list_editable = ['activo', 'orden']


@admin.register(Miembro)
class MiembroAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'nombre_masonico', 'grado_actual', 'cargo_actual', 
                   'estatus', 'antiguedad', 'foto_preview']
    list_filter = ['estatus', 'grado_actual', 'cargo_actual', 'es_publico']
    search_fields = ['nombre_completo', 'nombre_masonico', 'email']
    date_hierarchy = 'fecha_ingreso'
    
    fieldsets = (
        ('Información personal', {
            'fields': ('nombre_completo', 'nombre_masonico', 'fecha_nacimiento', 'estatus')
        }),
        ('Información masónica', {
            'fields': ('grado_actual', 'fecha_iniciacion', 'fecha_ascenso')
        }),
        ('Cargo actual', {
            'fields': ('cargo_actual', 'fecha_inicio_cargo', 'fecha_fin_cargo')
        }),
        ('Contacto', {
            'fields': ('email', 'telefono', 'direccion'),
            'classes': ('collapse',),
        }),
        ('Multimedia', {
            'fields': ('foto', 'firma'),
        }),
        ('Configuración', {
            'fields': ('es_publico', 'usuario', 'notas')
        }),
    )
    
    def foto_preview(self, obj):
        if obj.foto:
            return format_html('<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />', 
                             obj.foto.url)
        return '—'
    foto_preview.short_description = 'Foto'
    
    def antiguedad(self, obj):
        return f"{obj.antiguedad_anios} años"
    antiguedad.short_description = 'Antigüedad'


# ============================================
# EDUCACIÓN
# ============================================

class MaterialEducativoInline(admin.TabularInline):
    model = MaterialEducativo
    extra = 1
    fields = ['titulo', 'tipo', 'orden']
    classes = ['collapse']


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'grado_destinatario', 'instructor', 'fecha_inicio', 
                   'lecciones', 'destacado', 'es_activo']
    list_filter = ['grado_destinatario', 'destacado', 'es_activo']
    search_fields = ['titulo', 'descripcion_corta']
    prepopulated_fields = {'slug': ('titulo',)}
    inlines = [MaterialEducativoInline]
    filter_horizontal = ['inscritos']
    
    fieldsets = (
        ('Información del curso', {
            'fields': ('titulo', 'slug', 'grado_destinatario', 'instructor')
        }),
        ('Descripción', {
            'fields': ('descripcion_corta', 'descripcion_larga')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Contenido', {
            'fields': ('lecciones', 'duracion_horas')
        }),
        ('Recursos', {
            'fields': ('url_moodle', 'url_recurso', 'imagen_portada')
        }),
        ('Configuración', {
            'fields': ('cupo_maximo', 'es_activo', 'destacado', 'orden')
        }),
        ('Inscritos', {
            'fields': ('inscritos',),
            'classes': ('collapse',),
        }),
    )


@admin.register(MaterialEducativo)
class MaterialEducativoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'curso', 'tipo', 'solo_miembros', 'descargable']
    list_filter = ['tipo', 'solo_miembros', 'curso']
    search_fields = ['titulo', 'descripcion']


@admin.register(BibliotecaDigital)
class BibliotecaDigitalAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'categoria', 'año_publicacion', 'disponible']
    list_filter = ['categoria', 'disponible', 'solo_miembros']
    search_fields = ['titulo', 'autor', 'descripcion']


# ============================================
# EVENTOS
# ============================================

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['fecha_inicio', 'titulo', 'tipo', 'lugar', 'es_activo', 'destacado']
    list_filter = ['tipo', 'es_activo', 'destacado', 'es_publico']
    search_fields = ['titulo', 'descripcion']
    date_hierarchy = 'fecha_inicio'
    prepopulated_fields = {'slug': ('titulo',)}
    filter_horizontal = ['asistentes']
    
    fieldsets = (
        ('Información del evento', {
            'fields': ('titulo', 'slug', 'tipo', 'organizador')
        }),
        ('Descripción', {
            'fields': ('descripcion', 'descripcion_corta')
        }),
        ('Fecha y lugar', {
            'fields': ('fecha_inicio', 'fecha_fin', 'lugar', 'direccion')
        }),
        ('Capacidad', {
            'fields': ('cupo_maximo', 'asistentes')
        }),
        ('Configuración', {
            'fields': ('imagen', 'es_publico', 'es_activo', 'destacado')
        }),
        ('Recordatorios', {
            'fields': ('enviar_recordatorio', 'dias_recordatorio'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Tenida)
class TenidaAdmin(admin.ModelAdmin):
    list_display = ['dia_semana_display', 'hora', 'grado', 'lugar', 'es_activo']
    list_editable = ['es_activo']
    
    def dia_semana_display(self, obj):
        return obj.dia_semana_display
    dia_semana_display.short_description = 'Día'
    dia_semana_display.admin_order_field = 'dia_semana'
    
    def has_add_permission(self, request):
        return not Tenida.objects.exists()


# ============================================
# CONTACTO
# ============================================

@admin.register(MedioContacto)
class MedioContactoAdmin(OrdenableAdmin):
    list_display = ['titulo', 'tipo', 'valor', 'es_principal', 'es_activo', 'orden']
    list_filter = ['tipo', 'es_activo', 'es_principal']
    list_editable = ['es_activo', 'es_principal']


@admin.register(HorarioAtencion)
class HorarioAtencionAdmin(admin.ModelAdmin):
    list_display = ['get_dia_display', 'hora_apertura', 'hora_cierre', 'cerrado']
    list_editable = ['hora_apertura', 'hora_cierre', 'cerrado']
    ordering = ['dia']


@admin.register(MensajeContacto)
class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ['fecha_envio', 'nombre', 'email', 'asunto', 'leido', 'respondido', 'asignado_a']
    list_filter = ['asunto', 'leido', 'respondido', 'fecha_envio']
    search_fields = ['nombre', 'email', 'mensaje']
    date_hierarchy = 'fecha_envio'
    readonly_fields = ['fecha_envio', 'ip_origen']
    
    fieldsets = (
        ('Mensaje recibido', {
            'fields': ('nombre', 'email', 'asunto', 'asunto_personalizado', 'mensaje')
        }),
        ('Metadatos', {
            'fields': ('fecha_envio', 'ip_origen'),
            'classes': ('collapse',),
        }),
        ('Respuesta', {
            'fields': ('leido', 'respondido', 'fecha_respuesta', 'respuesta', 'asignado_a')
        }),
    )
    
    actions = ['marcar_como_leido', 'marcar_como_respondido']
    
    def marcar_como_leido(self, request, queryset):
        queryset.update(leido=True)
    marcar_como_leido.short_description = 'Marcar como leído'
    
    def marcar_como_respondido(self, request, queryset):
        from django.utils import timezone
        queryset.update(respondido=True, fecha_respuesta=timezone.now())
    marcar_como_respondido.short_description = 'Marcar como respondido'


# ============================================
# PUBLICACIONES
# ============================================

@admin.register(CategoriaPublicacion)
class CategoriaPublicacionAdmin(OrdenableAdmin):
    list_display = ['nombre', 'slug', 'orden']
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'fecha_publicacion', 'autor', 'destacado', 'importante', 
                   'es_activo', 'visitas']
    list_filter = ['destacado', 'importante', 'es_activo', 'solo_miembros', 'categorias']
    search_fields = ['titulo', 'contenido']
    date_hierarchy = 'fecha_publicacion'
    prepopulated_fields = {'slug': ('titulo',)}
    filter_horizontal = ['categorias']
    readonly_fields = ['visitas']
    
    fieldsets = (
        ('Contenido', {
            'fields': ('titulo', 'slug', 'subtitulo', 'contenido', 'resumen')
        }),
        ('Multimedia', {
            'fields': ('imagen_destacada', 'video_url')
        }),
        ('Clasificación', {
            'fields': ('categorias', 'etiquetas')
        }),
        ('Autoría', {
            'fields': ('autor', 'fecha_publicacion')
        }),
        ('Configuración', {
            'fields': ('es_activo', 'destacado', 'importante', 'solo_miembros')
        }),
        ('Estadísticas', {
            'fields': ('visitas',),
            'classes': ('collapse',),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.autor_id:
            obj.autor = request.user
        super().save_model(request, obj, form, change)


# ============================================
# COMPONENTES VISUALES
# ============================================

@admin.register(Carrusel)
class CarruselAdmin(OrdenableAdmin):
    list_display = ['titulo', 'orden', 'es_activo', 'imagen_preview']
    list_filter = ['es_activo', 'posicion_texto']
    list_editable = ['orden', 'es_activo']
    
    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="width: 80px; height: 40px; object-fit: cover; border-radius: 4px;" />', 
                             obj.imagen.url)
        return 'Sin imagen'
    imagen_preview.short_description = 'Vista previa'


@admin.register(Testimonial)
class TestimonialAdmin(OrdenableAdmin):
    list_display = ['autor', 'cargo', 'fecha', 'destacado', 'es_activo']
    list_filter = ['destacado', 'es_activo']
    list_editable = ['destacado', 'es_activo']


@admin.register(FraseCelebre)
class FraseCelebreAdmin(admin.ModelAdmin):
    list_display = ['contenido_corto', 'autor', 'categoria', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['contenido', 'autor']
    
    def contenido_corto(self, obj):
        return obj.contenido[:75] + '...' if len(obj.contenido) > 75 else obj.contenido
    contenido_corto.short_description = 'Frase'


# ============================================
# DASHBOARD PERSONALIZADO
# ============================================

class LogiaAdminSite(admin.AdminSite):
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        
        # Reordenar apps según importancia
        order = {
            'configuracion': 1,
            'navegacion': 2,
            'paginas': 3,
            'principios': 4,
            'historia': 5,
            'miembros': 6,
            'educacion': 7,
            'eventos': 8,
            'contacto': 9,
            'publicaciones': 10,
            'visual': 11,
        }
        
        for app in app_list:
            app['models'].sort(key=lambda x: order.get(x['object_name'].lower(), 999))
        
        return app_list


# Personalizar el admin existente
admin.site.site_header = 'Administración Logia Kukulkan #41'
admin.site.site_title = 'Panel Masónico'
admin.site.index_title = '∴ Panel de Control del Venerable Maestro ∴'
admin.site.site_url = '/'

# Añadir enlaces rápidos en el dashboard
admin.site.index_template = 'admin/dashboard.html'

# Registrar todos los modelos
@admin.register(Estadistica)
class EstadisticaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'valor_display', 'categoria', 'orden', 'es_activo', 'destacado']
    list_filter = ['categoria', 'es_activo', 'destacado', 'es_automatica']
    list_editable = ['orden', 'es_activo', 'destacado']
    search_fields = ['titulo', 'subtitulo']
    fieldsets = (
        ('Información básica', {
            'fields': ('titulo', 'valor', 'subtitulo', 'icono', 'categoria')
        }),
        ('Valor automático', {
            'fields': ('es_automatica', 'tipo_automatico'),
            'description': 'Si activas "es_automática", el valor se calculará solo y se ignorará el campo "valor"'
        }),
        ('Configuración', {
            'fields': ('orden', 'es_activo', 'destacado')
        }),
    )
    
    def valor_display(self, obj):
        if obj.es_automatica:
            return f"🔄 {obj.get_valor_calculado()} (automático)"
        return obj.valor
    valor_display.short_description = 'Valor'


@admin.register(Logia)
class LogiaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ubicacion', 'categoria', 'fundacion', 'bandera', 'orden', 'es_activo']
    list_filter = ['categoria', 'es_activo', 'destacado']
    list_editable = ['orden', 'es_activo']
    search_fields = ['nombre', 'ubicacion', 'descripcion']
    
    fieldsets = (
        ('Información básica', {
            'fields': ('nombre', 'ubicacion', 'categoria', 'bandera')
        }),
        ('Detalles', {
            'fields': ('fundacion', 'descripcion')
        }),
        ('Configuración', {
            'fields': ('orden', 'es_activo', 'destacado'),
            'classes': ('wide',),
        }),
    )

@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'orden', 'es_activo', 'destacado']
    list_editable = ['orden', 'es_activo', 'destacado']
    list_filter = ['es_activo', 'destacado']
    search_fields = ['titulo', 'descripcion']