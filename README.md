# Phone_pe_visualization

## PhonePe Pulse - Transaction Insights

This project visualizes and analyzes online transaction data using PhonePe Pulse. It provides insights on transaction counts, payment values, transaction categories, and state-wise transaction data in India.

## Project Overview

The project consists of the following major components:

1. Data Retrieval and Processing:
   - The code retrieves transaction data from JSON files stored in the local file system.
   - The data is processed and loaded into a MySQL database.
   - Required statistics and aggregations are performed on the data.

2. Data Visualization:
   - The code uses Streamlit, Folium, and Plotly Express libraries to visualize the data.
   - Interactive visualizations include choropleth maps, pie charts, and bar charts.

## Setup and Requirements

To run the project, you need to set up the following:

1. Python environment:
   - Install Python 3.x on your system.

2. Install the required libraries:
   - Run `pip install -r requirements.txt` to install the necessary Python libraries.

3. MySQL database setup:
   - Set up a MySQL database and update the connection details in the code.
   - Create a table named `data` with the required schema (provided in the code).

4. GeoJSON file download:
   - The code downloads a GeoJSON file for India state boundaries.
   - Ensure internet connectivity to download the file.

## Usage

1. Run the application:
   - Execute the code using `streamlit run app.py`.
   - The application will start and open in your default web browser.

2. Select a Quarter:
   - Use the dropdown menu to select a quarter for which you want to analyze the transaction data.

3. Explore Insights:
   - The application will display various visualizations and insights based on the selected quarter.
   - You can explore transaction counts, payment values, transaction categories, and state-wise transaction data.

4. Interact with Visualizations:
   - Hover over the visualizations to view specific data points.
   - Zoom in and out on maps using the zoom controls.
   - Click and drag to pan the maps.

## Contributing

Contributions to the project are welcome. You can fork the repository, make improvements or additions, and submit a pull request.


