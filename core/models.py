from django.db import models
from django.urls import reverse

class Item(models.Model):
    CATEGORY_CHOICES = [
        ('work', 'Travail'),
        ('personal', 'Personnel'),
        ('urgent', 'Urgent'),
        ('other', 'Autre'),
    ]
    
    STATUS_CHOICES = [
        ('todo', 'À faire'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name="Catégorie")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo', verbose_name="Statut")
    priority = models.IntegerField(default=1, verbose_name="Priorité", help_text="1=Basse, 2=Moyenne, 3=Haute")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "Élément"
        verbose_name_plural = "Éléments"
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('item_detail', kwargs={'pk': self.pk})
    
    def get_category_display_class(self):
        category_classes = {
            'work': 'bg-blue-100 text-blue-800',
            'personal': 'bg-green-100 text-green-800',
            'urgent': 'bg-red-100 text-red-800',
            'other': 'bg-gray-100 text-gray-800',
        }
        return category_classes.get(self.category, 'bg-gray-100 text-gray-800')
    
    def get_status_display_class(self):
        status_classes = {
            'todo': 'bg-yellow-100 text-yellow-800',
            'in_progress': 'bg-blue-100 text-blue-800',
            'completed': 'bg-green-100 text-green-800',
        }
        return status_classes.get(self.status, 'bg-gray-100 text-gray-800')
    
    def get_priority_display_class(self):
        if self.priority >= 3:
            return 'bg-red-100 text-red-800'
        elif self.priority == 2:
            return 'bg-yellow-100 text-yellow-800'
        else:
            return 'bg-green-100 text-green-800'
