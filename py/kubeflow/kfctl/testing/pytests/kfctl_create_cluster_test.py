import logging
import pytest
import os
from kubeflow.testing import util


def test_create_cluster(record_xml_attribute, app_name, app_path, project, use_basic_auth,
                        use_istio, config_path, build_and_apply, kfctl_repo_path,
                        cluster_name, cluster_creation_script, self_signed_cert, values):
  """Test Create Cluster For E2E Test.

  Args:
    app_name: kubeflow deployment name.
    app_path: The path to the Kubeflow app.
    project: The GCP project to use.
    use_basic_auth: Whether to use basic_auth.
    use_istio: Whether to use Istio or not
    config_path: Path to the KFDef spec file.
    cluster_name: Name of EKS cluster
    cluster_creation_script: script invoked to create a new cluster
    build_and_apply: whether to build and apply or apply
    kfctl_repo_path: path to the kubeflow/kfctl repo.
    self_signed_cert: whether to use self-signed cert for ingress.
    values: Comma separated list of variables to substitute into config_path
  """
  util.set_pytest_junit(record_xml_attribute, "test_create_cluster")

  if values:
    pairs = values.split(",")
    path_vars = {}
    for p in pairs:
      k, v = p.split("=")
      path_vars[k] = v

  # Create EKS Cluster
  logging.info("Creating EKS Cluster")
  os.environ["CLUSTER_NAME"] = cluster_name
  util.run(["/bin/bash", "-c", cluster_creation_script])


if __name__ == "__main__":
  logging.basicConfig(
      level=logging.INFO,
      format=('%(levelname)s|%(asctime)s'
              '|%(pathname)s|%(lineno)d| %(message)s'),
      datefmt='%Y-%m-%dT%H:%M:%S',
  )
  logging.getLogger().setLevel(logging.INFO)
  pytest.main()
