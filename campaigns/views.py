from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404
from django.core.files.base import ContentFile
import base64
import json
import uuid
from .models import Campaign, CampaignResult, Slide
from .forms import CampaignForm

class CampaignListView(ListView):
    model = Campaign
    template_name = 'home.html'
    context_object_name = 'campaigns'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['slides'] = Slide.objects.filter(is_active=True)
        return context

class CampaignCreateView(LoginRequiredMixin, CreateView):
    model = Campaign
    form_class = CampaignForm
    template_name = 'campaign_form.html'
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        
        # Check for edited image data (Magic Eraser)
        edited_image_data = self.request.POST.get('edited_image_data')
        if edited_image_data:
            print("DEBUG: CreateView - Received edited_image_data")
            try:
                # Force PNG for edited images to preserve transparency
                if ';base64,' in edited_image_data:
                    format, imgstr = edited_image_data.split(';base64,') 
                    ext = 'png'  # Always force PNG for canvas exports
                    
                    data = ContentFile(base64.b64decode(imgstr), name=f'edited_{uuid.uuid4()}.png')
                    
                    print(f"DEBUG: CreateView - Saving edited image {data.name}")
                    # Simpan sebagai frame_image
                    self.object.frame_image.save(data.name, data, save=False)
                else:
                    print("DEBUG: CreateView - Invalid base64 data")
            except Exception as e:
                print(f"DEBUG: CreateView - Error saving edited image: {e}")
        else:
            print("DEBUG: CreateView - No edited_image_data received")

        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class CampaignDetailView(DetailView):
    model = Campaign
    template_name = 'campaign_detail.html'
    context_object_name = 'campaign'

    def get_object(self):
        obj = super().get_object()
        obj.views_count += 1
        obj.save()
        return obj

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class CampaignUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Campaign
    form_class = CampaignForm
    template_name = 'campaign_form.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user or self.request.user.is_staff

    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        # Check for edited image data (Magic Eraser)
        edited_image_data = self.request.POST.get('edited_image_data')
        if edited_image_data:
            print("DEBUG: UpdateView - Received edited_image_data")
            try:
                # Force PNG for edited images to preserve transparency
                if ';base64,' in edited_image_data:
                    format, imgstr = edited_image_data.split(';base64,') 
                    ext = 'png'  # Always force PNG for canvas exports
                    
                    data = ContentFile(base64.b64decode(imgstr), name=f'edited_{uuid.uuid4()}.png')
                    
                    # hapus gambar lama kalau ada
                    if self.object.frame_image:
                        print(f"DEBUG: UpdateView - Deleting old image: {self.object.frame_image.name}")
                        self.object.frame_image.delete(save=False)
                        
                    print(f"DEBUG: UpdateView - Saving new image {data.name}")
                    self.object.frame_image.save(data.name, data, save=False)
                else:
                    print("DEBUG: UpdateView - Invalid base64 data")
            except Exception as e:
                print(f"DEBUG: UpdateView - Error: {e}")
        else:
            print("DEBUG: UpdateView - No edited_image_data")

        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

class CampaignDeleteView(AdminRequiredMixin, DeleteView):
    model = Campaign
    template_name = 'campaign_confirm_delete.html'
    success_url = reverse_lazy('home')

@require_POST
def increment_download_count(request, slug):
    if request.method == "POST":
        campaign = get_object_or_404(Campaign, slug=slug)
        campaign.downloads_count += 1
        campaign.save()
        return JsonResponse({'status': 'success', 'downloads_count': campaign.downloads_count})
    return JsonResponse({'status': 'error'}, status=400)

@require_POST
def save_campaign_result(request, slug):
    campaign = get_object_or_404(Campaign, slug=slug)
    data = json.loads(request.body)
    image_data = data.get('image')

    if image_data:
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name=f'{campaign.slug}-{uuid.uuid4()}.{ext}')
        
        result = CampaignResult.objects.create(campaign=campaign, image=data)
        return JsonResponse({'status': 'success', 'redirect_url': f'/result/{result.uuid}/'})
    
    return JsonResponse({'status': 'error'}, status=400)

def campaign_result(request, uuid):
    result = get_object_or_404(CampaignResult, uuid=uuid)
    return render(request, 'campaign_result.html', {'result': result})

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

class DashboardView(AdminRequiredMixin, ListView):
    model = Campaign
    template_name = 'dashboard.html'
    context_object_name = 'campaigns'
    ordering = ['-created_at']

class ResultListView(AdminRequiredMixin, ListView):
    model = CampaignResult
    template_name = 'result_list.html'
    context_object_name = 'results'
    ordering = ['-created_at']
    paginate_by = 20

from django.contrib.auth import login
from .forms import UserRegistrationForm
from django.views.generic.edit import FormView

class RegisterView(FormView):
    template_name = 'register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

class MyResultsView(ListView):
    model = CampaignResult
    template_name = 'my_results.html'
    context_object_name = 'results'
    ordering = ['-created_at']
    paginate_by = 20

    def get_queryset(self):
        # For now, show all results since we don't track user ownership
        # In future, you could add a user field to CampaignResult
        return CampaignResult.objects.all().order_by('-created_at')

class MyCampaignListView(LoginRequiredMixin, ListView):
    model = Campaign
    template_name = 'my_campaigns.html'
    context_object_name = 'campaigns'
    ordering = ['-created_at']
    login_url = reverse_lazy('login')

    def get_queryset(self):
        return Campaign.objects.filter(author=self.request.user).order_by('-created_at')

class ExploreView(ListView):
    model = Campaign
    template_name = 'explore.html'
    context_object_name = 'campaigns'
    ordering = ['-created_at']
    paginate_by = 20

from .models import SiteSettings
from .forms import SiteSettingsForm

class SiteSettingsView(AdminRequiredMixin, UpdateView):
    model = SiteSettings
    form_class = SiteSettingsForm
    template_name = 'site_settings.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        return SiteSettings.get_settings()

from .models import Slide
from .forms import SlideForm

class SlideListView(AdminRequiredMixin, ListView):
    model = Slide
    template_name = 'slide_list.html'
    context_object_name = 'slides'

class SlideCreateView(AdminRequiredMixin, CreateView):
    model = Slide
    form_class = SlideForm
    template_name = 'slide_form.html'
    success_url = reverse_lazy('slide_list')

class SlideUpdateView(AdminRequiredMixin, UpdateView):
    model = Slide
    form_class = SlideForm
    template_name = 'slide_form.html'
    success_url = reverse_lazy('slide_list')

class SlideDeleteView(AdminRequiredMixin, DeleteView):
    model = Slide
    template_name = 'campaign_confirm_delete.html'
    success_url = reverse_lazy('slide_list')


