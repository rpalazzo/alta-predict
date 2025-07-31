#!/usr/bin/env python3

"""
ALTA Division Score and Standings Predictor

Functionality:
This script parses the schedule and scores from an ALTA Division Standings web page.
For each future match, it calculates the predicted scores based on scores of the two teams against all their common opponents.
Subsequent matches are predicted based on the actual scores as well as the previously predicted scores.
The script supports both 5-point Tennis matches and 12-point Pickleball matches.

Usage:
From the ALTA Division Standings page (https://www.altatennis.org/Member/Teams/TeamsDivisionStandings.aspx),
select 'File > Save page as...' and choose `Webpage, HTML Only` as the format.
Pass the saved HTML file to this script as an argument.
You may optionally include a fudge factor using the `--fudge` argument.

Output:
The first column of the output table is the team ID.
The following integer columns are the actual scores, and the decimal columns are the predicted scores.
The second to last column is the sum of the scores, and the last column is the final team ranking.

MIT License
Copyright (c) 2025 Robert Palazzo
"""

import argparse
from bs4 import BeautifulSoup


def get_max_score(soup):

    team_header_title = soup.find(class_="team-header__title")
    if team_header_title:
        title_text = team_header_title.get_text(strip=True)
        # print(f"Team Header Title: {title_text}")

        if "Pickleball" in title_text:
            max_score = 12
            # print(f"Pickleball max score: {max_score}")
        else:
            max_score = 5
            # print(f"Tennis max score: {max_score}")
    else:
        print("No element with class 'team-header__title' found.")
        exit(1)

    return max_score


def get_schedule(soup):

    # Find the table with id ending in "_tblRosters"
    roster_table = soup.find("table", id=lambda x: x and x.endswith("_tblRosters"))
    if not roster_table:
        print("No table with id ending in '_tblRosters' found.")
        exit(1)

    # Initialize the second table for "TeamValue" rows
    schedule_table = []

    # Find all rows in the roster_table
    rows = roster_table.find_all("tr")
    for row in rows:
        # Initialize the row values with the leading column
        leading_column = ""
        roster_span = row.find("span", id=lambda x: x and x.endswith("TeamNumValue"))
        if roster_span:
            # Extract the text from the <span> element
            leading_column = roster_span.get_text(strip=True)

        # Find all <span> elements with IDs ending in "TeamValue"
        spans = row.find_all("span", id=lambda x: x and x.endswith("TeamValue"))
        opponents_row_values = []
        for span in spans:
            # Extract the text from the <span> element
            text = span.get_text(strip=True)
            opponents_row_values.append(text)  # Add the text directly to the row values

        # Add the leading column to the row values
        if opponents_row_values:
            schedule_table.append([leading_column] + opponents_row_values)

    # Print the team table
    # print("Schedule Table:")
    # for row in schedule_table:
    #    print("\t".join(map(str, row)))

    return schedule_table


def get_scores(soup):
    # Find the table with id ending in "_tblRosters"
    roster_table = soup.find("table", id=lambda x: x and x.endswith("_tblRosters"))
    if not roster_table:
        print("No table with id ending in '_tblRosters' found.")
        return

    scores_table = []

    # Find all rows in the roster_table
    rows = roster_table.find_all("tr")
    for row in rows:
        # Initialize the row values with the leading column
        leading_column = ""
        roster_span = row.find("span", id=lambda x: x and x.endswith("TeamNumValue"))
        if roster_span:
            # Extract the text from the <span> element
            leading_column = roster_span.get_text(strip=True)

        # Find all <span> elements with IDs ending in "PtsValue"
        spans = row.find_all("span", id=lambda x: x and x.endswith("PtsValue"))
        pts_row_values = []
        for span in spans:
            # Extract the text from the <span> element
            text = span.get_text(strip=True)

            # Convert the text to an integer if possible
            try:
                pts_row_values.append(int(text))
            except ValueError:
                pts_row_values.append("-")  # future games won't have a score, so insert a dash instead

        # Add the leading column to the row values
        if pts_row_values:
            scores_table.append([leading_column] + pts_row_values)

    # Print the table
    # print("Score Table:")
    # for row in scores_table:
    #    print("\t".join(map(str, row)))

    return scores_table


def predict_scores(schedule_table, scores_table, max_score):

    # Iterate through the scores table to calculate projected scores
    #
    for i, row in enumerate(scores_table):
        # Find the next_game column (first column with a value of "-")
        try:
            next_game_index = row.index("-")
        except ValueError:
            return []

        # Get the current team's schedule from the team_table
        this_team_schedule = next(
            (
                schedule_table[j]
                for j in range(len(schedule_table))
                if schedule_table[j][0] == row[0]
            ),
            None,
        )

        # Get the next opponent to be played
        opposing_team_id = schedule_table[i][next_game_index]

        # Find the row corresponding to the opposing_team_id
        opponent_schedule = next(
            (
                schedule_table[j]
                for j in range(len(schedule_table))
                if schedule_table[j][0] == opposing_team_id
            ),
            None,
        )
        # print(f"This team schedule for Team {row[0]}: {this_team_schedule}")
        # print(f"Oppoent team schedule: {opponent_schedule}")

        if opponent_schedule:
            # Create a list of common opponents
            common_opponents = [
                opponent
                for opponent in this_team_schedule[
                    1:next_game_index
                ]  # Skip the first column (team_id) and limit to before next_game_index
                if opponent in opponent_schedule[1:next_game_index]
                and opponent
                != "-"  # Check if the opponent exists in opposing_team_row and is not "-"
            ]

            # Debug: Print the common opponents
            # print(f"Common opponents between Team {row[0]} and Team {opponent}: {common_opponents}")

            # Create lists to store current and opponent common scores
            this_team_common_scores = []
            opponent_common_scores = []

            for opponent in common_opponents:
                # Find the index of the row in opponents_table that matches current_team_schedule
                this_team_row_index = next(
                    (
                        j
                        for j in range(len(schedule_table))
                        if schedule_table[j][0] == this_team_schedule[0]
                    ),
                    None,
                )

                # Find the index of the column in current_team_schedule that matches the common_opponent
                this_team_column_index = this_team_schedule.index(opponent)

                if (
                    this_team_row_index is not None
                    and this_team_column_index is not None
                ):
                    # Get the value from scores_table at the calculated indices for the current team
                    current_score = scores_table[this_team_row_index][
                        this_team_column_index
                    ]
                    this_team_common_scores.append(current_score)

                # Find the index of the row in opponents_table that matches oppoonent_schedule
                opponent_row_index = next(
                    (
                        j
                        for j in range(len(schedule_table))
                        if schedule_table[j][0] == opponent_schedule[0]
                    ),
                    None,
                )

                # Find the index of the column in opposing_team_row that matches the common_opponent
                opponent_column_index = opponent_schedule.index(opponent)

                if opponent_row_index is not None and opponent_column_index is not None:
                    # Get the value from scores_table at the calculated indices for the opposing team
                    opponent_score = scores_table[opponent_row_index][
                        opponent_column_index
                    ]
                    opponent_common_scores.append(opponent_score)

            # Debug: Print the current and opponent common scores
            # print(f"Current common scores for Team {row[0]}: {this_team_common_scores}")
            # print(f"Opponent common scores for Team {opposing_team_id}: {opponent_common_scores}")

            # Subtract opponent_common_scores from this_team_common_scores
            scores_delta = [
                int(current) - int(opponent)
                for current, opponent in zip(
                    this_team_common_scores, opponent_common_scores
                )
            ]

            # Debug: Print the scores delta
            # print(f"Scores delta for Team {row[0]} against Team {schedule_table[opponent_row_index][0]}: {scores_delta}")

            # Calculate the average score delta
            score_delta = sum(scores_delta) / len(scores_delta) if scores_delta else 0

            # Calculate the projected score
            projected_score = FUDGE * score_delta / 2.0 + max_score / 2.0
            projected_score = min(
                max(projected_score, 0), max_score
            )  # Ensure the projected score is within bounds

            # Update the next_game cell in the scores_table
            scores_table[i][next_game_index] = round(projected_score, 2)
        else:
            # Debug: Print if no opposing team row is found
            print(f"No row found for opposing team_id: {opposing_team_id}")
            exit(1)

    return scores_table


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Parse an HTML file and process scores."
    )
    parser.add_argument("file_name", help="The name of the HTML file to parse.")
    parser.add_argument(
        "--fudge", type=float, default=1.0, help="Optional fudge factor (default: 1.0)"
    )

    # Parse the arguments
    args = parser.parse_args()

    # Use the FUDGE value from the arguments
    FUDGE = args.fudge

    try:
        # Read the HTML file
        with open(args.file_name, "r") as file:
            soup = BeautifulSoup(file, "html.parser")
        # Populate the schedule array, scores array, and max_score
        schedule_array = get_schedule(soup)
        scores_array = get_scores(soup)
        max_score = get_max_score(soup)
        while True:
            predicted_array = predict_scores(schedule_array, scores_array, max_score)
            if predicted_array == []:
                # Add a column with the sum of each row (excluding the first column)
                row_sums = []
                for row in scores_array:
                    row_sum = sum(
                        row[1:]
                    )  # Calculate the sum excluding the first column
                    row.append(row_sum)  # Append the sum to the row
                    row_sums.append(row_sum)

                # Calculate rankings based on row_sums
                sorted_sums = sorted(
                    row_sums, reverse=True
                )  # Sort sums in descending order
                ranks = {
                    value: rank + 1 for rank, value in enumerate(sorted_sums)
                }  # Map sums to ranks

                # Add the rank as a new column
                for row in scores_array:
                    row.append(
                        ranks[row[-1]]
                    )  # Use the last column (row_sum) to get the rank

                # Print the updated scores table
                for score_row in scores_array:
                    # Format each value in the row to 2 decimal places if it's a float
                    formatted_row = [
                        f"{value:.2f}" if isinstance(value, float) else str(value)
                        for value in score_row
                    ]
                    print("\t".join(formatted_row))
                exit()

    except FileNotFoundError:
        print(f"File '{args.file_name}' not found.")
    except Exception as error:  # Renamed 'e' to 'error' for consistency
        print(f"An error occurred: {error}")
