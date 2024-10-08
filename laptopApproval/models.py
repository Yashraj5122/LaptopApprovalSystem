from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('Employee', 'Employee'),
        ('Manager', 'Manager'),
        ('Admin', 'Admin')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
class Employee(models.Model):
    emp_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=50)
    doj = models.DateTimeField()
    manager = models.ForeignKey('Manager', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
  
    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

class Manager(models.Model):
    manager_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

class LaptopRequest(models.Model):
    REQUEST_STATUS = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled')
    ]
    
    PRIORITY = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low')
    ]

    request_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    approved_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    request_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=REQUEST_STATUS, default='Pending')
    reason = models.TextField()
    comments = models.TextField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY, default='Medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

class ApprovalHistory(models.Model):
    request = models.ForeignKey(LaptopRequest, on_delete=models.CASCADE)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField()

class LaptopInventory(models.Model):
    laptop_id = models.AutoField(primary_key=True)
    model = models.CharField(max_length=100)
    specifications = models.TextField()
    quantity = models.IntegerField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

class RequestAssignment(models.Model):
    CONDITION = [
        ('Good', 'Good'),
        ('Needs Repair', 'Needs Repair'),
        ('Lost', 'Lost')
    ]
    RETURN_REASON = [
        ('Assigned', 'Assigned'),
        ('Returned', 'Returned'),
        ('Lost', 'Lost')
    ]

    assignment_id = models.AutoField(primary_key=True)
    request = models.ForeignKey(LaptopRequest, on_delete=models.CASCADE)
    laptop = models.ForeignKey(LaptopInventory, on_delete=models.CASCADE)
    assignment_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    condition = models.CharField(max_length=50, choices = CONDITION)
    status = models.CharField(max_length=20, choices=RETURN_REASON, default='Assigned')
    return_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()




