import csv
from collections import Counter

file_path = 'reviews.csv'

def count_ratings(file_path=file_path):
    """Count the frequencies of each rating in the CSV file."""
    rating_counter = Counter()

    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        # Iterate through each row in the CSV
        for row in csv_reader:
            # Get the rating from the row and convert it to an integer
            rating = int(row['rating'])
            # Increment the counter for this rating
            rating_counter[rating] += 1

    # Print the frequencies of each rating
    for rating in range(1, 6):  # Ratings from 1 to 5
        print(f"Rating {rating}: {rating_counter[rating]}")


def rm_col(file_path):
    """Remove the 'url' column from the CSV file and save the result."""
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        # Extract header
        header = next(csv_reader)
        
        # Find index of the 'url' column
        if 'url' in header:
            url_index = header.index('url')
        else:
            raise ValueError("'url' column not found in the file.")

        # Remove the 'url' column from the header
        new_header = [col for col in header if col != 'url']
        
        # Remove the 'url' column from the rest of the rows
        new_rows = []
        for row in csv_reader:
            new_row = [value for i, value in enumerate(row) if i != url_index]
            new_rows.append(new_row)
    
    # Write the modified CSV back to file or a new file
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        # Write new header
        csv_writer.writerow(new_header)
        # Write new rows
        csv_writer.writerows(new_rows)

        

if __name__ == '__main__':
    count_ratings()