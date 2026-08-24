import os
class TextFileReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_txt_file(self):
        """Reads the contents of a text file and returns it as a string."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content

        except FileNotFoundError:
            return f"Error: The file '{self.file_path}' was not found."

        except IOError:
            return "Error: An error occurred while reading the file."
if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), "text_file.txt")
    reader = TextFileReader(file_path)
    file_content = reader.read_txt_file()

    print(file_content)