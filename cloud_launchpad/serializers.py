from rest_framework import serializers
from cryptography.fernet import Fernet
import re
from .models import *

class UserDetailsSerializer(serializers.ModelSerializer):
    aws_access_key = serializers.CharField(max_length=100)
    aws_secret_key = serializers.CharField(max_length=100)
    server_type = serializers.ChoiceField(choices=["container", "server"])
    container_type = serializers.ChoiceField(choices=["docker", "kubernetes"])
    cluster_name = serializers.CharField(max_length=100)
    service_name = serializers.CharField(max_length=100)
    ecr_repo_name = serializers.CharField(max_length=100)
    region = serializers.CharField(max_length=100)
    github_token = serializers.CharField(max_length=100)
    repo_name = serializers.CharField(max_length=100)
    repo_owner_name = serializers.CharField(max_length=100)
    project_technology = serializers.CharField(max_length=100)
    technology_version = serializers.CharField(max_length=100)
    project_name = serializers.CharField(max_length=100)
    libraries = serializers.ListField(child=serializers.CharField(max_length=100))
    
    class Meta:
        model = UserDetails
        fields = '__all__'

    def validate_aws_access_key(self, value):
        # Validate AWS access key format
        if not re.match(r'^[A-Za-z0-9]+$', value):
            raise serializers.ValidationError("Invalid AWS access key format")
        return value


class UserMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMaster
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        # Validate Password format
        if not re.match(r'^[A-Za-z0-9]+$', value):
            raise serializers.ValidationError("Invalid Password format")
        return value 

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = UserMaster
        fields = ['email','password','user_id']

class CompanyMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyMaster
        fields = '__all__'

class ProjectMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMaster
        fields = '__all__'

class ProjectCredSerializer(serializers.ModelSerializer):
    """ Save Encrypted data into Project CRED Details table and read as Decrypted value"""
    
    project_id = serializers.IntegerField()  # Define project_id field explicitly

    class Meta:
        model = ProjectCredDetails
        fields = ['project_cred_id', 'aws_access_key', 'aws_secret_key', 'github_token', 'project_id']
        # read_only_fields = ['project_cred_id']
    def create(self, validated_data):
        project_id = validated_data.get('project_id')
        
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        encrypted_data = {
            'aws_access_key': cipher_suite.encrypt(validated_data['aws_access_key'].encode()).decode(),
            'aws_secret_key': cipher_suite.encrypt(validated_data['aws_secret_key'].encode()).decode(),
            'github_token': cipher_suite.encrypt(validated_data['github_token'].encode()).decode(),
            'project_id': project_id
        }
        
        return ProjectCredDetails.objects.create(**encrypted_data)

    def to_representation(self, instance):
        
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        decrypted_data = {
            'project_cred_id': instance.project_cred_id,
            'aws_access_key': cipher_suite.decrypt(instance.aws_access_key.encode()).decode(),
            'aws_secret_key': cipher_suite.decrypt(instance.aws_secret_key.encode()).decode(),
            'github_token': cipher_suite.decrypt(instance.github_token.encode()).decode(),
            'project': instance.project_id
        }
        print(decrypted_data)
        return decrypted_data



class MicroservicesSerializer(serializers.ModelSerializer):

    class Meta:
        model = MicroservicesDetails
        fields = '__all__'

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    user_id = serializers.IntegerField()
    new_password = serializers.CharField()