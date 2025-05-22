Note: This is a publicized version of a private Git project, I took out some sensitive information. Don't expect the best documentation. Here be dragons.

## Project Deployment and Development Instructions

### Prerequisites
- **Python Virtual Environment**: Create a virtual environment before installing packages from `requirements.txt`.
- **Redis**: Ensure Redis is installed and running on port 6379 for pass expiration scheduling.
- **Celery**: Required for managing expiring passes.
- **Gunicorn**: For production deployment.

### Environment Setup
1. **Create a Virtual Environment**:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
2. **Install Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```
3. **Create `.env` File**: In the root directory (where `manage.py` is located), create a `.env` file with:
   ```env
   SECRET_KEY="your_secure_secret_key_here"
   ```

### Development Server
1. **Update `settings.py`**:
   - Set `DEBUG` to `True`.
   - Remove any HTTPS-specific configurations.
2. **Run Django Development Server**:
   ```sh
   python manage.py runserver --insecure
   ```
   `--insecure` allows Django to serve static files even with `DEBUG` off.
3. **Run Celery Worker**:
   ```sh
   celery -A NHPA worker --loglevel=INFO
   ```

### Production Server
1. **Update `settings.py`**:
   - Set `DEBUG` to `False`.
   - Add HTTPS configurations as required.
2. **Run Gunicorn**:
   ```sh
   gunicorn --workers 3 NHPA.wsgi:application
   ```
   Using `--workers 3` enables multithreading but adjust based on your requirements.
3. **Run Celery Worker**:
   ```sh
   celery -A NHPA worker --loglevel=INFO
   ```
4. **Setup Web Server**:
   - Use a web server like NGINX or Caddy to serve static files.
