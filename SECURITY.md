# Security Policy

Open Local AI is pre-alpha software. Only the latest code on the `main` branch is supported.

## Reporting a vulnerability

Please do not open a public issue for a security problem.

- Use GitHub's private vulnerability reporting: open the repository's **Security** tab and choose **Report a vulnerability**.
- Or email [an8702299@gmail.com](mailto:an8702299@gmail.com) with "open-local-ai security" in the subject.

Include what you found, how to reproduce it, and which version or commit you tested. This is a small volunteer project, so responses are best effort.

## Scope

In scope: the code in this repository, such as unsafe handling of input, paths, or environment variables.

Please note that translation providers load model files from your own machine. The project never downloads models automatically, but converting or loading a model can run code from the model's source. Only convert and use models from sources you trust. Problems inside third-party libraries or model weights should be reported to those projects.

## Privacy

The library does not collect text, audio, or telemetry. Please do not paste private or sensitive text into public issues. Use short, non-personal example sentences instead.
