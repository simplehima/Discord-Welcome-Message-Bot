FROM python:3.9-slim-buster

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire directory
COPY . .

# Install the Arial font
RUN apt-get update && \
    apt-get install -y --no-install-recommends fontconfig && \
    mkdir -p /usr/share/fonts/truetype/msttcorefonts && \
    ln -s /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf /usr/share/fonts/truetype/msttcorefonts/arial.ttf && \
    fc-cache -f -v
COPY . .

CMD [ "python", "bot.py" ]
