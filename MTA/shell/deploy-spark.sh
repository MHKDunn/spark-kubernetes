cd mta
#docker build -t heleonu/spark-and-kubernetes:1 .
#docker push heleonu/spark-and-kubernetes:1
kubectl apply -f service-account.yaml
check if service account has permission
kubectl auth can-i <verb> <resource> --as=system:serviceaccount:<namespace>:<serviceaccountname> [-n <namespace>]
kubectl auth can-i create pod --as=system:serviceaccount:default:spark-sa -n default
kubectl apply -f postgres-login-secret.yaml
kubectl apply -f postgres-configmap.yaml
kubectl get configmap
kubectl apply -f spark-pod.yaml 