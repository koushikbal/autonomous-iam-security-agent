FROM python:3.11-slim
ARG TERRAFORM_VERSION=1.10.4
RUN apt-get update && apt-get install -y --no-install-recommends curl unzip git ca-certificates && rm -rf /var/lib/apt/lists/*
RUN curl -fsSLo /tmp/terraform.zip https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip && unzip /tmp/terraform.zip -d /usr/local/bin && rm /tmp/terraform.zip
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY src ./src
COPY dummy_terraform ./dummy_terraform
ENTRYPOINT ["iam-security-agent"]

