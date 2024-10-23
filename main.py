import argparse
import os

from art import text2art
from colour import Color
from Pylette import extract_colors

IMAGE_TYPES = ["jpg", "jpeg", "png", "webp"]


class Screen:
    def __init__(self, width: int, height: int):
        self.RST = "\033[0m"
        self.width, self.height = width, height

    def get_colored_text_prefix(self, rgb: tuple[float]):
        prefix = (
            f"\033[38;2;{round(rgb[0]*256)};{round(rgb[1]*256)};{round(rgb[2]*256)}m"
        )
        return prefix

    def get_colored_background_prefix(self, rgb: tuple[float]):
        prefix = (
            f"\033[48;2;{round(rgb[0]*256)};{round(rgb[1]*256)};{round(rgb[2]*256)}m"
        )
        return prefix

    def is_color_bright(self, rgb: tuple[float]):
        perceived_brightness = (
            0.2126 * rgb[0] * 256 + 0.7152 * rgb[1] * 256 + 0.0722 * rgb[2] * 256
        )
        if perceived_brightness > 128:
            return True
        else:
            return False

    def get_gradient_background(self, gradient_colors: list[list[Color]]):
        line = ""
        for i in range(4):
            for j in range(len(gradient_colors[i])):
                prefix = self.get_colored_background_prefix(gradient_colors[i][j].rgb)
                line += f"{prefix} {self.RST}"
        return line * self.height

    def embed_character_in_background(
        self, characters: list[dict], gradient_background: str
    ):
        space_locations = []
        start_index = 0
        for i in range(self.width * self.height):
            space_loc = gradient_background.find(" ", start_index)
            space_locations.append(space_loc)
            start_index = space_loc + 1
        for c in characters:
            x, y = c["x"], c["y"]
            char = c["char"]
            loc = y * self.width + x
            real_loc = space_locations[loc]
            gradient_background = (
                gradient_background[:real_loc]
                + char
                + gradient_background[real_loc + 1 :]
            )
        return gradient_background


def get_ready(directory: str):
    width, height = os.get_terminal_size()
    image_path = None
    for typ in IMAGE_TYPES:
        if os.path.isfile(f"{directory}/image.{typ}"):
            image_path = f"{directory}/image.{typ}"
    if image_path is None:
        raise FileNotFoundError(
            "Can't find album image file in the project directory.\nFile must be jpg, jpeg, webp or png format."
        )
    colors = extract_colors(image_path)
    dominant_colors = []
    gradient_colors = []
    for color in colors:
        dominant_colors.append(color.rgb)
    # print(dominant_colors)
    color_per_characters = width // 4
    left = width % 4
    if left == 0:
        for i in range(4):
            color_1 = Color(rgb=list(map(lambda a: a / 256, dominant_colors[i])))
            color_2 = Color(rgb=list(map(lambda a: a / 256, dominant_colors[i + 1])))
            gradient_colors.append(
                list(color_1.range_to(color_2, color_per_characters))
            )
    else:
        new = [color_per_characters] * 4
        for i in range(left):
            new[i] += 1
        for i in range(4):
            color_1 = Color(rgb=list(map(lambda a: a / 256, dominant_colors[i])))
            color_2 = Color(rgb=list(map(lambda a: a / 256, dominant_colors[i + 1])))
            gradient_colors.append(list(color_1.range_to(color_2, new[i])))
    screen = Screen(width, height)
    test = screen.get_gradient_background(gradient_colors)
    new = screen.embed_character_in_background([], test)
    print(new)


def translate(directory: str):
    with open(f"{directory}/script.txt", "r") as f:
        original_script = f.readlines()
    with open(f"{directory}/run.py", "w") as f:
        f.write("from time import sleep\n\ndef run_script():")
    for i in range(len(original_script)):
        if i in [0, 1, 2]:
            print(original_script[i])
        else:
            start_time_minute = int(original_script[i][1])
            start_time_seconds = int(original_script[i][3:5])
            start_time_total = 60 * start_time_minute + start_time_seconds
            lyrics_start_location = original_script[i].find("{") + 1
            lyrics_end_location = original_script[i].find("}")
            lyrics = original_script[i][lyrics_start_location:lyrics_end_location]
            end_time_minute = int(original_script[i][lyrics_end_location + 2])
            end_time_seconds = int(
                original_script[i][lyrics_end_location + 4 : lyrics_end_location + 6]
            )
            end_time_total = 60 * end_time_minute + end_time_seconds
            # print(start_time_total, end_time_total, lyrics)


def run():
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--translate", "-t", action="store_true", help="Translate the project."
    )
    # Run the project. Check if it is already translated. If not, translate and run.
    parser.add_argument(
        "--run",
        "-r",
        action="store_true",
        help="Run the project. Check if it is already translated. If not, translate and run.",
    )
    # Determine project directory
    parser.add_argument("directory", type=str, help="Determine the project directory.")
    args = parser.parse_args()
    print(f"Project directory: {args.directory}")
    if args.run:
        print("Run!")
    elif args.translate:
        # print("Translate")
        get_ready(args.directory)
        translate(args.directory)
        test = text2art("Test 1234.\nI love Python.", "colossal")
        print(test.split("\n"))


if __name__ == "__main__":
    main()
