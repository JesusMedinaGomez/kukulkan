# apps/pages/context_processors.py
from .models import (
    ConfiguracionSitio, ItemMenu, Tenida, 
    FraseCelebre, MedioContacto, HorarioAtencion,
    Estadistica, Miembro, Curso, Evento, 
    Publicacion, MaterialEducativo, BibliotecaDigital,
    EventoHistorico, Grado, Logia, Principio, Actividad
)
from django.utils import timezone
from django.db.models import Count, Sum

def sitio_context(request):
    
    # ============================================
    # CONFIGURACIÓN GENERAL
    # ============================================
    config = ConfiguracionSitio.objects.first()
    
    # ============================================
    # NAVEGACIÓN
    # ============================================
    nav_items = ItemMenu.objects.filter(
        es_activo=True, 
        padre__isnull=True
    ).prefetch_related('subitems').order_by('orden')
    
    # ============================================
    # ESTADÍSTICAS GENERALES 
    # ============================================
    
    # Miembros
    total_miembros_activos = Miembro.objects.filter(estatus='activo').count() or 0
    total_miembros_pasivos = Miembro.objects.filter(estatus='pasivo').count() or 0
    total_miembros_honorarios = Miembro.objects.filter(estatus='honorario').count() or 0
    total_miembros = Miembro.objects.count() or 0
    
    # Miembros nuevos este año
    total_miembros_nuevos = Miembro.objects.filter(
        fecha_ingreso__year=timezone.now().year
    ).count() or 0
    
    # Cursos
    total_cursos_activos = Curso.objects.filter(es_activo=True).count() or 0
    total_cursos_destacados = Curso.objects.filter(es_activo=True, destacado=True).count() or 0
    
    # Materiales educativos
    total_materiales = MaterialEducativo.objects.count() or 0
    total_materiales_publicos = MaterialEducativo.objects.filter(solo_miembros=False).count() or 0
    
    # Biblioteca
    total_biblioteca = BibliotecaDigital.objects.filter(disponible=True).count() or 0
    total_biblioteca_miembros = BibliotecaDigital.objects.filter(solo_miembros=True).count() or 0
    
    # Eventos
    total_eventos_proximos = Evento.objects.filter(
        es_activo=True,
        fecha_inicio__gte=timezone.now()
    ).count() or 0
    total_eventos_pasados = Evento.objects.filter(
        es_activo=True,
        fecha_inicio__lt=timezone.now()
    ).count() or 0
    total_eventos = Evento.objects.filter(es_activo=True).count() or 0
    
    # Publicaciones
    total_publicaciones = Publicacion.objects.filter(es_activo=True).count() or 0
    total_publicaciones_destacadas = Publicacion.objects.filter(es_activo=True, destacado=True).count() or 0
    
    # Grados
    total_grados = Grado.objects.count() or 3
    
    # Historia
    total_eventos_historicos = EventoHistorico.objects.count() or 0
    total_eventos_hito = EventoHistorico.objects.filter(es_hito=True).count() or 0
    
    # ============================================
    # ESTADÍSTICAS DE EDUCACIÓN
    # ============================================
    
    # Horas de formación (suma de duración de cursos)
    total_horas_formacion = Curso.objects.filter(es_activo=True).aggregate(
        total=Sum('duracion_horas')
    )['total'] or 0
    
    # Total de instructores únicos
    total_instructores = Curso.objects.filter(
        es_activo=True, 
        instructor__isnull=False
    ).values('instructor').distinct().count() or 0
    
    # Cursos por grado
    cursos_aprendiz = Curso.objects.filter(es_activo=True, grado_destinatario='aprendiz').count() or 0
    cursos_companero = Curso.objects.filter(es_activo=True, grado_destinatario='companero').count() or 0
    cursos_maestro = Curso.objects.filter(es_activo=True, grado_destinatario='maestro').count() or 0
    cursos_todos = Curso.objects.filter(es_activo=True, grado_destinatario='todos').count() or 0
    
    # ============================================
    # DATOS DE LA LOGIA 
    # ============================================
    
    # Calcular grado promedio
    grados = list(Miembro.objects.filter(estatus='activo').values_list('grado_actual__numero', flat=True))
    grado_promedio = round(sum(grados) / len(grados)) if grados else 0
    
    # Años de la logia
    ano_fundacion = config.ano_fundacion if config else 1980
    anos_logia = timezone.now().year - ano_fundacion
    
    # Talleres (cursos activos)
    total_talleres = Curso.objects.filter(es_activo=True).count() or 0
    
    # ENIDA 
    tenida = Tenida.objects.first()
    
    if tenida and tenida.es_activo:
        meeting_day = f"Todos los {tenida.dia_semana_display}s"
        meeting_time = tenida.hora.strftime('%H:%M hrs')
        temple = tenida.lugar
        address = tenida.direccion
        meeting_grado = tenida.get_grado_display()
    else:
        meeting_day = "Todos los lunes"
        meeting_time = "19:30 hrs"
        temple = 'Templo Masónico "Renacimiento"'
        address = 'Calle 60 No. 487 x 57, Centro, Mérida, Yucatán'
        meeting_grado = "Todos los grados"
    
    #ACTIVIDADES 
    actividades = Actividad.objects.filter(
        es_activo=True
    ).order_by('orden')
    
    #KUKULKAN LODGE 
    kukulkan_lodge = {
        'full_name': f'R∴ L∴ Simbólica {config.nombre_sitio if config else "Kukulkan No. 41"}',
        'founded': ano_fundacion,
        'members': total_miembros_activos,
        'avg_degree': f'{grado_promedio}°' if grado_promedio > 0 else '0°',
        'workshops': total_talleres,
        'years': anos_logia,
        'meeting_day': meeting_day,
        'meeting_time': meeting_time,
        'temple': temple,
        'address': address,
        'meeting_grado': meeting_grado,
        'activities': actividades,
    }
    
    # ============================================
    # LOGIAS DINÁMICAS
    # ============================================
    
    # Logias del Mundo
    world_lodges = Logia.objects.filter(
        es_activo=True,
        categoria='mundo'
    ).order_by('orden', 'nombre')
    
    # Logias de México
    mexico_lodges = Logia.objects.filter(
        es_activo=True,
        categoria='mexico'
    ).order_by('orden', 'nombre')
    
    # Logias de Yucatán
    yucatan_lodges = Logia.objects.filter(
        es_activo=True,
        categoria='yucatan'
    ).order_by('orden', 'nombre')
    
    # ============================================
    # ESTADÍSTICAS DESTACADAS (para home)
    # ============================================
    estadisticas_destacadas = Estadistica.objects.filter(
        es_activo=True, 
        destacado=True
    ).order_by('orden')
    
    if not estadisticas_destacadas.exists():
        estadisticas_destacadas = [
            {'titulo': 'Directorio', 'valor': total_miembros_activos, 'icono': '∴'},
            {'titulo': 'Educación', 'valor': total_cursos_activos, 'icono': '📚'},
            {'titulo': 'Calendario', 'valor': total_eventos_proximos, 'icono': '📅'},
            {'titulo': 'Historia', 'valor': anos_logia, 'icono': '📜'},
        ]
    
    # ============================================
    # ESTADÍSTICAS DE EDUCACIÓN 
    # ============================================
    estadisticas_educacion = Estadistica.objects.filter(
        es_activo=True,
        categoria__in=['educacion', 'miembros', 'general']
    ).order_by('orden')
    
    # ============================================
    # CONTENIDO 
    # ============================================
    
    # Cursos por grado (querysets)
    apprentice_courses = Curso.objects.filter(
        es_activo=True, 
        grado_destinatario='aprendiz'
    ).order_by('orden')
    
    fellow_courses = Curso.objects.filter(
        es_activo=True, 
        grado_destinatario='companero'
    ).order_by('orden')
    
    master_courses = Curso.objects.filter(
        es_activo=True, 
        grado_destinatario='maestro'
    ).order_by('orden')
    
    all_levels_courses = Curso.objects.filter(
        es_activo=True, 
        grado_destinatario='todos'
    ).order_by('orden')
    
    # Materiales recientes
    recent_materials = MaterialEducativo.objects.all().order_by('-id')[:6]
    
    # Biblioteca destacada
    featured_library = BibliotecaDigital.objects.filter(
        disponible=True
    ).order_by('?')[:8]
    
    # Próximos eventos
    upcoming_events = Evento.objects.filter(
        es_activo=True,
        fecha_inicio__gte=timezone.now()
    ).order_by('fecha_inicio')[:6]
    
    # Últimas publicaciones
    latest_publications = Publicacion.objects.filter(
        es_activo=True
    ).order_by('-fecha_publicacion')[:3]
    
    # ============================================
    # CONTACTO
    # ============================================
    contact_media = MedioContacto.objects.filter(
        es_activo=True
    ).order_by('-es_principal', 'orden')
    
    schedules = HorarioAtencion.objects.all().order_by('dia')
    regular_meeting = Tenida.objects.first()
    
    # ============================================
    # MOODLE
    # ============================================
    moodle_url = config.url_moodle if config and config.url_moodle else 'https://moodle.kukulkan41.org'
    moodle_login_url = config.url_moodle_login if config and config.url_moodle_login else 'https://moodle.kukulkan41.org/login'
    moodle_button_text = config.texto_boton_moodle if config and config.texto_boton_moodle else 'Ir a Moodle'
    
    # ============================================
    # PRINCIPIOS
    # ============================================
    north_principles = Principio.objects.filter(columna='norte', es_activo=True).order_by('orden')
    south_principles = Principio.objects.filter(columna='sur', es_activo=True).order_by('orden')
    central_principles = Principio.objects.filter(columna='central', es_activo=True).order_by('orden')
    
    # ============================================
    # CONTEXTO  
    # ============================================
    context = {
        # Configuración
        'configuracion': config,
        'nav_items': nav_items,
        'ano_actual': timezone.now().year,
        
        # Moodle
        'moodle_url': moodle_url,
        'moodle_login_url': moodle_login_url,
        'moodle_button_text': moodle_button_text,
        
        # Tenida
        'tenida_info': regular_meeting,
        'regular_meeting': regular_meeting,
        
        # Frases
        'frase_del_dia': FraseCelebre.objects.filter(activo=True).order_by('?').first(),
        
        # Contacto
        'medios_contacto': contact_media,
        'contact_media': contact_media,
        'schedules': schedules,
        
        # ========================================
        # ESTADÍSTICAS GENERALES 
        # ========================================
        'total_miembros': total_miembros,
        'total_miembros_activos': total_miembros_activos,
        'total_miembros_pasivos': total_miembros_pasivos,
        'total_miembros_honorarios': total_miembros_honorarios,
        'total_miembros_nuevos': total_miembros_nuevos,
        
        'total_cursos_activos': total_cursos_activos,
        'total_cursos_destacados': total_cursos_destacados,
        'cursos_activos_count': total_cursos_activos,
        
        'total_materiales': total_materiales,
        'materiales_count': total_materiales,
        'total_materiales_publicos': total_materiales_publicos,
        
        'total_biblioteca': total_biblioteca,
        'biblioteca_count': total_biblioteca,
        'total_biblioteca_miembros': total_biblioteca_miembros,
        
        'total_eventos_proximos': total_eventos_proximos,
        'total_eventos_pasados': total_eventos_pasados,
        'total_eventos': total_eventos,
        
        'total_publicaciones': total_publicaciones,
        'total_publicaciones_destacadas': total_publicaciones_destacadas,
        
        'total_grados': total_grados,
        
        'total_eventos_historicos': total_eventos_historicos,
        'total_eventos_hito': total_eventos_hito,
        
        # ========================================
        # ESTADÍSTICAS DE EDUCACIÓN
        # ========================================
        'total_horas_formacion': total_horas_formacion,
        'total_instructores': total_instructores,
        'cursos_aprendiz': cursos_aprendiz,
        'cursos_companero': cursos_companero,
        'cursos_maestro': cursos_maestro,
        'cursos_todos': cursos_todos,
        
        # ========================================
        # ESTADÍSTICAS DESTACADAS
        # ========================================
        'estadisticas_destacadas': estadisticas_destacadas,
        'estadisticas_generales': Estadistica.objects.filter(es_activo=True, categoria='general').order_by('orden'),
        'estadisticas_educacion': estadisticas_educacion,
        'estadisticas_kukulkan': Estadistica.objects.filter(es_activo=True, categoria__in=['miembros', 'historia']).order_by('orden')[:4],
        
        # ========================================
        # KUKULKAN LODGE
        # ========================================
        'kukulkan_lodge': kukulkan_lodge,
        
        # ========================================
        # LOGIAS 
        # ========================================
        'world_lodges': world_lodges,
        'mexico_lodges': mexico_lodges,
        'yucatan_lodges': yucatan_lodges,
        
        # ========================================
        # ACTIVIDADES DINÁMICAS
        # ========================================
        'actividades': actividades,
        
        # ========================================
        # QUERYSETS DINÁMICOS
        # ========================================
        'apprentice_courses': apprentice_courses,
        'fellow_courses': fellow_courses,
        'master_courses': master_courses,
        'all_levels_courses': all_levels_courses,
        'recent_materials': recent_materials,
        'featured_library': featured_library,
        'upcoming_events': upcoming_events,
        'latest_publications': latest_publications,
        
        # ========================================
        # PRINCIPIOS 
        # ========================================
        'north_principles': north_principles,
        'south_principles': south_principles,
        'central_principles': central_principles,
        
        # ========================================
        # VARIABLES ADICIONALES 
        # ========================================
        'antiguedad_logia': anos_logia,
        'grado_promedio': grado_promedio,
    }
    
    return context