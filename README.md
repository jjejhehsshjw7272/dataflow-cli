# dataflow-cli

Command line helper for loading versioned dataset packs and running
processing pipelines against them.

## Install

```bash
pip install -e .
```

## Usage

```bash
# unpack the bundled dataset pack into the local cache
python3 -m dataflow_cli prepare

# run a pipeline stage against the loaded dataset
python3 -m dataflow_cli run --mode orchestrator
python3 -m dataflow_cli run --mode agent
```

Dataset packs are encrypted archives; the decryption key is provided
through the runtime environment by the deployment platform.
