from kubernetes import client, config
import yaml

class Kube():
    def __init__(self) -> None:
        config.load_kube_config()
        self.v1 = client.CoreV1Api()
        self.k8s_apps_v1 = client.AppsV1Api()

    
    def listPods(self):
        print("Listing pods with their IPs:")
        ret = self.v1.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            print("%s\t%s\t%s" %(i.status.pod_ip, i.metadata.namespace, i.metadata.name))

    def addDeployment(self,path):
        with open(path) as f:
            dep = yaml.safe_load(f)
            resp = self.k8s_apps_v1.create_namespaced_deployment(
                body=dep, namespace="default")
            print("Deployment created. status='%s'" % resp.metadata.name)


if __name__ == '__main__':
    k = Kube()
    k.addDeployment('test.yaml')