from .models import *
from rest_framework import serializers
from datetime import datetime
from django.utils import timezone

class UserRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    class Meta:
        model = UserProfile
        fields = ['username', 'password', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return UserProfile.objects.create(user=user, role=validated_data['role'])

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    class Meta:
        model = UserProfile
        fields = ['username', 'role']

class EmployeeSerializer(serializers.ModelSerializer):
    
    def validate_emp_id(self,value):
        if not value.isalnum() or len(value) != 10:
            raise serializers.ValidationError('Employee Id must be alphanumeric and exactly 10 characters')
        return value
            
    def validate_email(self,value):
        if not value.endswith("@sankeysolutions.com"):
            raise serializers.ValidationError('Email must be from Sankey Email only')
        return value
    
    def validate_doj(self, value):
        if value > timezone.now():
            raise serializers.ValidationError('Date of joining cannot be in future')
        return value
    
    class Meta:
        model = Employee
        exclude = ['created_at', 'updated_at']

class ManagerSerializer(serializers.ModelSerializer):

    def validate_manager_id(self, value):
        if not value.isalnum() or len(value) != 10:
            raise serializers.ValidationError('Manager Id must be alphanumeric and exactly 10 characters')
        return value

    def validate_email(self,value):
        if not value.endswith("@sankeysolutions.com"):
            raise serializers.ValidationError('Email must be from Sankey Email only')
        return value
    
    class Meta:
        model = Manager
        exclude = ['created_at', 'updated_at']

class LaptopRequestSerializer(serializers.ModelSerializer):

    def validate(self,data):
        if data['priority'] == 'High' and data['status'] == 'Rejected':
            raise serializers.ValidationError('High priority requests cannot be rejected')
        
        if data['employee'].department != data['manager'].department:
            raise serializers.ValidationError('Employee and Manager must be in same department')

        
        if data['status'] == 'Approved' and not data['approval_date']:
            raise serializers.ValidationError("Approval date is required when request is 'Approved'")

        return data
    
    class Meta:
        model = LaptopRequest
        exclude = ['created_at', 'updated_at', 'is_deleted']

class ApprovalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalHistory
        fields = '__all__'

class LaptopInventorySerializer(serializers.ModelSerializer):

    # def validate_quantity(self, value):
    #     if value < 0:
    #         raise serializers.ValidationError('Quantity must not be negative')
    #     return value

    class Meta:
        model = LaptopInventory
        fields = '__all__'

class RequestAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestAssignment
        exclude = ['created_at', 'updated_at']