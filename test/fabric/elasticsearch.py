import json

from fabric.api import env, task, run
from envassert import detect, file, group, package, port, process, service, \
    user
from hot.utils.test import get_artifacts


def es_cluster_green():
    try:
        health_json = run(
            "curl -XGET 'http://localhost:9200/_cluster/health?pretty=true'")
        cluster_health = json.loads(health_json)
    except:
        return False

    if cluster_health.get("status") == "green":
        return True
    else:
        return False


@task
def check():
    env.platform_family = detect.detect()

    assert package.installed("java-common")
    assert package.installed("nginx")
    assert file.exists("/usr/local/bin/elasticsearch")
    assert port.is_listening(9200)
    assert port.is_listening(9300)
    assert port.is_listening(8080)
    assert user.exists("elasticsearch")
    assert group.is_exists("elasticsearch")
    assert user.is_belonging_group("elasticsearch", "elasticsearch")
    assert process.is_up("java")
    assert process.is_up("nginx")
    assert service.is_enabled("nginx")
    assert service.is_enabled("elasticsearch")
    assert es_cluster_green(), "Cluster status did not return 'green'"


@task
def artifacts():
    env.platform_family = detect.detect()
    get_artifacts()
