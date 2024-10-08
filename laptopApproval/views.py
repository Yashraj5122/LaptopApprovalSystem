from .models import * 
from .views import *
from .Serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import  AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.db import IntegrityError
from .permission import *
from .pagination import *
from rest_framework import pagination

#--------------------------User Profile and Authenticated API's----------------------------#

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    data = request.data
    serializer = UserRegistrationSerializer(data=data)

    if serializer.is_valid():
        try:
            serializer.save()  
            return Response({'message': 'User created successfully'}, status=201)
        except IntegrityError:
            return Response({'error': 'Username already exists'}, status=400)

    return Response({'error': serializer.errors}, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request,username=username,password=password)
    if user is not None:
        return Response({'message' : 'Login Successful'}, status=200)  
    return Response({'error' : 'Invalid Credentials'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_logged_in_user_profile(request):
    try:
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
        serializer = UserProfileSerializer(user_profile)
        return Response({'message' : 'User Profile retrieved successfully','data' : serializer.data}, status=200)
    except UserProfile.DoesNotExist:
        return Response({'error' : 'User Profile not found'}, status=404)

@api_view(['GET'])
@permission_classes([IsAdmin])
def view_user_profiles(request):
    users = UserProfile.objects.all()
    if not users.exists():
        return Response({'message' : 'No User Profiles found'}, status=404)
    paginator = CustomPagination()
    paginated_user = paginator.paginate_queryset(users,request)
    serializer = UserProfileSerializer(paginated_user, many=True)
    return paginator.get_paginated_response({'message' : 'User Profile retrieved successfully', 'data' : serializer.data}, status=200)


#--------------------------Employee----------------------------#

@api_view(['POST'])
@permission_classes([IsEmployee])
def create_employee(request):
    data = request.data
    if isinstance(data,list):
        serializer = EmployeeSerializer(data=data, many=True)
    else:
        serializer = EmployeeSerializer(data=data)
    if serializer.is_valid():
        if isinstance(data,list):
            Employee.objects.bulk_create(Employee(**item) for item in serializer.validated_data)
            return Response({'message' : 'Employees added successfully', 'data' : serializer.data},status=200)
        serializer.save()
        return Response({'message' : 'Employee added successfully', 'data' : serializer.data},status=200)
    return Response({'error' : serializer.errors}, status=400)

@api_view(['GET'])
@permission_classes([IsEmployee])
def get_employee_details(request, emp_id):
    try:
        employee = Employee.objects.get(emp_id=emp_id, is_deleted=False)
    except Employee.DoesNotExist:
        return Response({'error' : 'No employee details found for this id'})
    
    serializer = EmployeeSerializer(employee)
    return Response({'message' : 'Employee details retrieved successfully', 'data' : serializer.data})

@api_view(['GET'])
@permission_classes([IsAdmin])
def list_employee(request):
    employees = Employee.objects.filter(is_deleted=False).order_by('emp_id')
    if not employees.exists():
        return Response({'error' : 'No Employee found'}) 
    paginator = CustomPagination()
    paginated_employees = paginator.paginate_queryset(employees,request)
    serializer = EmployeeSerializer(paginated_employees, many=True)
    return paginator.get_paginated_response({'message' : 'Employees retrieved successfully', 'data' : serializer.data})

@api_view(['PUT','PATCH'])
@permission_classes([IsAdmin])
def update_employees(request):
    data = request.data
    try:
        employee = Employee.objects.get(emp_id=data['emp_id'])
        if employee.is_deleted:
            return Response({'error' : 'Employee details has already been deleted.'})
    except Employee.DoesNotExist:
        return Response({'error' : 'Employee Not Found'})
    
    if request.method == 'PUT':
        serializer = EmployeeSerializer(employee, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message' : 'Employee details updated succcessfully', 'data' : serializer.data})
        return Response({'error' : serializer.errors},status=400)
    elif request.method == 'PATCH':
        serializer = EmployeeSerializer(employee, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message' : 'Employee details updated successfully', 'data' : serializer.data})
        return Response({'error' : serializer.errors},status=400)
    
@api_view(['DELETE'])
@permission_classes([IsAdmin])
def delete_employees(request,emp_id):
    try:
        employee = Employee.objects.get(emp_id=emp_id)
        if employee.is_deleted:
            return Response({'error' : 'Employee detail has already been deleted'}, status=400)     
    except Employee.DoesNotExist:
        return Response({'error' : 'Employee Not Found'}, status=404)  
    employee.soft_delete()
    employee.save()
    return Response({'message' : 'Employee Deleted successfully'}, status=200)

@api_view(['GET'])
@permission_classes([IsAdmin])
def list_deleted_employee(request):
    employees = Employee.objects.filter(is_deleted=True).order_by('emp_id')
    if not employees.exists():
        return Response({'error' : 'No Deleted Employees found'},status=404)
    paginator = CustomPagination()
    paginated_employees = paginator.paginate_queryset(employees, request)
    serializer = EmployeeSerializer(paginated_employees, many=True)
    return paginator.get_paginated_response({'message': 'Deleted employees retrieved successfully', 'data': serializer.data})

@api_view(['POST'])
@permission_classes([IsAdmin])
def restore_employee(request):
    data = request.data
    try:
        employee = Employee.objects.get(emp_id=data['emp_id'])
        if not employee.is_deleted:
            return Response({'error': 'Employee is not deleted yet!'})
          
    except Employee.DoesNotExist:
        return Response({'message': 'Employee Not Found'}, status=404)  
    employee.restore()
    employee.save()
    serializer = EmployeeSerializer(employee) 
    return Response({'message': 'Employee restored successfully', 'data': serializer.data}, status=200)

#--------------------------Manager----------------------------#

@api_view(['POST'])
@permission_classes([IsAdmin])
def create_manager(request):
    data = request.data
    if isinstance(data, list):
        serializer = ManagerSerializer(data=data, many=True)
    else:
        serializer = ManagerSerializer(data=data)
    if serializer.is_valid():
        if isinstance(data, list):
            Manager.objects.bulk_create(Manager(**item) for item in serializer.validated_data)
            return Response({'message': 'Managers added successfully', 'data': serializer.data}, status=200)
        serializer.save()
        return Response({'message': 'Manager added successfully', 'data': serializer.data}, status=200)
    return Response({'error': serializer.errors}, status=400)

@api_view(['GET'])
@permission_classes([IsManager])
def get_manager_details(request, manager_id):
    try:
        manager = Manager.objects.get(manager_id=manager_id, is_deleted=False)
    except Manager.DoesNotExist:
        return Response({'error': 'No manager details found for this id'})

    serializer = ManagerSerializer(manager)
    return Response({'message': 'Manager details retrieved successfully', 'data': serializer.data})

@api_view(['GET'])
@permission_classes([IsAdmin])
def list_managers(request):
    managers = Manager.objects.filter(is_deleted=False).order_by('manager_id')
    if not managers.exists():
        return Response({'error': 'No Manager found'})
    paginator = CustomPagination()
    paginated_managers = paginator.paginate_queryset(managers,request)
    serializer = ManagerSerializer(paginated_managers, many=True)
    return paginator.get_paginated_response({'message': 'Managers retrieved successfully', 'data': serializer.data})

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdmin])
def update_manager(request):
    data = request.data
    try:
        manager = Manager.objects.get(manager_id=data['manager_id'])
        if manager.is_deleted:
            return Response({'error': 'Manager details have already been deleted.'})
    except Manager.DoesNotExist:
        return Response({'error': 'Manager Not Found'})
    if request.method == 'PUT':
        serializer = ManagerSerializer(manager, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Manager details updated successfully', 'data': serializer.data})
        return Response({'error': serializer.errors}, status=400)
    elif request.method == 'PATCH':
        serializer = ManagerSerializer(manager, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Manager details updated successfully', 'data': serializer.data})
        return Response({'error': serializer.errors}, status=400)

@api_view(['DELETE'])
@permission_classes([IsAdmin])
def delete_manager(request, manager_id):
    try:
        manager = Manager.objects.get(manager_id=manager_id)
        if manager.is_deleted:
            return Response({'error': 'Manager details have already been deleted'}, status=400)
    except Manager.DoesNotExist:
        return Response({'error': 'Manager Not Found'}, status=404)
    
    manager.soft_delete()
    manager.save()
    return Response({'message': 'Manager Deleted successfully'}, status=200)

@api_view(['GET'])
@permission_classes([IsAdmin])
def list_deleted_managers(request):
    managers = Manager.objects.filter(is_deleted=True).order_by('manager_id')
    if not managers.exists():
        return Response({'error': 'No Deleted Managers found'}, status=404)
    paginator = CustomPagination()
    paginated_managers = paginator.paginate_queryset(managers)
    serializer = ManagerSerializer(paginated_managers, many=True)
    return paginator.get_paginated_response({'message': 'Deleted managers retrieved successfully', 'data': serializer.data})

@api_view(['POST'])
@permission_classes([IsAdmin])
def restore_manager(request):
    data = request.data
    try:
        manager = Manager.objects.get(manager_id=data['manager_id'])
        if not manager.is_deleted:
            return Response({'error': 'Manager is not deleted yet!'})
    except Manager.DoesNotExist:
        return Response({'error': 'Manager Not Found'}, status=404)
    
    manager.restore()
    manager.save()
    serializer = ManagerSerializer(manager)
    return Response({'message': 'Manager restored successfully', 'data': serializer.data},status=200)


#--------------------------Laptop Request----------------------------#

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_laptop_request(request):
    data = request.data
    serializer = LaptopRequestSerializer(data=data)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response({'message' : 'Laptop Request created successfully', 'data' : serializer.data}, status=200)
        except IntegrityError:
            return Response({'error' : 'Request cannot be created'}, status=400)
    return Response({'error' : serializer.errors}, status=400)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_laptop_request(request,request_id):
    try:
        laptop_request = LaptopRequest.objects.get(request_id=request_id)
        if laptop_request.is_deleted:
            return Response({'error' : 'Laptop Request is already deleted'})
        if laptop_request.status != 'Pending':
            return Response({'error' : 'Only pending request can be updated'}, status=400)
    except LaptopRequest.DoesNotExist:
        return Response({'error' : 'Request not found'}, status=404)
    serializer = LaptopRequestSerializer(laptop_request, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response({'error' : serializer.error}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_laptop_request(request):
    try:
        if request.user.userprofile.role == 'Employee':
            requests = LaptopRequest.objects.filter(employee__user=request.user, is_deleted=False)
        elif request.user.userprofile.role == 'Manager':
            requests = LaptopRequest.objects.filter(manager__manager_id=request.user.userprofile.user.manager.manager_id)
        else:
            requests = LaptopRequest.objects.all()

        paginator = CustomPagination()
        paginated_requests = paginator.paginate_queryset(requests, request)
        serializer = LaptopRequestSerializer(paginated_requests, many=True)
        return paginator.get_paginated_response({'message' : 'Requests fetched successfully', 'data' : serializer.data})
    except Exception as e :
        return Response({'error' : str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_reject_laptop_request(request, request_id):
    try:
        laptop_request = LaptopRequest.objects.get(request_id=request_id)
        user_profile = request.user.userprofile

        if user_profile.role not in ['Admin', 'Manager']:
            return Response({'error' : 'You do not have permission to approve or reject this request'}, status=403)
        
        if user_profile.role == 'Manager' and laptop_request.manager != user_profile:
            return Response({'error' : 'You can only approve or reject requests from employees in your department.'}, status=403)
        
        action = request.data.get('action')
        if action not in ['approve', 'reject']:
            return Response({'error' : 'Invalid action'}, status=400)
        
        laptop_request.status = 'Approved' if action == 'approve' else 'Rejected'
        laptop_request.approved_by = user_profile
        laptop_request.approval_date = timezone.now()
        laptop_request.save()

        approval_history = ApprovalHistory(
            request = laptop_request,
            changed_by = request.user,  
            changes = {
                'status' : laptop_request.status,
                'comments' : laptop_request.comments,
                'reason' : laptop_request.reason
            }
        )
        approval_history.save()

        if laptop_request.status == 'Approved':
            laptop_inventory_item = LaptopInventory.objects.filter(is_available=True).first()
            if laptop_inventory_item:
                assignment = RequestAssignment(
                    request = laptop_request,
                    laptop = laptop_inventory_item,
                    condition = 'Good'
                )
                assignment.save()

                laptop_inventory_item.quantity -= 1
                laptop_inventory_item.save()

                return Response({'message' : 'Laptop request approved and assigned'}, status=200)
            else:
                return Response({'message' : 'Laptop request approved, but no available laptops'}, status=200)
        else :
            return Response({'message' : 'Laptop request rejected'}, status=200) 
    except LaptopRequest.DoesNotExist:
        return Response({'error': 'Laptop request not found.'}, status=404)
    except Exception as e:
        return Response({'error' : str(e)}, status=500)



@api_view(['DELETE'])
@permission_classes([IsAdmin])
def delete_laptop_request(request, request_id):
    try:
        requests = LaptopRequest.objects.get(request_id=request_id)
        if requests.is_deleted:
            return Response({'error' : 'Request is already deleted'})
    except LaptopRequest.DoesNotExist:
        return Response({'error' : 'Request Not Found'})  
    requests.soft_delete()
    requests.save()
    return Response({'message' : 'Request Deleted Successfully'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_laptop_request_stats(request):
    user_profile = request.user.userprofile

    laptop_requests = LaptopRequest.objects.filter(is_deleted=False)

    stats = {
        'total_requests': laptop_requests.count(),
        'approved_requests': laptop_requests.filter(status='Approved').count(),
        'rejected_requests': laptop_requests.filter(status='Rejected').count(),
        'pending_requests': laptop_requests.filter(status='Pending').count(),
        'cancelled_requests': laptop_requests.filter(status='Cancelled').count(),
    }

    if user_profile.role == 'Admin':
        return Response({'message': 'Laptop request statistics retrieved successfully', 'data': stats})
    
    elif user_profile.role == 'Manager':
        stats['manager_requests'] = laptop_requests.filter(manager=user_profile).count()
        return Response({'message': 'Laptop request statistics for manager retrieved successfully', 'data': stats})
    
    elif user_profile.role == 'Employee':
        stats['employee_requests'] = laptop_requests.filter(employee=user_profile).count()
        return Response({'message': 'Laptop request statistics for employee retrieved successfully', 'data': stats})

    return Response({'error': 'Unauthorized access'}, status=403)

#---------------------Approval History------------------#
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_approval_history(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.role == 'Manager':
        approvals = ApprovalHistory.objects.filter(request__manager__userprofile=user_profile)
    elif user_profile.role == 'Employee':
        approvals = ApprovalHistory.objects.filter(request__employee_userprofile=user_profile)   
    elif user_profile.role == 'Admin':
        approvals = ApprovalHistory.objects.all()
    else:
        return Response({'error' : 'Unauthorized Access'}, status=403)     
    serializer = ApprovalHistorySerializer(approvals, many=True)
    return Response({'message' : 'History fetched successfully', 'data' : serializer.data}, status=200)


#---------------------Laptop Inventory------------------#

@api_view(['POST'])
@permission_classes([IsAdmin])
def create_laptop_inventory(request):
    data = request.data
    serializer = LaptopInventorySerializer(data=data)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response({'message' : 'Laptop Added successfully', 'data' : serializer.data})
        except IntegrityError:
            return Response({'error' : 'Laptop inventory already exists'}, status=400)
    return Response({'error' : serializer.errors}, status=400)

@api_view(['GET'])
@permission_classes([IsAdmin])
def view_laptop_inventory(request):
    laptops = LaptopInventory.objects.filter(is_available = True).order_by('laptop_id')
    if not laptops.exists():
        return Response({'error' : 'No Laptop details found'})
    paginator = CustomPagination()
    paginated_laptops = paginator.paginate_queryset(laptops, request)
    serializer = LaptopInventorySerializer(paginated_laptops, many=True)
    return paginator.get_paginated_response({'message' : 'Laptop Details retrieved succesfully', 'data' : serializer.data})

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdmin])
def update_laptop_inventory(request, laptop_id):
    data = request.data
    try:
        laptop = LaptopInventory.objects.get(laptop_id=laptop_id)  
    except LaptopInventory.DoesNotExist:
        return Response({'error': 'Laptop not found.'}, status=404)
    
    if request.method == 'PUT':
        serializer = LaptopInventorySerializer(laptop, data=data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message' : 'Laptop Inventory Updated successfully','data' : serializer.data})
        return Response({'error' : serializer.errors}, status=400)
    
    elif request.method == 'PATCH':
        serializer = LaptopInventorySerializer(laptop, data=data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message' : 'Laptop Inventory Updated successfully','data' : serializer.data})
    return Response({'error' : serializer.errors}, status=400)

@api_view(['DELETE'])
@permission_classes([IsAdmin])
def delete_laptop_inventory(request, laptop_id):
    try:
        laptop = LaptopInventory.objects.get(laptop_id=laptop_id)
    except LaptopInventory.DoesNotExist:
        return Response({'error' : 'Laptop Not Found'}, status=404)
    laptop.soft_delete()
    laptop.save()
    return Response({'message' : 'Laptop Inventory details deleted successfully'})
    
    
#---------------------Searching--------------------#

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_laptop_requests(request):
    user_role = request.user.userprofile.role
    
    request_id = request.query_params.get('request_id')
    employee_email = request.query_params.get('employee_email')
    manager_email = request.query_params.get('manager_email')
    status = request.query_params.get('status')
    priority = request.query_params.get('priority')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    laptop_requests = LaptopRequest.objects.filter(is_deleted=False)

    if user_role == 'Admin':
        if request_id:
            laptop_requests = laptop_requests.filter(request_id=request_id)
        if employee_email:
            laptop_requests = laptop_requests.filter(employee__emp_email__icontains=employee_email)
        if manager_email:
            laptop_requests = laptop_requests.filter(manager__manager_email__icontains=manager_email)
        if status:
            laptop_requests = laptop_requests.filter(status=status)
        if priority:
            laptop_requests = laptop_requests.filter(priority=priority)

    elif user_role == 'Manager':
        laptop_requests = laptop_requests.filter(manager=request.user.userprofile)

        if request_id:
            laptop_requests = laptop_requests.filter(request_id=request_id)
        if status:
            laptop_requests = laptop_requests.filter(status=status)
        if priority:
            laptop_requests = laptop_requests.filter(priority=priority)

    elif user_role == 'Employee':
        laptop_requests = laptop_requests.filter(employee=request.user.employee)

        if request_id:
            laptop_requests = laptop_requests.filter(request_id=request_id)
        if status:
            laptop_requests = laptop_requests.filter(status=status)
        if priority:
            laptop_requests = laptop_requests.filter(priority=priority)

    if start_date and end_date:
        try:
            start_date_obj = timezone.datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = timezone.datetime.strptime(end_date, "%Y-%m-%d")
            laptop_requests = laptop_requests.filter(request_date__range=(start_date_obj, end_date_obj))
        except ValueError:
            return Response({'error': 'Invalid Date Format. Please use YYYY-MM-DD'}, status=400)

    if not laptop_requests.exists():
        return Response({'message': 'No laptop requests found matching the criteria'}, status=404)

    paginator = CustomPagination()
    paginated_requests = paginator.paginate_queryset(laptop_requests, request)
    serializer = LaptopRequestSerializer(paginated_requests, many=True)
    return paginator.get_paginated_response({'message': 'Laptop requests retrieved successfully', 'data': serializer.data})