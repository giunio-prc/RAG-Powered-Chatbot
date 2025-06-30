# RAG Powered Chatbot

Brief description of the project, what it does, and any important notes.

## Development environment

Before using this template, ensure you have:

- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

correctly installed on your machine.

You can clone the project to your local machine and start developing at your ease by running:
```bash
git clone https://github.com/rag-powered-chatbot.git
```

To run the server in development mode you can use the FastAPI CLI:
```bash
uv run fastapi dev
```
The production mode is:
```bash
uv run fastapi run
```

Once the project is cloned go to the folder `rag-powered-chatbot` and create the environment with `uv` by running
```bash
uv sync
```
The command will create a `.venv` that stores the environment to run the project

You can run a command within the virtual environment by prepending `uv run` to the command.
Alternatively, you can activate the environment and then run the command directly.

If you run on a Linux/Mac OS, you can activate the environment with:
```bash
source .venv/bin/activate
```
If you are on a Windows machine, run instead:
```cmd
.venv\Scripts\activate
```

The development environment comes with pre commit hooks installed with the [pre-commit](https://pre-commit.com/) package.

Pre-commit hooks are commands executed right before commiting such as unit tests, formatter, type check etc...
Before using it, make sure your project is tracked by git.

To use you it, install the hooks by running:
```bash
uv run pre-commit install
```

They will then run automatically before each commit.
You can also run the hooks from the command line as:
```bash
uv run pre-commit run
```
or

Each time you commit hooks will automatically run.
If any of hooks fail, the commit won't be added.
However, only exceptionally, you can bybass the pre-commit hooks
with the option `--no-verify` to the commit command as:

```bash
git commit --no-verify -m "commit message"
```
