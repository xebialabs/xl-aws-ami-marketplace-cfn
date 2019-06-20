# Executing the tests

1. Install taskcat (https://aws-quickstart.github.io/install-taskcat.html)
1. Modify `ci/new-vpc-e2e.json` and parameters that fits you(you can also use you local `~/.aws/taskcat_global_override.json` to override parameters like `KeyPairName` )
2. Modify `ci/taskcat.yaml` so it can work your your aws account. For example the region has to be the same as the region in your `~/.aws/config`
2. Now we can run `taskcat -c ci/taskcat.yaml` 


# Cleanup s3 buckets from taskcat runs

``` 
for i in `aws s3 ls | grep taskcat | awk '{print $3}'`; do aws s3 rb s3://$i --force; done
```
