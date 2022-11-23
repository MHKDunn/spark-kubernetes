aws iam create-policy --policy-name AmazonEKSClusterAutoscalerPolicy --policy-document file://./policy/cluster-autoscaler-policy.json
eksctl create cluster -f .\cluster\create-cluster.yaml
