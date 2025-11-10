# Dockerfile

# ---- Build Stage ----
# Use a full Python image to build dependencies
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install uv - a fast Python package installer
RUN pip install uv

# Copy requirements file
COPY requirements.txt .

# Create a virtual environment and install dependencies using uv
RUN python -m venv /opt/venv
RUN . /opt/venv/bin/activate && uv pip install --no-cache-dir -r requirements.txt


# ---- Final Stage ----
# Use a slim Python image for the final application
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application source code
COPY ./src ./src
COPY ./prefect_data ./prefect_data
COPY ./.env .

# Expose the port Gradio will run on
EXPOSE 7860

# Command to run the application
# We use `gradio` CLI to run the app which is better for production
CMD ["gradio", "src/app.py", "--server_name", "0.0.0.0", "--server_port", "7860"]