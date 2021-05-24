from kubernetes import client, config

class Kube():
    def __init__(self) -> None:
        config.load_kube_config()
        self.v1 = client.CoreV1Api()

    
    def listPods(self):
        print("Listing pods with their IPs:")
        ret = self.v1.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            print("%s\t%s\t%s" %(i.status.pod_ip, i.metadata.namespace, i.metadata.name))



if __name__ == '__main__':
    Kube().listPods()