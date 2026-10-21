FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PORT=8000
WORKDIR /app
COPY app ./app
RUN useradd -m appuser && chown -R appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import os,urllib.request as u;u.urlopen('http://127.0.0.1:%s/health'%os.environ.get('PORT','8000'))"
CMD ["python", "-m", "app.server"]
