from rest_framework import viewsets, permissions
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from firebase_admin import auth
from django.utils import timezone
from .login import firebase_login
from .permissions import *
from .filters import *
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.authentication import TokenAuthentication

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def create(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = auth.create_user(email=serializer.validated_data['email'], password=serializer.validated_data['password'], display_name=serializer.validated_data['name'])
            return Response({'message': 'Customer created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ManagerViewSet(viewsets.ModelViewSet):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer
    permission_classes = [IsAdminUser]

    def create(self, request):
        serializer = ManagerSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data['password']
            serializer.validated_data.pop('password')
            user = auth.create_user(email=serializer.validated_data['email'], password=password, display_name=serializer.validated_data['name'])
            serializer.save()
            return Response({'message': 'Manager created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BranchManagerViewSet(viewsets.ModelViewSet):
    queryset = BranchManager.objects.all()
    serializer_class = BranchManagerSerializer
    permission_classes = [IsManager]

    def create(self, request):
        serializer = BranchManagerSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data['password']
            serializer.validated_data.pop('password')
            user = auth.create_user(email=serializer.validated_data['email'], password=password, display_name=serializer.validated_data['name'])
            serializer.save()
            return Response({'message': 'Branch manager account successfully added'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Tasks.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [TaskPermission]

    def get_queryset(self):
        role = self.request.COOKIES.get('userType')
        if not role:
            return Tasks.objects.none()
        if role == 'manager':
            return Tasks.objects.filter(role='Manager')
        elif role == 'branch_manager':
            return Tasks.objects.filter(role='Branch Manager')
        else:
            return Tasks.objects.filter(role='Customer')
        return Tasks.objects.none()


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [BranchPermission]

    def create(self, request):
        serializer = BranchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Branch created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TruckViewSet(viewsets.ModelViewSet):
    queryset = Truck.objects.all()
    serializer_class = TruckSerializer
    filter_backends = [CurrentLocationFilterBackend]
    permission_classes = [TruckPermission]

    def create(self, request):
        serializer = TruckSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Truck created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        response = super().list(request)
        response.data = [item for item in response.data if item['id'] != 0]
        response.data = {
            'data': response.data,
            'total': len(response.data)
        }
        return response

class ConsignmentViewSet(viewsets.ModelViewSet):
    queryset = Consignment.objects.all()
    serializer_class = ConsignmentSerializer
    filter_backends = [CustomerFilterBackend]
    permission_classes = [ConsignmentPermission]

    def create(self, request):
        serializer = ConsignmentSerializer(data=request.data)
        if serializer.is_valid():
            email = request.COOKIES.get('email')
            if not email:
                return Response({'message': 'Customer not logged in'}, status=status.HTTP_400_BAD_REQUEST)
            customer = Customer.objects.get(email=email)
            serializer.validated_data['customer'] = customer
            serializer.save()
            weight = serializer.validated_data['weight']
            return Response({'message': 'Consignment created successfully', 'price': weight*100}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        instance = Consignment.objects.get(id=pk)
        serializer = ConsignmentSerializer(instance, data=request.data)
        if serializer.is_valid():
            if instance.status == 'Delivered':
                return Response({'message': 'Consignment already delivered'}, status=status.HTTP_400_BAD_REQUEST)
            consignment_status = serializer.validated_data['status']
            if consignment_status != 'Truck Assigned':
                serializer.validated_data['truck'] = instance.truck
            if consignment_status == 'Delivered':
                serializer.validated_data['updated_at'] = timezone.now()
                wait_time = timezone.now() - instance.created_at
                waiting_time_model = WaitingTime()
                waiting_time_model.consignment = instance
                waiting_time_model.waiting_time = format((wait_time.total_seconds()/3600), '.2f')
                waiting_time_model.save()

                instance.truck.current_location = instance.destination_branch
                instance.truck.save()
            serializer.save()
            return Response({'message': 'Consignment updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_queryset(self):
        email = self.request.COOKIES.get('email')
        user_type = self.request.COOKIES.get('userType')
        if user_type and user_type == 'customer':
            if email:
                return Consignment.objects.filter(customer__email=email)
            return Consignment.objects.none()
        return Consignment.objects.all()

class WaitingTimeViewSet(viewsets.ModelViewSet):
    queryset = WaitingTime.objects.all()
    serializer_class = WaitingTimeSerializer
    permission_classes = [WaitingTimePermission]

    def list(self, request):
        response = super().list(request)
        models = WaitingTime.objects.all()
        total = 0   
        for item in models:
            total += item.waiting_time
        response.data = {
            'total_waiting_time': total,
            'avg_waiting_time': format((total/len(response.data)), '.2f'),
            'data': response.data
        }
        return response

class CheckLoginViewSet(viewsets.ViewSet):
    def get(self, request):
        session = request.COOKIES.get('session')
        try:
            user = auth.verify_id_token(session)
            print(f"User: {user}")
            return Response({'logged_in': True}, status=status.HTTP_200_OK)
        except:
            return Response({'loggedin': False}, status=status.HTTP_200_OK)


class LoginViewSet(viewsets.ViewSet):
    serializer_class = LoginCustomerSerializer
    models = Customer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'login.html'

    def get(self, request):
        return Response({}, status=status.HTTP_200_OK)

    def create(self, request):
        email = request.data.get('username')
        try:
            customer_obj = Customer.objects.filter(email=email)
            if not customer_obj.exists():
                manager_obj = Manager.objects.filter(email=email)
                if not manager_obj.exists():
                    branch_manager_obj = BranchManager.objects.filter(email=email)
                    if not branch_manager_obj.exists():
                        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Customer.DoesNotExist:
            print("Customer not found")
            return Response({'message': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

        response = firebase_login(request)
        return response

class LogoutCustomerViewSet(viewsets.ViewSet):
    def get(self, request):
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

    def create(self, request):
        response = Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        session = request.COOKIES.get('session')
        print(f"Session: {session}")
        user_name = auth.verify_id_token(session)['name']
        print(f"User name: {user_name}")
        response.delete_cookie('session')
        response.delete_cookie('email')
        response.delete_cookie('userType')
        response.delete_cookie('name')
        return response
