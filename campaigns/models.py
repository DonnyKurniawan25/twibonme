from django.db import models
from django.utils.text import slugify
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
import os
import uuid

class Campaign(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    frame_image = models.ImageField(upload_to='frames/')
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    views_count = models.PositiveIntegerField(default=0)
    downloads_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            if Campaign.objects.filter(slug=self.slug).exists():
                self.slug = f"{self.slug}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class CampaignResult(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='results')
    image = models.ImageField(upload_to='results/')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.campaign.title} ({self.uuid})"

@receiver(post_delete, sender=Campaign)
def submission_delete(sender, instance, **kwargs):
    """Deletes file from filesystem when corresponding `Campaign` object is deleted."""
    if instance.frame_image:
        if os.path.isfile(instance.frame_image.path):
            os.remove(instance.frame_image.path)

@receiver(pre_save, sender=Campaign)
def submission_update(sender, instance, **kwargs):
    """Deletes old file from filesystem when corresponding `Campaign` object is updated with new file."""
    if not instance.pk:
        return False

    try:
        old_file = Campaign.objects.get(pk=instance.pk).frame_image
    except Campaign.DoesNotExist:
        return False

    new_file = instance.frame_image
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=255, default="Twibbon Lombok Barat")
    site_logo = models.ImageField(upload_to='site/', null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteSettings.objects.exists():
            return SiteSettings.objects.first()
        super().save(*args, **kwargs)

    def __str__(self):
        return "Site Settings"

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class Slide(models.Model):
    image = models.ImageField(upload_to='slides/')
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title or f"Slide {self.id}"
