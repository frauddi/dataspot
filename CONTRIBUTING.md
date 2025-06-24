# Contributing to Dataspot 🔥

First off, thank you for considering contributing to Dataspot! It's people like you that make open source such a great community. Your help is essential for keeping it great.

Following these guidelines helps to communicate that you respect the time of the developers managing and developing this project. In return, they should reciprocate that respect in addressing your issue, assessing changes, and helping you finalize your pull requests.

## Code of Conduct

This project and everyone participating in it is governed by the [Dataspot Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [elio@frauddi.com](mailto:elio@frauddi.com).

## How Can I Contribute?

We welcome many forms of contributions, including but not limited to:

- 🐛 Reporting bugs
- 💡 Suggesting features and enhancements
- 📝 Improving documentation
- 🔧 Adding new analysis methods or performance improvements

If you're unsure where to start, check the [open issues](https://github.com/frauddi/dataspot/issues) for tasks labeled `good first issue`.

### Reporting Bugs or Suggesting Enhancements

Before creating a new issue, please check the [existing issues](https://github.com/frauddi/dataspot/issues) to see if your problem or idea has already been reported.

If you don't see it, please [open a new issue](https://github.com/frauddi/dataspot/issues/new/choose). Provide as much detail as possible, including steps to reproduce for bugs, and a clear use case for enhancements.

For general questions or ideas, feel free to start a conversation in our [Discussions tab](https://github.com/frauddi/dataspot/discussions).

## Your First Code Contribution

Ready to contribute code? Here's how to set up `Dataspot` for local development.

1. **Fork the repository:** Fork the project on GitHub and then clone your fork locally.

    ```bash
    git clone git@github.com:your-username/dataspot.git
    cd dataspot
    ```

2. **Set up the Development Environment:** The project includes a development setup that installs all necessary tools like `pytest`, `mypy`, and `ruff`.

    ```bash
    # This command installs Dataspot in editable mode and all dev dependencies
    pip install -e ".[dev]"
    ```

    This ensures you have the exact same environment the project's CI uses. We recommend using a Python virtual environment.

3. **Create a branch:** Create a new branch for your changes from the `main` branch.

    ```bash
    # Use a descriptive branch name like 'feature/new-thing' or 'fix/bug-name'
    git checkout -b feature/add-new-export-format
    ```

4. **Make Your Changes:** Write the code for your new feature or bug fix.

5. **Run Tests and Linters:** We use a `Makefile` to run quality checks. Before committing, please run our full suite to ensure your changes pass all checks.

    ```bash
    # This runs all linters (ruff, mypy) and tests (pytest)
    make check

    # You can also run them individually
    make lint
    make tests
    ```

6. **Commit Your Changes:** We follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification. This helps us automate versioning and changelogs.

    ```bash
    # Examples:
    # feat: Add support for exporting patterns to JSON
    # fix: Correctly handle datasets with null values
    # docs: Update README with new performance benchmarks
    git commit -m "feat: Your descriptive commit message"
    ```

7. **Push and Open a Pull Request:** Push your branch to your fork on GitHub and open a Pull Request to the `main` branch of `frauddi/dataspot`.
    - Provide a clear description of the problem and solution in your PR.
    - Include the relevant issue number (e.g., `Closes #123`).
    - Be responsive to feedback from the maintainers.

We will review your PR as soon as possible. Thank you for your contribution!
