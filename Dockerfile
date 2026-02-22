# Use a lightweight "slim" image for production
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install Chrome and dependencies for Selenium
RUN apt-get update && apt-get install -y \
    # Install tools needed to download files (wget), handle encryption keys (gnupg), and verify SSL certificates.
    wget \
    gnupg \
    ca-certificates \
    # Download Google’s public GPG key
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    # Add Google’s official server to your system’s "address book" of software sources
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    # Update system
    && apt-get update \
    # Install Google Chrome browser
    && apt-get install -y google-chrome-stable \
    # Delete the temporary list of packages downloaded in step 1
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
# (Doing this before copying your code makes future builds much faster!)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose the Streamlit port
EXPOSE 8501

# Start the Streamlit server
CMD ["streamlit", "run", "streamlit_app.py", "--server.enableCORS", "false", "--server.enableXsrfProtection", "false"]