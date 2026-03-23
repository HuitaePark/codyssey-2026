import pickle  # Standard library used for binary file handling in bonus task

def process_inventory():
    """
    Main function to process the Mars base inventory list according to the
    given requirements.
    """
    input_filename = 'Mars_Base_Inventory_List.csv'
    danger_filename = 'Mars_Base_Inventory_danger.csv'
    binary_filename = 'Mars_Base_Inventory_List.bin'

    inventory_list = []

    # Task 1 & 2: Read CSV file and convert it into a Python list
    print('--- [Task 1] Reading and printing Mars_Base_Inventory_List.csv ---')
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            header = f.readline().strip().split(',')
            print(f'Header: {header}')
            
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Print each line as it's read
                print(line)
                
                # Split and convert to list
                row = line.split(',')
                # Convert Flammability to float for sorting/filtering
                try:
                    row[4] = float(row[4])
                except ValueError:
                    # In case of "Various" or non-numeric values, set to 0.0 or handle
                    row[4] = 0.0
                
                inventory_list.append(row)
                
    except FileNotFoundError:
        print(f"Error: '{input_filename}' not found.")
        return
    except Exception as e:
        print(f'An unexpected error occurred during reading: {e}')
        return

    # Task 3: Sort by flammability in descending order
    # Using lambda to sort by the 5th column (index 4)
    inventory_list.sort(key=lambda x: x[4], reverse=True)

    # Task 4: Filter items with flammability >= 0.7 and print them
    print('\n--- [Task 4] Items with Flammability >= 0.7 ---')
    danger_list = [item for item in inventory_list if item[4] >= 0.7]
    
    for item in danger_list:
        print(item)

    # Task 5: Save high flammability items to CSV
    print(f'\n--- [Task 5] Saving danger list to {danger_filename} ---')
    try:
        with open(danger_filename, 'w', encoding='utf-8') as f:
            # Write header
            f.write(','.join(header) + '\n')
            for item in danger_list:
                # Convert back to string for CSV
                str_item = [str(val) for val in item]
                f.write(','.join(str_item) + '\n')
    except Exception as e:
        print(f'Error saving to {danger_filename}: {e}')

    # Bonus 1: Save sorted list as a binary file
    print(f'\n--- [Bonus 1] Saving sorted list to {binary_filename} ---')
    try:
        with open(binary_filename, 'wb') as f:
            pickle.dump(inventory_list, f)
    except Exception as e:
        print(f'Error saving binary file: {e}')

    # Bonus 2: Read binary file and print contents
    print(f'\n--- [Bonus 2] Reading and printing {binary_filename} ---')
    try:
        with open(binary_filename, 'rb') as f:
            loaded_data = pickle.load(f)
            for row in loaded_data:
                print(row)
    except Exception as e:
        print(f'Error reading binary file: {e}')

    # Explanation for Bonus 3
    print_explanation()

def print_explanation():
    """
    Prints the difference between text and binary files.
    """
    explanation = '''
--- [Bonus 3] Comparison: Text File vs Binary File ---

1. Text File (.csv, .txt):
   - Definition: Stores data as a sequence of characters (e.g., UTF-8, ASCII).
   - Pros:
     - Human-readable: Can be opened and edited with any text editor (Notepad, Vim).
     - Portable: Easy to share across different operating systems.
   - Cons:
     - Less space-efficient: Numbers are stored as strings (e.g., "0.78" takes 4 bytes instead of a float's 4/8 bytes).
     - Slower parsing: Must be parsed (split by commas, converted to types) every time it is read.

2. Binary File (.bin, .dat):
   - Definition: Stores data in the same format as it is represented in memory (bits and bytes).
   - Pros:
     - Space-efficient: Often much smaller because it doesn't use character encoding for every value.
     - Faster performance: Can be read directly into memory structures (like pickle in Python) without manual parsing.
     - Security: Not easily readable by humans without specific software, providing a minor layer of obfuscation.
   - Cons:
     - Not human-readable: Opening in a text editor shows "gibberish".
     - Portability issues: Sometimes dependent on the specific architecture or serialization library (e.g., pickle versions).
'''
    print(explanation)

if __name__ == '__main__':
    process_inventory()
