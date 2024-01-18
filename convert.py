#!/usr/bin/env python3
import yaml
import sys

f = open(sys.argv[1], 'r').read()
juju_model_name = sys.argv[2]

docs = yaml.safe_load_all(f)

num_docs = 0

bundles = []
for doc in docs:
    num_docs+=1
    bundles.append(doc)

bundle = bundles[0]

if num_docs == 2:
    cmr_offers = bundles[1]

resource_juju_model = """
resource "juju_model" "{}" {{
  name = "{}"
}}
"""

resource_applications = """
resource "juju_application" "{}" {{
  name  = "{}"
  model = juju_model.{}.name
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
  model = juju_model.{}.name

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

resource_offer = """
resource "juju_offer" "{}" {{
  model            = juju_model.{}.name
  application_name = juju_application.{}.name
  endpoint         = {}
}}
"""

print(resource_juju_model.format(juju_model_name, juju_model_name))

if 'applications' in bundle:
    applications = bundle['applications']
    application_names = list(applications.keys())
    for app_name in application_names:
        app = applications[app_name]
        charm = app['charm']
        channel = app['channel'] if 'channel' in app else ''
        # num_units is part of baremetal bundles, scale - kubernetes, 0 means
        # subordinate
        if 'num_units' in app:
            num_units = app['num_units']
        elif 'scale' in app:
            num_units = app['scale']
        else:
            num_units = 0
        const = app['constraints'] if 'constraints' in app else None
        charm_config = app['options'] if 'options' in app else None
        conf = ''
        if charm_config:
            configs_keys = charm_config.keys()
            for key in configs_keys:
                conf += '"' + key + '"' + ' : ' +  ' <<-EOT\n' + str(charm_config[key]) + '\nEOT,\n    '
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
            juju_model_name,
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
            juju_model_name,
            left_app_name,
            left_app_relation,
            right_app_name,
            right_app_relation
            ))


if cmr_offers:
    for app_name in application_names:
        if app_name in list(cmr_offers['applications'].keys()):
            if 'offers' in cmr_offers['applications'][app_name]:
                offers = cmr_offers['applications'][app_name]['offers']
                for offer in offers:
                    endpoints = (offers[offer]['endpoints'])
                    for endpoint in endpoints:

                        print(resource_offer.format(
                            offer,
                            juju_model_name,
                            app_name,
                            endpoint
                            ))
