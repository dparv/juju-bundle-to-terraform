#!/usr/bin/env python3
import yaml
import sys

f = open(sys.argv[1], 'r').read()

bundle = yaml.safe_load(f)

resource_applications = """
resource "juju_application" "{}" {{
  name  = "{}"
  model = juju_model.k8s.name
  charm {{
    name     = "{}"
    base     = "ubuntu@22.04"
    channel  = "{}"
  }}
  units     = {}
  {}
  {}
}}
"""

resource_applications_constraints = """
  constraints = "{}"
"""

resource_applications_config = """
  config = {{
    {}
  }}
"""

resource_relations = """
resource "juju_integration" "{}" {{
  model = juju_model.k8s.name

  application {{
    name     = juju_application.{}.name
    endpoint = "{}"
  }}

  application {{
    name     = juju_application.{}.name
    endpoint = "{}"
  }}
}}
"""

if 'applications' in bundle:
    applications = bundle['applications']
    #print(applications)
    application_names = list(applications.keys())
    for app_name in application_names:
        app = applications[app_name]
        charm = app['charm']
        channel = app['channel']
        num_units = app['num_units'] if 'num_units' in app else 0
        const = app['constraints'] if 'constraints' in app else None
        charm_config = app['options'] if 'options' in app else None
        conf = ''
        if charm_config:
            configs_keys = charm_config.keys()
            for key in configs_keys:
                conf += '"' + key + '"' + ' : ' +  '"' + str(charm_config[key]) + '",\n    '
            conf = conf.removesuffix(',\n    ')
            config = resource_applications_config.format(conf)
        else:
            config = ''

        if const:
            constraints = resource_applications_constraints.format(const)
        else:
            constraints = ''

        print(resource_applications.format(
            app_name,
            app_name,
            app_name,
            channel,
            num_units,
            constraints,
            config
            ))


if 'relations' in bundle:
    relations = bundle['relations']
    for relation in relations:
        left_app, right_app = relation
        left_app_name, left_app_relation = left_app.split(':')
        right_app_name, right_app_relation = right_app.split(':')

        print(resource_relations.format(
            left_app_name + "-" + right_app_name,
            left_app_name,
            left_app_relation,
            right_app_name,
            right_app_relation
            ))
