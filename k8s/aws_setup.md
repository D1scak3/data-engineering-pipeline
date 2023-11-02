# AWS Helper and EKS setup

## AWS EC2 Helper

### install kubectl

```
curl -O https://s3.us-west-2.amazonaws.com/amazon-eks/1.27.1/2023-04-19/bin/linux/amd64/kubectl

chmod +x ./kubectl

mkdir -p $HOME/bin && cp ./kubectl $HOME/bin/kubectl && export PATH=$HOME/bin:$PATH

echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc

kubectl version --short --client
```

### install eksctl

```
ARCH=amd64
PLATFORM=$(uname -s)_$ARCH

curl -sLO "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$PLATFORM.tar.gz"

tar -xzf eksctl_$PLATFORM.tar.gz -C /tmp && rm eksctl_$PLATFORM.tar.gz

sudo mv /tmp/eksctl /usr/local/bin
```

## EKS cluster setup

Access to the cluster in the beginning is made only through the account that created it.

Use temporary credentials present in the start link to grant access to the aws cli and interact with the cluster.

### Get information about current user and aws-auth configmap

```
kubectl describe -n kube-system configmap/aws-auth

kubectl get roles -A

kubectl get clusterroles

aws sts get-caller-identity

eksctl get iamidentitymapping --cluster cluster-name --region=region-code

aws eks describe-cluster --name cluster-name --query cluster.endpoint --output text

aws eks describe-cluster --name cluster-name --query cluster.certificateAuthority --output text
```

### Update kubeconfig

Create cluster's control pane and configure access.
Use for both cluster creator account and ec2 ci-cd-helper.

```
aws eks update-kubeconfig --region region-code --name cluster-name
```

### Add new role to aws-auth (w/ cluster creator account)

```
# create identity mapping
eksctl create iamidentitymapping \
--cluster cluster-name \
--region=region-code \
--arn arn:aws:iam::############:role/data-eng-helper-role \
--username ci-cd-helper \
--group eks-ci-cd-helper-group \
--no-duplicate-arns

# create role and rolebinding for ci/cd
kubectl apply -f cicd_clusterrole.yaml
```
