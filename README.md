# Aranet4 Prometheus Bridge

This app takes readings from an Aranet 4 and exposes them as Prometheus Metrics for scraping

## Build container

Ensure `buildkitd` is running:

```shell
sudo buildkitd --oci-worker=false --containerd-worker=true --containerd-worker-addr=/run/k3s/containerd/containerd.sock
```

Build the image:

```shell
sudo buildctl build \
    --frontend=dockerfile.v0 \
    --local context=. \
    --local dockerfile=. \
    --output type=image,name=aranet4-bridge:202312.1
```

Check the image in the registry:

```shell
sudo k3s ctr --namespace=buildkit images ls
```