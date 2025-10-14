FROM anasty17/mltb:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

RUN python3 -m venv mltbenv

COPY requirements.txt .
RUN mltbenv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

# Setup cookies to database (if DATABASE_URL is set)
# This will run during build and save cookies to MongoDB
RUN if [ -f "setup_cookies.py" ]; then \
        echo "Setting up cookies..." && \
        mltbenv/bin/python3 setup_cookies.py || true; \
    fi

CMD ["bash", "start.sh"]
