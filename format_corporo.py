def remove_leading_spaces(text):
    lines = text.split('\n')
    # Remove leading spaces from each line
    cleaned_lines = [line.lstrip() for line in lines]
    # Join the lines back together
    cleaned_text = '\n'.join(cleaned_lines)
    return cleaned_text

def format_text_file(input_file, output_file):
    try:
        with open(input_file, 'r') as file:
            text = file.read()
            cleaned_text = remove_leading_spaces(text)

            with open(output_file, 'w') as new_file:
                new_file.write(cleaned_text)
                print("Formatted text has been written to", output_file)
    except FileNotFoundError:
        print("File not found!")

# Replace 'input.txt' and 'output.txt' with your file names
input_filename = 'data/legally_blonde.txt'
output_filename = 'data/output.txt'

format_text_file(input_filename, output_filename)
