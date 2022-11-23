$pod = kubectl get pods -n spark -o=name
$pod = $pod.Substring(4)

kubectl exec -ti -n spark $pod -- bash -c "tail /mnt/data-files/log -f"


