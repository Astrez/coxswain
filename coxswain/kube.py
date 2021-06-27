from kubernetes import client, config
import yaml

class Kube():
    
    def __init__(self) -> None:
        config.load_kube_config()
        self.v1 = client.CoreV1Api()
        self.k8s_apps_v1 = client.AppsV1Api()
        self.deploymentObj = None

    def createDeploymentObject(self,deploymentName,conatinerName,conatinerImage,replicas):
        # Configureate Pod template container
        container = client.V1Container(
            # name="nginx",
            name=conatinerName,
            # image="nginx:1.15.4",
            image=conatinerImage,
            ports=[client.V1ContainerPort(container_port=80)],
            resources=client.V1ResourceRequirements(
                requests={"cpu": "100m", "memory": "200Mi"},
                limits={"cpu": "500m", "memory": "500Mi"},
            ),
        )

        # Create and configurate a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": conatinerName}),
            spec=client.V1PodSpec(containers=[container]),
        )

        # Create the specification of deployment
        spec = client.V1DeploymentSpec(
            replicas=replicas, template=template, selector={
                "matchLabels":
                {"app": conatinerName}})

        # Instantiate the deployment object
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=deploymentName),
            spec=spec,
        )

        return deployment

    def createDeployment(self,deploymentName,deploymentNameSpace,conatinerName,conatinerImage,Replicas):
        # Create deployement
        self.deploymentObj = self.createDeploymentObject(deploymentName,conatinerName,conatinerImage,Replicas)

        resp = self.k8s_apps_v1.create_namespaced_deployment(
            body=self.deploymentObj, namespace=deploymentNameSpace
        )

        # print("\n[INFO] deployment `nginx-deployment` created.\n")
        # print("%s\t%s\t\t\t%s\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE"))
        # print(
        #     "%s\t\t%s\t%s\t\t%s\n"
        #     % (
        #         resp.metadata.namespace,
        #         resp.metadata.name,
        #         resp.metadata.generation,
        #         resp.spec.template.spec.containers[0].image,
        #     )
        # )

    def getDeploymentInfo(self,name,namespace):
        resp = self.k8s_apps_v1.read_namespaced_deployment(name, namespace, pretty=pretty, exact=exact, export=export)
        ans = {"name" : resp.metadata.name, "namespace" :resp.metadata.namespace
                "revision" : resp.metadata.generation, "numberOfContainers" : len(resp.spec.template.spec.containers),
                "containerName" : resp.spec.template.spec.containers[0].name,
                "containerImage" : resp.spec.template.spec.containers[0].image, "replicas" : resp.spec.replicas,
                "maxContainerCpuLimit": resp.spec.template.spec.containers[0].resources.limits.cpu , 
                "maxContainerMemoryLimit" : resp.spec.template.spec.containers[0].resources.limits.memory,
                "minContainerCpu" : resp.spec.template.spec.containers[0].resources.requests.cpu,
                "minContainerMemory" : resp.spec.template.spec.containers[0].resources.requests.memory,
            }
        return ans
    
    def listPods(self):
        print("Listing pods with their IPs:")
        ret = self.v1.list_pod_for_all_namespaces(watch=False)
        ans = list()
        for i in ret.items: 
            d = {"podName" :  i.metadata.name, "podNameSpace" :  i.metadata.namespace ,"podIP" : i.status.pod_ip,
            "numberOfContainers" : len(i.spec.containers),"containerName" :  i.spec.containers[0].name,
            "containerImage" : i.spec.containers[0].image, 
            "maxContainerCpuLimit":i.spec.containers[0].resources.limits.cpu , 
            "maxContainerMemoryLimit" : i.spec.containers[0].resources.limits.memory,
            "minContainerCpu" : i.spec.containers[0].resources.requests.cpu,
            "minContainerMemory" : i.spec.containers[0].resources.requests.memory}
            ans.append(d)
            # print("%s\t%s\t%s" %(i.status.pod_ip, i.metadata.namespace, i.metadata.name))
        return ans


    def listAllDeployments(self):
        print("Listing all deployments:")
        ret = self.k8s_apps_v1.list_deployment_for_all_namespaces(watch=False,pretty=True)
        print("%s\t%s\t%s\t\t%s\t\t\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE","REPLICAS"))
        ans = list()
        for resp in ret.items:
            d = {"name" : resp.metadata.name, "namespace" :resp.metadata.namespace
                "revision" : resp.metadata.generation,"numberOfContainers" : len(resp.spec.template.spec.containers),
                 "containerName" : resp.spec.template.spec.containers[0].name,
                "containerImage" : resp.spec.template.spec.containers[0].image, "replicas" : resp.spec.replicas,
                "maxContainerCpuLimit": resp.spec.template.spec.containers[0].resources.limits.cpu , 
                "maxContainerMemoryLimit" : resp.spec.template.spec.containers[0].resources.limits.memory,
                "minContainerCpu" : resp.spec.template.spec.containers[0].resources.requests.cpu,
                "minContainerMemory" : resp.spec.template.spec.containers[0].resources.requests.memory,
            }
            ans.append(d)
            # print(
            # "%s\t%s\t%s\t\t%s\t\t\t%s"
            # % (
            #     resp.metadata.namespace,
            #     resp.metadata.name,
            #     resp.metadata.generation,
            #     resp.spec.template.spec.containers[0].image,
            #     resp.spec.replicas
            # )
            # )
        return ans

    def getReplicaNumber(self,name,namespace):
        resp = self.k8s_apps_v1.read_namespaced_deployment(name, namespace, pretty=pretty, exact=exact, export=export)
        return resp.spec.replicas

    def updateDeploymentImage(self,name,namespace,image):
        # Update container image
        self.deploymentObj.spec.template.spec.containers[0].image = image
        # deployment = self.create_deployment_object("mydep1","nginx",image, replicas)

        # patch the deployment
        resp = self.k8s_apps_v1.patch_namespaced_deployment(
            name=name, namespace=namespace, body=self.deploymentObj
        )

        # print("\n[INFO] deployment's container image updated.\n")
        # print("%s\t%s\t%s\t\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE"))
        # print(
        #     "%s\t%s\t%s\t\t%s\n"
        #     % (
        #         resp.metadata.namespace,
        #         resp.metadata.name,
        #         resp.metadata.generation,
        #         resp.spec.template.spec.containers[0].image,
        #     )
        # )

    def updateDeploymentReplicas(self,name,namespace,replicas):
        # Update container image
        self.deploymentObj.spec.replicas += replicas
        # deployment = self.create_deployment_object("mydep1","nginx",image, replicas)
        # deployment.spec.replicas = replicas

        # patch the deployment
        resp = self.k8s_apps_v1.patch_namespaced_deployment(
            name=name, namespace=namespace, body=self.deploymentObj
        )

        # print("\n[INFO] deployment's container replicas updated.\n")

    def deleteDeployment(self,name,namespace):
        resp = self.k8s_apps_v1.delete_namespaced_deployment(
            name=name,
            namespace=namespace,
            body=client.V1DeleteOptions(
                propagation_policy="Foreground", grace_period_seconds=5
            ),
        )
        # print("\n[INFO] deployment deleted.")

    # def create_pod(self):
    #     pod=client.V1Pod()
    #     spec=client.V1PodSpec()
    #     pod.metadata=client.V1ObjectMeta(name="busybox")
    #     container=client.V1Container()
    #     container.image="busybox"
    #     container.args=["sleep", "3600"]
    #     container.name="busybox"    
    #     spec.containers = [container]
    #     pod.spec = spec
    #     self.v1.create_namespaced_pod(namespace="default",body=pod)
    #     print("Pod created.")

    # def display_pods_of_node(self,node_name):
    #     print("Listing pods with their IPs on node: ", node_name)
    #     field_selector = 'spec.nodeName='+node_name
    #     ret = self.v1.list_pod_for_all_namespaces(watch=False, field_selector=field_selector)
    #     for i in ret.items:
    #         print("%s\t%s\t%s" %(i.status.pod_ip, i.metadata.namespace, i.metadata.name))

    # def display_pods_log(self,name,namespace):    
    #     res = self.v1.read_namespaced_pod_log(name=name, namespace=namespace)
    #     print(res)

    # def delete_pod(self,name,namespace):
    #     self.v1.delete_namespaced_pod(name=name, namespace=namespace, body=client.V1DeleteOptions())
    #     print("Pod deleted.")



if __name__ == '__main__':
    k = Kube()
    # k.listPods()
    # k.createDeployment("mydep123","default","nginx","nginx:1.16.0",1)
    # print(k.deploymentObj);
    # k.deleteDeployment("mydep1","default")
    k.listAllDeployments()
    # k.updateDeploymentImage("mydep1","default","nginx:1.16.0")
    # k.updateDeploymentReplicas("mydep1","default",2)
    # k.updateDeploymentReplicas("mydep1","default",-1)
    
    
