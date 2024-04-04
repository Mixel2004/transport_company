from django.db import models

class Branch(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField("Branch Name", max_length=100, help_text="Enter the branch name")
    address = models.TextField("Branch Address", help_text="Enter the branch address")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Branch"
        verbose_name_plural = "Branches"
        ordering = ['name']

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField("Name", max_length=100, help_text="Enter your customer name")
    email = models.EmailField("Email address", unique=True, help_text="Enter your valid email address")
    address = models.TextField("Address", help_text="Enter your address")
    phone = models.CharField("Phone Number", max_length=10, help_text="Enter your phone number")
    password = models.CharField("Password", max_length=100, help_text="Enter your password")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('customer-detail', args=[str(self.id)])


    class Meta:
        ordering = ['created_at']
        verbose_name = "Customer"
    
class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField("Name", max_length=100, help_text="Enter your employee name")
    email = models.EmailField("Email address", unique=True, help_text="Enter your valid email address")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('employee-detail', args=[str(self.id)])
    
    def save(self, *args, **kwargs):
        print("Saving the employee")
        super().save(*args, **kwargs)
        print(f'Employee {self.name} has been saved')

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Employee"
        abstract = True

class BranchManager(Employee):
    branch_name = models.ForeignKey(Branch, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Branch Manager"
        verbose_name_plural = "Branch Managers"

class Manager(Employee):
    class Meta:
        verbose_name = "Manager"
        verbose_name_plural = "Managers"

class Tasks(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField("Task Title", max_length=100, help_text="Enter the task title")
    description = models.TextField("Task Description", help_text="Enter the task description")
    role = models.CharField("Role", max_length=50, choices=(
        ('Manager', 'Manager'),
        ('Branch Manager', 'Branch Manager'),
        ('Customer', 'Customer'),
    ))
    url = models.CharField("Task URL", help_text="Enter the task URL", max_length=100)
    request_method = models.CharField("Request Method", max_length=10, choices=(
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
    ), default='GET')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['role']

class Truck(models.Model):
    license_number = models.CharField("License Number", max_length=100, help_text="Enter the driver license number", unique=True)
    current_location = models.ForeignKey(Branch, on_delete=models.PROTECT)

    def __str__(self):
        return self.license_number

    class Meta:
        verbose_name = "Truck"
        verbose_name_plural = "Trucks"
        ordering = ['license_number']

class Consignment(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    weight = models.FloatField("Consignment Weight", help_text="Enter the consignment weight")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    truck = models.ForeignKey(Truck, on_delete=models.PROTECT, default=0)
    source_branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="source_branch")
    destination_branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="destination_branch")
    status = models.CharField("Consignment Status", max_length=50, choices=(
        ('Placed', 'Placed'),
        ('Truck Assigned', 'Truck Assigned'),
        ('In Transit', 'In Transit'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ), default='Placed')

    def __str__(self):
        return f"ID-{self.id} - {self.weight}kg - {self.source_branch.name} -> {self.destination_branch.name}"
    
    class Meta:
        verbose_name = "Consignment"
        verbose_name_plural = "Consignments"
        ordering = ['-created_at']

class WaitingTime(models.Model):
    id = models.AutoField(primary_key=True)
    consignment = models.ForeignKey(Consignment, on_delete=models.PROTECT, unique=True)
    waiting_time = models.FloatField("Waiting Time", help_text="Enter the waiting time in hours")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.consignment} - {self.waiting_time} hours"

    class Meta:
        verbose_name = "Waiting Time"
        verbose_name_plural = "Waiting Times"
        ordering = ['-created_at']
