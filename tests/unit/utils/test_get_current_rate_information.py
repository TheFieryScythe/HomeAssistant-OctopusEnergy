from datetime import (datetime, timedelta)
import pytest

from unit import (create_rate_data)
from custom_components.octopus_energy.utils.rate_information import get_current_rate_information

@pytest.mark.asyncio
async def test_when_target_has_no_rates_and_gmt_then_no_rate_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-03-01T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_min_price = 10
  expected_max_price = 30

  rate_data = create_rate_data(period_from, period_to, [expected_min_price, 20, 20, expected_max_price])

  # Act
  rate_information = get_current_rate_information(rate_data, now)

  # Assert
  assert rate_information is None

@pytest.mark.asyncio
async def test_when_target_has_no_rates_and_bst_then_no_rate_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-03-02T00:00:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_min_price = 10
  expected_max_price = 30

  rate_data = create_rate_data(period_from, period_to, [expected_min_price, 20, 20, expected_max_price])

  # Act
  rate_information = get_current_rate_information(rate_data, now)

  # Assert
  assert rate_information is None

@pytest.mark.asyncio
async def test_when_target_has_rates_and_gmt_then_rate_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-27T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-02T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-02-28T00:32:00Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_min_price = 10
  expected_max_price = 30
  expected_rate = 20

  rate_data = create_rate_data(period_from, period_to, [expected_min_price, expected_rate, expected_rate, expected_max_price])

  # Act
  rate_information = get_current_rate_information(rate_data, now)

  # Assert
  assert rate_information is not None

  assert "all_rates" in rate_information
  expected_period_from = period_from
  
  total_rate_value = 0
  min_target = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  max_target = min_target + timedelta(days=1)
  
  for index in range(len(rate_data)):
    assert rate_information["all_rates"][index]["valid_from"] == expected_period_from
    assert rate_information["all_rates"][index]["valid_to"] == expected_period_from + timedelta(minutes=30)

    assert rate_information["all_rates"][index]["value_inc_vat"] == (expected_min_price if index % 4 == 0 else expected_max_price if index % 4 == 3 else expected_rate)
    assert rate_information["all_rates"][index]["is_capped"] == False
    expected_period_from = expected_period_from + timedelta(minutes=30)

    if rate_information["all_rates"][index]["valid_from"] >= min_target and rate_information["all_rates"][index]["valid_to"] <= max_target:
      total_rate_value = total_rate_value + rate_information["all_rates"][index]["value_inc_vat"]

  assert "current_rate" in rate_information
  assert rate_information["current_rate"]["valid_from"] == datetime.strptime("2022-02-28T00:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["current_rate"]["valid_to"] == rate_information["current_rate"]["valid_from"] + timedelta(minutes=60)

  assert rate_information["current_rate"]["value_inc_vat"] == expected_rate
  
  assert "min_rate_today" in rate_information
  assert rate_information["min_rate_today"] == expected_min_price
  
  assert "max_rate_today" in rate_information
  assert rate_information["max_rate_today"] == expected_max_price
  
  assert "average_rate_today" in rate_information
  assert rate_information["average_rate_today"] == total_rate_value / 48

@pytest.mark.asyncio
async def test_when_target_has_rates_and_bst_then_rate_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-27T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-02T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-02-28T00:32:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_min_price = 10
  expected_max_price = 30
  expected_rate = 20

  rate_data = create_rate_data(period_from, period_to, [expected_min_price, expected_rate, expected_rate, expected_max_price])

  # Act
  rate_information = get_current_rate_information(rate_data, now)

  # Assert
  assert rate_information is not None

  assert "all_rates" in rate_information
  expected_period_from = period_from
  
  total_rate_value = 0
  min_target = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  max_target = min_target + timedelta(days=1)
  
  for index in range(len(rate_data)):
    assert rate_information["all_rates"][index]["valid_from"] == expected_period_from
    assert rate_information["all_rates"][index]["valid_to"] == expected_period_from + timedelta(minutes=30)

    assert rate_information["all_rates"][index]["value_inc_vat"] == (expected_min_price if index % 4 == 0 else expected_max_price if index % 4 == 3 else expected_rate)
    assert rate_information["all_rates"][index]["is_capped"] == False
    expected_period_from = expected_period_from + timedelta(minutes=30)

    if rate_information["all_rates"][index]["valid_from"] >= min_target and rate_information["all_rates"][index]["valid_to"] <= max_target:
      total_rate_value = total_rate_value + rate_information["all_rates"][index]["value_inc_vat"]

  assert "current_rate" in rate_information
  assert rate_information["current_rate"]["valid_from"] == datetime.strptime("2022-02-28T00:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["current_rate"]["valid_to"] == rate_information["current_rate"]["valid_from"] + timedelta(minutes=60)

  assert rate_information["current_rate"]["value_inc_vat"] == expected_rate
  
  assert "min_rate_today" in rate_information
  assert rate_information["min_rate_today"] == expected_min_price
  
  assert "max_rate_today" in rate_information
  assert rate_information["max_rate_today"] == expected_max_price
  
  assert "average_rate_today" in rate_information
  assert rate_information["average_rate_today"] == total_rate_value / 48

@pytest.mark.asyncio
async def test_when_all_rates_identical_costs_then_rate_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-27T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-02T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-02-28T00:32:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_rate = 20

  rate_data = create_rate_data(period_from, period_to, [expected_rate])

  # Act
  rate_information = get_current_rate_information(rate_data, now)

  # Assert
  assert rate_information is not None

  assert "all_rates" in rate_information
  expected_period_from = period_from
  
  total_rate_value = 0
  min_target = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  max_target = min_target + timedelta(days=1)
  
  for index in range(len(rate_data)):
    assert rate_information["all_rates"][index]["valid_from"] == expected_period_from
    assert rate_information["all_rates"][index]["valid_to"] == expected_period_from + timedelta(minutes=30)

    assert rate_information["all_rates"][index]["value_inc_vat"] == expected_rate
    assert rate_information["all_rates"][index]["is_capped"] == False
    expected_period_from = expected_period_from + timedelta(minutes=30)

    if rate_information["all_rates"][index]["valid_from"] >= min_target and rate_information["all_rates"][index]["valid_to"] <= max_target:
      total_rate_value = total_rate_value + rate_information["all_rates"][index]["value_inc_vat"]

  assert "current_rate" in rate_information
  assert rate_information["current_rate"]["valid_from"] == period_from
  assert rate_information["current_rate"]["valid_to"] == period_to

  assert rate_information["current_rate"]["value_inc_vat"] == expected_rate
  
  assert "min_rate_today" in rate_information
  assert rate_information["min_rate_today"] == expected_rate
  
  assert "max_rate_today" in rate_information
  assert rate_information["max_rate_today"] == expected_rate
  
  assert "average_rate_today" in rate_information
  assert rate_information["average_rate_today"] == total_rate_value / 48