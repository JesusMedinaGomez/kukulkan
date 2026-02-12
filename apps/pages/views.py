from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q, Count, Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.conf import settings
import json
from django.db.models import Sum
from django.views.generic import ListView, DetailView, TemplateView, UpdateView
from .models import *
from .forms import ContactoForm


# ============================================
# VISTAS DE PÁGINAS ESTÁTICAS DINÁMICAS
# ============================================

class PaginaView(DetailView):
    """Vista genérica para páginas estáticas desde la DB"""
    model = Pagina
    template_name = 'page.html'
    context_object_name = 'page'
    slug_field = 'slug'
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(es_activo=True)
        
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(solo_miembros=False)
        
        return queryset.prefetch_related('secciones')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pagina = self.get_object()
        
        context['sections'] = pagina.secciones.all().order_by('orden')
        context['meta_title'] = pagina.get_meta_titulo
        context['meta_description'] = pagina.meta_descripcion or pagina.contenido_resumido[:160]
        
        return context


# ============================================
# VISTAS DE INICIO
# ============================================

class HomeView(TemplateView):
    """Vista principal - Home (home.html)"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['carousel'] = Carrusel.objects.filter(es_activo=True).order_by('orden')
        context['featured_principles'] = Principio.objects.filter(
            destacado=True
        ).order_by('columna', 'orden')[:6]
        
        publicaciones = Publicacion.objects.filter(es_activo=True)
        if not self.request.user.is_authenticated:
            publicaciones = publicaciones.filter(solo_miembros=False)
        context['latest_publications'] = publicaciones.order_by('-fecha_publicacion')[:3]
        
        context['upcoming_events'] = Evento.objects.filter(
            es_activo=True,
            fecha_inicio__gte=timezone.now()
        ).order_by('fecha_inicio')[:4]
        
        context['historical_milestones'] = EventoHistorico.objects.filter(
            es_hito=True
        ).order_by('-fecha')[:6]
        
        context['featured_courses'] = Curso.objects.filter(
            es_activo=True,
            destacado=True
        ).order_by('orden')[:4]
        
        context['testimonials'] = Testimonial.objects.filter(
            es_activo=True,
            destacado=True
        ).order_by('-fecha')[:3]
        
        return context


# ============================================
# VISTAS DE HISTORIA
# ============================================

class HistoryView(TemplateView):
    """Vista de línea de tiempo histórica (history.html)"""
    template_name = 'history.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            history_page = Pagina.objects.get(slug='historia', es_activo=True)
            context['history_page'] = history_page
        except Pagina.DoesNotExist:
            context['history_page'] = None
        
        events = EventoHistorico.objects.all().order_by('-fecha')
        
        events_by_decade = {}
        for event in events:
            decade = (event.fecha.year // 10) * 10
            if decade not in events_by_decade:
                events_by_decade[decade] = []
            events_by_decade[decade].append(event)
        
        context['events_by_decade'] = dict(sorted(events_by_decade.items(), reverse=True))
        context['featured_images'] = ImagenHistorica.objects.filter(
            destacado=True
        ).order_by('-fecha')[:12]
        
        context['public_documents'] = DocumentoHistorico.objects.filter(
            solo_miembros=False
        ).order_by('-fecha')[:6]
        
        return context


class HistoricalEventDetailView(DetailView):
    """Detalle de un evento histórico específico"""
    model = EventoHistorico
    template_name = 'historical_event_detail.html'
    context_object_name = 'event'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        
        context['images'] = event.imagenes.all().order_by('orden')
        context['documents'] = DocumentoHistorico.objects.filter(
            evento_relacionado=event
        )
        context['protagonists'] = event.protagonistas.filter(estatus='activo')
        
        return context


# ============================================
# VISTAS DE PRINCIPIOS
# ============================================

class PrinciplesView(TemplateView):
    """Vista de principios y valores (principles.html)"""
    template_name = 'principles.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            principles_page = Pagina.objects.get(slug='principios', es_activo=True)
            context['principles_page'] = principles_page
        except Pagina.DoesNotExist:
            context['principles_page'] = None
        
        context['north_principles'] = Principio.objects.filter(
            columna='norte'
        ).order_by('orden')
        
        context['south_principles'] = Principio.objects.filter(
            columna='sur'
        ).order_by('orden')
        
        context['central_principles'] = Principio.objects.filter(
            columna='central'
        ).order_by('orden')
        
        context['featured_phrase'] = FraseCelebre.objects.filter(
            activo=True, categoria='masonica'
        ).order_by('?').first()
        
        return context


# ============================================
# VISTAS DE MASONERÍA (PANORAMA GENERAL)
# ============================================
class FreemasonryView(TemplateView):
    """Vista de panorama general de la masonería (freemasonry.html)"""
    template_name = 'freemasonry.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            freemasonry_page = Pagina.objects.get(slug='masoneria', es_activo=True)
            context['freemasonry_page'] = freemasonry_page
        except Pagina.DoesNotExist:
            context['freemasonry_page'] = None
        
        return context

# ============================================
# VISTAS DE EDUCACIÓN
# ============================================
class EducationView(TemplateView):
    """Vista principal de educación (education.html)"""
    template_name = 'education.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            education_page = Pagina.objects.get(slug='educacion', es_activo=True)
            context['education_page'] = education_page
        except Pagina.DoesNotExist:
            context['education_page'] = None
        
        context['apprentice_courses'] = Curso.objects.filter(
            es_activo=True,
            grado_destinatario='aprendiz'
        ).order_by('orden')
        
        context['fellow_courses'] = Curso.objects.filter(
            es_activo=True,
            grado_destinatario='companero'
        ).order_by('orden')
        
        context['master_courses'] = Curso.objects.filter(
            es_activo=True,
            grado_destinatario='maestro'
        ).order_by('orden')
        
        context['all_levels_courses'] = Curso.objects.filter(
            es_activo=True,
            grado_destinatario='todos'
        ).order_by('orden')
        
        materials = MaterialEducativo.objects.all()
        if not self.request.user.is_authenticated:
            materials = materials.filter(solo_miembros=False)
        context['recent_materials'] = materials.order_by('-id')[:6]
        
        library = BibliotecaDigital.objects.filter(disponible=True)
        if not self.request.user.is_authenticated:
            library = library.filter(solo_miembros=False)
        context['featured_library'] = library.order_by('?')[:8]
        
        return context


class CourseDetailView(DetailView):
    """Detalle de un curso específico"""
    model = Curso
    template_name = 'course_detail.html'
    context_object_name = 'course'
    slug_field = 'slug'
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(es_activo=True)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        
        context['materials'] = course.materiales.all().order_by('orden')
        
        if self.request.user.is_authenticated and hasattr(self.request.user, 'miembro'):
            context['user_enrolled'] = course.inscritos.filter(
                id=self.request.user.miembro.id
            ).exists()
        
        return context


@login_required
def enroll_course(request, course_id):
    """Inscribir a un miembro en un curso"""
    course = get_object_or_404(Curso, id=course_id, es_activo=True)
    member = request.user.miembro
    
    if member in course.inscritos.all():
        messages.warning(request, 'Ya estás inscrito en este curso')
    else:
        if course.cupo_maximo > 0 and course.inscritos.count() >= course.cupo_maximo:
            messages.error(request, 'El curso ha alcanzado su cupo máximo')
        else:
            course.inscritos.add(member)
            messages.success(request, 'Te has inscrito exitosamente al curso')
    
    return HttpResponseRedirect(reverse('course_detail', args=[course.slug]))


# ============================================
# VISTAS DE MIEMBROS (DIRECTORIO)
# ============================================

class DirectoryView(TemplateView):
    """Directorio de miembros (público)"""
    template_name = 'directory.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        public_members = Miembro.objects.filter(
            es_publico=True,
            estatus='activo'
        ).select_related('grado_actual', 'cargo_actual').order_by('orden', 'nombre_completo')
        
        paginator = Paginator(public_members, 12)
        page = self.request.GET.get('page', 1)
        
        try:
            context['members'] = paginator.page(page)
        except PageNotAnInteger:
            context['members'] = paginator.page(1)
        except EmptyPage:
            context['members'] = paginator.page(paginator.num_pages)
        
        context['officers'] = Miembro.objects.filter(
        Q(cargo_actual__isnull=False),
        Q(estatus='activo'),
        Q(fecha_inicio_cargo__lte=timezone.now().date()) &
        (Q(fecha_fin_cargo__isnull=True) | Q(fecha_fin_cargo__gte=timezone.now().date()))
    ).select_related('cargo_actual', 'grado_actual').order_by('cargo_actual__jerarquia', 'cargo_actual__orden')
        return context


class MemberDetailView(DetailView):
    """Perfil público de un miembro"""
    model = Miembro
    template_name = 'member_detail.html'
    context_object_name = 'member'
    
    def get_queryset(self):
        return Miembro.objects.filter(es_publico=True, estatus='activo')


# ============================================
# VISTAS DE EVENTOS
# ============================================

class CalendarView(TemplateView):
    """Calendario de eventos (calendar.html)"""
    template_name = 'calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['upcoming_events'] = Evento.objects.filter(
            es_activo=True,
            fecha_inicio__gte=timezone.now()
        ).order_by('fecha_inicio')
        
        events = Evento.objects.filter(
            es_activo=True,
            fecha_inicio__year=timezone.now().year
        ).order_by('fecha_inicio')
        
        events_by_month = {}
        for event in events:
            month = event.fecha_inicio.strftime('%Y-%m')
            if month not in events_by_month:
                events_by_month[month] = []
            events_by_month[month].append(event)
        
        context['events_by_month'] = events_by_month
        
        return context


class EventDetailView(DetailView):
    """Detalle de un evento específico"""
    model = Evento
    template_name = 'event_detail.html'
    context_object_name = 'event'
    slug_field = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        
        context['total_attendees'] = event.asistentes.count()
        
        if self.request.user.is_authenticated and hasattr(self.request.user, 'miembro'):
            context['user_attending'] = event.asistentes.filter(
                id=self.request.user.miembro.id
            ).exists()
        
        return context


@login_required
def confirm_attendance(request, event_id):
    """Confirmar asistencia a un evento"""
    event = get_object_or_404(Evento, id=event_id, es_activo=True)
    member = request.user.miembro
    
    if member in event.asistentes.all():
        event.asistentes.remove(member)
        messages.success(request, 'Has cancelado tu asistencia')
    else:
        if event.cupo_maximo > 0 and event.asistentes.count() >= event.cupo_maximo:
            messages.error(request, 'El evento ha alcanzado su cupo máximo')
        else:
            event.asistentes.add(member)
            messages.success(request, '¡Asistencia confirmada!')
    
    return HttpResponseRedirect(reverse('event_detail', args=[event.slug]))


# ============================================
# VISTAS DE BLOG
# ============================================

class PublicationListView(ListView):
    """Listado de publicaciones/noticias (publications.html)"""
    model = Publicacion
    template_name = 'publications.html'
    context_object_name = 'publications'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Publicacion.objects.filter(es_activo=True)
        
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(solo_miembros=False)
        
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(categorias__slug=category)
        
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(titulo__icontains=q) | 
                Q(contenido__icontains=q) |
                Q(subtitulo__icontains=q)
            )
        
        return queryset.select_related('autor').prefetch_related('categorias').order_by('-fecha_publicacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CategoriaPublicacion.objects.annotate(
            total=Count('publicacion')
        ).filter(total__gt=0).order_by('nombre')
        context['current_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class PublicationDetailView(DetailView):
    """Detalle de una publicación (publication.html)"""
    model = Publicacion
    template_name = 'publication.html'
    context_object_name = 'publication'
    slug_field = 'slug'
    
    def get_queryset(self):
        queryset = Publicacion.objects.filter(es_activo=True)
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(solo_miembros=False)
        return queryset.select_related('autor').prefetch_related('categorias')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        publication = self.get_object()
        
        publication.visitas += 1
        publication.save(update_fields=['visitas'])
        
        categories = publication.categorias.all()
        if categories:
            context['related_publications'] = Publicacion.objects.filter(
                es_activo=True,
                categorias__in=categories
            ).exclude(id=publication.id).distinct().order_by('-fecha_publicacion')[:3]
        
        return context


# ============================================
# VISTAS DE CONTACTO
# ============================================

class ContactView(TemplateView):
    """Vista de contacto con formulario (contact.html)"""
    template_name = 'contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['contact_media'] = MedioContacto.objects.filter(
            es_activo=True
        ).order_by('-es_principal', 'orden')
        
        context['schedules'] = HorarioAtencion.objects.all().order_by('dia')
        context['form'] = ContactoForm()
        context['regular_meeting'] = Tenida.objects.first()
        
        return context
    
    def post(self, request, *args, **kwargs):
        form = ContactoForm(request.POST)
        
        if form.is_valid():
            message = form.save(commit=False)
            
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                message.ip_origen = x_forwarded_for.split(',')[0]
            else:
                message.ip_origen = request.META.get('REMOTE_ADDR')
            
            message.save()
            
            try:
                send_mail(
                    f'Nuevo mensaje de contacto: {message.get_asunto_display()}',
                    f'De: {message.nombre} ({message.email})\n\n{message.mensaje}',
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_EMAIL],
                    fail_silently=True,
                )
            except:
                pass
            
            messages.success(request, 'Tu mensaje ha sido enviado. Te contactaremos pronto.')
            return HttpResponseRedirect(reverse('contact'))
        else:
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)


# ============================================
# VISTAS DE API (AJAX)
# ============================================

def api_events_json(request):
    """API para obtener eventos en formato JSON"""
    events = Evento.objects.filter(
        es_activo=True,
        fecha_inicio__gte=timezone.now()
    ).order_by('fecha_inicio')[:50]
    
    data = []
    for event in events:
        data.append({
            'id': event.id,
            'title': event.titulo,
            'start': event.fecha_inicio.isoformat(),
            'end': event.fecha_fin.isoformat() if event.fecha_fin else None,
            'url': reverse('event_detail', args=[event.slug]),
            'type': event.get_tipo_display(),
            'className': f'event-{event.tipo}',
        })
    
    return JsonResponse(data, safe=False)


def api_phrase_of_day(request):
    """API para obtener frase del día"""
    phrase = FraseCelebre.objects.filter(activo=True).order_by('?').first()
    
    if phrase:
        data = {
            'content': phrase.contenido,
            'author': phrase.autor,
        }
    else:
        data = {
            'content': 'La luz disipa las sombras',
            'author': 'Masonería',
        }
    
    return JsonResponse(data)


# ============================================
# VISTAS DE ERROR PERSONALIZADAS
# ============================================

def error_404(request, exception):
    """Página de error 404 personalizada"""
    return render(request, '404.html', status=404)


def error_500(request):
    """Página de error 500 personalizada"""
    return render(request, '500.html', status=500)


# ============================================
# VISTAS DE BÚSQUEDA GLOBAL
# ============================================

class SearchView(TemplateView):
    """Búsqueda global en el sitio (search.html)"""
    template_name = 'search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        
        if query and len(query) >= 3:
            publications = Publicacion.objects.filter(
                Q(es_activo=True) &
                Q(titulo__icontains=query) | 
                Q(contenido__icontains=query) |
                Q(subtitulo__icontains=query)
            )
            if not self.request.user.is_authenticated:
                publications = publications.filter(solo_miembros=False)
            context['publication_results'] = publications[:5]
            context['total_publications'] = publications.count()
            
            courses = Curso.objects.filter(
                Q(es_activo=True) &
                Q(titulo__icontains=query) | 
                Q(descripcion_larga__icontains=query) |
                Q(descripcion_corta__icontains=query)
            )
            context['course_results'] = courses[:5]
            context['total_courses'] = courses.count()
            
            events = Evento.objects.filter(
                Q(es_activo=True) &
                Q(titulo__icontains=query) | 
                Q(descripcion__icontains=query)
            )
            context['event_results'] = events[:5]
            context['total_events'] = events.count()
            
            pages = Pagina.objects.filter(
                Q(es_activo=True) &
                Q(titulo__icontains=query) | 
                Q(contenido__icontains=query) |
                Q(subtitulo__icontains=query)
            )
            if not self.request.user.is_authenticated:
                pages = pages.filter(solo_miembros=False)
            context['page_results'] = pages[:5]
            context['total_pages'] = pages.count()
            
            context['query'] = query
        
        return context


# ============================================
# VISTAS PROTEGIDAS PARA MIEMBROS
# ============================================

@method_decorator(login_required, name='dispatch')
class MembersAreaView(TemplateView):
    """Área privada para miembros (members_area.html)"""
    template_name = 'members_area.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = self.request.user.miembro
        
        context['member'] = member
        context['upcoming_events'] = Evento.objects.filter(
            es_activo=True,
            fecha_inicio__gte=timezone.now()
        ).order_by('fecha_inicio')[:5]
        
        context['my_courses'] = member.cursos_inscritos.filter(es_activo=True)
        context['my_events'] = member.eventos_asistidos.filter(
            es_activo=True,
            fecha_inicio__gte=timezone.now()
        )[:5]
        
        context['private_documents'] = DocumentoHistorico.objects.filter(
            solo_miembros=True
        ).order_by('-fecha')[:10]
        
        return context


@method_decorator(login_required, name='dispatch')
class MyProfileView(UpdateView):
    """Vista del perfil propio - permite ver y editar"""
    model = Miembro
    template_name = 'my_profile.html'
    context_object_name = 'member'
    fields = [
        'nombre_masonico',
        'nombre_completo',
        'email', 
        'telefono',
        'direccion',
        'foto',
        'es_publico'
    ]
    success_url = '/members-area/'
    
    def get_object(self, queryset=None):
        return self.request.user.miembro
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modo_edicion'] = True  
        return context


# ============================================
# VISTAS DE SITEMAP Y RSS (SEO)
# ============================================

class SitemapView(TemplateView):
    """Sitemap XML para SEO (sitemap.xml)"""
    template_name = 'sitemap.xml'
    content_type = 'application/xml'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['pages'] = Pagina.objects.filter(es_activo=True)
        context['publications'] = Publicacion.objects.filter(es_activo=True)
        context['events'] = Evento.objects.filter(es_activo=True)
        context['courses'] = Curso.objects.filter(es_activo=True)
        
        return context