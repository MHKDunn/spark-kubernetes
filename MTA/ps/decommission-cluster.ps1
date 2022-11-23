#eksctl delete fargateprofile --name spark-fargate --cluster spark-eks
eksctl delete cluster -f .\cluster\create-cluster.yaml
aws iam delete-policy --policy-arn arn:aws:iam::177609904360:policy/AmazonEKSClusterAutoscalerPolicy