# Environment classes

We support various environments for executing code through different backends.

If you run `mini`, you will run in the `local` environment by default.

However, particularly for evaluating on SWE-bench, we offer multiple environment backends that you can use.

You can specify the environment class with the `--environment-class` flag or the
`environment.environment_class` key in the [agent config file](yaml_configuration.md).

* **`local`** ([`LocalEnvironment`](../reference/environments/local.md)). Executes commands directly on the host machine using `subprocess.run`. No isolation. Directly works in your current python environment.

* **`docker`** ([`DockerEnvironment`](../reference/environments/docker.md)). Executes commands with `docker exec`.

* **`singularity`** ([`SingularityEnvironment`](../reference/environments/singularity.md)) - Executes commands in Singularity/Apptainer containers. Good alternative to Docker in HPC environments where Docker is not available.

On top, there are a few more specialized environment classes that you can use:

* **`swerex_docker`** ([`SwerexDockerEnvironment`](../reference/environments/swerex_docker.md)) - Docker execution through [SWE-ReX](https://github.com/swe-agent/swe-rex)

* **`bubblewrap`** ([`BubblewrapEnvironment`](../reference/environments/bubblewrap.md)) - **Linux only**. Uses [bubblewrap](https://github.com/containers/bubblewrap) for lightweight, unprivileged sandboxing. Experimental.
