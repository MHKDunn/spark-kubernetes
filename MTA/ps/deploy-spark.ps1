# docker build -t spark-kubernetes .

# docker tag spark-kubernetes:latest mattdunn022/spark-kubernetes:latest

# docker push mattdunn022/spark-kubernetes:latest

docker tag spark-base/spark mattdunn022/spark-base

docker tag spark-base/spark-py mattdunn022/spark-base-py

docker push mattdunn022/spark-base

docker push mattdunn022/spark-base-py


kubectl apply -f ./build/service-account.yaml

kubectl apply -f ./build/spark-deployment.yaml

kubectl apply -f ./build/spark-pod.yaml 


# Start-Sleep -Seconds 20

# kubectl exec -ti spark-pod -- bash




