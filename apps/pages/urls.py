from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('page/<slug:slug>/', views.PaginaView.as_view(), name='page'),
    path('history/', views.HistoryView.as_view(), name='history'),
    path('history/event/<int:pk>/', views.HistoricalEventDetailView.as_view(), name='historical_event'),
    path('freemasonry/', views.FreemasonryView.as_view(), name='freemasonry'),
    path('education/', views.EducationView.as_view(), name='education'),
    path('education/course/<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('education/course/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('directory/', views.DirectoryView.as_view(), name='directory'),
    path('member/<int:pk>/', views.MemberDetailView.as_view(), name='member_detail'),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('event/<slug:slug>/', views.EventDetailView.as_view(), name='event_detail'),
    path('event/<int:event_id>/attend/', views.confirm_attendance, name='confirm_attendance'),
    path('publications/', views.PublicationListView.as_view(), name='publications'),
    path('publication/<slug:slug>/', views.PublicationDetailView.as_view(), name='publication_detail'),
    path('api/events/', views.api_events_json, name='api_events'),
    path('api/phrase-of-day/', views.api_phrase_of_day, name='api_phrase'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('members-area/', views.MembersAreaView.as_view(), name='members_area'),
    path('my-profile/', views.MyProfileView.as_view(), name='my_profile'),
    path('sitemap.xml/', views.SitemapView.as_view(), name='sitemap'),
]