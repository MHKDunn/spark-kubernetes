kubectl delete service postgres 
kubectl delete deployment postgres
kubectl delete -f postgres-login-secret.yaml
kubectl delete persistentvolumeclaim postgres-pv-claim
kubectl delete persistentvolume postgres-pv-volume