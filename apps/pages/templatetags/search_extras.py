from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape
import re

register = template.Library()

@register.filter
def highlight(text, query):
    """
    Resalta las ocurrencias de query en text con <mark>
    Uso: {{ texto|highlight:query }}
    """
    if not query or not text:
        return text
    
    try:
        text_str = str(text)
        query_str = str(query)
        
        query_escaped = re.escape(query_str)
        
        pattern = re.compile(f'({query_escaped})', re.IGNORECASE)
        
        highlighted = pattern.sub(
            r'<mark class="bg-gold/30 text-gray-900 dark:text-white px-1 rounded font-medium">\1</mark>', 
            text_str
        )
        
        return mark_safe(highlighted)
    except Exception as e:
        return text


@register.filter
def truncate_chars(text, length):
    """
    Corta texto por número de caracteres
    Uso: {{ texto|truncate_chars:100 }}
    """
    if not text:
        return ""
    
    text_str = str(text)
    if len(text_str) <= length:
        return text_str
    
    return text_str[:length].rsplit(' ', 1)[0] + "..."


@register.simple_tag
def active_page(request, url_name, css_class="active"):
    """
    Determina si la página actual está activa
    Uso: {% active_page request 'home' 'text-gold' %}
    """
    from django.urls import resolve
    
    try:
        if resolve(request.path_info).url_name == url_name:
            return css_class
    except:
        pass
    return ""


@register.filter
def get_grade_symbol(grade):
    """
    Devuelve el símbolo correspondiente al grado masónico
    Uso: {{ grado|get_grade_symbol }}
    """
    symbols = {
        'aprendiz': '∴',
        'companero': '⌖',
        'maestro': '◈',
        'todos': '⚜️',
    }
    return symbols.get(str(grade).lower(), '∴')


@register.filter
def format_date_spanish(date):
    """
    Formatea fecha en español
    Uso: {{ fecha|format_date_spanish }}
    """
    if not date:
        return ""
    
    meses = [
        'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
    ]
    dias = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
    
    try:
        return f"{dias[date.weekday()]} {date.day} de {meses[date.month-1]} de {date.year}"
    except:
        return str(date)


@register.filter
def mask_email(email):
    """
    Oculta parcialmente un email para privacidad
    Uso: {{ email|mask_email }}
    """
    if not email:
        return ""
    
    try:
        username, domain = email.split('@')
        if len(username) > 3:
            masked_username = username[:2] + '***' + username[-1:]
        else:
            masked_username = username[0] + '***'
        
        domain_parts = domain.split('.')
        masked_domain = domain_parts[0][0] + '***.' + domain_parts[-1]
        
        return f"{masked_username}@{masked_domain}"
    except:
        return email


@register.simple_tag
def breadcrumb(request):
    """
    Genera migas de pan automáticas
    Uso: {% breadcrumb request %}
    """
    from django.urls import resolve
    
    path = request.path
    parts = path.split('/')[1:-1]
    html = '<nav class="flex text-sm" aria-label="Breadcrumb"><ol class="flex items-center gap-2">'
    html += '<li><a href="/" class="text-gray-500 hover:text-gold">Inicio</a></li>'
    
    url_accum = ''
    for part in parts:
        url_accum += f'/{part}'
        try:
            resolve(url_accum)
            name = part.replace('-', ' ').title()
            html += f'<li class="flex items-center"><span class="mx-2 text-gray-400">/</span><a href="{url_accum}" class="text-gray-500 hover:text-gold">{name}</a></li>'
        except:
            name = part.replace('-', ' ').title()
            html += f'<li class="flex items-center"><span class="mx-2 text-gray-400">/</span><span class="text-gray-700 dark:text-gray-300">{name}</span></li>'
    
    html += '</ol></nav>'
    return mark_safe(html)


@register.filter
def masonic_date(date):
    """
    Convierte fecha a formato masónico: "Era Masónica"
    Uso: {{ fecha|masonic_date }}
    """
    if not date:
        return ""
    
    try:
        # Año masónico: Año de la Gran Luz + 4000
        masonic_year = date.year + 4000
        return f"{date.day}º día del {date.strftime('%B')} de {masonic_year} E∴M∴"
    except:
        return str(date)


@register.filter
def ordinal_spanish(number):
    """
    Convierte número a ordinal en español
    Uso: {{ numero|ordinal_spanish }}
    """
    ordinals = {
        1: 'primer',
        2: 'segundo', 
        3: 'tercer',
        4: 'cuarto',
        5: 'quinto',
        6: 'sexto',
        7: 'séptimo',
        8: 'octavo',
        9: 'noveno',
        10: 'décimo',
    }
    return ordinals.get(number, str(number) + '°')


@register.filter
def time_ago(date):
    """
    Muestra tiempo transcurrido en formato legible
    Uso: {{ fecha|time_ago }}
    """
    from django.utils import timezone
    from datetime import timedelta
    
    if not date:
        return ""
    
    now = timezone.now()
    diff = now - date
    
    if diff < timedelta(minutes=1):
        return "hace unos segundos"
    elif diff < timedelta(hours=1):
        minutes = int(diff.seconds / 60)
        return f"hace {minutes} {'minuto' if minutes == 1 else 'minutos'}"
    elif diff < timedelta(days=1):
        hours = int(diff.seconds / 3600)
        return f"hace {hours} {'hora' if hours == 1 else 'horas'}"
    elif diff < timedelta(days=30):
        days = diff.days
        return f"hace {days} {'día' if days == 1 else 'días'}"
    elif diff < timedelta(days=365):
        months = int(diff.days / 30)
        return f"hace {months} {'mes' if months == 1 else 'meses'}"
    else:
        years = int(diff.days / 365)
        return f"hace {years} {'año' if years == 1 else 'años'}"


@register.simple_tag
def meta_tags(title, description, image=None):
    """
    Genera meta tags para SEO
    Uso: {% meta_tags titulo descripcion imagen_url %}
    """
    html = f"""
    <meta name="title" content="{escape(title)}">
    <meta name="description" content="{escape(description)}">
    <meta property="og:title" content="{escape(title)}">
    <meta property="og:description" content="{escape(description)}">
    <meta property="og:type" content="website">
    """
    
    if image:
        html += f'<meta property="og:image" content="{escape(image)}">'
        html += f'<meta name="twitter:card" content="summary_large_image">'
    else:
        html += f'<meta name="twitter:card" content="summary">'
    
    return mark_safe(html)


@register.filter
def strip_masonic(text):
    """
    Elimina caracteres masónicos especiales para URLs
    Uso: {{ titulo|strip_masonic|slugify }}
    """
    if not text:
        return ""
    
    replacements = {
        '∴': '',
        '⌖': '',
        '◈': '',
        '⚜️': '',
        '•': '',
        '·': '',
    }
    
    text_str = str(text)
    for old, new in replacements.items():
        text_str = text_str.replace(old, new)
    
    return text_str.strip()


@register.filter
def md_to_html(text):
    """
    Convierte Markdown simple a HTML
    Uso: {{ texto|md_to_html }}
    """
    if not text:
        return ""
    
    import re
    text_str = str(text)
    
    # Encabezados
    text_str = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text_str, flags=re.MULTILINE)
    text_str = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text_str, flags=re.MULTILINE)
    text_str = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text_str, flags=re.MULTILINE)
    
    # Negrita e itálica
    text_str = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text_str)
    text_str = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text_str)
    text_str = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text_str)
    
    # Listas
    lines = text_str.split('\n')
    in_list = False
    result = []
    
    for line in lines:
        if re.match(r'^[-*•] ', line):
            if not in_list:
                result.append('<ul>')
                in_list = True
            result.append(f'<li>{line[2:]}</li>')
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(line)
    
    if in_list:
        result.append('</ul>')
    
    text_str = '\n'.join(result)
    
    # Párrafos
    paragraphs = text_str.split('\n\n')
    text_str = ''.join([f'<p>{p}</p>' if not p.strip().startswith('<') else p for p in paragraphs])
    
    return mark_safe(text_str)


@register.filter
def phone_format(phone):
    """
    Formatea número telefónico
    Uso: {{ telefono|phone_format }}
    """
    if not phone:
        return ""
    
    # Eliminar todo excepto dígitos
    digits = re.sub(r'\D', '', str(phone))
    
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 7:
        return f"{digits[:3]}-{digits[3:]}"
    else:
        return phone


@register.simple_tag
def get_random_phrase():
    """
    Obtiene una frase masónica aleatoria
    Uso: {% get_random_phrase %}
    """
    phrases = [
        {"text": "La luz disipa las sombras", "author": "Masonería"},
        {"text": "Pulir la piedra bruta es pulir el espíritu", "author": "Tradición"},
        {"text": "El masón trabaja en su templo interior", "author": "Anónimo"},
        {"text": "La escuadra ajusta la conducta, el nivel iguala a los hombres", "author": "R∴E∴A∴A∴"},
        {"text": "Tres grandes columnas sostienen la orden: Sabiduría, Fuerza y Belleza", "author": "Tradición"},
        {"text": "El secreto masónico es la belleza de lo no dicho", "author": "Anónimo"},
    ]
    
    import random
    phrase = random.choice(phrases)
    
    html = f'<p class="text-gold italic">"{phrase["text"]}"</p>'
    html += f'<p class="text-xs text-gray-500 mt-1">— {phrase["author"]}</p>'
    
    return mark_safe(html)


@register.filter
def youtube_embed(url):
    """
    Convierte URL de YouTube a embed
    Uso: {{ video_url|youtube_embed }}
    """
    if not url:
        return ""
    
    # Extraer ID de YouTube
    patterns = [
        r'youtube\.com/watch\?v=([^&]+)',
        r'youtu\.be/([^?]+)',
        r'youtube\.com/embed/([^?]+)',
    ]
    
    video_id = None
    for pattern in patterns:
        match = re.search(pattern, str(url))
        if match:
            video_id = match.group(1)
            break
    
    if video_id:
        return f"https://www.youtube.com/embed/{video_id}"
    return url