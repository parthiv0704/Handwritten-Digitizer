import requests
import os

def test_download():
    url = "http://localhost:5002/download"
    content = "This is a test content for verification.\nLine 2.\nLine 3."
    
    formats = ['txt', 'json', 'pdf']
    
    for fmt in formats:
        print(f"Testing {fmt} download...")
        try:
            html_content = f"<h1>Test Title</h1><p>{content}</p>"
            response = requests.post(url, data={'content': content, 'html_content': html_content, 'format': fmt})
            if response.status_code == 200:
                filename = f"test_result.{fmt}"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"Success: {filename} downloaded. Size: {os.path.getsize(filename)} bytes")
                
                # Basic content check
                if fmt == 'txt':
                    with open(filename, 'r') as f:
                        downloaded_content = f.read()
                        if content in downloaded_content:
                            print("Content verification passed.")
                        else:
                            print("Content verification failed.")
                elif fmt == 'json':
                    import json
                    with open(filename, 'r') as f:
                        data = json.load(f)
                        if data['content'] == content:
                            print("Content verification passed.")
                        else:
                            print("Content verification failed.")
                elif fmt == 'pdf':
                    # Just check if it's a valid PDF header
                    with open(filename, 'rb') as f:
                        header = f.read(4)
                        if header == b'%PDF':
                            print("PDF header verification passed.")
                        else:
                            print("PDF header verification failed.")
            else:
                print(f"Failed: Status code {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
            
if __name__ == "__main__":
    test_download()
