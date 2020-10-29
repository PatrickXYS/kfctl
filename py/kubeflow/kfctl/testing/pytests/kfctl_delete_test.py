"""Run kfctl delete as a pytest.

We use this in order to generate a junit_xml file.
"""
import datetime
import logging
import os
import subprocess
import tempfile
import uuid
from retrying import retry
import yaml

import pytest

from kubeflow.testing import util
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

# TODO(gabrielwen): Move this to a separate test "kfctl_go_check_post_delete"
def get_endpoints_list(project):
  cred = GoogleCredentials.get_application_default()
  services_mgt = discovery.build('servicemanagement', 'v1', credentials=cred, cache_discovery=False)
  services = services_mgt.services()
  next_page_token = None
  endpoints = []

  while True:
    results = services.list(producerProjectId=project,
                            pageToken=next_page_token).execute()

    for s in results.get("services", {}):
      name = s.get("serviceName", "")
      endpoints.append(name)
    if not "nextPageToken" in results:
      break
    next_page_token = results["nextPageToken"]

  return endpoints

# TODO(https://github.com/kubeflow/kfctl/issues/56): test_kfctl_delete is flaky
# and more importantly failures block upload of GCS artifacts so for now we mark
# it as expected to fail.
@pytest.mark.xfail
def test_kfctl_delete(record_xml_attribute, kfctl_path, app_path, project,
                      cluster_deletion_script, cluster_name):
  util.set_pytest_junit(record_xml_attribute, "test_kfctl_delete")
  
  # TODO(PatrickXYS): do we need to load kubeconfig again?

  if not kfctl_path:
    raise ValueError("kfctl_path is required")

  if not app_path:
    raise ValueError("app_path is required")

  logging.info("Using kfctl path %s", kfctl_path)
  logging.info("Using app path %s", app_path)

  kfdef_path = os.path.join(app_path, "tmp.yaml")
  logging.info("Using kfdef file path %s", kfdef_path)

  # We see failures because delete operation will delete cert-manager and
  # kfserving, and encounter timeout. To deal with this we do retries.
  # This has a potential downside of hiding errors that are fixed by retrying.
  @retry(stop_max_delay=60*3*1000)
  def run_delete():
    util.run([kfctl_path, "delete", "-V", "-f", kfdef_path],
             cwd=app_path)

  run_delete()

  # TODO(yanniszark): split this into a separate workflow step
  if cluster_deletion_script:
    logging.info("cluster_deletion_script specified: %s", cluster_deletion_script)
    util.run(["/bin/bash", "export", "CLUSTER_NAME=", cluster_name])
    util.run(["/bin/bash", "-c", cluster_deletion_script])
    return


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO,
                      format=('%(levelname)s|%(asctime)s'
                              '|%(pathname)s|%(lineno)d| %(message)s'),
                      datefmt='%Y-%m-%dT%H:%M:%S',
                      )
  logging.getLogger().setLevel(logging.INFO)
  pytest.main()
