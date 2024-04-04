from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        user_type = request.COOKIES.get('userType')
        return user_type == 'manager'

class IsBranchManager(permissions.BasePermission):
    def has_permission(self, request, view):
        user_type = request.COOKIES.get('userType')
        return user_type == 'branch_manager' or user_type == 'manager'

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        user_type = request.COOKIES.get('userType')
        return user_type == 'customer'

class WaitingTimePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user_type = request.COOKIES.get('userType')
        if not user_type or user_type != 'manager':
            return False
        print(user_type)
        return request.method in ['GET', 'PUT', 'DELETE']
    
class TruckPermission(permissions.AllowAny):
    def has_permission(self, request, view):
        user_type = request.COOKIES.get('userType')
        if not user_type or user_type not in ['manager', 'branch_manager']:
            return False
        allowed_map = {
            'manager': ['GET', 'POST', 'PUT', 'DELETE'],
            'branch_manager': ['GET', 'PUT'],
        }
        return request.method in allowed_map[user_type]

class ConsignmentPermission(permissions.AllowAny):
    def has_permission(self, request, view):
        user_type = request.COOKIES.get('userType')
        email = request.COOKIES.get('email')
        if not user_type and user_type not in ['manager', 'branch_manager', 'customer']:
            return False
        allowed_map = {
            'manager': ['GET', 'PUT', 'DELETE'],
            'branch_manager': ['GET', 'PUT'],
            'customer': ['GET', 'POST'],
        }
        return request.method in allowed_map[user_type]

class BranchPermission(permissions.AllowAny):
    def has_permission(self, request, view):
        user_type = request.COOKIES.get('userType')
        if not user_type and user_type not in ['manager']:
            return False
        allowed_map = {
            'manager': ['GET', 'POST', 'PUT', 'DELETE'],
        }
        return request.method in allowed_map[user_type]

class TaskPermission(permissions.AllowAny):
    def has_permission(self, request, view):
        user_type = request.COOKIES.get('userType')
        role = request.query_params.get('role')
        if not user_type and user_type not in ['manager', 'branch_manager', 'customer'] and not role:
            return False
        allowed_map = {
            'manager': ['GET', 'POST', 'PUT', 'DELETE'],
            'branch_manager': ['GET'],
            'customer': ['GET'],
        }
        if role == 'customer' and user_type != 'customer':
            return False
        return request.method in allowed_map[user_type]
