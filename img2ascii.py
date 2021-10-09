import PIL.Image
import requests

# ASCII characters
ASCII = [ "@", "#", "$", "%", "?", "*", "+", ";", ":", ",", "." ]
new_width = 80

# Resze image while maintaining aspect ratio
def resize_img(image, new_width=80):
    width, height = image.size
    ratio = height/width
    new_height = int(new_width * ratio)//1.75
    resized_img = image.resize((new_width, int(new_height)))
    return resized_img

# Convert each Pixel to Grayscale
def fifty_shades_of_grey(image):
    grayscale_img = image.convert("L")
    return grayscale_img

# Pixel to equivalent ASCII string
def pixel_to_ascii(image):
    pixels = image.getdata()
    characters = "".join([ASCII[pixel//25] for pixel in pixels])
    return characters

def ascii_output(image_path):
    # Read Image
    try:
        image = PIL.Image.open(image_path)
    except:
        print(image_path, "Not a valid Pathname to any image.")
    
    # Do Stuff
    # image -> ASCII
    new_image_data = pixel_to_ascii(fifty_shades_of_grey(resize_img(image)))
    
    # Format
    pixel_count = len(new_image_data)
    ascii_img = "\n".join([new_image_data[index:(index+new_width)] for index in range(0, pixel_count, new_width)])

    return ascii_img