from typing import TypeVar, Callable, Any, List
from kubernetes import client, config
from kubernetes.client import exceptions

import yaml
import traceback
import logging

F = TypeVar('F', bound=Callable[..., Any])
logger = logging.getLogger("app.logger")

class Kube():

    def _errorHandler(func : F) -> F:
        def wrapper(self, *args, **kwargs) -> Any:
            try:
                return func(self, *args, **kwargs)
            except exceptions.ApiException as e:
                logger.error(str(e) + '\n' + traceback.format_exc())
                return None
        return wrapper
    
    def __init__(self, configFile : str = None) -> None:
        config.load_kube_config(config_file=configFile)
        self.v1 = client.CoreV1Api()
        self.k8s_apps_v1 = client.AppsV1Api()
        self.deploymentObj = None

    
    def _createDeploymentObject(self, deploymentName : str, conatinerName : str, conatinerImage : str, replicas : int = 1):
        # Configureate Pod template container
        container = client.V1Container(
            # name="nginx",
            name = conatinerName,
            # image="nginx:1.15.4",
            image = conatinerImage,
            ports = [
                client.V1ContainerPort(container_port=80)
            ],
            resources = client.V1ResourceRequirements(
                requests = {"cpu": "100m", "memory": "200Mi"},
                limits = {"cpu": "500m", "memory": "500Mi"},
            ),
        )

        # Create and configurate a spec section
        template = client.V1PodTemplateSpec(
            metadata = client.V1ObjectMeta(
                labels = {"app": conatinerName}
            ),
            spec = client.V1PodSpec(
                containers=[container]
            ),
        )

        # Create the specification of deployment
        spec = client.V1DeploymentSpec(
            replicas = replicas, 
            template = template, 
            selector = {
                "matchLabels":
                {"app": conatinerName}
            }
        )

        # Instantiate the deployment object
        deployment = client.V1Deployment(
            api_version = "apps/v1",
            kind = "Deployment",
            metadata = client.V1ObjectMeta(name = deploymentName),
            spec = spec,
        )

        return deployment
    
    def _createLoadBalancer(self, deploymentName : str):
        
        ports = client.V1ServicePort(
            # protocol="TCP",
            port=6000,
            target_port=5000
        )

        spec = client.V1ServiceSpec(
            selector = {"app": deploymentName},
            ports = [client.V1ServicePort(port=8080, target_port=5000)],
            type = "LoadBalancer",
            # external_i_ps=["172.31.37.96"]
        )

        deployment = client.V1Service(
            api_version = "v1",
            kind = "Service",
            metadata = client.V1ObjectMeta(name = deploymentName + '-service-beta', annotations={"metallb.universe.tf/address-pool" : "production-public-ips"}),
            spec = spec,
            # status = client.V1LoadBalancerStatus(
            #     ingress= client.V1LoadBalancerIngress(
            #         ip="172.31.37.96",
            #     )
            # )
        )
        return deployment

    @_errorHandler
    def createDeployment(self,deploymentName : str, conatinerName : str, conatinerImage : str, Replicas : int = 1, deploymentNameSpace : str = 'default') -> bool:
        # Create deployement
        self.deploymentObj = self._createDeploymentObject(deploymentName, conatinerName, conatinerImage, Replicas)

        resp = self.k8s_apps_v1.create_namespaced_deployment(
            body = self.deploymentObj, 
            namespace = deploymentNameSpace
        )

        # resp = self.v1.create_namespaced_service(
            
        #     namespace = deploymentNameSpace,
        #     body = self._createLoadBalancer(deploymentName), 
        # )
        return True

    @_errorHandler
    def getDeploymentInfo(self, name : str, namespace : str = 'default') -> dict:
        resp = self.k8s_apps_v1.read_namespaced_deployment(name, namespace)
        ans = None
        if resp:
            ans = {
                "name" : resp.metadata.name, 
                "namespace" :resp.metadata.namespace,
                "revision" : resp.metadata.generation, 
                "numberOfContainers" : len(resp.spec.template.spec.containers),
                "containerName" : resp.spec.template.spec.containers[0].name,
                "containerImage" : resp.spec.template.spec.containers[0].image, 
                "replicas" : resp.spec.replicas,
                "limits": resp.spec.template.spec.containers[0].resources.limits , 
                "requests" : resp.spec.template.spec.containers[0].resources.requests
            }
        return ans
    
    @_errorHandler
    def listPods(self, sendall : bool = False) -> List[dict]:
        pods = self.v1.list_pod_for_all_namespaces(watch=False)
        response = [
            {
                "podName" :  i.metadata.name, 
                "namespace" :  i.metadata.namespace ,
                "podIP" : i.status.pod_ip,
                "numberOfContainers" : len(i.spec.containers),
                "containerName" :  i.spec.containers[0].name,
                "containerImage" : i.spec.containers[0].image, 
                "limits": i.spec.containers[0].resources.limits , 
                "requests" : i.spec.containers[0].resources.requests,
                "status" : i.status.phase
            } 
            for i in pods.items if i.metadata.namespace != "kube-system" or sendall
        ]
        return response

    @_errorHandler
    def listAllDeployments(self, sendall : bool = False) -> List[dict]:
        ret = self.k8s_apps_v1.list_deployment_for_all_namespaces(watch=False,pretty=True)
        ans = list()
        for resp in ret.items:
            if resp.metadata.name != "coredns" or sendall:
                d = {
                    "name" : resp.metadata.name, 
                    "namespace" :resp.metadata.namespace,
                    "revision" : resp.metadata.generation,
                    "numberOfContainers" : len(resp.spec.template.spec.containers),
                    "containerName" : resp.spec.template.spec.containers[0].name,
                    "containerImage" : resp.spec.template.spec.containers[0].image, 
                    "replicas" : resp.spec.replicas,
                    "limits": resp.spec.template.spec.containers[0].resources.limits, 
                    "requests" : resp.spec.template.spec.containers[0].resources.requests
                }
                ans.append(d)
        print(ans)
        return ans

    @_errorHandler
    def getReplicaNumber(self,name : str, namespace : str = 'default') -> int:
        resp = self.k8s_apps_v1.read_namespaced_deployment(name, namespace)
        return int(resp.spec.replicas)

    @_errorHandler
    def updateDeploymentImage(self, name : str, image : str, namespace : str = 'default') -> bool:
        # Update container image
        response = self.k8s_apps_v1.read_namespaced_deployment(name, namespace)
        response.spec.template.spec.containers[0].image = image
        # self.deploymentObj.spec.template.spec.containers[0].image = image
        # deployment = self.create_deployment_object("mydep1","nginx",image, replicas)
        # print(self.deploymentObj.spec.template.spec.containers[0].image)
        # patch the deployment
        resp = self.k8s_apps_v1.patch_namespaced_deployment(
            name = name, 
            namespace = namespace, 
            body = response

        )
        return True

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

    @_errorHandler
    def updateDeploymentReplicas(self, name : str, replicas : int, namespace : str = 'default') -> bool:
        # Update container image
        response = self.k8s_apps_v1.read_namespaced_deployment(name, namespace)
        response.spec.replicas  += replicas
        if response.spec.replicas > 5:
            response.spec.replicas = 5
        elif response.spec.replicas < 1:
            response.spec.replicas = 1
        # self.deploymentObj.spec.replicas  += replicas
        # deployment.spec.replicas = replicas

        # patch the deployment
        resp = self.k8s_apps_v1.patch_namespaced_deployment(
            name = name, 
            namespace = namespace, 
            body = response
        )
        return True
        # print("\n[INFO] deployment's container replicas updated.\n")

    
    @_errorHandler
    def replaceDeploymentReplicas(self, name : str, replicas : int, namespace : str = 'default') -> bool:
        response = self.k8s_apps_v1.read_namespaced_deployment(name, namespace)
        response.spec.replicas  = replicas
        resp = self.k8s_apps_v1.patch_namespaced_deployment(
            name = name, 
            namespace = namespace, 
            body = response
        )
        return True

    @_errorHandler
    def deleteDeployment(self,name,namespace) -> bool:
        resp = self.k8s_apps_v1.delete_namespaced_deployment(
            name = name,
            namespace = namespace,
            body = client.V1DeleteOptions(
                propagation_policy = "Foreground", 
                grace_period_seconds = 5
            ),
        )
        return True
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
    from time import sleep
    k = Kube("config.yaml")
    # print(k.getDeploymentInfo('updated'))
    # k.updateDeploymentReplicas('updated', -2)
    # print(k.getReplicaNumber('updated', 'default'))
    # print(k.getDeploymentInfo('updated'))
    # print(k.createDeployment('updated', 'updated', 'shriramashagri/backend-flask:version1'))
    # sleep(15)
    # bp = k.updateDeploymentImage('updated', 'shriramashagri/backend-flask:version2')
    # print(k.listPods())
    # k.deleteDeployment('updated', 'default')
    
#     print(bp)
    # k.createDeployment("mydep1","mycontainer","nginx:1.16.0",3,"default")
    # print(k.deploymentObj);
    # k.deleteDeployment("mydep1","default")
    # print(k.listAllDeployments())
    # k.updateDeploymentImage("mydep1","nginx:1.15.0","default")
    # k.updateDeploymentReplicas("mydep1","default",-2)
    # k.updateDeploymentReplicas("mydep1","default",2)
    # print(k.getDeploymentInfo("test-deploy","default"))
    # print(k.getReplicaNumber("test-deploy","default"))
    
    
