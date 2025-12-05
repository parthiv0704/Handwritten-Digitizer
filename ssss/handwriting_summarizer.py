import os
import base64
import argparse
import sys
from groq import Groq
from pdf2image import convert_from_path
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def encode_image(image_path):
    """Encodes an image file to a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def enhance_resolution(path):
    """Enhances image resolution using Pillow (2x upscale)."""
    try:
        img = Image.open(path)
        # Resize by factor of 2 using LANCZOS resampling
        img = img.resize((img.width * 2, img.height * 2), Image.Resampling.LANCZOS)
        
        # Create new filename
        directory, filename = os.path.split(path)
        name, ext = os.path.splitext(filename)
        enhanced_filename = f"{name}_hd{ext}"
        enhanced_path = os.path.join(directory, enhanced_filename)
        
        img.save(enhanced_path)
        return enhanced_path
    except Exception as e:
        print(f"Error enhancing image: {e}")
        return path

def convert_pdf_to_images(pdf_path):
    """Converts a PDF file to a list of images."""
    try:
        return convert_from_path(pdf_path)
    except Exception as e:
        print(f"Error converting PDF: {e}")
        return []

def get_groq_client():
    """Initializes and returns the Groq client."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY environment variable not set.")
        print("Please set it in your environment or a .env file.")
        sys.exit(1)
    return Groq(api_key=api_key)

def process_image_with_model(client, base64_image, language):
    """Sends the image to the Groq API for processing."""
    
    prompt = f"""
    Analyze the handwritten image and perform the following tasks:

    1. **Handwriting OCR**: Digitize the handwritten text accurately.
    2. **Table Extraction**: Detect and extract any tables. Output them in both Markdown and CSV format.
    3. **Context-Aware Correction**: If the handwriting is unclear, use context to intelligently correct or reconstruct missing/incomplete words. Fix grammar & spelling while keeping the original meaning.
    4. **Summary**: Provide a concise summary of the content in {language}.

    Output Format:
    ---
    **Digitized Text:**
    [The recognized text]

    **Detected Tables (Markdown):**
    [Markdown table representation, or "No tables detected"]

    **Detected Tables (CSV):**
    [CSV table representation, or "No tables detected"]

    **Summary ({language}):**
    [The summary in {language}]
    ---
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error processing image: {e}"

def main():
    parser = argparse.ArgumentParser(description="Handwriting Recognition and Summarizer")
    parser.add_argument("input_file", help="Path to the image or PDF file")
    parser.add_argument("--lang", default="English", help="Target language for the summary (e.g., Hindi, Tamil, Bengali)")
    
    args = parser.parse_args()
    
    input_path = args.input_file
    language = args.lang
    
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        return

    client = get_groq_client()
    
    print(f"Processing '{input_path}'...")
    print(f"Target Language: {language}")

    if input_path.lower().endswith('.pdf'):
        print("Converting PDF to images...")
        images = convert_pdf_to_images(input_path)
        
        if not images:
            print("No images extracted from PDF.")
            return

        # Process the first page for now, or loop through all
        # For simplicity in this script, we'll process the first page. 
        # You can extend this to loop through `images`.
        print(f"Processing first page of PDF (Total pages: {len(images)})...")
        
        # Save temp image to encode
        temp_img_path = "temp_page_0.jpg"
        images[0].save(temp_img_path, 'JPEG')
        
        base64_image = encode_image(temp_img_path)
        result = process_image_with_model(client, base64_image, language)
        print("\n" + result)
        
        # Cleanup
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)
            
    else:
        # Assume it's an image
        try:
            base64_image = encode_image(input_path)
            result = process_image_with_model(client, base64_image, language)
            print("\n" + result)
        except Exception as e:
            print(f"Error processing file: {e}")

if __name__ == "__main__":
    main()
