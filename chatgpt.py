# coding: utf-8
import asyncio
import aiohttp
import requests
import json
from .config import Config

default_md_promt = """
I'd like you to help me create Midjourney prompts. Let me first explain what Midjourney is and how we'll generate prompts for it. We'll also go through 20 examples to ensure you understand.
Midjourney is an AI tool that makes images from user's input, similar to DALL-E.
The key part of the prompt are words or phrases that describe the image you want. More adjectives and specific descriptive nouns create unique images. On the contrary, basic nouns or adjectives make plain images. Keep in mind, Midjourney doesn't understand grammar. So, very long prompts may not work well. When creating prompts, remove any unnecessary words. Fewer words give each word more importance, ensuring the image aligns with your theme.
For instance, "illustrate for me a beautiful sunset over a serene ocean, make the colors warm and soothing, and render it in an impressionistic style." This prompt has words that Midjourney might not understand or work with. Phrases like "Illustrate for me" are unnecessary. Verbs like "make" and "render" are also redundant. Midjourney usually accepts descriptive words like nouns and adjectives. The prompt could be simpler: "warm soothing sunset over serene ocean, impressionistic oil paint."
More specific synonyms often work better than general ones. For example, use precise words like "petite", "compact", "diminutive" and "tiny" instead of "small". When creating your prompt, focus on specific details you want:
• Theme: People, animals, places, character, objects, events, etc.
• Use Case: Logos, web design, interior design, prototypes, product design, etc.
• Medium: Photos, drawings, illustrations, paintings, cartoons, watercolors, collages, sculptures, graffiti, mosaics, tapestries, pottery, etc.
• Environment: Indoor, outdoor, city, forest, island, desert, underwater, cave, future city, space, moon, space station, etc.
• Lighting: Soft, twilight, ambient, direct sunlight, overcast, moonlight, neon, candlelight, firelight, etc.
• Color: Vibrant, muted, bright, monochromatic, colorful, black and white, pastel, etc.
• Mood: Energetic, sedate, calm, raucous, restless, melancholy, dreamy, mysterious, etc.
• Composition: Portrait, close-up, headshot, bird's eye view, symmetrical, leading lines, minimalist, silhouette, panorama, etc.
• Artists: Van Gogh, Picasso, Dali, Paul Cézanne, Leonardo da Vinci, Botticelli, Rembrandt, Hayao Miyazaki, etc.
• Art styles: Oriental landscape painting, Ukiyo-e, conceptual art, Bauhaus, Impressionism, Rococo, Surrealism, long exposure, etc.
You can also use a comma, plus sign, or "and" to separate different subjects. For instance, to depict a light and a house, you should separate them. Otherwise, if you type "light house," Midjourney will show you a lighthouse.
With this knowledge, we'll now explore 20 examples of prompts:
1. white cow inside pink flowers in style of national geographic photography
2. Giraffee, tropical, Paul Klee style, surreal masterpiece, octane rendering, focus, colorful background, detailed, intricate details, rich colors
3. a girl with long dark hair wearing a black hat, in the style of childlike innocence and charm, detailed facial features, enchanting, 32k uhd, rococo whimsy, ferrania p30, cartoon realism
4. she is posing in black and gold, in the style of eye-catching resin jewelry, urban decay, rim light, iconic, exotic, bold, cartoonish lines, meticulous design
5. Smiling sunflower, Paul Klee style, surreal masterpiece, artistic, focus, colorful background, detailed, intricate details, rich colors
6. falkor by Atey Ghailan and John Singer Sargent, Neverending Story
7. SSSniperwolf Nelliel Tu Odelschwanck from Bleach cosplay for women with cosplay sleeve, in the style of light emerald and light cyan, appropriation artist, anime influenced, exaggerated expressions, made of vines, heistcore, bombacore
8. a gold fish with human swimming in a bathtub filled with clouds, in the style of dusseldorf school of photography, 1970s, balloon
9. cinematic medieval interior photography in the style of Akos Major, Fine art
10. Young woman, long red hair, glasses, looking in camera with a small beautiful smile, red dress, futuristic background
11. 3D cartoon art, painting, Cats on the roof, masterpiece, octane rendering, focus, colorful background, detailed, intricate details, rich colors
12. abstract futuristic dystopian Japanese fashion craze, vibrant abstract surreal photography by Ed Emshwiller and Masamune Shirow and Beeple
13. A cyberpunk-inspired full-length illustration featuring a futuristic tight-fitting suit. The suit wraps the wearer's body with a snug fit, exuding an air of sleekness and functionality. Embedded within the suit's fabric are numerous tactile sensors, meticulously integrated to provide enhanced tactile feedback and data analysis. A holographic layer is projected onto the suit's surface, producing shifting patterns and colors that mesmerize the viewer. Set against a black background, the suit stands out, evoking a sense of mystery and futuristic elegance. Illustration, digital art, brings this vision to life with meticulous attention to detail
14. oldtimer car in front of a vintage sunset, vintage tshirt design vector graphics, detail design contour, turqoise, pink, neon colors, white background
15. Sunset over the sea, dramatic clouds, masterpiece, octane rendering, focus, realistic photography, colorful background, detailed, intricate details, rich colors, realistic style
16. a large room with a center island and wooden flooring, in the style of dark bronze and dark beige, dark gray and dark black, rustic scenes, avocadopunk, cabincore, multiple styles, dark white and gray
17. knight of thorns woman in a spotlight, gradient, vector, fiberoptic, Hokusai, Banner Saga, glossy, cel shaded
18. traditional slavic folkloric monster, baba yaga, wurdulac, upyr in the style of alberto seveso
19. a teenage girl in black fur wears purple lipstick, in the style of monochromatic color schemes, dark brown and dark black, urban decay, bold yet graceful, emila medková, eye-catching, double tone effect
20. a girl with colorful eye makeup and a star shaped haircut, in the style of acidwave, dark brown and dark azure, sumi-e inspired, superheroes, babycore, bec winnel
You've learned how to use Midjourney prompt words by examples. Now, let them inspire you. I'll share brief image ideas. Your task? Turn them into full, clear, creative prompt words. From now on, I'll just give you my ideas. You'll then provide two Midjourney prompts for each. Make sure you have added all the available parameters.

Your task is to output json, whose keys is "prompt", value is the whole prompt, only one response is fine.
The following is the short idea I ask you, please output according to the above rules:

 """

default_sd_prompt = """
	You will act as an assistant with an artistic flair for Stable Diffusion prompts. I will communicate to you the theme of the prompt using natural language, and your task will be to imagine a complete picture based on this theme, then translate it into a detailed, high-quality prompt that enables Stable Diffusion to generate high-quality images.
Stable Diffusion is a model that uses deep learning for text-to-image generation, supporting the creation of new images by using prompts to describe elements to include or exclude.
Concept of prompt:
- The prompt describes an image and consists of common English words separated by commas (",").
- Each word or phrase separated by a comma is called a tag. Thus, both prompt and negative prompt are series of tags separated by commas.
() and [] syntax:
- To adjust the strength of a keyword, use () and [].
- (keyword) increases the strength of a tag by 1.1 times, same as (keyword:1.1), and can be nested up to three times.
- [keyword] decreases the strength by 0.9 times, same as (keyword:0.9).
Prompt Format Requirements:
Next, I will explain the steps to generate a prompt. This prompt can be used to describe characters, landscapes, objects, or abstract numerical art paintings. You can add reasonable details as required, but not less than five.
1. Prompt requirements:
- The content of the prompt should include the main subject, texture, additional details, image quality, artistic style, color tone, and lighting, but the prompt you produce cannot be segmented, and descriptors like "medium:" are not required and cannot include ":" or "."
- Main subject: A brief English description of the main subject, such as A girl in a garden, summarizing the main details (the subject can be a person, event, object, or scenery). This part is generated based on the theme you give me each time. You can add more reasonable details related to the theme.
- For character themes, you must describe the character's eyes, nose, lips, for example, 'beautiful detailed eyes, beautiful detailed lips, extremely detailed eyes and face, long eyelashes' to prevent Stable Diffusion from randomly generating deformed facial features. This is very important. You can also describe the character's appearance, emotion, clothing, posture, viewpoint, action, background, etc. In character attributes, 1girl means one girl, 2girls means two girls.
- Texture: Materials used to create the artwork, such as illustration, oil painting, 3D rendering, and photography. Medium has a strong effect because a single keyword can greatly change the style.
- Additional details: Scene details or character details, describing the content of the image details to make the image look fuller and more reasonable. This part is optional, and the overall harmony of the picture should be noted so as not to conflict with the theme.
- Image quality: This part should always start with "(best quality, 4k, 8k, highres, masterpiece:1.2), ultra-detailed, (realistic, photorealistic, photo-realistic:1.37)," which are indicators of high quality. Other commonly used quality-improving tags include HDR, UHD, studio lighting, ultra-fine painting, sharp focus, physically-based rendering, extreme detail description, professional, vivid colors, bokeh, and you can add them according to the needs of the theme.
- Artistic style: This part describes the style of the image. Adding the appropriate artistic style can enhance the effect of the generated image. Common artistic styles include portraits, landscape, horror, anime, sci-fi, photography, concept artists

Your task is to output json, whose keys is "prompt", value is the whole prompt, only one response is fine.
The following is the short idea I ask you, please output according to the above rules:
"""


class OpenAIClient(object):
	def __init__(self, api_key="", config_path=None):
		self.url = "https://chat.inhyperloop.com/v1/chat/completions"
		if not api_key:
			config = Config(config_path=config_path)
			self.api_key = config.gpt_api_key

	def expand_prompt(self, user_prompt, prompt=None, prompt_type="md"):
		if not prompt:
			if prompt_type == "MD":

				prompt = default_md_promt
			elif prompt_type == "SD":
				prompt = default_sd_prompt

		else:
			prompt += 'Your task is to output json, whose keys is "prompt", value is the whole prompt, only one response is fine. \
						The following is the short idea I ask you, please output according to the above rules:'
		headers = {
			"Content-Type": "application/json",
			"Authorization": "Bearer {}".format(self.api_key),
		}
		default_prompt = {"role": "system", "content": prompt}
		user_message = {"role": "user", "content": user_prompt}
		data = {
			# "model": "gpt-4-0314",
			"model": "gpt-4-1106-preview",
			"messages": [default_prompt, user_message],
			"temperature": 0.7,
			"response_format": {"type": "json_object"},
		}
		resp = requests.post(self.url, json.dumps(data), headers=headers)
		resp = resp.json()
		choices = resp.get("choices", [])
		if not choices:
			# send_slack_alerts("get_ai_reply_error, ai_response_error, need check!!!")
			print(f"open_ai_reply, no_choices, reply: {resp}, user_message: {user_message}")
			return ""
		content = choices[0].get("message", {}).get("content", "")
		print(
			f"open_ai_reply, user_prompt: {user_prompt},  reply: {content}, resp:{resp}"
		)
		resp_prompt = json.loads(content).get("prompt", "")
		return resp_prompt


class OpenAIClientAsync(OpenAIClient):

	async def post(self, data, headers):
		async with aiohttp.ClientSession() as session:
			async with session.post(self.url, data=json.dumps(data), headers=headers) as resp:
				resp_json = await resp.json()
				return resp_json

	async def _expand_prompt_single(
		self, user_prompt, prompt=None, prompt_type="md"
	):
		if not prompt:
			if prompt_type == "MD":

				prompt = default_md_promt
			elif prompt_type == "SD":
				prompt = default_sd_prompt
		headers = {
			"Content-Type": "application/json",
			"Authorization": "Bearer {}".format(self.api_key),
		}
		default_prompt = {"role": "system", "content": prompt}
		user_message = {"role": "user", "content": user_prompt}
		data = {
			# "model": "gpt-4-0314",
			"model": "gpt-4-1106-preview",
			"messages": [default_prompt, user_message],
			"temperature": 0.7,
			"response_format": {"type": "json_object"},
		}
		resp = await self.post(data, headers)
		choices = resp.get("choices", [])
		if not choices:
			# send_slack_alerts("get_ai_reply_error, ai_response_error, need check!!!")
			print(f"open_ai_reply, no_choices, reply: {resp}")
			return ""
		content = choices[0].get("message", {}).get("content", "")
		print(
			f"open_ai_reply, user_prompt: {user_prompt},  reply: {content}, resp:{resp}"
		)
		resp_prompt = json.loads(content).get("prompt", "")
		return resp_prompt

	async def expand_prompt_batch(
		self, user_prompt_list, prompt=None, prompt_type="md"
	):
		
		tasks = [
			self._expand_prompt_single(user_prompt, prompt, prompt_type)
			for user_prompt in user_prompt_list
		]

		results = await asyncio.gather(*tasks)
		return results
	
	def expand_prompt(self, user_prompt_list, prompt=None, prompt_type="md"):
		results = asyncio.run(self.expand_prompt_batch(user_prompt_list, prompt, prompt_type))

		print(f"expand_prompt, results:{results}")
		return results



open_ai_client = OpenAIClient()
open_ai_client_async = OpenAIClientAsync()
