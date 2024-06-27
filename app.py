from flask import Flask, render_template, url_for,request
import os
from datetime import datetime
# import datetime
from openai import AzureOpenAI
import os
import requests
import json

app = Flask(__name__)

IMAGE_FOLDER = 'static/img'
DESCRIPTION_FOLDER = 'descriptions'

user_prompt = ''

#I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:

def get_images_and_descriptions():
    images = []
    for image_filename in os.listdir(IMAGE_FOLDER):
        if image_filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            image_path = os.path.join(IMAGE_FOLDER, image_filename)
            description_path = os.path.join(DESCRIPTION_FOLDER, f"{os.path.splitext(image_filename)[0]}.txt")
            if os.path.exists(description_path):
                with open(description_path, 'r') as file:
                    description = file.read().strip()
            else:
                description = "No description available."
            images.append((image_path, description, os.path.getctime(image_path)))
    # Sort images by creation time, newest first
    images.sort(key=lambda x: x[2], reverse=True)
    return images

@app.route('/')
def index():
    images = get_images_and_descriptions()
    return render_template('index.html', prompt=user_prompt,images=images)

#####################   API KEY and DEPLOYMENT ENPOINT ################

client = AzureOpenAI(
    api_version="2024-02-01",  
    api_key="your API Here ",  
    azure_endpoint="your deployment endpoint here"
)

#######################################################################


@app.route('/', methods=['POST'])
def my_form_post():
    global user_prompt
    user_prompt = request.form['prompt']
    result = client.images.generate(

        ########################## PUT your MODEL NAME HERE ################
            model="your model name ", #MODEL NAME
        ####################################################################

            prompt=user_prompt, #+' I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:',
            n=1
        )
    json_response = json.loads(result.model_dump_json())


    # print(json_response) 'revised_prompt'
    # Initialize the image path (note the filetype should be png)
    current_time = datetime.now()
    name = f'{current_time.year}-{current_time.month}-{current_time.day}-{current_time.hour}-{current_time.minute}-{current_time.second}'
    image_name = name+'.png'
    file_name = 'descriptions/'+name+'.txt'

    file = open(file_name,'w')
    file.write(user_prompt+'\n'+f'<< Revised prompt >> {json_response["data"][0]["revised_prompt"]}')
    file.close()

    # Set the directory for the stored image
    image_dir = os.path.join(os.curdir, 'static/img')

    image_path = os.path.join(image_dir, image_name)
    image_url = json_response["data"][0]["url"]  # extract image URL from response
    generated_image = requests.get(image_url).content  # download the image
    with open(image_path, "wb") as image_file:
        image_file.write(generated_image)

    images = get_images_and_descriptions()
    return render_template('index.html', prompt=user_prompt,images=images)
    


if __name__ == '__main__':
    app.run(debug=True)
