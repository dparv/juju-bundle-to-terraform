Simple code to convert juju bundles in to terraform files.

Export the bundle:

```
juju export-bundle > bundle.yaml
```

Run it simply with: 

```
python3 convert.py bundle.yaml > file.tf
```

Test for any wrong-conversions with:

```
terraform validate
```

It is possible that multi-line strings in juju config options are malformed
and need to be manually fixed.
