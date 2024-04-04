from rest_framework import serializers
from .models import *

class CustomerSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    address = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'address', 'phone', 'password', 'confirm_password', 'created_at', 'updated_at']

    
    def validate(self, data):
        if len(data['phone']) != 10:
            raise serializers.ValidationError("Phone number must be 10 digits")
        if len(data['password']) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters")
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        data.pop('confirm_password')
        
        return data

    def perform_destroy(self, instance):
        print("Deleting a customer")
        instance.delete()
        print(f'Customer {instance.name} has been deleted')

class ManagerSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    class Meta:
        model = Manager
        fields = '__all__'
    
    def perform_destroy(self, instance):
        print("Deleting a manager")
        instance.delete()
        print(f'Manager {instance.name} has been deleted')
    
class BranchManagerSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    branch_name = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=True)

    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    class Meta:
        model = BranchManager
        fields = '__all__'
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['branch_name'] = instance.branch_name.name
        return data

    def perform_destroy(self, instance):
        print("Deleting a branch manager")
        instance.delete()
        print(f'Branch Manager {instance.name} has been deleted')

class TruckSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    license_number = serializers.CharField(required=True)
    current_location = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    class Meta:
        model = Truck
        fields = '__all__'
    
    def perform_destroy(self, instance):
        print("Deleting a truck")
        instance.delete()
        print(f'Truck {instance.name} has been deleted')
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['current_location'] = instance.current_location.name
        return data

class ConsignmentSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    customer = serializers.CharField(source='customer.email', read_only=True)

    class Meta:
        model = Consignment
        fields = '__all__'
    
    def get_fields(self):
        fields = super().get_fields()
        print(f"Get field called with fields: {fields}")
        if not self.context.get('request'):
            print("No request context")
            print(f"self.context: {self.context}")
            return fields
        if self.context.get('request').method == 'GET':
            self.Meta.fields = ['id', 'weight', 'source_branch', 'destination_branch', 'created_at', 'updated_at', 'customer', 'status']
        if self.context.get('request').method != 'PUT':
            self.Meta.fields = ['id', 'weight', 'source_branch', 'destination_branch', 'created_at', 'updated_at', 'customer']
        else:
            # fields = {
            #     'weight': serializers.FloatField(read_only=True),
            #     'status': serializers.ChoiceField(choices=[
            #         ('Placed', 'Placed'),
            #         ('Truck Assigned', 'Truck Assigned'),
            #         ('In Transit', 'In Transit'),
            #         ('Delivered', 'Delivered'),
            #         ('Cancelled', 'Cancelled'),
            #     ]),
            #     'truck': serializers.PrimaryKeyRelatedField(queryset=Truck.objects.all())
            # }
            self.Meta.fields = ['id', 'status', 'truck', 'created_at', 'updated_at', 'customer']
        return fields
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['truck'] = instance.truck.license_number if instance.truck.id != 0 else "Not assigned"
        data['weight'] = f"{int(instance.weight)}kg"
        data['source_branch'] = instance.source_branch.name
        data['destination_branch'] = instance.destination_branch.name
        data['price'] = instance.weight * 100
        return data

    def validate(self, data):
        if not self.context.get('request'):
            return data
        if self.context.get('request').method != 'PUT':
            if data['weight'] < 0:
                raise serializers.ValidationError("Weight must be a positive number")
            if data['source_branch'] == data['destination_branch']:
                raise serializers.ValidationError("Source and destination branches must be different")
            if not data.get('truck'):
                data['truck'] = Truck.objects.get(id=0)
            elif data['truck'].current_location != data['source_branch']:
                raise serializers.ValidationError("Truck must be at the source branch")
        else:
            source_branch = self.instance.source_branch
            print(f"Source branch: {source_branch}")
            if data['truck'].current_location != source_branch:
                raise serializers.ValidationError("Truck must be at the source branch")
        return data
    
    def perform_destroy(self, instance):
        print("Deleting a consignment")
        instance.delete()
        print(f'Consignment {instance.name} has been deleted')

class WaitingTimeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    consignment = serializers.PrimaryKeyRelatedField(queryset=Consignment.objects.all())
    waiting_time = serializers.DecimalField(decimal_places=2, max_digits=10, required=True)
    class Meta:
        fields = '__all__'
    
    def create(self, validated_data):
        instance = WaitingTime.objects.create(**validated_data)
        print(f'Waiting time for {instance.consignment} has been created')
        return instance
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['consignment'] = str(instance.consignment)
        data['waiting_time'] = f"{instance.waiting_time} hours"
        return data

class LoginCustomerSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'})
    class Meta:
        fields = ['email', 'password'] 
    
class TaskSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    
    class Meta:
        model = Tasks
        fields = ['id', 'title', 'description', 'role', 'url', 'request_method', 'created_at', 'updated_at']
    

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.url.startswith('http'):
            data['url'] = instance.url
        else:
            data['url'] = f'http://localhost:8000/{instance.url}'
        return data

class BranchSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = Branch
        fields = ['id', 'name', 'address', 'created_at', 'updated_at']
    
    def perform_destroy(self, instance):
        print("Deleting a branch")
        instance.delete()
        print(f'Branch {instance.name} has been deleted')
