# Utility commands

## Monitoring CPU and GPU

The `monitor` command opens two windows, one for CPU Status and one for GPU status. It will update every `<seconds>` seconds.

```shell
monitor <seconds>
```

The windows can be closed with `Ctrl+C`.
The command calls the subsequent commands `cpustat`and `gpustat`, which should not be called directly.

## Install the NVIDIA Container Toolkit

The `install-container-toolkit` command installs the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker) on the host machine, if it is not already installed.

```shell
install-container-toolkit
```

## List the available Ollama models

The `ollama_models` command lists the available Ollama models with a short description.

```shell
ollama_models
```

The information about the models is retrieved from the [Ollama website](https://ollama.ai/library).

## Control Ollama Docker Container

The `ollama` command controls the Ollama Docker container. It can be used to start and stop the container, get its status and view the logs.

### Start the Ollama Docker Container

The `ollama start` command starts the Ollama Docker container.

```shell
ollama start <port>
```

The `<port>` argument is optional. If not specified, the default port `11434` is used.

### Stop the Ollama Docker Container

The `ollama stop` command stops the Ollama Docker container.

```shell
ollama stop
```

### Get the status of the Ollama Docker Container

The `ollama status` command gets the status of the Ollama Docker container.

```shell
ollama status
```

### View the logs of the Ollama Docker Container

The `ollama logs` command views the logs of the Ollama Docker container.

```shell
ollama logs
```

The log output can be stopped with `Ctrl+C`.

