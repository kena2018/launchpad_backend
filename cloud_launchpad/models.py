
# Create your models here.
from django.db import models
import uuid
from django.contrib.auth.hashers import make_password,check_password


class KeyFiels(models.Model):
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('UserMaster', on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created_by')
    updated_by = models.ForeignKey('UserMaster', on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_updated_by')
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        abstract = True
        
class UserDetails(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    aws_access_key = models.CharField(max_length=50)
    aws_secret_key = models.CharField(max_length=100)
    server_type = models.CharField(max_length = 20)
    container_type = models.CharField(max_length = 20)
    cluster_name = models.CharField(max_length = 50)
    node_group_name = models.CharField(max_length = 50)
    container_name = models.CharField(max_length = 50)
    service_name = models.CharField(max_length = 50) 
    ecr_repo_name = models.CharField(max_length = 50) 
    region = models.CharField(max_length = 50)
    github_token= models.CharField(max_length = 100)
    repo_name= models.CharField(max_length = 50)
    repo_owner_name= models.CharField(max_length = 50)
    project_technology= models.CharField(max_length = 20)
    technology_version= models.CharField(max_length = 20)
    project_name = models.CharField(max_length = 20)
    libraries = models.CharField(max_length = 500)
    
    class Meta:
        db_table = 'user_details'
        app_label = 'cloud_launchpad'

class UserMaster(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=False,unique=True)
    password = models.CharField(max_length=128)  # Length increased for hashed passwords
    is_super_admin = models.BooleanField(null=True, blank=True)
    is_company_admin = models.BooleanField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('UserMaster', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_by_user')
    updated_by = models.ForeignKey('UserMaster', on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_by_user')
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    company_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'user_master'
        app_label = 'cloud_launchpad'
    
    def __str__(self):
        return self.email
    
    def set_password(self, raw_password):
        print("1")
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        print("2")
        return check_password(raw_password, self.password)
    
    # def set_password(self, raw_password):
    #     self.password = raw_password #make_password(raw_password)
    #     self.save(update_fields=['password'])
    
class Role(KeyFiels):
    role_id = models.AutoField(primary_key=True)
    rolename = models.CharField(max_length=100)

    class Meta:
        db_table = 'role'

class UserRole(models.Model):
    user_role_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserMaster, on_delete=models.DO_NOTHING)
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'user_role'

class UserLoginHistory(models.Model):
    """ This model for user login history """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(UserMaster, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=200)
    browser = models.CharField(max_length=200)
    login_date_time = models.DateTimeField(max_length=200)
    device = models.CharField(max_length=200,blank = True,null = True)
    
    class Meta:
        db_table = 'user_login_history'

    def __int__(self):
        return self.user

class CompanyMaster(KeyFiels):
    """ This model for create company"""

    company_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=100,blank=False)
    
    class Meta:
        db_table = 'company_master'

class CompanyAdminDetail(models.Model):
    """ This model for company admin detail"""
    company_admin_detail_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserMaster, on_delete=models.DO_NOTHING)
    company = models.ForeignKey(CompanyMaster, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'company_admin_detail'
    
class ProjectMaster(KeyFiels):
    """ This model for creating Project """
    
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=100,blank=False)
    repo_owner_name = models.CharField(max_length=100)
    cluster_name = models.CharField(max_length = 100)
    container_type = models.CharField(max_length = 100)
    node_group_name = models.CharField(max_length = 100)
    
    class Meta:
        db_table = 'project_master'

class ProjectCredDetails(models.Model):
    """ This model for Project Details """

    project_cred_id = models.AutoField(primary_key=True)
    aws_access_key = models.CharField(max_length=200)
    aws_secret_key = models.CharField(max_length=200)
    github_token = models.CharField(max_length= 256)
    project = models.ForeignKey(ProjectMaster, on_delete=models.DO_NOTHING)
    
    class Meta:
        db_table = 'project_cred_details'

class MicroservicesDetails(KeyFiels):
    """ This model for Project Microservices Details """
    pm_id = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=100,blank = True,null = True)
    ecr_repo_name = models.CharField(max_length=100,blank = True,null = True)
    repo_name = models.CharField(max_length =100,blank = True,null = True)
    container_name = models.CharField(max_length= 100,blank = True,null = True)
    project_technology = models.CharField(max_length= 100,blank = True,null = True)
    technology_version = models.CharField(max_length= 100,blank = True,null = True)
    branch_name = models.CharField(max_length= 100,blank = True,null = True)
    technology_type = models.CharField(max_length= 100,blank = True,null = True)
    container_port = models.CharField(max_length= 100,blank = True,null = True)
    host_port= models.CharField(max_length= 100,blank = True,null = True)
    default_service_name = models.CharField(max_length= 100,blank = True,null = True)
    project = models.ForeignKey(ProjectMaster, on_delete=models.DO_NOTHING)
    
    class Meta:
        db_table = 'microservices_details'