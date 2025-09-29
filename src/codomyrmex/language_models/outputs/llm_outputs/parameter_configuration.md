# Test Output: parameter_configuration

**Generated:** 2025-09-29 08:33:59

**Configuration:** Model: llama3.1:latest, Temperature: 0.7, Max Tokens: 1000

## Test Name

parameter_configuration

## Status

passed

## Timestamp

1759160039.9388769

## Prompt

Write a creative story about a robot.

## Configurations Tested

5

## Results

{'conservative': {'config': {'temperature': 0.1, 'top_p': 0.5}, 'response_length': 3828, 'response_preview': 'In the heart of the bustling metropolis, where steel and concrete skyscrapers pierced the sky, there...'}, 'creative': {'config': {'temperature': 0.8, 'top_p': 0.9}, 'response_length': 4010, 'response_preview': 'In the heart of a bustling metropolis, where towering skyscrapers pierced the sky and neon lights da...'}, 'very_creative': {'config': {'temperature': 1.2, 'top_p': 0.95}, 'response_length': 3719, 'response_preview': 'In the heart of the sprawling metropolis, in a city that never slept, there lived a robot like no ot...'}, 'short_response': {'config': {'num_predict': 50, 'temperature': 0.5}, 'response_length': 223, 'response_preview': 'In the year 2154, in a world where robots had become an integral part of human society, there was a ...'}, 'long_response': {'config': {'num_predict': 200, 'temperature': 0.5}, 'response_length': 921, 'response_preview': 'In the heart of the bustling metropolis, where steel and concrete skyscrapers pierced the sky, there...'}}

