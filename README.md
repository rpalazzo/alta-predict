# ALTA Division Score and Standings Predictor

## Functionality
This script parses the schedule and scores from an ALTA Division Standings web page.
For each future match, it calculates the predicted scores based on scores of the two teams against all their common opponents.
Subsequent matches are predicted based on the actual scores as well as the previously predicted scores.
The script supports both 5-point Tennis matches and 12-point Pickleball matches.

## Usage
From the ALTA Division Standings page (https://www.altatennis.org/Member/Teams/TeamsDivisionStandings.aspx),
select 'File > Save page as...' and choose `Webpage, HTML Only` as the format.
Pass the saved HTML file to this script as an argument.
You may optionally include a fudge factor using the `--fudge` argument.

## Output
The first column of the output table is the team ID.
The following integer columns are the actual scores, and the decimal columns are the predicted scores.
The second to last column is the sum of the scores, and the last column is the final team ranking. 

MIT License
Copyright (c) 2025 Robert Palazzo
