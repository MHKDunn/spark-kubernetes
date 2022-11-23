$pod = kubectl get pods -n spark -o=name
$pod = $pod.Substring(4)
$port = 30007
$thread_count = 8
$driver_memory = '3G'
$executor_memory = '500M'

$command = '/opt/spark/bin/spark-submit --master local[' + $thread_count + '] --jars /opt/spark-apps/postgresql-42.2.22.jar --driver-memory ' + $driver_memory + ' --executor-memory ' + $executor_memory + ' /opt/spark-apps/Persistor.py --port ' + $port

kubectl exec -ti -n spark $pod -- bash -c $command

