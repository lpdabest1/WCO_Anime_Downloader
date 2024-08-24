from flask import Flask, request, jsonify, Response
from playwright.sync_api import sync_playwright
import requests
from PIL import Image
from io import BytesIO
import os
import logging
from flask_cors import CORS  # Import CORS
import base64  # Import base64 module
import time # Import time for simulation of real-time logging

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) # Enable CORS for all routes

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Change level to DEBUG for detailed logs

# In-memory list to store log messages
action_logs = []

# Global variable to hold current log message for SSE
current_log_message = ""

def log_message(message):
    global current_log_message
    current_log_message = message
    action_logs.append(message)

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/test')
def test():
    return "This is a test route!"

@app.route('/logs', methods=['GET'])
def stream_logs():
    def event_stream():
        global current_log_message
        previous_message = ""
        while True:
            if current_log_message != previous_message:
                yield f'data: {current_log_message}\n\n'
                previous_message = current_log_message
            time.sleep(1)
    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/scrape', methods=['POST'])
def login_and_scrape():
    data = request.json
    sign_in_url = data.get('sign_in_url')
    username = data.get('username')
    password = data.get('password')
    anime_url = data.get('anime_url')
    download_folder = data.get('download_folder')
    
    print(f"Received data: {data}")
    print(f"Sign-In URL: {sign_in_url}")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Anime URL: {anime_url}")
    print(f"Download Folder: {download_folder}")

    ### Original Code has been commented out for testing purposes
    '''
    sign_in_url = data['sign_in_url']
    username = data['username']
    password = data['password']
    anime_url = data['anime_url']
    download_folder = data['download_folder']
    '''

    #print(f"Received data: {data}")

    # Log received data
    log_message(f"Received data: {data}")
    log_message(f"Sign-In URL: {sign_in_url}")
    log_message(f"Username: {username}")
    log_message(f"Anime URL: {anime_url}")
    log_message(f"Download Folder: {download_folder}")


    try:
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            page = browser.new_page()

            page.goto(sign_in_url)
            page.fill('#user_login', username)
            page.fill('#user_pass', password)
            page.click('#wp-submit')

            page.wait_for_selector('div.header-top-right > span')
            span_content = page.locator('div.header-top-right > span').text_content()
            print(span_content)
            log_message(f"Logged in successfully: {span_content}")


            page.goto(anime_url)
            page.wait_for_selector('h1 div a')

            link_element = page.locator('div h1 a')
            anime_title = link_element.inner_text().strip().replace('/', '_')
            print(f'Navigated to new URL: {page.url}\nAnime Title: {anime_title}')
            log_message(f'Navigated to new URL: {page.url}\nAnime Title: {anime_title}')

            anime_folder = os.path.join(download_folder, anime_title)
            os.makedirs(anime_folder, exist_ok=True)

            anime_image_element = page.locator('img.img5')
            image_src = anime_image_element.get_attribute('src')

            response = requests.get(f'https:{image_src}')
            image_data = BytesIO(response.content)
            image = Image.open(image_data)
            image_path = os.path.join(anime_folder, f"{anime_title}.jpg")
            image.save(image_path)

            log_message(f"Anime image saved to: {image_path}")

            # Convert the image to base64
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            image_data_url = f"data:image/jpeg;base64,{image_base64}"

            page.wait_for_selector('a#download-links')
            page.locator('a#download-links').click()
            page.wait_for_selector('div#div-download')

            def check_link(url):
                try:
                    response = requests.head(url, allow_redirects=True)
                    return response.status_code == 200
                except requests.RequestException as e:
                    print(f"An error occurred while checking the link: {e}")
                    log_message(f"An error occurred while checking the link: {e}")
                    return False

            download_sections = page.locator('div#div-download > div')
            download_results = []

            for i in range(download_sections.count()):
                section = download_sections.nth(i)
                section_text = section.inner_text().splitlines()[0].strip()
                links = section.locator('a')
                video_links = []

                for j in range(links.count()):
                    video_link = links.nth(j).get_attribute('href')

                    if video_link and ('.mkv' in video_link or '.mp4' in video_link):
                        if check_link(video_link):
                            video_links.append((video_link, section_text))

                prioritized_links = sorted(
                    video_links,
                    key=lambda x: (
                        '.mkv' not in x[0],
                        '1080' not in x[0],
                        '720' not in x[0]
                    )
                )

                if prioritized_links:
                    highest_quality_link, highest_quality_text = prioritized_links[0]
                    video_response = requests.get(highest_quality_link, stream=True)
                    video_filename = f"{highest_quality_text}.mp4" if '.mp4' in highest_quality_link else f"{highest_quality_text}.mkv"
                    video_path = os.path.join(anime_folder, video_filename)

                    with open(video_path, 'wb') as video_file:
                        for chunk in video_response.iter_content(chunk_size=65536):
                            if chunk:
                                video_file.write(chunk)

                    #download_results.append(f"Episode '{highest_quality_text}' downloaded and saved to: {video_path}")
                    download_results.append(f"{highest_quality_text} downloaded and saved to: {video_path}")
                    log_message(f"Downloaded {video_filename} to {video_path}")
                else:
                    download_results.append(f"No valid video links found for episode: {section_text}")
                    log_message(f"No valid video links found for episode: {section_text}")

            browser.close()
            log_message("Browser closed, scraping completed.")
            return jsonify({'message': 'Scraping completed', 'anime_title': anime_title, 'downloads': download_results, 'image_path': image_path, 'image_data_url': image_data_url})

    except Exception as e:
        print(f"An error occurred: {e}")
        log_message(f"An error occurred: {e}")
        return jsonify({'message': 'Scraping failed', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, threaded=True, use_reloader=False)
