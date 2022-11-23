kubectl delete -n default all --all --grace-period=0
kubectl delete -n default configmap --all --grace-period=0
kubectl delete -n default pvc --all --grace-period=0
kubectl delete -n default pv --all --grace-period=0
kubectl delete -n default secret mysecret --grace-period=0
