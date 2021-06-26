from kubernetes import client, config
import yaml

class Kube():
    deploymentObj = None
    def __init__(self) -> None:
        config.load_kube_config()
        self.v1 = client.CoreV1Api()
        self.k8s_apps_v1 = client.AppsV1Api()
        
    
    def listPods(self):
        print("Listing pods with their IPs:")
        ret = self.v1.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            # spec.nodeName - the node's name
            print("%s\t%s\t%s" %(i.status.pod_ip, i.metadata.namespace, i.metadata.name))


    def create_deployment_object(self,deployment_name,conatiner_name,conatiner_image,replicas):
        # Configureate Pod template container
        container = client.V1Container(
            # name="nginx",
            name=conatiner_name,
            # image="nginx:1.15.4",
            image=conatiner_image,
            ports=[client.V1ContainerPort(container_port=80)],
            resources=client.V1ResourceRequirements(
                requests={"cpu": "100m", "memory": "200Mi"},
                limits={"cpu": "500m", "memory": "500Mi"},
            ),
        )

        # Create and configurate a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": "nginx"}),
            spec=client.V1PodSpec(containers=[container]),
        )

        # Create the specification of deployment
        spec = client.V1DeploymentSpec(
            replicas=replicas, template=template, selector={
                "matchLabels":
                {"app": "nginx"}})

        # Instantiate the deployment object
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=deployment_name),
            spec=spec,
        )

        return deployment

    def create_deployment(self):
        # Create deployement
        deployment = self.create_deployment_object("mydep2","nginx", "nginx:1.15.4", 2)

        resp = self.k8s_apps_v1.create_namespaced_deployment(
            body=deployment, namespace="default"
        )

        print("\n[INFO] deployment `nginx-deployment` created.\n")
        print("%s\t%s\t\t\t%s\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE"))
        print(
            "%s\t\t%s\t%s\t\t%s\n"
            % (
                resp.metadata.namespace,
                resp.metadata.name,
                resp.metadata.generation,
                resp.spec.template.spec.containers[0].image,
            )
        )

    def list_all_deployments(self):
        print("Listing all deployments:")
        ret = self.k8s_apps_v1.list_deployment_for_all_namespaces(watch=False,pretty=True)
        print("%s\t%s\t%s\t\t%s\t\t\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE","REPLICAS"))
        for resp in ret.items:
            print(
            "%s\t%s\t%s\t\t%s\t\t\t%s"
            % (
                resp.metadata.namespace,
                resp.metadata.name,
                resp.metadata.generation,
                resp.spec.template.spec.containers[0].image,
                resp.spec.replicas
            )
            )

    def update_deployment_image(self,name,namespace,image,replicas):
        # Update container image
        # deployment.spec.template.spec.containers[0].image = "nginx:1.16.0"
        deployment = self.create_deployment_object("mydep1","nginx",image, replicas)
        # deployment.spec.template.spec.containers[0].image = image
        # deployment.spec.replicas = replicas

        # patch the deployment
        resp = self.k8s_apps_v1.patch_namespaced_deployment(
            name=name, namespace=namespace, body=deployment
        )

        print("\n[INFO] deployment's container image updated.\n")
        print("%s\t%s\t%s\t\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE"))
        print(
            "%s\t%s\t%s\t\t%s\n"
            % (
                resp.metadata.namespace,
                resp.metadata.name,
                resp.metadata.generation,
                resp.spec.template.spec.containers[0].image,
            )
        )

    def delete_deployment(self,name,namespace):
        resp = self.k8s_apps_v1.delete_namespaced_deployment(
            name=name,
            namespace=namespace,
            body=client.V1DeleteOptions(
                propagation_policy="Foreground", grace_period_seconds=5
            ),
        )
        print("\n[INFO] deployment deleted.")

    def create_pod(self):
        pod=client.V1Pod()
        spec=client.V1PodSpec()
        pod.metadata=client.V1ObjectMeta(name="busybox")
        container=client.V1Container()
        container.image="busybox"
        container.args=["sleep", "3600"]
        container.name="busybox"    
        spec.containers = [container]
        pod.spec = spec
        self.v1.create_namespaced_pod(namespace="default",body=pod)
        print("Pod created.")

    def display_pods_of_node(self,node_name):
        print("Listing pods with their IPs on node: ", node_name)
        field_selector = 'spec.nodeName='+node_name
        ret = self.v1.list_pod_for_all_namespaces(watch=False, field_selector=field_selector)
        for i in ret.items:
            print("%s\t%s\t%s" %(i.status.pod_ip, i.metadata.namespace, i.metadata.name))

    def display_pods_log(self,name,namespace):    
        res = self.v1.read_namespaced_pod_log(name=name, namespace=namespace)
        print(res)

    def delete_pod(self,name,namespace):
        self.v1.delete_namespaced_pod(name=name, namespace=namespace, body=client.V1DeleteOptions())
        print("Pod deleted.")



if __name__ == '__main__':
    k = Kube()
    k.listPods()
    # k.create_deployment()
    # k.delete_deployment("mydep1","default")
    k.list_all_deployments()
    # k.update_deployment_image("mydep1","default","nginx:1.16.0",1)
    
    
