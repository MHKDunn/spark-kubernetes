kubectl delete -n spark all --all --grace-period=0
kubectl delete -n spark configmap --all --grace-period=0
kubectl delete -n spark pvc --all --grace-period=0


