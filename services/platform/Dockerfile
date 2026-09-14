FROM python:3.12-slim
WORKDIR /workspace
COPY services/platform/requirements.lock /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY services/platform /workspace/services/platform
COPY packages/contracts /workspace/packages/contracts
COPY docs/rebuild/baseline.json /workspace/docs/rebuild/baseline.json
WORKDIR /workspace/services/platform
RUN useradd --system --uid 10001 --create-home movena && chown -R movena:movena /workspace
USER movena
ENV MOVENA_ENV=production
EXPOSE 8020
CMD ["uvicorn", "movena.asgi:application", "--host", "0.0.0.0", "--port", "8020", "--no-access-log"]
