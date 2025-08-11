from PIL import Image
import numpy as np
import cv2
import copy


def get_crop_box(box, expand):
    x, y, x1, y1 = box
    x_c, y_c = (x+x1)//2, (y+y1)//2
    w, h = x1-x, y1-y
    s = int(max(w, h)//2*expand)
    crop_box = [x_c-s, y_c-s, x_c+s, y_c+s]
    return crop_box, s


def face_seg(image, mode="raw", fp=None):
    """
    Perform face parsing on an image to generate a mask of the facial region.

    Args:
        image (PIL.Image): Input image.

    Returns:
        PIL.Image: Mask image of the facial region.
    """
    seg_image = fp(image, mode=mode)  # 使用 FaceParsing 模型解析面部
    if seg_image is None:
        print("error, no person_segment")  # Return error if no face is detected
        return None

    seg_image = seg_image.resize(image.size)  # Resize mask image to input image size
    return seg_image


def get_image(image, face, face_box, upper_boundary_ratio=0.5, expand=1.5, mode="raw", fp=None):
    """
    Paste the cropped face image back to the original image with some processing.

    Args:
        image (numpy.ndarray): Original image (body part).
        face (numpy.ndarray): Cropped face image.
        face_box (tuple): Face bounding box coordinates (x, y, x1, y1).
        upper_boundary_ratio (float): Ratio for controlling the preserved proportion of face region.
        expand (float): Expansion factor for enlarging the crop box.
        mode: Blending mask construction method

    Returns:
        numpy.ndarray: Processed image.
    """
    # Convert numpy arrays to PIL images
    body = Image.fromarray(image[:, :, ::-1])  # Body part image (full image)
    face = Image.fromarray(face[:, :, ::-1])  # Face image

    x, y, x1, y1 = face_box  # Get face bounding box coordinates
    crop_box, s = get_crop_box(face_box, expand)  # Calculate expanded crop box
    x_s, y_s, x_e, y_e = crop_box  # Crop box coordinates
    face_position = (x, y)  # Face position in original image

    # Crop expanded face region from body image (with distance from chin to boundary)
    face_large = body.crop(crop_box)
        
    ori_shape = face_large.size  # Original size of cropped image

    # Perform face parsing on cropped face region to generate mask
    mask_image = face_seg(face_large, mode=mode, fp=fp)
    
    mask_small = mask_image.crop((x - x_s, y - y_s, x1 - x_s, y1 - y_s))  # Crop face region mask
    
    mask_image = Image.new('L', ori_shape, 0)  # Create a black mask image
    mask_image.paste(mask_small, (x - x_s, y - y_s, x1 - x_s, y1 - y_s))  # Paste face mask onto black image
    
    
    # Keep upper part of face region (for controlling talking area)
    width, height = mask_image.size
    top_boundary = int(height * upper_boundary_ratio)  # Calculate upper part boundary
    modified_mask_image = Image.new('L', ori_shape, 0)  # Create new black mask image
    modified_mask_image.paste(mask_image.crop((0, top_boundary, width, height)), (0, top_boundary))  # Paste upper part mask
    
    
    # Apply Gaussian blur to mask for smoother edges
    blur_kernel_size = int(0.05 * ori_shape[0] // 2 * 2) + 1  # Calculate blur kernel size
    mask_array = cv2.GaussianBlur(np.array(modified_mask_image), (blur_kernel_size, blur_kernel_size), 0)  # Gaussian blur
    #mask_array = np.array(modified_mask_image)
    mask_image = Image.fromarray(mask_array)  # Convert blurred mask back to PIL image
    
    # Paste cropped face image back to expanded face region
    face_large.paste(face, (x - x_s, y - y_s, x1 - x_s, y1 - y_s))
    
    body.paste(face_large, crop_box[:2], mask_image)
    
    body = np.array(body)  # Convert PIL image back to numpy array

    return body[:, :, ::-1]  # Return processed image (BGR to RGB)


def get_image_blending(image, face, face_box, mask_array, crop_box):
    body = Image.fromarray(image[:,:,::-1])
    face = Image.fromarray(face[:,:,::-1])

    x, y, x1, y1 = face_box
    x_s, y_s, x_e, y_e = crop_box
    face_large = body.crop(crop_box)

    mask_image = Image.fromarray(mask_array)
    mask_image = mask_image.convert("L")
    face_large.paste(face, (x-x_s, y-y_s, x1-x_s, y1-y_s))
    body.paste(face_large, crop_box[:2], mask_image)
    body = np.array(body)
    return body[:,:,::-1]


def get_image_prepare_material(image, face_box, upper_boundary_ratio=0.5, expand=1.5, fp=None, mode="raw"):
    body = Image.fromarray(image[:,:,::-1])

    x, y, x1, y1 = face_box
    #print(x1-x,y1-y)
    crop_box, s = get_crop_box(face_box, expand)
    x_s, y_s, x_e, y_e = crop_box

    face_large = body.crop(crop_box)
    ori_shape = face_large.size

    mask_image = face_seg(face_large, mode=mode, fp=fp)
    mask_small = mask_image.crop((x-x_s, y-y_s, x1-x_s, y1-y_s))
    mask_image = Image.new('L', ori_shape, 0)
    mask_image.paste(mask_small, (x-x_s, y-y_s, x1-x_s, y1-y_s))

    # keep upper_boundary_ratio of talking area
    width, height = mask_image.size
    top_boundary = int(height * upper_boundary_ratio)
    modified_mask_image = Image.new('L', ori_shape, 0)
    modified_mask_image.paste(mask_image.crop((0, top_boundary, width, height)), (0, top_boundary))

    blur_kernel_size = int(0.1 * ori_shape[0] // 2 * 2) + 1
    mask_array = cv2.GaussianBlur(np.array(modified_mask_image), (blur_kernel_size, blur_kernel_size), 0)
    return mask_array, crop_box
