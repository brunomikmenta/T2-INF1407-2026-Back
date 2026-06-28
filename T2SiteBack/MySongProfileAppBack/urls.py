from django.urls import path
from MySongProfileAppBack import views

app_name = 'MySongProfileAppBack'

urlpatterns = [
	path('api/users/', views.CadastrarUsuarioView.as_view(), name='api_users'),
	path('api/login/', views.LoginUsuarioView.as_view(), name='api_login'),
	path('api/logout/', views.LogoutUsuarioView.as_view(), name='api_logout'),
	path('api/password-reset/', views.PasswordResetView.as_view(), name='api_password_reset'),
	path('api/profile/', views.ProfileView.as_view(), name='api_profile'),
    path('api/songlist/', views.SongListView.as_view(), name='api_songlist'),
    path('api/songlist/<int:song_id>/', views.SongListSongDetailView.as_view(), name='api_songlist_song_detail'),
    
]