import os
import subprocess
import json
import shutil
import time
import logging


def get_user_input():
    app_name = input("Enter the app name: ")
    language = input("Enter the code language [python/bash/JS]: ")
    ports = input("Enter ports to open (Please do not use 3000 or 9090 for Grafana and Prometheus): ").split(',')
    base_image_url = input("Enter base image URL: ")
    metrics_to_collect = input("Enter metrics to collect for Prometheus (comma-separated): ").split(',')

    return app_name, language, ports, base_image_url, metrics_to_collect


def generate_repository(app_name):
    os.makedirs(app_name, exist_ok=True)
    readme_path = os.path.join(app_name, "README.md")
    open(readme_path, "w").close()

    gitignore_path = os.path.join(app_name, ".gitignore")
    with open(gitignore_path, "w") as gitignore_file:
        gitignore_file.write("__pycache__/\n*.pyc\n*.pyo\n*.pyd\nkubernetes_manifests/\n")

    app_file_path = app_name + ".py"
    if os.path.exists(app_file_path):
        shutil.copy(app_file_path, os.path.join(app_name, app_file_path))

    requirements_path = "requirements.txt"
    if os.path.exists(requirements_path):
        shutil.copy(requirements_path, os.path.join(app_name, "requirements.txt"))


def generate_dockerfile(app_name, ports, base_image_url):
    dockerfile_content = f'''
FROM {base_image_url}
WORKDIR /app

COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . /app

EXPOSE {ports}  
CMD ["python", "{app_name}.py"]
'''

    with open(os.path.join(app_name, 'Dockerfile'), 'w') as dockerfile:
        dockerfile.write(dockerfile_content)


def generate_prometheus_config(app_name, metrics_to_collect):
    prometheus_config_content = f'''
apiVersion: v1
kind: ConfigMap
metadata:
  name: {app_name}-prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
      - job_name: '{app_name}'
        static_configs:
          - targets: ['localhost:5000']  
        metrics_path: /metrics
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_app]
            separator: ;
            regex: (.+)
            target_label: job
            replacement: $1
        metric_relabel_configs:
          - source_labels: [__name__]
            regex: '({"|".join(metrics_to_collect)})'
'''

    prometheus_config_path = os.path.join(app_name, 'prometheus.yml')

    with open(prometheus_config_path, 'w') as prometheus_config:
        prometheus_config.write(prometheus_config_content)

    logging.info(f"Prometheus configuration written to: {prometheus_config_path}")


def deploy_prometheus(app_name):
    try:
        result = subprocess.run(['kubectl', 'apply', '-f', os.path.join(app_name, 'prometheus.yml')], check=True)
        subprocess.run(['kubectl', 'apply', '-f', 'prometheus-deployment.yaml'], check=True)

        logging.info(f"Prometheus deployment succeeded with exit code {result.returncode}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error: Prometheus deployment failed with exit code {e.returncode}")


def generate_kubernetes_manifests(app_name, ports):
    deployment_content = f'''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
    spec:
      containers:
      - name: {app_name}-container
        image: {app_name}:latest
        ports:
        - containerPort: {ports}
'''
    service_content = f'''
apiVersion: v1
kind: Service
metadata:
  name: {app_name}-service
spec:
  selector:
    app: {app_name}
  ports:
    - protocol: TCP
      port: {ports}
      targetPort: {ports}
  type: LoadBalancer
'''
    manifests_dir = os.path.join(app_name, "kubernetes_manifests")
    os.makedirs(manifests_dir, exist_ok=True)

    with open(os.path.join(manifests_dir, 'deployment.yaml'), 'w') as deployment_file:
        deployment_file.write(deployment_content)

    with open(os.path.join(manifests_dir, 'service.yaml'), 'w') as service_file:
        service_file.write(service_content)


def generate_skaffold_config(app_name):
    skaffold_content = f'''
apiVersion: skaffold/v2beta3
kind: Config
metadata:
  name: {app_name}
build:
  artifacts:
    - image: {app_name}
deploy:
  kubectl:
    manifests:
      - ./kubernetes_manifests/*.yaml
'''
    with open(os.path.join(app_name, 'skaffold.yaml'), 'w') as skaffold_file:
        skaffold_file.write(skaffold_content)


def generate_grafana_dashboard(app_name):
    dashboard_config = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": f'{app_name}-grafana-dashboard-config'
        },
        "data": {
            "dashboard.json": json.dumps({
                "id": None,
                "title": f'{app_name} Dashboard',
                "panels": [
                    {
                        "id": 1,
                        "type": "graph",
                        "title": "My Graph Panel",
                        "targets": [
                            {
                                "target": "metric_name",
                                "refId": "A"
                            }
                        ]
                    }
                ],
                "time": {
                    "from": "now-6h",
                    "to": "now"
                },
                "timezone": "browser",
                "schemaVersion": 21,
                "version": 1
            })
        }
    }

    with open(os.path.join(app_name, 'grafana_dashboard.json'), 'w') as f:
        json.dump(dashboard_config, f, indent=2)


def deploy_grafana(app_name):
    try:
        result = subprocess.run(['kubectl', 'apply', '-f', os.path.join(app_name, 'grafana_dashboard.json')],
                                check=True)
        subprocess.run(['kubectl', 'apply', '-f', 'grafana-deployment.yaml'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Grafana deployment failed with exit code {e.returncode}")


SKAFFOLD_PATH = r'C:\Program Files (x86)\Skaffold\skaffold.exe'


def initialize_skaffold():
    try:
        subprocess.run(["skaffold", "init"])
    except subprocess.CalledProcessError as e:
        logging.info("Try skaffold init manually in the project directory.")
        logging.error(f"Error: Skaffold initialization failed with exit code {e.returncode}")
        exit(1)


def main():
    # app_name, language, ports, base_image_url, metrics_to_collect = get_user_input()
    app_name = "app"
    ports = "5000"
    base_image_url = "python:3.8"
    metrics_to_collect = "metric_name"

    generate_repository(app_name)
    generate_dockerfile(app_name, ports, base_image_url)
    generate_prometheus_config(app_name, metrics_to_collect)
    generate_grafana_dashboard(app_name)
    generate_kubernetes_manifests(app_name, ports)
    generate_skaffold_config(app_name)
    initialize_skaffold()

    try:
        subprocess.run([SKAFFOLD_PATH, "run", "--tail"], check=True)
    except subprocess.CalledProcessError as e:
        logging.info(f"Error: Skaffold run failed with exit code {e.returncode}")
        exit(1)
    deploy_prometheus(app_name)
    deploy_grafana(app_name)


if __name__ == "__main__":
    logging.basicConfig(filename='example.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Starting the application")
    main()
