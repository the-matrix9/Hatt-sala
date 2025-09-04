import requests
import webbrowser

class ChatGptEs:
    TEXT_API = "https://chatapi.anshppt19.workers.dev/?prompt="
    IMAGE_API = "https://direct-img.rishuapi.workers.dev/?prompt="

    def ask_question(self, message: str) -> str:
        try:
            lower_msg = message.lower()

            # Agar image related keyword hai toh image API use karo
            trigger_words = ["image", "pic", "photo", "draw", "make picture", "generate image"]

            if any(word in lower_msg for word in trigger_words):
                # Keyword ke baad ka text nikaalo
                for word in trigger_words:
                    if word in lower_msg:
                        # Example: "generate image of a cat" -> "of a cat"
                        prompt = message.lower().split(word, 1)[-1].strip()
                        break

                if not prompt:  # Agar keyword ke baad kuch nahi likha
                    prompt = "random cute wallpaper"

                url = self.IMAGE_API + requests.utils.quote(prompt)
                return url   # Image link return karo
            else:
                # Text API call
                url = self.TEXT_API + requests.utils.quote(message)
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                return data.get("reply", "❖ Error: Text API ne reply nahi diya.").strip()

        except Exception as e:
            return f"❖ I got an error: {str(e)}"


# Example run
chatbot_api = ChatGptEs()

# Text reply
print(chatbot_api.ask_question("Hello Taunu ❤️"))

# Image generation
image_url = chatbot_api.ask_question("Generate image of a cute anime cat")
print(image_url)

# Browser me image kholne ke liye
webbrowser.open(image_url)