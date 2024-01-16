Simple code to convert juju bundles in to terraform files.

Export the bundle:

```
juju export-bundle > bundle.yaml
```

Run it simply with: 

```
python3 convert.py bundle.yaml juju_model_name > file.tf
```

You will need to fix the juju model resource, by adding a credential and
configuring a juju_credential resource with your provider and auth mechanism.

Test for any wrong-conversions with:

```
terraform validate
```

It is possible that multi-line strings in juju config options are malformed
and need to be manually fixed.

== Known Issues ==

N/A
