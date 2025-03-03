import pandas as pd

def read_csv(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None

def calculate_pythagorean_win_rate(points_scored, points_allowed):
    """Calculate the pythagorean win rate using the 7.01 exponent."""
    if points_scored == 0 and points_allowed == 0:
        return 0.5  # Default value when no prior games
    return (points_scored ** 7.01) / ((points_scored ** 7.01) + (points_allowed ** 7.01))

# Read the CSV file
df = read_csv("games_2022 - games_2022.csv")
if df is None:
    exit()

# Initialize a dictionary to track aggregated team statistics
team_stats = {}

# Process each game in the DataFrame
for index, row in df.iterrows():
    # Skip non-D1 games if applicable (assumes column "opponent_d1" exists)
    if "opponent_d1" in df.columns and not row["opponent_d1"]:
        continue

    team = row["team"]
    opponent = row["opponent_team"]  # Assuming opponent team name is provided
    team_score = row["team_score"]
    opp_score = row["opponent_team_score"]
    score_diff = team_score - opp_score

    # Initialize team data if first appearance
    for t in [team, opponent]:
        if t not in team_stats:
            team_stats[t] = {"points_scored": 0, "points_allowed": 0, "total_score": 0}
    
    # Get the Pythagorean win rate of the opponent (or default if first game)
    opp_pythag_win_rate = calculate_pythagorean_win_rate(
        team_stats[opponent]["points_scored"],
        team_stats[opponent]["points_allowed"]
    )

    # Calculate game score based on the opponent's Pythagorean win rate
    if score_diff > 0:  # Win
        game_score = (abs(score_diff) ** (1/19)) * (1 - opp_pythag_win_rate)
    elif score_diff < 0:  # Loss
        game_score = -(abs(score_diff) ** (1/19)) * ((1 - opp_pythag_win_rate) ** 2)
    else:  # Tie
        game_score = 0

    # Update the aggregated statistics for the team AFTER calculating this game's score
    team_stats[team]["points_scored"] += team_score
    team_stats[team]["points_allowed"] += opp_score
    team_stats[team]["total_score"] += game_score
    
    # Also update the opponent's stats
    team_stats[opponent]["points_scored"] += opp_score
    team_stats[opponent]["points_allowed"] += team_score

# Build a final aggregated DataFrame with one row per team
aggregated_data = []
for team, stats in team_stats.items():
    final_pythag = calculate_pythagorean_win_rate(stats["points_scored"], stats["points_allowed"])
    aggregated_data.append({
        "Team": team,
        "Total Score": stats["total_score"],
        "Points Scored": stats["points_scored"],
        "Points Allowed": stats["points_allowed"],
        "Final Pythagorean Win Rate": final_pythag
    })

team_df = pd.DataFrame(aggregated_data)

# Sort teams by Total Score from highest to lowest
team_df = team_df.sort_values(by="Total Score", ascending=False).reset_index(drop=True)

# Insert a Rank column (starting at 1)
team_df.insert(0, "Rank", team_df.index + 1)

print("Team Rankings (sorted by Total Score):")
print(team_df)

# Print detailed team statistics in sorted order
print("\nDetailed Team Statistics (from highest to lowest Total Score):")
for _, row in team_df.iterrows():
    print(f"Rank {int(row['Rank'])}: {row['Team']}")
    print(f"  Total Score: {row['Total Score']:.2f}")
    print(f"  Points Scored: {row['Points Scored']}")
    print(f"  Points Allowed: {row['Points Allowed']}")
    print(f"  Final Pythagorean Win Rate: {row['Final Pythagorean Win Rate']:.4f}\n")

