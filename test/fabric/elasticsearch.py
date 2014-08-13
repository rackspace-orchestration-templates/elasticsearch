from fabric.api import env, run, task
from envassert import detect, file, group, package, port, process, service, \
    user


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
