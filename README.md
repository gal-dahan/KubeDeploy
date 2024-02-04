# Home assignment - Skaffold app automation

When developing a large app, we use many microservices, each one has its own purpose. It can be pretty exhausting to start from scratch, so we want to give our developers an automation platform that creates the basic development environment for them.

# Goal:
Create an automation for establishing a new micro-service. 

## Tools:
- [Python](https://www.python.org/)
- [Docker](https://www.docker.com/get-started) - Automatically generates a Dockerfile based on user input for the application name, language, ports, and base image URL.

- [Kubernetes](https://kubernetes.io/docs/setup/)- Creates deployment and service manifests for Kubernetes to deploy the application.

- [Prometheus](https://prometheus.io/docs/prometheus/latest/getting_started/)-Generates a Prometheus configuration for collecting specified metrics from the application.
- [Grafana](https://grafana.com/docs/grafana/latest/getting-started/getting-started-prometheus/)-Sets up a basic Grafana dashboard configuration for visualizing collected metrics.
- [Skaffold](https://skaffold.dev)-Configures Skaffold for seamless development and deployment workflows.



## Usage

1. Run the script by executing `python main.py` in the terminal.
2. Follow the prompts to input necessary information such as app name, language, ports, etc.
3. Skaffold will be initialized, and the application will be deployed to your Kubernetes cluster.
4. Prometheus and Grafana will also be deployed and configured to monitor the application.


## Port Forwarding
- **Application Port (Your App):** `5000`
  - Used for accessing your deployed application.

- **Grafana Port:** `3000`
  - Used for accessing the Grafana web interface.

- **Prometheus Port:** `9090`
  - Used for accessing the Prometheus web interface.

Step 1
```
kubectl get pods
```
Step 2
```
kubectl port-forward pod-name local-port:pod-port
```
Replace pod-name with the actual name of the pod, local-port with the desired local port on your machine, and pod-port with the port on which the service is running inside the pod.


## Questions:

- What would you add/change if you had a week to work on this?

Jenkins Pipeline - Set up a Jenkins pipeline to automate the build, test, and deployment processes. And incorporate stages for linting, unit testing, building Docker images, and deploying to Kubernetes.
Port Forwarding with [Kubernetes Client for Python](https://github.com/kubernetes-client/python) or HELM - Alternatively, evaluate HELM charts for simplifying the deployment and port forwarding processes.
And of course add more Testing, Security and Documentation

- What would you add/change if the tool was meant to be used by more than 100 users?

Scalability - Optimize the application and deployment configurations for scalability to handle increased usage and traffic.

Use load balancing - like NGINX to distribute incoming traffic efficiently across multiple instances, ensuring better performance and responsiveness.

Improve monitoring - capabilities to effectively track the application performance.

