import os
import json
import shutil
import urllib.parse
import requests
import time

# --- CONFIGURATION ---
Gallery_Url = "https://gallery.isic-archive.com/#!/topWithHeader/onlyHeaderTop/gallery?filter=%5B%22fitzpatrick_skin_type%7CVI%22%2C%22fitzpatrick_skin_type%7CV%22%2C%22fitzpatrick_skin_type%7CIV%22%5D&name="

# UPDATE THESE PATHS IF NEEDED
Local_Source_Folder = r"D:\3rd sem\Research Ideas\Fitzpatrick IV - VI"
Destination_Folder = r"D:\3rd sem\Research Ideas\Sorted_Skin_Images"


# --- FUNCTIONS ---

def parse_gallery_filters(url):
    parsed = urllib.parse.urlparse(url)
    query_string = parsed.query
    if not query_string and '?' in parsed.fragment:
        query_string = parsed.fragment.split('?', 1)[1]
    
    query_params = urllib.parse.parse_qs(query_string)
    filter_json = query_params.get('filter', [None])[0]
    
    if not filter_json: return ""
    
    try:
        filters = json.loads(filter_json)
        api_conditions = []
        for f in filters:
            if '|' in f:
                key, val = f.split('|', 1)
                api_conditions.append(f'{key}:"{val}"')
        return " OR ".join(api_conditions)
    except:
        return ""

def fetch_all_images(query_string):
    base_url = "https://api.isic-archive.com/api/v2/images/search/"
    params = {"limit": 100, "query": query_string} 
    
    all_results = []
    next_url = base_url
    
    print(f"Contacting API... (This may take a moment)")
    
    while next_url:
        try:
            if next_url == base_url:
                response = requests.get(next_url, params=params)
            else:
                response = requests.get(next_url)
            
            if response.status_code != 200:
                print(f"Error fetching data: {response.status_code}")
                break
                
            data = response.json()
            results = data.get('results', [])
            all_results.extend(results)
            next_url = data.get('next')
            
            print(f"Fetched batch. Total found so far: {len(all_results)}")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Connection error: {e}")
            break
            
    return all_results

def determine_category(img_data):
    metadata = img_data.get('metadata', {})
    clinical = metadata.get('clinical', {})
    
    diag1 = clinical.get('diagnosis_1')
    
    if diag1:
        if "Benign" in diag1:
            return "Benign"
        elif "Malignant" in diag1:
            return "Malignant"
    
    # --- FALLBACK LOGIC (Just in case) ---
    cat = clinical.get('benign_malignant')
    if cat: return cat

    return "Unknown"

def move_file(image_id, category):
    if not category: category = "Unknown"
    category = category.capitalize()
    
    extensions = ['.jpg', '.jpeg', '.png']
    
    for ext in extensions:
        filename = f"{image_id}{ext}"
        src = os.path.join(Local_Source_Folder, filename)
        
        if os.path.exists(src):
            dst_dir = os.path.join(Destination_Folder, category)
            if not os.path.exists(dst_dir): 
                os.makedirs(dst_dir)
            
            try:
                shutil.move(src, os.path.join(dst_dir, filename))
                return category 
            except Exception as e:
                print(f"Error moving {filename}: {e}")
                
    return None 


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("--- ISIC Image Sorter Final ---")
    
    api_query = parse_gallery_filters(Gallery_Url)
    
    if api_query:
        print(f"Query generated: {api_query}")
        
        all_images = fetch_all_images(api_query)
        print(f"Total images metadata found: {len(all_images)}")
        
        if len(all_images) == 0:
            print("No images found in API.")
            exit()

        moved_counts = {"Benign": 0, "Malignant": 0, "Unknown": 0}
        
        print("Starting file move...")
        for img in all_images:
            image_id = img.get('isic_id')
            category = determine_category(img)
            
            result = move_file(image_id, category)
            
            if result:
                if result not in moved_counts: 
                    moved_counts[result] = 0
                moved_counts[result] += 1

        print("\n--- Summary ---")
        print(f"Benign moved: {moved_counts.get('Benign', 0)}")
        print(f"Malignant moved: {moved_counts.get('Malignant', 0)}")
        print(f"Unknown moved: {moved_counts.get('Unknown', 0)}")
        
    else:
        print("Could not generate a valid query from the URL.")