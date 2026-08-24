import os
class TextFileReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_file(self):
        with open(self.file_path, "r") as file:
            self.content = file.read()

    def count_lines(self):
        return len(self.content.splitlines())

    def count_words(self):
        return len(self.content.split())

    def count_characters(self):
        return len(self.content)

    def display_content(self):
        print(self.content)
file_path = os.path.join(os.path.dirname(__file__), "text_file.txt")
read = TextFileReader(file_path)
read.read_file()
print("Number of lines:", read.count_lines())
print("Number of words:", read.count_words())
print("Number of characters:", read.count_characters())
print("\nFile content:")
read.display_content()