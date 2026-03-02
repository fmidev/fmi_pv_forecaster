import pandas as pd
import pytest

import fmi_pv_forecaster.pv_forecaster as pvfc


@pytest.fixture(scope="module", autouse=True)
def setUp():
    """
    This function runs when any of the tests in this file is called.
    Geolocation should be the only required input for these tests.
    """
    print("\nFeeding geolocation to pvfc via setup function.")
    pvfc.set_location(65, 25)


def test_forecast_returns_dataframe():
    radiation_forecast = pvfc.get_fmi_radiation_forecast()

    assert type(radiation_forecast) is pd.DataFrame, (
        "Radiation forecasting function returned something else than a pandas dataframe."
    )
    print("Radiation forecast returns a dataframe like it should. ")


def test_radiation_forecasting_timestep():
    """
    This function tests if the FMI open data server is returning a valid dataframe with 60 minute timesteps.
    """

    radiation_forecast = pvfc.get_fmi_radiation_forecast()

    timedelta_minutes = None  # This value holds the time delta between two rows in the dataframe
    expected_timedelta_minutes = 60  # this is the expected timedelta

    # going through the forecast each row by row checking if timedelta is wrong.
    for i in range(len(radiation_forecast)):
        if i == 0:
            continue
        row = radiation_forecast.iloc[i]
        last_row = radiation_forecast.iloc[i - 1]

        timedelta = row.name - last_row.name
        timedelta_minutes = timedelta.seconds // 60

        assert timedelta_minutes == expected_timedelta_minutes, (
            "Error with FMI radiation forecast timesteps."
            "Distance between rows should have been 60 minutes."

        )

    print("Timedelta between rows was " + str(timedelta_minutes) + " minutes")
    print("The set timestep was: " + str(60))


def test_required_parameters():
    """
    This function tests if the FMI open data is returning all required parameters.
    """
    radiation_forecast = pvfc.get_fmi_radiation_forecast()

    columns = radiation_forecast.columns
    # expected columns = ['dni', 'dhi', 'ghi', 'albedo', 'T', 'wind', 'cloud_cover']

    # radiation components
    assert "dni" in columns, (
        "Direct normal irradiance \"dni\" is missing from radiation forecast. "
        "dni is a critical component, something is wrong."
    )
    assert "dhi" in columns, (
        "Diffuse horizontal radiation \"dhi\" is missing from radiation forecast. "
        "dhi is a critical component, something is wrong."
    )
    assert "ghi" in columns, (
        "Global horizontal radiation \"ghi\" is missing from radiation forecast. "
        "ghi is a critical component, something is wrong."
    )


def test_nice_to_have_parameters():
    """
    This function tests if the FMI open data is returning all optional parameters.
    """
    radiation_forecast = pvfc.get_fmi_radiation_forecast()

    columns = radiation_forecast.columns
    # expected columns = ['dni', 'dhi', 'ghi', 'albedo', 'T', 'wind', 'cloud_cover']
    # cloud cover is not really used, leaving it untested

    # radiation components
    assert "T" in columns, (
        "Air temperature T is missing from fmi open data forecast. "
        "This should not happen, forecasts can still be generated, but issue should be investigated."
    )

    assert "wind" in columns, (
        "Wind speed \"wind\" is missing from fmi open data forecast."
        "This should not happen, forecasts can still be generated, but issue should be investigated."
    )

    assert "albedo" in columns, (
        "Ground reflectivity \"albedo\" is missing from fmi open data forecast."
        "This should not happen, forecasts can still be generated, but issue should be investigated."
    )


def test_row_count_after_nandrop_reasonable():
    radiation_forecast = pvfc.get_fmi_radiation_forecast()

    radiation_forecast = radiation_forecast.dropna()

    # length should be 65. Apparently dni and dhi radiations are lacking for the first hour for some reason.
    assert len(radiation_forecast) > 60, (
        "Got less than 60 rows from FMI open data."
        "This is suspicious as timestep should be 60min and forecast len 66 hours."
    )
    assert len(radiation_forecast.index) < 70, (
        "Got more than 70 rows from FMI open data. "
        "This is suspicious as timestep should be 60min and forecast len 66 hours."
    )


    print("Forecast length checkup looks fine.")