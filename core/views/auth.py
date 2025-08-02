from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import update_session_auth_hash


@never_cache
@csrf_protect
@require_http_methods(["GET", "POST"])
def custom_login(request):
    """Vue de connexion personnalisée utilisant le matricule"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        matricule = request.POST.get('username', '').upper()
        password = request.POST.get('password', '')
        
        if matricule and password:
            user = authenticate(request, username=matricule, password=password)
            if user is not None:
                login(request, user)
                
                # Vérifier si l'utilisateur doit changer son mot de passe
                if user.must_change_password:
                    messages.warning(request, 'Vous devez changer votre mot de passe pour continuer.')
                    return redirect('change_password')
                
                # Redirection vers la page demandée ou le dashboard
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard')
            else:
                messages.error(request, 'Matricule ou mot de passe incorrect.')
        else:
            messages.error(request, 'Veuillez saisir votre matricule et votre mot de passe.')
    
    # Préparer les données du formulaire pour l'affichage
    form_data = {
        'username': {
            'value': request.POST.get('username', '') if request.method == 'POST' else ''
        },
        'errors': {},
        'non_field_errors': []
    }
    
    # Ajouter les erreurs si nécessaire
    if request.method == 'POST':
        if 'Matricule ou mot de passe incorrect.' in [str(m.message) for m in messages.get_messages(request)]:
            form_data['non_field_errors'].append('Matricule ou mot de passe incorrect.')
    
    return render(request, 'core/auth/login.html', {'form': form_data})


@never_cache
def custom_logout(request):
    """Vue de déconnexion personnalisée"""
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login')


@login_required
@never_cache
@csrf_protect
@require_http_methods(["GET", "POST"])
def change_password(request):
    """Vue de changement de mot de passe"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            
            # Marquer que l'utilisateur n'a plus besoin de changer son mot de passe
            user.must_change_password = False
            user.save()
            
            # Maintenir la session après le changement de mot de passe
            update_session_auth_hash(request, user)
            
            return redirect('dashboard')
        else:
            # Les erreurs du formulaire seront affichées dans le template
            pass
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'core/auth/change_password.html', {'form': form})


@login_required
def force_password_change(request):
    """Middleware pour forcer le changement de mot de passe"""
    if request.user.must_change_password:
        # Permettre l'accès seulement aux pages de changement de mot de passe et de déconnexion
        allowed_paths = [
            reverse_lazy('change_password'),
            reverse_lazy('logout'),
        ]
        
        if request.path not in [str(path) for path in allowed_paths]:
            messages.warning(request, 'Vous devez changer votre mot de passe avant de continuer.')
            return redirect('change_password')
    
    return None