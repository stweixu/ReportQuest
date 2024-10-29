import ollama
import aiofiles
import asyncio


class OllamaChat:
    def __init__(self, model_name: str):
        # Initialize with a model name for text or image analysis
        self.model_name = model_name

    async def ask(self, prompt: str) -> str:
        # Generate a text response using ollama asynchronously
        response = await asyncio.to_thread(
            ollama.generate, model=self.model_name, prompt=prompt
        )
        return response["response"]  # Return only the 'response' part

    async def analyze_image(self, image_path: str, prompt: str) -> str:
        # Open the image in binary mode asynchronously
        async with aiofiles.open(image_path, "rb") as image_file:
            image_data = await image_file.read()

        # Generate response based on the image and prompt using the 'llava' model asynchronously
        response = await asyncio.to_thread(
            ollama.generate,
            model="llava",  # Use 'llava' for image-based prompts
            prompt=prompt,
            images=[image_data],  # Pass image as bytes
        )
        return response["response"]  # Return only the 'response' part

    async def compare_analysis_and_description(
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
            f"   - 10: Immediate action required, prioritizing issues where delays could cause irreversible effects, "
            f"       permanent injury, or fatal damage to property\n\n"
            f"Respond only with the numbers in this format: 'X,Y,Z', where:\n"
            f"   - X = Relevance\n"
            f"   - Y = Severity\n"
            f"   - Z = Urgency\n"
        )

        # Get the comparison response asynchronously
        response = await asyncio.to_thread(
            ollama.generate, model=self.model_name, prompt=prompt
        )

        # Return the response as a structured string
        return response["response"].strip()

    async def analyse_image_and_text(
        self, image_path: str, image_prompt: str, text_description: str
    ) -> dict:
        # Analyze an image with a prompt using the 'llava' model asynchronously

        image_prompt = (
            "Provide a brief, factual description of the main action or event occurring in this image. "
            "Only respond with the description. Focus on what is happening, not just what is present, and do not hallucinate or provide factually incorrect information."
        )

        # Await the asynchronous image analysis
        image_analysis = await self.analyze_image(image_path, image_prompt)
        print("Image Analysis Response:", image_analysis)

        # Await the asynchronous comparison for ratings
        ratings = await self.compare_analysis_and_description(
            image_analysis, text_description
        )
        ratings_int = [int(x) for x in ratings.split(",")]

        # Await the asynchronous ask for title generation
        title = await self.ask(
            f"Generate a clear, factual title (under 10 words) for a fault report based on:\n"
            f"description: {text_description}\n"
            f"analysis: {image_analysis}\n"
            f"Only respond with the title, without any additional explanation. "
            f"Make it straightforward and specific, without figurative language. Do not hallucinate or provide factually incorrect information."
        )

        print(title, image_analysis, ratings_int)
        return {"ratings": ratings_int, "title": title}


async def main():
    chat = OllamaChat("llama3.2")

    # Run analyse_image_and_text and await it directly to get results asynchronously
    print("Starting image and text analysis...")
    res_task = asyncio.create_task(
        chat.analyse_image_and_text(
            "images/image.png",
            "What is this image?",
            "Man falling over, with crutches. He is wearing a blue shirt and black pants. The man is sitting on a bench and is looking down at the ground. There are trees in the background.",
        )
    )

    # Simulate doing other tasks while waiting for `analyse_image_and_text` to finish
    print("Doing other tasks while waiting...")
    await asyncio.sleep(100)  # Replace with any other asynchronous work if needed

    # Await the result of the image and text analysis task
    res = await res_task
    print("Analysis result:", res)


if __name__ == "__main__":
    asyncio.run(main())
