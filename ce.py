import pandas as pd

def read_csv(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None

def calculate_pythagorean_win_rate(points_scored, points_allowed):
    """Calculate the pythagorean win rate using the 7.01 exponent"""
    if points_scored == 0 and points_allowed == 0:
        return 0.5  # Default value when no prior games
    return (points_scored**7.01) / ((points_scored**7.01) + (points_allowed**7.01))

# Read the CSV file
df = read_csv("games_2022 - games_2022.csv")
if df is None:
    exit()

# Initialize a dictionary to track team statistics
team_stats = {}

# Process games chronologically
for i in df.index:
    team = df.at[i, "team"]
    team_score = df.at[i, "team_score"]
    opp_score = df.at[i, "opponent_team_score"]

    # Check if the opponent is a D1 team (assuming there's a column "opponent_d1" with True/False)
    if "opponent_d1" in df.columns and not df.at[i, "opponent_d1"]:
        continue  # Skip non-D1 games entirely

score_diff = team_score - opp_score
    
    # Initialize team data if first appearance
    if team not in team_stats:
        team_stats[team] = {
            "points_scored": 0, 
            "points_allowed": 0, 
            "total_score": 0
        }
    
    # Calculate pythag win rate based on PREVIOUS games only
    pythag_win_rate = calculate_pythagorean_win_rate(
        team_stats[team]["points_scored"], 
        team_stats[team]["points_allowed"]
    )
    
    # Calculate game score based on the formula
    if score_diff > 0:  # Win
        game_score = (abs(score_diff)**(1/19)) * (1 - pythag_win_rate)
    elif score_diff < 0:  # Loss
        game_score = -(abs(score_diff)**(1/19)) * ((1 - pythag_win_rate)**2)
    else:  # Tie
        game_score = 0
    
    # Update team stats AFTER calculating this game's score
    team_stats[team]["points_scored"] += team_score
    team_stats[team]["points_allowed"] += opp_score
    team_stats[team]["total_score"] += game_score
    
    # Update the dataframe with results
    df.at[i, "pythag_win_rate"] = pythag_win_rate
    df.at[i, "game_score"] = game_score
    df.at[i, "cumulative_score"] = team_stats[team]["total_score"]

# Create team rankings
team_df = pd.DataFrame([
    {"Team": team, "Score": stats["total_score"]}
    for team, stats in team_stats.items()
])

# Sort by score
team_df = team_df.sort_values(by="Score", ascending=False)
print("Team Rankings:")
print(team_df)

# Display detailed team stats
print("\nDetailed Team Statistics:")
for team, stats in team_stats.items():
    print(f"{team}:")
    print(f"  Total Score: {stats['total_score']:.2f}")
    print(f"  Points Scored: {stats['points_scored']}")
    print(f"  Points Allowed: {stats['points_allowed']}")
    pythag = calculate_pythagorean_win_rate(stats['points_scored'], stats['points_allowed'])
    print(f"  Final Pythagorean Win Rate: {pythag:.4f}")
    print()

# Original dataframe with added scores
print("\nGame Details:")
print(df[["team", "team_score", "opponent_team_score", "pythag_win_rate", "game_score", "cumulative_score"]])
