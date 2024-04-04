from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.contrib.auth.tokens import default_token_generator
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from scripts import launchpad_python
import json
from cryptography.fernet import Fernet
# from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.contrib.auth.backends import BaseBackend
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from datetime import datetime
from django.contrib.auth.hashers import check_password

class CustomAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            user = UserMaster.objects.get(email=email)
            if check_password(password, user.password):
                return user
        except UserMaster.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return UserMaster.objects.get(pk=user_id)
        except UserMaster.DoesNotExist:
            return None
        
# class LaunchpadView(APIView):
#     def post(self, request):
#         data = request.data
#         json_data = json.dumps(data)
#         serializer = InputSerializer(data=request.data)
    
#         if serializer.is_valid():
#             try:
#                 # Execute the script using subprocess.run() with arguments
                
#                 process = subprocess.Popen(['/usr/bin/python3', '/home/dell/launchpad_backend/launchpad/scripts/test_scrpit.py',json_data], 
#                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
#                  # Read output from the process
#                 output = ""
#                 for line in process.stdout:
#                     output += line
                
#                 # return Response({"output": output}, status=status.HTTP_200_OK)
#                 return Response({"message": "Input is valid","output":output}, status=status.HTTP_200_OK)
#             except Exception as e:
#                 print(e)
#                 return Response({"message": "Error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailsAPIView(APIView):
    """Api for create user details with validations."""
    serializer_class = UserDetailsSerializer
    
    def post(self, request):

        # validation will check in serializer
        serializer = self.serializer_class(data=request.data)

        # If serializer is valid then save the data 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #api for get userdetail list
    def get(self, request):
        data=request.data
        user_id = data.get('id',None)
        
        # if user is given then 
        if user_id:
            try:
                user_detail = UserDetails.objects.get(id=user_id)
                serializer = self.serializer_class(user_detail)
                return Response(serializer.data)
            except UserDetails.DoesNotExist:
                return Response({"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        else:
            user_details = UserDetails.objects.all()
            print(user_details)
            serializer = self.serializer_class(user_details, many=True)
            print(serializer.data)
        return Response(serializer.data)

class UserAPIView(APIView):
    """Api for create user details (It could be Super Admin, Company Admin or User)."""
    serializer_class = UserMasterSerializer

    def post(self, request):
        # validation will check in serializer
        serializer = self.serializer_class(data=request.data)

        # If serializer is valid then save the data 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #api for get userdetail list
    def get(self, request):
        data=request.data
        user_id = data.get('user_id',None)
        
        # if user is given then 
        if user_id:
            try:
                user_data = UserMaster.objects.get(user_id=user_id)
                serializer = self.serializer_class(user_data)
                return Response(serializer.data)
            except UserMaster.DoesNotExist:
                return Response({"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        else:
            user_details = UserMaster.objects.all()
            print(user_details)
            serializer = self.serializer_class(user_details, many=True)
            print(serializer.data)
        return Response(serializer.data)
    
    # API for delete user 
    def delete(self, request):
        data=request.data
        user_id = data.get('user_id')
        if user_id:
            try:
                user = UserMaster.objects.get(user_id=user_id)
                user.delete()
                return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            except UserMaster.DoesNotExist:
                return Response({"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "Please provide user_id to delete user"}, status=status.HTTP_400_BAD_REQUEST)

# class LoginAPIView(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         password = request.data.get('password')

#         user = CustomAuthBackend().authenticate(request, email=email, password=password)

#         if user is not None:
#             # User is authenticated, perform login tasks here
#             return Response({'user_id': user.user_id}, status=status.HTTP_200_OK)
#         else:
#             return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        

class LoginAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = UserMaster.objects.get(email=email)
            if user.check_password(password):
                return Response({'user_id': user.user_id}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        except UserMaster.DoesNotExist:
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

class CompanyAPIView(APIView):
    """Api for CRUD Company details by Super Admin"""

    serializer_class = CompanyMasterSerializer
    
    def post(self, request):
        # send data to serializer
        serializer = self.serializer_class(data=request.data)

        # If serializer is valid then save the data 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #api for get Companies list
    def get(self, request):
        data=request.data
        company_id = data.get('company_id',None)
        
        # if user is given then 
        if company_id:
            try:
                company_detail = CompanyMaster.objects.get(company_id=company_id)
                serializer = self.serializer_class(company_detail)
                return Response(serializer.data)
            except CompanyMaster.DoesNotExist:
                return Response({"message": "Company does not exist"}, status=status.HTTP_404_NOT_FOUND)
        else:
            company_details = CompanyMaster.objects.all()
            serializer = self.serializer_class(company_details, many=True)
            
        return Response(serializer.data)
    
    # API for delete Company 
    def delete(self, request):
        data=request.data
        company_id = data.get('company_id')
        if company_id:
            try:
                company = CompanyMaster.objects.get(company_id=company_id)
                company.delete()
                return Response({"message": "Company deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            except UserMaster.DoesNotExist:
                return Response({"message": "Company does not exist"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "Please provide company id to delete Company"}, status=status.HTTP_400_BAD_REQUEST)
    
    # API for update Company 
    def put(self, request):
        # Retrieve data from request
        company_id = request.data.get('company_id')
        
        # Retrieve existing company instance from database
        try:
            company_instance = CompanyMaster.objects.get(company_id=company_id)
        except CompanyMaster.DoesNotExist:
            return Response({"message": "Company does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the updated data
        serializer = self.serializer_class(company_instance, data=request.data)

        # If serializer is valid, save the updated data
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LaunchpadView(APIView):
    def post(self, request):
        data = request.data
        json_data = json.dumps(data)
        serializer = UserDetailsSerializer(data=request.data)
        print(type(data))
        print(type(json_data))
        if serializer.is_valid():
            #call script here.
            # Execute the script using subprocess.run() with arguments
            
            try:
                # result = subprocess.run(['python', '/home/dell/launchpad_backend/launchpad/scripts/launchpad_python.py', data], capture_output=True, text=True)
                result = launchpad_python.main(json_data)
                print("#########",result)
                #django code which read vs code terminal output and show that on ui

                return Response({"message": "Input is valid"}, status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
            # # Check result...
            # if result.returncode == 0:
            #     # Script executed successfully
            #     return Response({"output": result.stdout}, status=status.HTTP_200_OK)

            # If input is valid, return success message
            # return Response({"message": "Input is valid"}, status=status.HTTP_200_OK)
        
        else:
            # If input is invalid, return validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# Api for taking input from user and save into different tables.
class ProjectDetailsAPIView(APIView):

    def post(self, request):
        try:
            data = request.data
            # List of key names for project master
            pm_key_list = ['project_name', 'repo_owner_name', 'cluster_name', 'container_type','node_group_name']
            pm_cred_list = ['aws_access_key','aws_secret_key','github_token']
            microservices_list =['service_name','ecr_repo_name','repo_name','container_name','technology_type',
                                 'project_technology','technology_version','branch_name','container_port','host_port','default_service_name']
            # Create dictionary dynamically using dictionary comprehension
            project_master_data = {key: data.get(key) for key in pm_key_list}
            
            # save data into Project Master table.
            pm_serializer = ProjectMasterSerializer(data=project_master_data)
            if pm_serializer.is_valid():
                pm_serializer.save()
                
                # Prepare response
                pm_data = {key: pm_serializer.data[key] for key in pm_key_list if key in pm_serializer.data}

                # Fetch saved project id for save data in Project CRED Details and Microservices Details
                project_id = pm_serializer.data.get('project_id')
                
                if project_id:
                    #save detail from Project CRED detail against project id.
                    project_cred = {key: data.get(key) for key in pm_cred_list}
                    project_cred["project_id"] = project_id
                    
                    cred_serializer = ProjectCredSerializer(data=project_cred)
                    
                    if cred_serializer.is_valid():
                        # Save the serializer instance
                        cred_instance = cred_serializer.save()

                        # Retrieve the project_cred_id from the saved instance
                        project_cred_id = cred_instance.project_cred_id
                        print("project cred id:", project_cred_id)

                        # Fetch Microservices details
                        microservices_dict = data.get('microservices')
                        for service_dict in microservices_dict:
                            micrservices_data = {key: service_dict.get(key) for key in microservices_list}
                            # assign corresponding project reference
                            micrservices_data["project"] = project_id
 
                            micrservices_serializer = MicroservicesSerializer(data=micrservices_data)
                            if micrservices_serializer.is_valid():
                                # Save the serializer instance
                                service_instance = micrservices_serializer.save()

                                # Retrieve the project_MicroService from the saved instance
                                microservice_id = service_instance.pm_id
                                print("Microservice id:", microservice_id)
                                
                                # Prepare Dict to call launchpad script.
                                combined_dict = {**project_master_data, **project_cred,**micrservices_data}
                                keys_to_remove = ['project_id', 'project']
                                launchpad_dict = {key: value for key, value in combined_dict.items() if key not in keys_to_remove}

                                print(launchpad_dict)
                            else:
                                return Response(micrservices_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response(cred_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    result = {'project_master_data': pm_data}
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                return Response(pm_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    #api for get userdetail list
    def get(self, request):
        
        try:
            
            data=request.data
            project_id = data.get('project_id',None)

            remove_keys =['is_active','created_by_id','updated_by_id','created_on','updated_on','is_deleted']
            
            # if user is given then 
            if project_id:
                
                # Retrieve data from three tables using Django's ORM
                projects = ProjectMaster.objects.filter(project_id=project_id)
                project_credentials = ProjectCredDetails.objects.filter(project_id=project_id)
                microservices = MicroservicesDetails.objects.filter(project_id=project_id)

                # Convert queryset to dictionaries
                project_data = [self.remove_common_keys(project, remove_keys) for project in projects.values()]
                cred_data = [self.remove_common_keys(cred, remove_keys) for cred in project_credentials.values()]
                microservices_data = [self.remove_common_keys(microservice,remove_keys) for microservice in microservices.values()]
                
                # Construct response data
                response_data = {
                    'projects': project_data,
                    'project_credentials': cred_data,
                    'microservices': microservices_data
                }
                
                return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def remove_common_keys(self, dictionary, keys_to_remove):
        return {key: value for key, value in dictionary.items() if key not in keys_to_remove}


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        # data=request.data
        # email = data.get('email',None)
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = UserMaster.objects.filter(email=email).first()
            print("u s e r :",user)
            if user:
                # token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                reset_url = f"http://example.com/reset-password/{uid}/"
                subject = 'Password Reset'
                message = render_to_string('reset_password_email.html', {
                    'user': user,
                    'reset_url': reset_url
                })
                send_mail(subject, message, 'kena.patel@techifysolutions.com', [email])
            return Response({'message': 'Password reset link sent'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            
            email = serializer.validated_data['email']
            user_id = serializer.validated_data['user_id']
            new_password = serializer.validated_data['new_password']
            user = UserMaster.objects.filter(email=email).first()
            
            if user:
                # Assuming `updated_by_user_id` contains the ID of the user who is performing the update
                updated_by_user = UserMaster.objects.filter(pk=user_id).first()
                user.updated_on=datetime.now()
                user.updated_by = updated_by_user
                user.set_password(new_password)
                user.save()

                return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


