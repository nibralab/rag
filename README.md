# AI Prototyping

## Installation

1. Clone the repository
2. Run `docker compose up -d`
3. Enjoy!

The API is available at `http://localhost:5000`.

Ollama is available directly at `http://localhost:11434`.

## Pulling Models

To pull models, enter the `ollama` container and run `ollama pull <model_name>`.

~~~
$ docker compose exec ollama bash
root@ollama:/# ollama pull <model_name>
~~~

