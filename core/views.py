from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Item
from .forms import ItemForm

def item_list(request):
    items = Item.objects.all()
    return render(request, 'core/item_list.html', {'items': items})

def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, 'Élément créé avec succès!')
            # Return the new item row for HTMX
            html = render_to_string('core/item_row.html', {'item': item}, request=request)
            response = HttpResponse(html)
            response['HX-Trigger'] = 'itemCreated'
            return response
    else:
        form = ItemForm()
    
    return render(request, 'core/item_form_modal.html', {'form': form, 'title': 'Créer un élément'})

def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            messages.success(request, 'Élément modifié avec succès!')
            # Return the updated item row for HTMX
            html = render_to_string('core/item_row.html', {'item': item}, request=request)
            response = HttpResponse(html)
            response['HX-Trigger'] = 'itemUpdated'
            return response
    else:
        form = ItemForm(instance=item)
    
    return render(request, 'core/item_form_modal.html', {
        'form': form, 
        'item': item, 
        'title': f'Modifier: {item.title}'
    })

@require_http_methods(["DELETE"])
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    item.delete()
    messages.success(request, 'Élément supprimé avec succès!')
    response = HttpResponse()
    response['HX-Trigger'] = 'itemDeleted'
    return response

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'core/item_detail_modal.html', {'item': item})
