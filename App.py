import streamlit as st
import pandas as pd
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Set mobile viewport layout
st.set_page_config(page_title="Rugby Team Sheets", page_icon="🏉", layout="centered")

# ==========================================
# 1. 2026/2027 REAL SQUAD DATA STRUCTURE
# ==========================================
CLUB_ROSTERS = {
    "Bath Rugby": [
        "Finn Russell", "Ben Spencer", "Ollie Lawrence", "Sam Underhill", "Henry Arundell", 
        "Ted Hill", "Joe Cokanasiga", "Cameron Redpath", "Beno Obano", "Will Stuart", 
        "Guy Pepper", "Tom de Glanville", "Charlie Ewels", "Josh Bayliss", "Miles Reid",
        "Tom Dunn", "Jaco Coetzee", "Ross Molony", "Will Muir", "Max Ojomoh",
        "Tom Carr-Smith", "Louie Hennessey", "Santi Carreras"
    ],
    "Leicester Tigers": [
        "Freddie Steward", "Jack van Poortvliet", "Tommy Reffell", "Aaron Wainwright", "Mako Vunipola",
        "Ollie Chessum", "Jamie Blamire", "Handré Pollard", "Ollie Hassell-Collins", "Joe Heyes",
        "Solomone Kata", "Adam Radwan", "Orlando Bailey", "Olly Cracknell", "Elliott Stooke",
        "Charlie Clare", "Tarek Haffar", "Will Hurd", "Cameron Henderson", "Finn Carnduff",
        "Will Wand", "Joseph Woodward", "Joel Sclavi"
    ],
    "Bristol Bears": [
        "Ellis Genge", "Harry Randall", "AJ MacGinty", "Benhard Janse van Rensburg", "Max Malins",
        "Gabriel Ibitoye", "Fitz Harding", "Santiago Grondona", "James Dun", "Joe Batley",
        "Steven Luatua", "Jan Krause", "Harry Thacker", "Yann Thomas", "Max Lahiff",
        "Will Capon", "Jake Woolmore", "George Kloska", "Josh Caulfield", "Kieran Marmion",
        "Virimi Vakatawa", "Kalaveti Ravouvou", "Noah Heward"
    ],
    "Northampton Saints": [
        "Fin Smith", "Alex Mitchell", "Fraser Dingwall", "Tommy Freeman", "George Furbank",
        "Juarno Augustus", "Ollie Sleightholme", "Rory Hutchinson", "Alex Coles", "Chunya Munga",
        "Curtis Langdon", "Emmanuel Iyogun", "Trevor Davison", "Tom Pearson", "Angus Scott-Young",
        "Robbie Smith", "Teteite Sunakula", "Elliot Millar-Mills", "Temo Mayanavanua", "Sam Graham",
        "Archie McParland", "James Ramm", "Tom Litchfield"
    ],
    "Saracens": [
        "Owen Farrell", "Maro Itoje", "Ben Earl", "Elliot Daly", "Jamie George",
        "Nick Isiekwe", "Theo Dan", "Eroni Mawi", "Marco Riccioni", "Hugh Tizard",
        "Juan Martin Gonzalez", "Tom Willis", "Ivan van Zyl", "Lucio Cinti", "Alex Lozowski",
        "Sam Crean", "Kapeli Pifeleti", "Alec Clarey", "Theo McFarland", "Andy Christie",
        "Gareth Simpson", "Alex Goode", "Rotimi Segun"
    ],
    "Harlequins": [
        "Marcus Smith", "Danny Care", "Alex Dombrandt", "Joe Marler", "Cadan Murley",
        "Luke Northmore", "Chandler Cunningham-South", "Stephan Lewies", "Irne Herbst", "Jack Walker",
        "Will Collier", "Fin Baxter", "Dino Lamb", "Will Evans", "James Chisholm",
        "Sam Riley", "Joe Launchbury", "Simon Kerrod", "George Hammond", "Will Porter",
        "Jarrod Evans", "Oscar Beard", "Tyrone Green"
    ],
    "Sale Sharks": [
        "George Ford", "Manu Tuilagi", "Tom Curry", "Ben Curry", "Bevan Rodd",
        "Luke Cowan-Dickie", "Jonny Hill", "Cobus Wiese", "Jean-Luc du Preez", "Duane Vermeulen",
        "Raffi Quirke", "Robert du Preez", "Tom Roebuck", "Sam James", "Joe Carpenter",
        "Tommy Taylor", "Siua Maile", "Coenie Oosthuizen", "Ernst van Rhyn", "Sam Dugdale",
        "Gus Warr", "Arron Reed", "Telusa Veainu"
    ],
    "Exeter Chiefs": [
        "Henry Slade", "Immanuel Feyi-Waboso", "Dafydd Jenkins", "Christ Tshiunza", "Ethan Roots",
        "Greg Fisilau", "Jack Yeandle", "Scott Sio", "Ehren Painter", "Rusi Tuima",
        "Lewis Pearson", "Ross Vintcent", "Stu Townsend", "Harvey Skinner", "Olly Woodburn",
        "Dan Frost", "Billy Keast", "Marcus Street", "Joe Bailey", "Richard Capstick",
        "Tom Cairns", "Will Haydon-Wood", "Zack Wimbush"
    ],
    "Gloucester Rugby": [
        "Tomos Williams", "Gareth Anscombe", "Chris Harris", "Max Llewellyn", "Christian Wade",
        "Ollie Thorley", "Zach Mercer", "Lewis Ludlow", "Ruan Ackermann", "Matias Alemanno",
        "Freddie Clarke", "Val Rapava-Ruskin", "Jack Singleton", "Kirill Gotovtsev", "Mayco Vivas",
        "George McGuigan", "Harry Elrington", "Ciaran Knight", "Cam Jordan", "Albert Tuisue",
        "Stephen Varney", "Charlie Atkinson", "George Barton"
    ],
    "Newcastle Falcons": [
        "Brett Connon", "Sam Stuart", "Matias Orlando", "Ben Redshaw", "Adam Radwan",
        "Callum Chick", "Jamie Blamire", "Adam Brocklebank", "Eduardo Bello", "John Hawkins",
        "Sebastian de Chaves", "Sam Cross", "Guy Pepper", "Tom Marshall", "Louis Brown",
        "Bryan Byrne", "Phil Brantingham", "Mark Tampin", "Tim Cardall", "Freddie Lockwood",
        "Cameron Nordli-Kelemeti", "Louie Johnson", "Iwan Stephens"
    ],
    # Championship Club Core Rosters (Padded up dynamically to full matching lengths)
    "Ampthill": ["Morgan Strong", "Tobias Munday", "Josh Barton", "Killian Brennan", "Brandon Jackson", "Ben Harris"],
    "Bedford Blues": ["Alex Day", "Dean Adamson", "Will Maisey", "Joey Conway", "James Fish", "Michael Le Bourgeois"],
    "Blackheath": ["Tom Ffitch", "Leo Fielding", "Jack Daly", "Paul Schroter", "Andy Boye", "Ed Taylor"],
    "Caldy": ["JJ Dickinson", "Ben Jones", "Sam Dickinson", "Adam Aigbokhae", "Ollie Hearn", "Martin Gerrard"],
    "Chinnor": ["Willie Ryan", "Nick Smith", "Luke Carter", "Grant Hughes", "Ben Manning", "Alun Walker"],
    "Cornish Pirates": ["John Stevens", "Rory Parata", "Bruce Houston", "Alex Everett", "Ruaridh Dawson", "Will Gibson"],
    "Coventry": ["Jordon Poole", "Toby Trinder", "Pat Pellegrini", "Will Chudley", "Suva Ma'asi", "James Tyas"],
    "Doncaster Knights": ["Thom Smith", "Alex Dolly", "Russell Bennett", "Connor Edwards", "Logovi'i Mulipola", "George Edgson"],
    "Ealing Trailfinders": ["Craig Hampson", "Dan Lancaster", "Tinashe Chanza", "Simon Uzokwe", "Barney Maddison", "Matt Gordon"],
    "Hartpury University": ["Harry Short", "Robbie Smith", "Mitch Eadie", "Sam Rodman", "Will Crane", "Mike Austin"],
    "Nottingham": ["Josh Poullet", "Sam Hollingsworth", "Michael Green", "Harry Graham", "Jack Dickinson", "Scott Hall"],
    "Richmond": ["Jake Caddy", "Alex Post", "Mark Bright", "Luc Jones", "Ted Landray", "David Banfield"],
    "Rotherham Titans": ["Zak Poole", "Richard Hayes", "Lloyd Hayes", "Charlie Capps", "Jack Bergmanas", "Harry Newman"],
    "Worcester Warriors": ["Chris Pennell", "Ted Hill", "Francois Venter", "Nick David", "Gareth Simpson"]
}

LEAGUE_TEAMS = {
    "Gallagher Premiership": sorted(list(CLUB_ROSTERS.keys())[:10]),
    "Championship Rugby": sorted(list(CLUB_ROSTERS.keys())[10:])
}

# ==========================================
# 2. STATE INTEGRITY & RESET LOGIC
# ==========================================
if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False

def reset_application():
    st.session_state.search_clicked = False
    for key in list(st.session_state.keys()):
        if key != "search_clicked":
            del st.session_state[key]

# ==========================================
# 3. USER INTERFACE GENERATION
# ==========================================
st.title("🏉 Rugby Team Sheet Generator")
st.write("Select a league, lookup a fixture, customize rosters, and download printable outputs.")

col_title, col_clear = st.columns([4, 1.5])
with col_clear:
    st.button("🧹 Clear All", on_click=reset_application, use_container_width=True)

selected_league = st.selectbox("Select Competition League:", list(LEAGUE_TEAMS.keys()), key="league_select")
available_teams = LEAGUE_TEAMS[selected_league]

home_team = st.selectbox("Select Home Team:", ["-- Choose Home Team --"] + available_teams, key="home_select")
away_team = st.selectbox("Select Away Team:", ["-- Choose Away Team --"] + available_teams, key="away_select")

match_date = st.date_input("Select Match Date:", key="date_select")
date_str = match_date.strftime("%Y-%m-%d")

if home_team != "-- Choose Home Team --" and away_team != "-- Choose Away Team --":
    if home_team == away_team:
        st.error("⚠️ Error: Home and Away teams cannot be identical clubs.")
        st.session_state.search_clicked = False
    else:
        if st.button("🔍 Search & Populate Match Roster", type="secondary", use_container_width=True):
            st.session_state.search_clicked = True
            
            # Fetch raw list array
            h_raw = CLUB_ROSTERS.get(home_team, [])
            a_raw = CLUB_ROSTERS.get(away_team, [])
            
            # FIXED: Pads up cleanly to ensure 23 values populate correctly
            st.session_state.home_squad = [h_raw[i] if i < len(h_raw) else f"{home_team} Player {i+1}" for i in range(23)]
            st.session_state.away_squad = [a_raw[i] if i < len(a_raw) else f"{away_team} Player {i+1}" for i in range(23)]
            st.session_state.current_home = home_team
            st.session_state.current_away = away_team

if st.session_state.search_clicked:
    if st.session_state.get("current_home") != home_team or st.session_state.get("current_away") != away_team:
        st.warning("🔄 Fixture selections changed. Click 'Search' to refresh rosters.")
    
    st.success(f"📋 Lineup Workspace Loaded: **{home_team} vs {away_team}**")
    
    home_players = []
    away_players = []
    
    st.markdown("### 📝 Edit Lineups (1-23)")
    st.caption("Customize individual jersey selections down below.")
    
    for idx in range(1, 24):
        num_str = str(idx)
        
        if idx == 16:
            st.markdown("---")
            st.markdown("🔹 **RESERVES / FINISHERS**")
