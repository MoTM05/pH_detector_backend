import numpy as np
import cv2
from PIL import Image


class ColorGradient:
    def __init__(self, start_ph, end_ph, colors_list, length=800, width=100):
        self.start_ph = start_ph
        self.end_ph = end_ph
        self.length = length
        self.width = width
        self.colors_list = colors_list
        self.gradient = self.create_multi_gradient()

    def create_gradient_segment(self, start_color, end_color, width):
        start_color = np.array(start_color[::-1], dtype=np.uint8)
        end_color = np.array(end_color[::-1], dtype=np.uint8)
        gradient = np.zeros((1, width, 3), dtype=np.uint8)

        for x in range(width):
            alpha = x / (width - 1)
            color = (1 - alpha) * start_color + alpha * end_color
            gradient[0, x] = color

        return gradient

    def create_multi_gradient(self):
        segments_count = len(self.colors_list) - 1
        segment_width = self.length // segments_count
        gradient = np.zeros((self.width, self.length, 3), dtype=np.uint8)

        for i in range(segments_count):
            segment = self.create_gradient_segment(self.colors_list[i], self.colors_list[i + 1], segment_width)
            segment = cv2.resize(segment, (segment_width, self.width), interpolation=cv2.INTER_LINEAR)
            gradient[:, i * segment_width:(i + 1) * segment_width] = segment

        if self.length % segments_count != 0:
            last_segment_width = self.length - (segments_count - 1) * segment_width
            last_segment = self.create_gradient_segment(self.colors_list[-2], self.colors_list[-1], last_segment_width)
            last_segment = cv2.resize(last_segment, (last_segment_width, self.width), interpolation=cv2.INTER_LINEAR)
            gradient[:, -last_segment_width:] = last_segment

        return gradient

    def find_closest_color(self, target_rgb):
        target_bgr = target_rgb[::-1]
        distances = np.sqrt(np.sum((self.gradient - target_bgr) ** 2, axis=2))
        min_dist_index = np.unravel_index(np.argmin(distances), distances.shape)
        closest_color = self.gradient[min_dist_index]

        return closest_color[::-1], min_dist_index


def find_circle(img, left, top, right, bottom):
    cropped_image = img[top:bottom, left:right]
    # plt.imshow(cropped_image)
    # plt.show()
    return cropped_image


def calculate_ph(img, gradient_type):
    if gradient_type == 1:
        colors = [(201, 193, 159),
                  (201, 195, 159),
                  (206, 201, 172),
                  (209, 204, 172),
                  (201, 198, 173),
                  (203, 199, 171),
                  (201, 197, 171),
                  (210, 204, 174),
                  (198, 196, 176),
                  (206, 200, 176),
                  (201, 197, 176),
                  (197, 191, 172),
                  (190, 184, 168),
                  (187, 184, 174),
                  (184, 181, 174),
                  (181, 181, 181),
                  (177, 176, 178),
                  (177, 177, 181),
                  (179, 178, 185),
                  (180, 178, 185),
                  (175, 176, 191),
                  (165, 166, 182),
                  (166, 167, 186),
                  (161, 161, 184),
                  (155, 156, 177)]
        gradient = ColorGradient(start_ph=4.8, end_ph=7.2, length=800, width=100, colors_list=colors)
    elif gradient_type == 0:
        colors = [(205, 188, 109),
                  (202, 188, 126),
                  (187, 177, 130),
                  (182, 174, 130),
                  (191, 188, 150),
                  (180, 180, 154),
                  (188, 193, 168),
                  (175, 186, 174),
                  (167, 182, 176),
                  (158, 178, 179),
                  (148, 172, 178),
                  (143, 170, 184),
                  (125, 162, 180)]
        gradient = ColorGradient(start_ph=5.8, end_ph=8, length=800, width=100, colors_list=colors)
    else:
        raise ValueError('Выбранной шкалы не существует.')

    img_pil = Image.open(img)
    img_cv = np.array(img_pil)

    height, width = img_cv.shape[:2]

    center_x = width // 2
    center_y = height // 2

    rect_width = 100
    rect_height = 100

    left = center_x - rect_width // 2
    top = center_y - rect_height // 2
    right = center_x + rect_width // 2
    bottom = center_y + rect_height // 2

    cropped_image = find_circle(img_cv, left, top, right, bottom)

    average_color = cv2.mean(cropped_image)
    target_rgb = (average_color[0], average_color[1], average_color[2])
    closest_color, position = gradient.find_closest_color(target_rgb)
    delta_ph = gradient.end_ph - gradient.start_ph
    res = gradient.start_ph + delta_ph * (position[1] / gradient.length)

    return round(res, 2), int(average_color[0]), int(average_color[1]), int(average_color[2])