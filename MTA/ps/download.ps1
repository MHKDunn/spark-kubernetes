
$pod = kubectl get pods -n default -o=name
$pod = $pod.Substring(4)
$file_count = 2


$command = '/opt/spark/bin/spark-submit \
--conf spark.kubernetes.authenticate.driver.serviceAccountName=spark-sa \
--deploy-mode cluster \
--name download-app \
--conf spark.jars.ivy=/tmp/.ivy \
--master k8s://https://F139BCD223DA0D0ED62BD0B6C19B2C09.gr7.eu-west-2.eks.amazonaws.com \
--conf spark.dynamicAllocation.enabled=true \
--conf spark.dynamicAllocation.shuffleTracking.enabled=true \
--conf spark.dynamicAllocation.shuffleTracking.timeout=120 \
--conf spark.dynamicAllocation.minExecutors=1 \
--conf spark.dynamicAllocation.maxExecutors=3 \
--conf spark.kubernetes.allocation.batch.size=3 \
--conf spark.dynamicAllocation.executorAllocationRatio=1 \
--conf spark.dynamicAllocation.schedulerBacklogTimeout=1 \
--conf spark.kubernetes.namespace=default \
--conf spark.kubernetes.container.image=mattdunn022/spark-kubernetes:latest \
--conf spark.kubernetes.driver.secretKeyRef.POSTGRES_USER=mysecret:POSTGRES_USER \
--conf spark.kubernetes.executor.secretKeyRef.POSTGRES_USER=mysecret:POSTGRES_USER \
--conf spark.kubernetes.driver.secretKeyRef.POSTGRES_PASSWORD=mysecret:POSTGRES_PASSWORD \
--conf spark.kubernetes.executor.secretKeyRef.POSTGRES_PASSWORD=mysecret:POSTGRES_PASSWORD \
--jars local:///opt/spark-apps/postgresql-42.2.22.jar \
local:///opt/spark-apps/Downloader.py --file-count ' + $file_count

kubectl exec -ti -n default spark-pod -- bash -c $command

#Write-Host $command