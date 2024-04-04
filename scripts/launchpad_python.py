import json
import sys
import modules
import subprocess
import os
import base64
import requests
import time
import boto3

def validate_aws_credentials(access_key, secret_access_key, region):
    try:
        # Create an STS client
        sts_client = boto3.client('sts', region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_access_key)

        # Make a request to the get-caller-identity operation
        identity_response = sts_client.get_caller_identity()
        account_id = identity_response['Account']
        return True, account_id

    except Exception as e:
        # If there is an exception, the credentials are invalid
        return False, None

def check_github_credentials(token):
    # print("CLOUD --> VALIDATING GITHUB CREDENTIALS")
    url = "https://api.github.com/user"
    response = requests.get(url, headers={"Authorization": f"token {token}"})
    return response

def generate_dockerfile_based_on_tech(choice, project_name, technology_version):
    print(f"Cloud_Launchpad --> Generating Dockerfile...")
    sys.stdout.flush()
    valid_choices = ['python', 'node']

    while choice.lower() not in valid_choices:
        print("Invalid choice. Please choose either 'python' or 'node'")
        sys.stdout.flush()
        # choice = input("Enter your project technology (python or node): ")

    if not project_name:
        print("Project name cannot be empty. Please provide a valid project name.")
        sys.stdout.flush()
        return None, None

    # Clean up the project name to create a valid Dockerfile path
    clean_project_name = project_name.replace(" ", "_").lower()

    # Create a folder for the technology (if it doesn't exist)
    tech_folder_path = f"./{choice.lower()}"
    os.makedirs(tech_folder_path, exist_ok=True)

    # Define Dockerfile path inside the technology folder
    dockerfile_path = f"{tech_folder_path}/Dockerfile"

    python_version = ""
    database_type = ""
    dockerfile_content = ""

    if choice.lower() == 'python':
        while True:
            # python_version = input("Enter the desired Python version (e.g., 3.8): ")
            if technology_version.strip():
                break
            else:
                print("Please provide a valid Python version.")
          
        while True:
            database_type = input("Enter the database type (e.g., postgres, mysql): ").lower()
            if database_type in ['postgres', 'mysql']:
                break
            else:
                print("Please provide a valid database type (postgres or mysql).")

        dockerfile_content = f"""
# Base image
FROM python:{technology_version}-slim

# Set the working directory to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
ADD requirements.txt /app/requirements.txt
RUN pip{technology_version} install --no-cache-dir -r requirements.txt

# Expose ports based on the database type
{"EXPOSE 5432" if database_type == 'postgres' else ""}
{"EXPOSE 3306" if database_type == 'mysql' else ""}

# Default port for the application
EXPOSE 8000

# Define environment variable
ENV NAME {clean_project_name}

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
"""
    elif choice.lower() == 'node':
        # node_version = input("Enter Node.js version (e.g., 14): ")
        #entry_point = input("Enter the command to start (e.g., npm start app.js): ")
        #expose_ports = input("Enter additional ports to expose (comma-separated, e.g., 3000,8080): ")

        dockerfile_content = f"""

# Use an official Node.js {technology_version} image as the base image
FROM node:{technology_version} as build

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install project dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the React app
RUN npm run build

# Use a smaller image for production
FROM nginx:alpine

# Copy the built app from the previous stage
COPY --from=build /usr/src/app/build /usr/share/nginx/html

# Expose port 80 for the Nginx server
EXPOSE 80

# Command to start Nginx
CMD ["nginx", "-g", "daemon off;"]
"""
    
    with open(dockerfile_path, "w") as dockerfile:
        dockerfile.write(dockerfile_content)

    print(f"Cloud_Launchpad --> Dockerfile has been generated successfully for {project_name} at {dockerfile_path}.")
    sys.stdout.flush()

    return dockerfile_content, dockerfile_path

def generate_manifestfile_eks(project_technology, project_name, account_id, region, ecr_repo_name):
    time.sleep(1)
    print(f"Cloud_Launchpad --> Generating Manifest file...")
    sys.stdout.flush()

    valid_choices = ['python', 'node']
    
    # Clean up the project name to create a valid manifestfile path
    clean_project_name = project_name.replace(" ", "_").lower()

    # Create a folder for the technology (if it doesn't exist)
    tech_folder_path = f"./{project_technology.lower()}"
    os.makedirs(tech_folder_path, exist_ok=True)

    # Define manifestfile path inside the technology folder
    manifestfile_path = f"{tech_folder_path}/manifest.yaml"

    
    manifestfile_content = ""

    manifestfile_content = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {clean_project_name}
spec:
  replicas: 2         
  selector:
    matchLabels:
      app: {clean_project_name}
  template:
    metadata:
      labels:
        app: {clean_project_name}
    spec:
      containers:
      - name: react-container
        image: {account_id}.dkr.ecr.{region}.amazonaws.com/{ecr_repo_name}:latest
        ports:
        - containerPort: 80

---
apiVersion: v1
kind: Service
metadata:
  name: react-service
spec:
  selector:
    app: {clean_project_name}
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: LoadBalancer

"""
    
    with open(manifestfile_path, "w") as manifestfile:
        manifestfile.write(manifestfile_content)

    print(f"Cloud_Launchpad --> Manifestfile has been generated successfully for {project_name} at {manifestfile_path}.")
    sys.stdout.flush()

    return manifestfile_content, manifestfile_path

def create_github_repo_file(token, repo_owner, repo_name, file_path, file_content, commit_message):
    time.sleep(1)
    print("Cloud_Launchpad --> Uploading Dockerfile to Github...")
    sys.stdout.flush()
    sha = get_file_sha(token, repo_owner, repo_name, file_path)
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
    }
    encoded_content = base64.b64encode(file_content.encode()).decode()
    payload = {
        "message": commit_message,
        "content": encoded_content,
        "sha": sha,
    }

    response = requests.put(url, headers=headers, json=payload)

    return response

def get_file_sha(token, repo_owner, repo_name, file_path):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()["sha"]
    else:
        return None

def create_ec2_resources(instance_size, config_params):
    try:
        # Convert the JSON string to a dictionary
        config_params_dict = config_params
        # Terraform code to create VPC and EC2 resources
        terraform_code = f"""
    
        module "EC2" {{
        source                 = "./modules/EC2"
        ami                    = "ami-079db87dc4c10ac91"
        instance_type          = "{instance_size}"
        key_name               = "{config_params_dict.get('key_name')}"
        subnet_id              = "{config_params_dict.get('subnet_id')}"
        instance_name          = "{config_params_dict.get('instance_name')}"
        region                 = "{config_params_dict.get('region')}"
        }}
        """

    # Save the Terraform code to a file
        with open("ec2_resources.tf", "w") as file:
            file.write(terraform_code)

    # Execute Terraform commands to apply the configuration
        execute_terraform_commands("ec2_resources.tf")
      # Code for EC2 resource creation
    except Exception as e:
        # Handle specific errors related to EC2 resource creation
        print(f"Error creating EC2 resources: {e}")

# def write_terraform_file(terraform_code):
#     # Determine a unique filename
#     counter = 1
#     while True:
#         filename = f"terraform_config_{counter}.tf"
#         if not os.path.exists(filename):
#             break
#         counter += 1

#     # Save the Terraform code to the new file
#     with open(filename, "w") as file:
#         file.write(terraform_code);
    
#     return filename

def create_ecs_resources(cluster_name, service_name, ecr_repo_name, region, aws_access_key, aws_secret_key):
    try:
        # Terraform code to create ECS resources
        terraform_code = f"""
        terraform {{
          backend "local" {{
            path = "ecs.tfstate"
          }}
        }}

        module "ECR_ECS" {{
          source = "./modules/ECR_ECS"
          ecr_repository_name = "{ecr_repo_name}"
          access_key = "{aws_access_key}"
          secret_key = "{aws_secret_key}"
        }}

        output "ecr_repository_name" {{
          value = module.ECR_ECS.ecr_repository_name
        }}

        module "ecs_cluster" {{
          source = "./modules/ECS"
          cluster_name = "{cluster_name}"
          service_name = "{service_name}"
          desired_count = "1"
          container_image = "${{module.ECR_ECS.ecs_repository_url}}:latest"
          container_port = 80
          host_port = 80
          container_name = "my-container"
          task_family = "infra"
          region = "{region}"
          access_key = "{aws_access_key}"
          secret_key = "{aws_secret_key}"
        }}

        output "ecs_task_definition_arn" {{
          value = module.ecs_cluster.ecs_task_definition_arn
        }}

        output "ecs_cluster_name" {{
          value = module.ecs_cluster.ecs_cluster_name
        }}

        output "ecs_service_name" {{
          value = module.ecs_cluster.ecs_service_name
        }}

        provider "aws" {{
          region = "{region}"
        }}
        """
# # Write the Terraform code to a new file
#         # filename = write_terraform_file(terraform_code)

#         # Execute Terraform commands to apply the configuration
#         # execute_terraform_commands(filename)
#         print("Cloud_Launchpad --> Infrastructure successfully created")
#         sys.stdout.flush()
#         time.sleep(1)
#         print("Cloud_Launchpad --> Triggering Jenkins... Please Wait...")
#         sys.stdout.flush()
#         time.sleep(10)
#         execute_jenkins(ecr_repo_name)

#     except Exception as e:
#         # Handle specific errors related to ECS resource creation
#         print(f"Cloud_Launchpad_Error --> {str(e)}", file=sys.stderr)
#         sys.stdout.flush()
#         sys.exit(1)


        # Save the Terraform code to a file
        with open("ecs_resources.tf", "w") as file:
            file.write(terraform_code)

        # Execute Terraform commands to apply the configuration
        execute_terraform_commands("ecs_resources.tf")
        print("Cloud_Launchpad --> Infrastructure successfully created")
        sys.stdout.flush()
        time.sleep(1)
        print("Cloud_Launchpad --> Triggering Jenkins... Please Wait...")
        sys.stdout.flush()
        time.sleep(10)
        execute_jenkins(ecr_repo_name)

    except Exception as e:
        # Handle specific errors related to ECS resource creation
        print(f"Cloud_Launchpad_Error --> {str(e)}", file=sys.stderr)
        sys.stdout.flush()
        sys.exit(1)


def create_eks_resources(ecr_repo_name, aws_access_key, aws_secret_key, region, cluster_name, node_group_name):
    try:
        # Terraform code to create EKS resources
        terraform_code = f"""
       
        module "ECR_EKS" {{
          source = "./modules/ECR_EKS"
          ecr_repository_name = "{ecr_repo_name}"
          access_key = "{aws_access_key}"
          secret_key = "{aws_secret_key}"
        }}

        module "eks_cluster" {{
          source = "./modules/EKS"
          cluster_name = "{cluster_name}"
          node_group_name = "{node_group_name}"
          region = "{region}"
          access_key = "{aws_access_key}"
          secret_key = "{aws_secret_key}"
        }}
        """

        # Save the Terraform code to a file
        with open("main.tf", "w") as file:
            file.write(terraform_code)

        # Execute Terraform commands to apply the configuration
        execute_terraform_commands("main.tf")
        print("Cloud_Launchpad --> Infrastructure successfully created")
        sys.stdout.flush()
        time.sleep(1)
        print("Cloud_Launchpad --> Triggering Jenkins... Please Wait...")
        sys.stdout.flush()
        time.sleep(10)
        execute_jenkins(ecr_repo_name)

    except Exception as e:
        # Handle specific errors related to EKS resource creation
        print(f"Cloud_Launchpad_Error --> {str(e)}", file=sys.stderr)
        sys.stdout.flush()
        sys.exit(1)


# def create_ecs_resources(cluster_name, service_name, ecr_repo_name, region, aws_access_key, aws_secret_key):
#     try:
#     # Terraform code to create ECS resources
#         terraform_code = f"""
#         terraform {{
#         backend "local" {{
#         path = "ecs.tfstate"
#        }}
#        }}
       
#        module "ECR"{{
#         source          = "./modules/ECR_ECS"
#         ecr_repository_name = "{ecr_repo_name}"
#         access_key = "{aws_access_key}"
#         secret_key = "{aws_secret_key}"

#        }}  
       
#        output "ecr_repository_name" {{
#        value = module.ECR_ECS.ecr_repository_name
#        }}

#         module "ecs_cluster"{{
#         source = "./modules/ECS"
#         cluster_name = "{cluster_name}"
#         service_name = "{service_name}"
#         desired_count = "1"                     #Set the Count
#        container_image = "${{module.ECR.ecs_repository_url}}:latest"
        
#         container_port = 80
#         host_port = 80
#         container_name = "my-container"             #Can be made as variable
#         region = "{region}"
#         task_family = "infra"
#         access_key = "{aws_access_key}"
#         secret_key = "{aws_secret_key}"
        
#        }}
#                                                                         #Need to make output in json
#        output "ecs_task_definition_arn" {{
#       value = module.ecs_cluster.ecs_task_definition_arn
  
#        }}
       
#       output "ecs_cluster_name" {{
#       value = module.ecs_cluster.ecs_cluster_name
#       }}

#       output "ecs_service_name" {{
#       value = module.ecs_cluster.ecs_service_name
#        }}
#       provider "aws" {{
#       region = "us-east-1"
#       }}
#         """

#         # Save the Terraform code to a file
#         with open("ecs_resources.tf", "w") as file:
#             file.write(terraform_code)

#        # Execute Terraform commands to apply the configuration
#         execute_terraform_commands("ecs_resources.tf")
#         print("Cloud_Launchpad --> Infrastructure successfully created")
#         sys.stdout.flush()
#         time.sleep(1)
#         print("Cloud_Launchpad --> Triggering Jenkins... Please Wait...")
#         sys.stdout.flush()
#         time.sleep(10)
#         execute_jenkins(ecr_repo_name)

#        # Code for ECS resource creation
#     except Exception as e:
#          # Handle specific errors related to EC2 resource creation
#         print(f"Cloud_Launchpad_Error --> {str(e)}", file=sys.stderr)
#         sys.stdout.flush()
#         sys.exit(1)


# def create_eks_resources(ecr_repo_name, aws_access_key, aws_secret_key, region, cluster_name, node_group_name):
#     try:
#     # Terraform code to create EKS resources
#         # Inside terraform_code
#     #    output "ecr_repository_name" {{
#     #    value = module.ECR_EKS.ecr_repository_name
#     #    }}
#         terraform_code = f"""
#         terraform {{
#         backend "local" {{
#         path = "eks.tfstate"
#        }}
#        }}
       
#        module "ECR"{{
#         source          = "./modules/ECR_EKS"
#         ecr_repository_name = "{ecr_repo_name}"
#         access_key = "{aws_access_key}"
#         secret_key = "{aws_secret_key}"

#        }}  
       
  

#         module "eks_cluster"{{
#         source = "./modules/EKS"
#         cluster_name = "{cluster_name}"
#         node_group_name = "{node_group_name}"
        
        
#         region = "{region}"
#         access_key = "{aws_access_key}"
#         secret_key = "{aws_secret_key}"
        
#        }}
#         """

#         # Save the Terraform code to a file
#         with open("eks_resources.tf", "w") as file:
#             file.write(terraform_code)

#        # Execute Terraform commands to apply the configuration
#         execute_terraform_commands("eks_resources.tf")
#         print("Cloud_Launchpad --> Infrastructure successfully created")
#         sys.stdout.flush()
#         time.sleep(1)
#         print("Cloud_Launchpad --> Triggering Jenkins... Please Wait...")
#         sys.stdout.flush()
#         time.sleep(10)
#         execute_jenkins(ecr_repo_name)

#        # Code for EKS resource creation
#     except Exception as e:
#          # Handle specific errors related to EKS resource creation
#         print(f"Cloud_Launchpad_Error --> {str(e)}", file=sys.stderr)
#         sys.stdout.flush()
#         sys.exit(1)

# def execute_terraform_commands(terraform_file):
#     try:
#         print("Cloud_Launchpad --> Creating Infrastructure... Please Wait...")
#         sys.stdout.flush()
#         # Run Terraform commands
#         init_result = subprocess.run(["tofu", "init", "-reconfigure"], check=True)
#         plan_result = subprocess.run(["tofu", "plan", "-out", f"{terraform_file}.plan"], check=True)
#         with open(f"{terraform_file}.txt", "w") as tfplan_file:
#             show_result = subprocess.run(["tofu", "show", f"{terraform_file}.plan"], stdout=tfplan_file, check=True)
      
#        # show_command = ["tofu", "show", Manan998"-json", terraform_file]
#             # Run Tofu apply using the plan file and specify the state file
#         apply_result = subprocess.run(["tofu", "apply","-auto-approve", f"{terraform_file}.plan"], check=True)
    
#     except subprocess.CalledProcessError as e:
#         print(f"Cloud_Launchpad_Error --> Error executing OpenTofu commands: {str(e)}, Destroying infrastructure", file=sys.stderr)
#         sys.stdout.flush()
#         destroy_result = subprocess.run(["tofu", "destroy", "-auto-approve"], check=True)
#         raise RuntimeError("Infrastructure destroyed")
        
def execute_terraform_commands(terraform_file):
    try:
        print("Cloud_Launchpad --> Creating Infrastructure... Please Wait...")
        sys.stdout.flush()

        # Check and create .terraform directory if it doesn't exist
        if not os.path.exists('.terraform'):
            os.makedirs('.terraform')

        # Check and create plan file if it doesn't exist
        plan_file_path = f"{terraform_file}.plan"
        if not os.path.exists(plan_file_path):
            with open(plan_file_path, "w") as plan_file:
                plan_file.write("")

        # Run Terraform initialization if not initialized
        if not os.path.exists('.terraform'):
            # init_result = subprocess.check_call(['tofu', 'init'], cwd='./modules/EKS')
             init_result = subprocess.run(["tofu", "init"], check=True)
        else:
            # Run Terraform reconfigure
            # init_result = subprocess.check_call(['tofu', 'init'], cwd='./modules/EKS')
             init_result = subprocess.run(["tofu", "init", "-reconfigure"], check=True)

        # Run Terraform plan
            # plan_result =subprocess.check_call(['tofu', 'plan', '-out', plan_file_path], cwd='./modules/EKS')
        plan_result = subprocess.run(["tofu", "plan", "-out", plan_file_path], check=True)
        
        # Save plan to a file
        with open(f"{terraform_file}.txt", "w") as tfplan_file:
            show_result = subprocess.run(["tofu", "show", plan_file_path], stdout=tfplan_file, check=True)
      
        # Run Terraform apply using the plan file and specify the state file
        apply_result = subprocess.run(["tofu", "apply","--auto-approve", plan_file_path], check=True)
    
    except subprocess.CalledProcessError as e:
        print(f"Cloud_Launchpad_Error --> Error executing OpenTofu commands: {str(e)}, Destroying infrastructure", file=sys.stderr)
        sys.stdout.flush()
        destroy_result = subprocess.run(["tofu", "destroy", "-auto-approve"], check=True)
        raise RuntimeError("Infrastructure destroyed")


def execute_jenkins(ecr_repo_name):
    try:
        # config_params_dict = config_params
        jenkins_command = f"java -jar jenkins-cli.jar -s http://localhost:8080/ build temp -p ecr={ecr_repo_name}"
        subprocess.run(jenkins_command, shell=True, check=True)
        print("Cloud_Launchpad --> Jenkins has now been successfully triggered, Please check ECR and ECS...")
        sys.stdout.flush()
        time.sleep(2)
        print("Cloud_Launchpad --> Process completed!")
        sys.stdout.flush()
    except subprocess.CalledProcessError as e:
        raise("Error triggering Jenkins")
        # print(f"Cloud_Launchpad_Error --> Error triggering Jenkins: {str(e)}", file=sys.stderr)
        # sys.stdout.flush()
        # sys.exit(1)

def main(args):
    try:         
        # time.sleep(10)
        # Read json string from stdin
        # fields_json = sys.stdin.read()
        # parse json string to a python project
        # fields = json.loads(fields_json)
        # print(f"FIELDS----: {fields}")
        
        data = json.loads(args)
        aws_access_key = data['aws_access_key']
        aws_secret_key = data['aws_secret_key']
        server_type = data['server_type']
        container_type = data['container_type']
        cluster_name = data['cluster_name']
        node_group_name = data['node_group_name']
        container_name = data['container_name']
        service_name = data['service_name']
        ecr_repo_name = data['ecr_repo_name']
        region = data['region']
        github_token = data['github_token']
        repo_name = data['repo_name']
        repo_owner_name = data['repo_owner_name']
        project_technology = data['project_technology']
        technology_version = data['technology_version']
        project_name = data['project_name']
        
        # aws_access_key = input("Enter your AWS access key: ")
        # aws_secret_key = input("Enter your AWS secret key: ") 
        # server_type = input("Enter server type: ") 
        # container_type = input("Enter container type: ") 
        # cluster_name = input("Enter cluster name: ") 
        # node_group_name = input("Enter node group name: ") 
        # container_name = input("Enter container name: ") 
        # service_name = input("Enter service name: ") 
        # ecr_repo_name = input("Enter ECR repository name: ") 
        # region = input("Enter AWS region: ") 
        # github_token = input("Enter GitHub token: ")
        # repo_name = input("Enter repository name: ") 
        # repo_owner_name = input("Enter repository owner name: ") 
        # project_technology = input("Enter project technology: ") 
        # technology_version = input("Enter technology version: ") 
        # project_name = input("Enter project name: ") 

        
        # To validate AWS Credentials
        print("Cloud_Launchpad --> Validating AWS Credentials...")
        sys.stdout.flush()
        validation_result, account_id = validate_aws_credentials(aws_access_key, aws_secret_key, region)
        if validation_result:
            print("Cloud_Launchpad --> AWS Credentials are valid")
            sys.stdout.flush()
        else: 
            raise RuntimeError("Invalid AWS credentials")    


        # Configure AWS credentials
        os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key
        os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_key
    
        # Check server type and call corresponding function
        if server_type == "ec2":
            instance_size = input("Enter EC2 instance type: ")
            config_params =  {
                "key_name": input("Enter key name: "),
                "instance_name": input("Enter instance name: "),
                "region": input("Enter region: ")
            }
        
        elif server_type == "container":
            response = check_github_credentials(github_token)

            if response.status_code == 200:
                dockerfile_content, dockerfile_path = generate_dockerfile_based_on_tech(project_technology, project_name, technology_version)

                if dockerfile_content is not None and dockerfile_path is not None:
                    # Upload the generated Dockerfile to GitHub
                    commit_message = "Update Dockerfile"
                    dockerfile_relative_path = os.path.relpath(dockerfile_path, ".")

                    upload_response = create_github_repo_file(
                        github_token, repo_owner_name, repo_name, dockerfile_relative_path, dockerfile_content, commit_message
                    )

                    if upload_response.status_code == 200 or upload_response.status_code == 201:
                        print("Cloud_Launchpad --> Dockerfile uploaded to GitHub successfully!")
                        sys.stdout.flush()
                    else:
                        raise RuntimeError(f"Failed to upload Dockerfile to GitHub. STATUS_CODE:{upload_response.status_code} STATUS_TEXT:{upload_response.text}")
            
                if container_type == 'docker':
                    print("Cloud_Launchpad --> docker part commented temporarily")
                    # create_ecs_resources(cluster_name, service_name, ecr_repo_name, region, aws_access_key, aws_secret_key)
                elif container_type == "kubernetes":
                    if response.status_code == 200:
                        manifestfile_content, manifestfile_path = generate_manifestfile_eks(project_technology, project_name, account_id, region, ecr_repo_name)
                        if manifestfile_content is not None and manifestfile_path is not None:
                            commit_message = "Update Manifestfile"
                            manifestfile_relative_path = os.path.relpath(manifestfile_path, ".")
                            upload_response = create_github_repo_file(
                                github_token, repo_owner_name, repo_name, manifestfile_relative_path, manifestfile_content, commit_message
                            )

                            if upload_response.status_code == 200 or upload_response.status_code ==201:
                                print("Cloud_Launchpad --> Manifestfile uploaded to GitHub successfully!")
                                sys.stdout.flush()
                            else:
                                raise RuntimeError(f"Failed to upload Manifestfile to GitHub. STATUS_CODE:{upload_response.status_code} STATUS_TEXT:{upload_response.text}")
                    time.sleep(2)
                    # create_eks_resources(ecr_repo_name, aws_access_key, aws_secret_key, region, cluster_name, node_group_name)
        else:
            pass
        return "success"
    except Exception as e:
        print(f"Cloud_Launchpad_Error --> {str(e)}", file=sys.stderr)
        sys.stdout.flush()
        sys.exit(1)


if __name__ == "__main__":
    main()