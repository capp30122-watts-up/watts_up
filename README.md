# watts_up
CAPP 30122 Group Project

## Team Members
[Frank Vasquez](https://github.com/frankvasquez7), [Jacob Trout](https://github.com/jacobtrout), [Praveen Devarajan](https://github.com/pravchand), [Xiaoyue Wei](https://github.com/Wxy-23)

## Project Summary
This project analyses data and builds interactive visualizations on electricity generation in the United States

## To Launch the Application

1. Clone the repository.
```
git clone git@github.com:capp30122-watts-up/watts_up.git
```

2. Navigate to the repository.
```
cd ./watts_up
```
3. Download Poetry, which allows the user to run the application in a virtual environment, [following these instructions](https://python-poetry.org/docs/). Then install poetry.
```
poetry install
```
4. Activate the virtual environment in poetry.
```
poetry shell
```
5. [OPTIONAL] Pull data from API, combine multiple years of E-Grid data, clean, and create the database
Note that one of the API key is needed to extract data from US. Energy Information Administration (EIA). We recommend requesting API key from the EIA directly. This step is optional since the completed database is already present in the application. This step takes approximately 1 minute to run.

Once the API key is acquired, set the variable in your terminal with the following code:
```
export API_KEY="Your_API_KEY_Here"
```
After the key is set, run the data processing.
```
python3 -m watts_up getdata
```
6. Launch the Application.
```
python3 -m watts_up dashboard
```
The IDE may automatically launch a new web browser tab, or may provide a local URL. If the latter, paste it into your browser to view the interactive dashboard.

## For further information on the project:

[Click here for a summary of the project](https://github.com/capp30122-watts-up/watts_up/tree/main/watts_up/documentation/proj-paper.pdf)

## Acknowledgments

Professor: James Turk

Teaching Assistant: Reza Rizky Pratama 

Data Sources:
- Energy Information Agency
- Enviromental Protection Agency 
- US Census
