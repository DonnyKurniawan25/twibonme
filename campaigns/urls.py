from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    CampaignListView, CampaignCreateView, CampaignDetailView,
    CampaignUpdateView, CampaignDeleteView, increment_download_count,
    ProfileView, save_campaign_result, campaign_result, DashboardView,
    ResultListView, RegisterView, MyResultsView, MyCampaignListView,
    ExploreView, SiteSettingsView, SlideListView, SlideCreateView,
    SlideUpdateView, SlideDeleteView
)

urlpatterns = [
    path('', CampaignListView.as_view(), name='home'),
    path('create/', CampaignCreateView.as_view(), name='create_campaign'),
    path('campaign/<slug:slug>/', CampaignDetailView.as_view(), name='campaign_detail'),
    path('campaign/<slug:slug>/edit/', CampaignUpdateView.as_view(), name='edit_campaign'),
    path('campaign/<slug:slug>/delete/', CampaignDeleteView.as_view(), name='delete_campaign'),
    path('campaign/<slug:slug>/download/', increment_download_count, name='increment_download_count'),
    path('campaign/<slug:slug>/save/', save_campaign_result, name='save_campaign_result'),
    path('result/<uuid:uuid>/', campaign_result, name='campaign_result'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/settings/', SiteSettingsView.as_view(), name='site_settings'),
    path('dashboard/slides/', SlideListView.as_view(), name='slide_list'),
    path('dashboard/slides/add/', SlideCreateView.as_view(), name='add_slide'),
    path('dashboard/slides/<int:pk>/edit/', SlideUpdateView.as_view(), name='edit_slide'),
    path('dashboard/slides/<int:pk>/delete/', SlideDeleteView.as_view(), name='delete_slide'),
    path('dashboard/results/', ResultListView.as_view(), name='result_list'),
    path('dashboard/results/', ResultListView.as_view(), name='result_list'),
    path('my-results/', MyResultsView.as_view(), name='my_results'),
    path('my-campaigns/', MyCampaignListView.as_view(), name='my_campaigns'),
    path('explore/', ExploreView.as_view(), name='explore'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('accounts/profile/', ProfileView.as_view(), name='profile'),
]
