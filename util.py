import os

def sort_by(positions, field):
    """ sorts a list of positions (text, x, y dicts) by a field """
    positions.sort(key=lambda x: x[field])
    return positions

def get_position(positions, string):
    """ returns position object of text from list of positions """
    choices = get_positions(positions, string)
    assert len(choices) == 1, f'expected list of length 1 {choices} for string "{string}"'
    return choices[0]

def get_positions(positions, string):
    """ returns position objects of text from list of positions """
    return [p for p in positions if string.lower() in p['text']]

def clip(positions, min_x=None, min_y=None, max_x=None, max_y=None):
    """ clips a list of position objects by x and y"""
    min_x = min_x or 0
    min_y = min_y or 0
    max_x = max_x or max(p['x'] for p in positions)
    max_y = max_y or max(p['y'] for p in positions)

    return [p for p in positions if within_bounds(p['x'], min_x, max_x) and within_bounds(p['y'], min_y, max_y)]

def within_bounds(a, min_, max_):
    """ returns True if a is within the bounds """
    return a >= min_ and a <= max_

def group_rows(positions, tolerance=10):
    """ parses a list of positions into rows by x-location
        returns a list of rows. each row is a list of positions
        tolerance*2 is the max diff in y values to be considered part of the same row
    """
    # this is terribly inefficient, but the input size is small
    # return header_row, data rows
    rows = []
    for p in positions:
        placed = False

        for row in rows:
            in_row = within_bounds(
                p['y'],
                min(x['y'] for x in row) - tolerance,
                max(x['y'] for x in row) + tolerance
            )

            if in_row:
                assert not placed
                row.append(p)
                placed = True
            
        if not placed:
            rows.append([p])

    return rows


def print_data(data):
    for row in data:
        print('\t'.join([x if len(x) > 0 else "<empty>\t" for x in row[:6]]))

def save_to_csv(data, path):
    with open(path, 'w') as f:
        for row in data:
            f.write(','.join([f'"{x}"' for x in row]))
            f.write('\n')


def get_paths(directory):
    paths = [os.path.join(directory, x) for x in os.listdir(directory)]
    return [x for x in paths if os.path.isfile(x)]
