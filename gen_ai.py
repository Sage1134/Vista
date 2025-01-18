from lumaai import LumaAI
from dotenv import load_dotenv
from os import getenv
import requests
import time

print("Are you sure you want to run? You must run the whole file WITHOUT STOP, or you will be wasting $0.40.")
user_input = input("Proceed? (Y/N) ")

if user_input != "Y":
    raise RuntimeError("User chose to stop.")

HOW_TO_BAKE_BREAD="""How to make Bread:
Proof the yeast: In a large bowl or stand mixer add the yeast, water and a pinch of the sugar or honey. Allow to rest for 5-10 minutes until foaming and bubbly. (This is called “proofing” the yeast, to make sure it is active. If it doesn’t foam, the yeast is no good, and you need to start over with fresh yeast).
Prepare the dough: Add remaining sugar or honey, salt, oil, and 3 cups of flour. Mix to combine. Add another cup of flour and mix to combine. With the mixer running add more flour, ½ cup at a time, until the dough begins to pull away from the sides of the bowl.
Knead the dough: Mix the dough for 5 minutes on medium speed (or knead with your hands on a lightly floured surface, for 5-8 minutes). The dough should be smooth and elastic, and slightly stick to a clean finger, but not be overly sticky.
First Rise: Grease a large bowl with oil or cooking spray and place the dough inside. Cover with a dish towel or plastic wrap and allow to rise in a warm place* until doubled in size (about 1 ½ hours).
Four process photos for making bread dough in a mixer.

5. Punch the dough down really well to remove air bubbles.

6. Divide into two equal portions. Shape each ball into long logs and place into greased loaf pans.

7. Second rise: Spray two pieces of plastic wrap with cooking spray and lay them gently over the pans. Allow dough to rise again for about 45 minutes to one hour, or until risen 1 inch above the loaf pans.

8.Bake: Adjust oven racks to lower/middle position. Preheat the oven to 350 F. Bake bread for about 30-33 minutes, or until golden brown on top. Give the top of a loaf a gentle tap; it should sound hollow.

Four process photos for shaping and baking homemade bread. 

Invert the baked loaves onto a wire cooling rack. Brush the tops with butter and allow to cool for at least 15 minutes before slicing.

A loaf of homemade white bread cooling on a wire rack.

Storing: Once cool, store bread in an airtight container or bag for 2-3 days at room temperature, or up to 5 days in the refrigerator."""

load_dotenv()
LUMA_API_KEY = getenv('LUMA_KEY')

client = LumaAI(
    auth_token=LUMA_API_KEY
)

# How to make bread?
generation = client.generations.create(
    prompt=HOW_TO_BAKE_BREAD, 
    aspect_ratio="4:3", 
    loop=False
)


start = time.time()
completed = False
while not completed:
    generation = client.generations.get(id=generation.id)
    if generation.state == 'completed':
        end = time.time()
        completed = True
    elif generation.state == 'failed':
        end = time.time()
        raise RuntimeError(f"Generation failed: {generation.failure_reason}")
    print("Generating video...")
    time.sleep(3)
    
video_url = generation.assets.video
    
# get the video, once its done
response = requests.get(video_url, stream=True)
with open(f'./videos/{generation.id}.mp4', 'wb') as file:
    file.write(response.content)
print(f"File downloaded as ./videos/{generation.id}.mp4") # - $0.40 per run lol
print(f"Took {end - start} seconds to generate that.")