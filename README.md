# Covid19 Tracker-India

A web dashboard to analyse and visualize the COVID-19 pandemic in India deployed on Heroku at [https://covid19india1.herokuapp.com/](https://covid19india1.herokuapp.com/)
Built using Python and [Dash](https://dash.plot.ly/) by ploltly, with charts made in [Plotly](https://plot.ly/) and [Plolty express](https://plotly.com/python/plotly-express/)

---
The data used is directly from the Government of India's portal [https://www.mohfw.gov.in/index.html](https://www.mohfw.gov.in/index.html) which gets updated twice daily and henceforth automatically updates the dashboard.

The day wise new cases are being recorded from [https://indiacovid19.github.io/](https://indiacovid19.github.io/)

The dashboard provides an easy way to gain insights with regard to the increasing coronavirus cases in India, the plots have been designed to be easy to interact with, and view on mobile devices.
 
 ## The latest updates
Four tiles at the top that display the latest rise in Total Confirmed, Active, Recovered and Death cases along with the rise from the previous day in India.
 ![dashboard](images/Counts.png)
 
 ## Day-wise rise in confirmed cases
A day wise rise in confirmed cases is being recorded since the rise of the pandemic in India
 ![dashboard](images/Cases_new.png)
 
 ## State- wise rise in confirmed cases
The plot shows the rise in confirmed cases in comparison with yesterday. Each state is shown as a circle, and the size of the cricle is dependent on the rise in confirmed cases in that state. You can touch or move your mouse on the circles to see values.
![dashboard](images/States_new.png)

## Trends in the cases
The plot contains the trend for "Confirmed Cases", "Recovered Cases", "Active Cases", "Deaths". By default, the plot will show all the trends. You can choose the trends you want to see by using the drop-down menu below.
![dashboard](images/Trajectory.png)

## State-wise count of cases
The plot is a display of the exact count of corona virus cases in the country, a drop down menu is provided to select what the user wishes to see
![dashboard](images/Rise.png)
 
