# ALTA Division Score and Standings Predictor

## Functionality
This script parses the schedule and scores from an ALTA Division Standings web page.<br>
For each future match, it calculates the predicted scores based on scores of the two teams against all their common opponents.<br>
Subsequent matches are predicted based on the actual scores as well as the previously predicted scores.<br>
The script supports both 5-point Tennis matches and 12-point Pickleball matches.<br>

## Usage
From the ALTA Division Standings page (https://www.altatennis.org/Member/Teams/TeamsDivisionStandings.aspx),<br>
select 'File > Save page as...' and choose `Webpage, HTML Only` as the format.<br>
Pass the saved HTML file to this script as an argument.<br>
You may optionally include a fudge factor using the `--fudge` argument.<br>

## Output
The first column of the output table is the team ID.<br>
The following integer columns are the actual scores, and the decimal columns are the predicted scores.<br>
The second to last column is the sum of the scores, and the last column is the final team ranking.<br>

MIT License<br>
Copyright (c) 2025 Robert Palazzo
