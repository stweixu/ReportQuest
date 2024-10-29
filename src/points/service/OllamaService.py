import ollama


class OllamaChat:
    def __init__(self, model_name: str):
        # Initialize with a model name for text or image analysis
        self.model_name = model_name

    def ask(self, prompt: str) -> str:
        # Generate a text response using ollama
        response = ollama.generate(model=self.model_name, prompt=prompt)
        return response["response"]  # Return only the 'response' part

    def analyze_image(self, image_path: str, prompt: str) -> str:
        # Open the image in binary mode
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        # Generate response based on the image and prompt using the 'llava' model
        response = ollama.generate(
            model="llava",  # Use 'llava' for image-based prompts
            prompt=prompt,
            images=[image_data],  # Pass image as bytes
        )
        return response["response"]  # Return only the 'response' part

    def compare_analysis_and_description(
        self, image_analysis: str, text_description: str
    ) -> str:
        # Generate a prompt for comparison to get numeric ratings for relevance, severity, and urgency
        prompt = (
            f"Based on the details below, please rate each aspect for a fault report:\n\n"
            f"Image Analysis: {image_analysis}\n\n"
            f"Text Description: {text_description}\n\n"
            f"1. **Relevance**: Rate how closely the text description matches the content of the image (1-10).\n"
            f"   - 1: Completely unrelated\n"
            f"   - 5: Partially relevant\n"
            f"   - 10: Highly relevant\n\n"
            f"2. **Severity**: Rate the level of seriousness or potential harm depicted in the image (1-10).\n"
            f"   - 1: Minor issue with little impact\n"
            f"   - 5: Moderate issue that could cause inconvenience\n"
            f"   - 10: Critical issue with high risk or damage\n\n"
            f"3. **Urgency**: Rate the need for immediate action based on the situation (1-10).\n"
            f"   - 1: No action needed\n"
            f"   - 5: Action needed soon\n"
            f"   - 10: Immediate action required\n\n"
            f"Respond only with the numbers in this format: 'X,Y,Z', where:\n"
            f"   - X = Relevance\n"
            f"   - Y = Severity\n"
            f"   - Z = Urgency\n"
        )

        # Get the comparison response
        response: str = ollama.generate(model=self.model_name, prompt=prompt)

        # Return the response as a structured string
        return response["response"].strip()

    async def analyse_image_and_text(
        self, image_path: str, image_prompt: str, text_description: str
    ) -> str:
        # Analyze an image with a prompt using the 'llava' model
        image_path = "images/image.png"  # Replace with your image path
        image_prompt = "What is this image?"
        image_analysis = self.analyze_image(image_path, image_prompt)
        print("Image Analysis Response:", image_analysis)

        # Example text description to compare
        text_description = "Man falling over, with crutches. He is wearing a blue shirt and black pants. The man is sitting on a bench and is looking down at the ground. There are trees in the background."
        ratings = self.compare_analysis_and_description(
            image_analysis, text_description
        )
        # print(ratings)  # Print the structured output of ratings
        ratings_int = [int(x) for x in ratings.split(",")]

        # ask to generate a title from description
        title = self.ask(
            f"Generate a title in under 10 words for the given:\ndescription: {text_description}\nanalysis: {image_analysis}"
        )
        # print(title)

        return {"ratings": ratings_int, "title": title}


# Usage Example
if __name__ == "__main__":
    # Initialize the chat model with a text-based model like 'llama2'
    chat = OllamaChat("llama3.2")

    # Analyze an image with a prompt using the 'llava' model
    image_path = "images/image.png"  # Replace with your image path
    image_prompt = "What is this image?"
    image_analysis = chat.analyze_image(image_path, image_prompt)
    print("Image Analysis Response:", image_analysis)

    # Example text description to compare
    text_description = "Man falling over, with crutches. He is wearing a blue shirt and black pants. The man is sitting on a bench and is looking down at the ground. There are trees in the background."
    ratings = chat.compare_analysis_and_description(image_analysis, text_description)
    print(ratings)  # Print the structured output of ratings

    # ask to generate a title from description
    title = chat.ask(
        f"Generate a title in under 10 words for the given:\ndescription: {text_description}\nanalysis: {image_analysis}"
    )
    print(title)
