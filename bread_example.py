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

HOW_QUESTION="How do I bake bread?"

# Only one action allowed per step
# No implicit conditions
# "Give a short and direct summary of the step."

# Use GPT to transform user input into steps for video generation?

# BREAD_STEPS = [
#     "In a large bowl or stand mixer add the yeast, water and a pinch of the sugar or honey."
#     "Allow to rest for 5-10 minutes until foaming and bubbly.",
#     "Prepare the dough: Add remaining sugar or honey, salt, oil, and 3 cups of flour. Mix to combine.", 
#     "Add another cup of flour and mix to combine.",
#     "With the mixer running add more flour, ½ cup at a time, until the dough begins to pull away from the sides of the bowl.",
#     "Grease a large bowl with oil or cooking spray and place the dough inside.",
#     "Cover with a dish towel or plastic wrap and allow to rise in a warm place until doubled in size.",
#     "Bake dough in oven at 350F."
# ]

BREAD_STEPS = [
    "Proof the yeast: Add the yeast, water, and a pinch of sugar or honey to a bowl.",  
    "Allow the mixture to rest for 5-10 minutes until foaming and bubbly.",  
    "Discard the yeast if it does not foam.",  
   " Prepare the dough: Add sugar or honey, salt, oil, and 3 cups of flour.",  
    "Mix the ingredients to combine.",  
    "Add another cup of flour and mix again.",  
    "Add more flour, ½ cup at a time, until the dough pulls away from the bowl.",  
    "Knead the dough: Knead the dough for 5 minutes on medium speed.",  
    "Ensure the dough is smooth and elastic.", 
    "First Rise: Grease a large bowl with oil or cooking spray.",  
    "Place the dough inside the greased bowl.",  
    "Cover the bowl with a dish towel or plastic wrap.",  
    "Allow the dough to rise in a warm place until doubled in size.",  
    "Punch the dough down to remove air bubbles.",  
    "Divide the dough into two equal portions.",  
    "Shape each portion into long logs.",  
    "Place the logs into greased loaf pans.",
    "Second Rise: Spray plastic wrap with cooking spray.",
    "Lay the plastic wrap gently over the pans.",
    "Allow the dough to rise until it is 1 inch above the loaf pans.",
    "Bake: Adjust oven racks to a lower-middle position.",  
    "Preheat the oven to 350°F.",
    "Bake the bread for 30-33 minutes until golden brown.",
    "Tap the top of the loaf to check if it sounds hollow.",
    "Invert the baked loaves onto a wire cooling rack.",
    "Brush the tops with butter.",  
    "Allow the loaves to cool for at least 15 minutes.",
    "Store the bread in an airtight container or bag once cooled."
]

BAD_BREAD_STEPS = [
    "Mix chlorine and bleach.",
    "Inhale deeply."
]