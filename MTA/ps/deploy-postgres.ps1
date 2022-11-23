kubectl apply -f ./build/postgres-storage.yaml
Start-Sleep -Seconds 1
kubectl apply -f ./build/postgres-login-secret.yaml
Start-Sleep -Seconds 1
kubectl apply -f ./build/postgres-deployment.yaml
Start-Sleep -Seconds 1
kubectl apply -f ./build/postgres-service.yaml 
# $pod = kubectl get pods -n default -o=name
# $pod = $pod.Substring(4)

# kubectl exec -ti spark-pod -- bash