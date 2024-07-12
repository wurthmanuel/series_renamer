# series_renamer

series_renamer is a Python application that helps you rename your local TV series files based on episode titles fetched from the internet. The application uses the Tkinter library for the GUI and TVMaze API to fetch episode details.

## Features

- Import multiple series files from your local directory.
- Search for TV series by name and select specific seasons.
- Preview the renaming of files before applying changes.

## Requirements

- Python 3.x
- `requests` library
- `tkinter` library (comes with Python standard library)

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/wurthmanuel/series_renamer.git
   cd series_renamer
   ```

2. Install the required libraries:
   ```sh
   pip install requests
   ```

## Usage

1. Run the application:
   ```sh
   python series_renamer.py
   ```

2. The main window will open. Follow these steps to use the application:

    - Click on the **Import Files** button to select the series files from your local directory. The files will be listed on the left side.

    - Enter the name of the TV series in the **Series Name** field and click **Search**. Select the series from the search results.

    - Select the seasons you want to fetch episodes for and click **Fetch Episodes**. The episodes will be listed on the right side.

    - Ensure that the number of files matches the number of episodes. If not, you can remove the unnecessary files or episodes.

    - Once the lists match, click **Preview Renaming** to see a preview of the renamed files.

    - If the preview looks good, click **Start Renaming** to rename the files.

## License

This project is licensed under the MIT License. See the [LICENSE](https://opensource.org/license/MIT) file for details.