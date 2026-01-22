import os
import json
import shutil
import urllib.parse
import requests

Galery_Url = "https://gallery.isic-archive.com/#!/topWithHeader/onlyHeaderTop/gallery?filter=%5B%22fitzpatrick_skin_type%7CVI%22%2C%22fitzpatrick_skin_type%7CV%22%2C%22fitzpatrick_skin_type%7CIV%22%5D&name="

Local_Source_Folder = r"D:\3rd sem\Research Ideas\Fitzpatrick IV - VI"

Destination_Folder = r"D:\3rd sem\Research Ideas\Sorted_Skin_Images"

# Extracts filters from the gallery URL and converts them to an ISIC API query.
def parse_gallery_filters(url):
    
    parsed = urllib.parse.urlparse(url)
    # Extract the 'filter' query parameter
    query_string = parsed.query
    if not query_string and '?' in parsed.fragment:
        query_string = parsed.fragment.split('?', 1)[1]
        
    query_params = urllib.parse.parse_qs(query_string)
    filter_json = query_params.get('filter', [None])[0]
    
    if not filter_json:
        print("No filters found in URL. Fetching all images?")
        return ""
    
    try:
        filters = json.loads(filter_json)
        
        api_conditions = []
        for f in filters:
            if '|' in f:
                key, val = f.split('|', 1)
                # Handle spaces in values by quoting them
                api_conditions.append(f'{key}:"{val}"')
        
        full_query = " OR ".join(api_conditions)
        return full_query
    except Exception as e:
        print(f"Error parsing URL filters: {e}")
        return ""
    
# Searches the ISIC Archive API for images matching the query.
def get_images_from_api(query_string, limit=100):
    
    search_url = "https://api.isic-archive.com/api/v2/images/search/"
    
    params = {
        "limit": limit,
        "query": query_string
    }
    
    print(f"Querying API with: {query_string}...")
    response = requests.get(search_url, params=params)
    
    # Returns a list of image objects
    if response.status_code == 200:
        return response.json()
    else:
        print(f"API Error: {response.status_code} - {response.text}")
        return []

# Finds the file locally and moves it.
def move_file(image_id, category):
    #Define filenames
    extensions = ['.jpg', '.jpeg', '.png']
    
    found = False
    for ext in extensions:
        filename = f"{image_id}{ext}"
        source_path = os.path.join(Local_Source_Folder, filename)
        
        if os.path.exists(source_path):
            # Define destination
            dest_dir = os.path.join(Destination_Folder, category)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                
            dest_path = os.path.join(dest_dir, filename)
            
            try:
                shutil.move(source_path, dest_path)
                print(f"Moved: {filename} to {dest_dir}")
                found = True
                break
            except Exception as e:
                print(f"[ERROR] Could not move {filename}: {e}")
    
    if not found:
        print(f"[NOT FOUND] {image_id} with extensions {extensions}")
        pass

# Main execution
if __name__ == "__main__":
    print("--- ISIC Image Sorter ---")
    
    # Parse filters from the gallery URL
    query_string = parse_gallery_filters(Galery_Url)
    
    if query_string:
        # Fetch images from the API
        results = get_images_from_api(query_string, limit=1000)
        
        print(f"Found {len(results)} images in ISIC Archive matching your URL.")
    
        # Move each image to its category folder
        for img in results:
            image_id = img.get("isic_id")
            
            # Extract Benign/Malignant status from metadata
            metadata = img.get('metadata', {}).get('clinical', {})
            
            category = metadata.get('benign_malignant')
            
            # If explicit category is missing, fallback to logic (optional)
            if not category:
                category = "Unknown"
            else:
                # Capitalize for folder name (benign -> Benign)
                category = category.capitalize()
                
            # Move File
            if image_id:
                move_file(image_id, category)
                
        print("Sorting complete.")
    else:
        print("Could not generate a valid query from the URL.")
