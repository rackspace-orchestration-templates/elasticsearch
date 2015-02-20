import json
import os
import re
import yaml

from colorama import Fore, Style, init, deinit
from fabric.api import env, task, run
from envassert import detect, file, group, package, port, process, service, \
    user
from hot.utils.test import get_artifacts
from github3 import GitHub
from pkg_resources import parse_version


def es_cluster_green():
    try:
        health_json = run(
            "curl -XGET 'http://localhost:9200/_cluster/health?pretty=true'")
        cluster_health = json.loads(health_json)
    except:
        print "cluster health query failed to execute."
        return False

    if cluster_health.get("status") == "green":
        return True
    else:
        return False


def latest_template_es_version():
    template = yaml.load(open('elasticsearch.yaml'))
    straints = template.get('parameters').get('es_version').get('constraints')
    versions = []
    for constraint in straints:
        allowed_values = constraint.get('allowed_values')
        if allowed_values:
            versions.extend(allowed_values)
    highest_supported_version = '0.0.0'
    for version in versions:
        if parse_version(version) > parse_version(highest_supported_version):
            highest_supported_version = version
    print "The latest version the template supports is {}.".format(
        highest_supported_version)
    return "v" + highest_supported_version


def check_for_newer_es_release():
    init()
    most_recent_version_supported = latest_template_es_version()
    g = GitHub(token=os.environ.get('GITHUB_TOKEN'))
    repo = g.repository('elasticsearch', 'elasticsearch')
    tags = [t.name for t in repo.tags()]
    version = parse_version(most_recent_version_supported)
    for tag in tags:
        if tag.startswith('v') and not re.search('[Bb]eta', tag):
            assert version >= parse_version(tag), \
                (Fore.RED + Style.BRIGHT + \
                 '\nIt would seem there is a newer version of '
                 'elasticsearch available: {}-- update the template '
                 'to support it!\n' + Fore.RESET + Style.RESET_ALL).format(tag)

    print Fore.GREEN + Style.BRIGHT +                                        \
        "Looks like {} is the most".format(most_recent_version_supported),   \
        "recent version of es. The template supports that, so we're good!" + \
        "\n" + Fore.RESET + Style.RESET_ALL
    deinit()


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
    check_for_newer_es_release()


@task
def artifacts():
    env.platform_family = detect.detect()
    get_artifacts()
