from rest_framework.response import Response
from rest_framework import status
from firebase_admin import auth
from .models import Customer, Manager, BranchManager

import requests

def sign_in(email, password):
    api_key = "AIzaSyDrNs_IXZBvaIUfFoJOI5BX_F1R-m7gbMI"
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def firebase_login(request):
    # Authenticate user with email and password
    email = request.data.get('username')
    password = request.data.get('password')
    
    # User authenticated, set session cookie
    sign_in_response = sign_in(email, password)
    id_token = sign_in_response.get('idToken')
    if not id_token:
        return Response({'message': 'Login failed'}, status=status.HTTP_400_BAD_REQUEST)
    response = Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
    expiration = 3600
    response.set_cookie('session', id_token, max_age=expiration)
    response.set_cookie('name', sign_in_response.get('displayName'), max_age=expiration)
    response.set_cookie('email', sign_in_response.get('email'), max_age=expiration)
    customer = Customer.objects.filter(email=email)
    if customer.exists():
        response.set_cookie('userType', 'customer', max_age=expiration)

    else:
        manager = Manager.objects.filter(email=email)
        if manager.exists():
            response.set_cookie('userType', 'manager', max_age=expiration)
        else:
            branch_manager = BranchManager.objects.filter(email=email)
            if branch_manager.exists():
                response.set_cookie('userType', 'branch_manager', max_age=expiration)
    return response    
