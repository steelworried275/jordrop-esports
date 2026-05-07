from django.urls import path
from . import views

urlpatterns = [
    # Per-game wiki index
    path('<slug:game_slug>/', views.wiki_list, name='wiki_list'),
    # Page creation (contributor+)
    path('<slug:game_slug>/new/', views.create_page, name='wiki_create_page'),
    # Page detail
    path('<slug:game_slug>/<slug:slug>/', views.page_detail, name='wiki_detail'),
    # Submit edit (contributor+)
    path('<slug:game_slug>/<slug:slug>/edit/', views.submit_edit, name='wiki_submit_edit'),
    # Revision history
    path('<slug:game_slug>/<slug:slug>/history/', views.page_history, name='wiki_history'),
    # Single revision view + diff
    path('<slug:game_slug>/<slug:slug>/history/<int:revision_number>/', views.revision_detail, name='wiki_revision_detail'),
    # Restore revision (moderator+)
    path('<slug:game_slug>/<slug:slug>/history/<int:revision_number>/restore/', views.restore_revision, name='wiki_restore_revision'),
    # Moderation queue (moderator+)
    path('moderation/queue/', views.moderation_queue, name='moderation_queue'),
    path('moderation/approve/<int:pk>/', views.approve_edit, name='wiki_approve_edit'),
    path('moderation/reject/<int:pk>/', views.reject_edit, name='wiki_reject_edit'),
]
