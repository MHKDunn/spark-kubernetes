$pod = kubectl get pods -n spark -o=name
$pod = $pod.Substring(4)
$file_count = 2
$thread_count = 4
$driver_memory = '2G'
$executor_memory = '500M'

$command = '/opt/spark/bin/spark-submit --master local[' + $thread_count + '] --jars /opt/spark-apps/postgresql-42.2.22.jar --driver-memory ' + $driver_memory + ' --executor-memory ' + $executor_memory + ' /opt/spark-apps/Downloader.py --file-count ' + $file_count

kubectl exec -ti -n spark spark-cbf6f798b-gg5kb -- bash -c $command 