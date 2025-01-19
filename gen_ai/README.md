The gen ai backend for Vista. Generates a series of videos to accompany the steps.

HOW TO SET UP:

1. Create a ```.env``` file in root. Within, add ```OPENAI_API_KEY=your OpenAI API Key```.
2. Run ```pip install -r requirements.txt```
3. Import ```VideoMaker``` class from ```backend_ai.py```. 
4. Initialize a ```VideoMaker``` object with some FPS you desire (typically 5, or some value in range 1-10)
5. Feed user input as a plain string to the object via its ```conv_resp_to_videos``` function.
6. Read videos from ```./OUTPUT``` folder.