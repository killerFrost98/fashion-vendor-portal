import requests
import PIL.Image
import json
import base64
import io

API_KEY = "AIzaSyD7Si85gthpEPaFF3wlFUtQcIZbMVho2As"  # Replace with your actual Gemini API key
model_name = "gemini-2.5-flash-lite"
image_path = "IMAGE_PATH"  # Replace with the path to your image file

APPAREL_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {
            "type": "string",
            "description": "The main category of the apparel item.",
            "enum": ["Tops", "Bottoms", "Outerwear", "Full Body", "Footwear", "Accessory", "Other"]
        },
        "apparel_type": {
            "type": "string",
            "description": "The specific type of clothing within the category (e.g., 'T-Shirt', 'Jeans', 'Sneakers', 'Handbag')."
        },
        "target_audience": {
            "type": "string",
            "description": "The intended audience for the apparel.",
            "enum": ["Men", "Women", "Unisex", "Kids", "Baby"]
        },
        "main_color": {
            "type": "string",
            "description": "The dominant color of the apparel. Use simple color names (e.g., 'Blue', 'Red', 'Black')."
        },
        "color_palette": {
            "type": "array",
            "description": "An array of all significant colors present in the item.",
            "items": {"type": "string"}
        },
        "material": {
            "type": "string",
            "description": "The likely material of the apparel (e.g., 'Cotton', 'Denim', 'Polyester', 'Leather', 'Wool', 'Silk')."
        },
        "pattern": {
            "type": "string",
            "description": "The pattern on the fabric (e.g., 'Solid', 'Striped', 'Floral', 'Checkered'). If none, use 'Solid'.",
            "enum": ["Solid", "Striped", "Floral", "Checkered", "Polka Dot", "Geometric", "Abstract", "Camouflage", "Animal Print", "Other"]
        },
        "fit": {
            "type": "string",
            "description": "The fit or silhouette of the garment.",
            "enum": ["Slim", "Regular", "Loose", "Oversized", "Fitted", "Straight", "Bootcut", "Not Applicable"]
        },
        "sleeve_length": {
            "type": "string",
            "description": "The length of the sleeves, if applicable.",
            "enum": ["Sleeveless", "Short Sleeve", "Long Sleeve", "Three-Quarter", "Not Applicable"]
        },
        "neckline": {
            "type": "string",
            "description": "The style of the neckline, if applicable.",
            "enum": ["Crew Neck", "V-Neck", "Round Neck", "Collared", "Scoop Neck", "Hooded", "Turtleneck", "Not Applicable"]
        },
        "occasion": {
            "type": "array",
            "description": "Suitable occasions for the item (e.g., 'Casual', 'Formal', 'Sportswear', 'Business').",
            "items": {"type": "string"}
        },
        "style_tags": {
            "type": "array",
            "description": "Descriptive tags for the aesthetic style (e.g., 'Minimalist', 'Vintage', 'Bohemian', 'Streetwear').",
            "items": {"type": "string"}
        },
        "description": {
            "type": "string",
            "description": "A brief, one-sentence summary of the apparel item."
        }
    },
    "required": ["category", "apparel_type", "main_color", "material", "pattern", "description"]
}


def image_to_base64(image: PIL.Image.Image) -> tuple[str, str]:
    # The API supports JPEG and PNG
    image_format = image.format if image.format in ['JPEG', 'PNG'] else 'JPEG'
    mime_type = f"image/{image_format.lower()}"
    
    buffered = io.BytesIO()
    image.save(buffered, format=image_format)
    img_byte = buffered.getvalue()
    
    base64_string = base64.b64encode(img_byte).decode('utf-8')
    return base64_string, mime_type


def generate_apparel_features(image_path: str) -> dict:
    print(f"🖼️  Analyzing image: {image_path}")

    try:
        img = PIL.Image.open(image_path)
    except FileNotFoundError:
        print(f"❌ Error: The file '{image_path}' was not found.")
        return None
    except Exception as e:
        print(f"❌ Error opening image: {e}")
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={API_KEY}"

    base64_image, mime_type = image_to_base64(img)

    prompt = f"""
    You are a fashion and apparel expert. Analyze the clothing item in the provided image.
    Based on your analysis, generate a JSON object that strictly adheres to the following schema.
    Do not add any text or formatting before or after the JSON object.

    JSON Schema:
    {json.dumps(APPAREL_SCHEMA, indent=2)}

    Analyze the image and provide the JSON output.
    """

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": base64_image
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    headers = {"Content-Type": "application/json"}

    print(f"🤖 Sending request to Gemini ({model_name})...")
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        response_data = response.json()
        
        json_string = response_data['candidates'][0]['content']['parts'][0]['text']
        
        print("✅ Successfully received and parsed response from Gemini.")
        return json.loads(json_string)

    except requests.exceptions.RequestException as e:
        print(f"❌ An HTTP error occurred: {e}")
        print(f"   Response Body: {response.text}")
        return None
    except (KeyError, IndexError) as e:
        print(f"❌ Error parsing the API response. Unexpected format: {e}")
        print(f"   Full API Response: {response_data}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding the final JSON object: {e}")
        return None

def main():
    feature_json = generate_apparel_features(image_path)

    print("\n--- Apparel Feature JSON ---")
    print(json.dumps(feature_json, indent=2))

if __name__ == "__main__":
    main()