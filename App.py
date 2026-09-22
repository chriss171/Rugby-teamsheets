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
# 1. 2026/2027 LEAGUE STRUCTURE
# ==========================================
LEAGUE_TEAMS = {
    "Gallagher Premiership": [
        "Bath Rugby", "Bristol Bears", "Exeter Chiefs", "Gloucester Rugby", 
        "Harlequins", "Leicester Tigers", "Newcastle Falcons", 
        "Northampton Saints", "Sale Sharks", "Saracens"
    ],
    "Championship Rugby": [
        "Ampthill", "Bedford Blues", "Blackheath", "Caldy", 
        "Chinnor", "Cornish Pirates", "Coventry", "Doncaster Knights", 
        "Ealing Trailfinders", "Hartpury University", "Nottingham", 
        "Richmond", "Rotherham Titans", "Worcester Warriors"
    ]
}

# Standard World Rugby Position Mapping (1-23)
POSITIONS_MAP = {
    "1": "Loosehead Prop", "2": "Hooker", "3": "Tighthead Prop",
    "4": "Second Row", "5": "Second Row", "6": "Blindside Flanker",
    "7": "Openside Flanker", "8": "Number 8", "9": "Scrum-Half",
    "10": "Fly-Half", "11": "Left Wing", "12": "Inside Centre",
    "13": "Outside Centre", "14": "Right Wing", "15": "Fullback",
    "16": "Repl. Hooker", "17": "Repl. Prop 1", "18": "Repl. Prop 2",
    "19": "Repl. Lock/Forward", "20": "Repl. Back Row", "21": "Repl. Scrum-Half",
    "22": "Repl. Fly-Half/Back", "23": "Repl. Outside Back"
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
# 3. USER INTERFACE (TOUCH RESIZING)
# ==========================================
st.title("🏉 Rugby Team Sheet Generator")
st.write("Select a league, lookup a fixture, customize rosters, and download printable outputs.")

# Clear UI Actions Row
col_title, col_clear = st.columns([4, 1.5])
with col_clear:
    st.button("🧹 Clear All", on_click=reset_application, use_container_width=True)

# Select League & Teams
selected_league = st.selectbox("Select Competition League:", list(LEAGUE_TEAMS.keys()), key="league_select")
available_teams = LEAGUE_TEAMS[selected_league]

home_team = st.selectbox("Select Home Team:", ["-- Choose Home Team --"] + available_teams, key="home_select")
away_team = st.selectbox("Select Away Team:", ["-- Choose Away Team --"] + available_teams, key="away_select")

match_date = st.date_input("Select Match Date:", key="date_select")
date_str = match_date.strftime("%Y-%m-%d")

# Search and Activation Logic
if home_team != "-- Choose Home Team --" and away_team != "-- Choose Away Team --":
    if home_team == away_team:
        st.error("⚠️ Error: Home and Away teams cannot be identical clubs.")
        st.session_state.search_clicked = False
    else:
        if st.button("🔍 Search & Populate Match Roster", type="secondary", use_container_width=True):
            st.session_state.search_clicked = True
            st.session_state.current_home = home_team
            st.session_state.current_away = away_team

# Display editor and download utilities once search completes successfully
if st.session_state.search_clicked:
    if st.session_state.get("current_home") != home_team or st.session_state.get("current_away") != away_team:
        st.warning("🔄 Fixture selections changed. Click 'Search' to refresh rosters.")
    
    st.success(f"📋 Lineup Workspace Loaded: **{home_team} vs {away_team}**")
    
    home_players = []
    away_players = []
    
    st.markdown("### 📝 Edit Lineups (1-23)")
    st.caption("Type directly inside any box to customize player selections.")
    
    for idx in range(1, 24):
        num_str = str(idx)
        pos_label = POSITIONS_MAP[num_str]
        
        # Injected visual divider for mobile layout clarity
        if idx == 16:
            st.markdown("---")
            st.markdown("🔹 **RESERVES / FINISHERS**")
            st.markdown("---")
            
        col1, col2 = st.columns(2)
        with col1:
            h_val = st.text_input(f"{home_team} No. {num_str} ({pos_label})", value=f"{home_team} Player {num_str}", key=f"h_field_{idx}")
            home_players.append(h_val)
        with col2:
            a_val = st.text_input(f"{away_team} No. {num_str} ({pos_label})", value=f"{away_team} Player {num_str}", key=f"a_field_{idx}")
            away_players.append(a_val)

    st.markdown("### 📥 Export Documents")
    action_col1, action_col2 = st.columns(2)

    # ==========================================
    # 4. EXPORT ENGINE: REPORTLAB PDF
    # ==========================================
    def generate_pdf_bytes():
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('TStyle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#1a365d'), alignment=1)
        sub_style = ParagraphStyle('SStyle', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#4a5568'), alignment=1)
        th_style = ParagraphStyle('THStyle', parent=styles['Normal'], fontSize=10, fontName="Helvetica-Bold", textColor=colors.white)
        tb_style = ParagraphStyle('TBStyle', parent=styles['Normal'], fontSize=9, fontName="Helvetica")
        pos_style = ParagraphStyle('PStyle', parent=styles['Normal'], fontSize=9, fontName="Helvetica-Bold", textColor=colors.HexColor('#4a5568'))
        
        elements = []
        elements.append(Paragraph("OFFICIAL MATCHDAY TEAM SHEET", title_style))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(f"<b>League:</b> {selected_league}  |  <b>Date:</b> {date_str}", sub_style))
        elements.append(Paragraph(f"<b>Fixture:</b> {home_team} vs {away_team}", sub_style))
        elements.append(Spacer(1, 15))
        
        table_data = [[
            Paragraph("#", th_style), Paragraph("Position", th_style), Paragraph(f"{home_team}", th_style),
            Paragraph("#", th_style), Paragraph(f"{away_team}", th_style)
        ]]
        
        # Track the precise index where the row subheader sits
        separator_row_idx = None
        
        for idx in range(1, 24):
            num_str = str(idx)
            pos = POSITIONS_MAP.get(num_str, "Player")
            p_home = home_players[idx-1]
            p_away = away_players[idx-1]
            
            # If we hit index 16, append the subheader row first
            if idx == 16:
                separator_row_idx = len(table_data)  # Track row index safely
                table_data.append([
                    Paragraph("-", tb_style), Paragraph("<b>RESERVES / FINISHERS</b>", pos_style), 
                    Paragraph("", tb_style), Paragraph("-", tb_style), Paragraph("", tb_style)
                ])
                
            table_data.append([
                Paragraph(num_str, tb_style), Paragraph(pos, pos_style), Paragraph(p_home, tb_style),
                Paragraph(num_str, tb_style), Paragraph(p_away, tb_style)
            ])
        
        col_widths = [25, 110, 185, 25, 185]
        lineup_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        t_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ])
        
        # Apply zebra striping and separator formatting based on strict structural indexes
        for r in range(1, len(table_data)):
            if r == separator_row_idx:
                t_style.add('BACKGROUND', (0, r), (-1, r), colors.HexColor('#edf2f7'))
                t_style.add('SPAN', (1, r), (2, r))
                t_style.add('SPAN', (3, r), (4, r))
            elif r % 2 == 0:
                t_style.add('BACKGROUND', (0, r), (-1, r), colors.HexColor('#f7fafc'))
                
        lineup_table.setStyle(t_style)
        elements.append(lineup_table)
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    # ==========================================
    # 5. EXPORT ENGINE: PLAIN TEXT SQUAD
    # ==========================================
    def generate_text_bytes():
        text_output = []
        text_output.append(f"MATCH DAY ROSTER — {selected_league.upper()}")
        text_output.append(f"Fixture: {home_team} vs {away_team}")
        text_output.append(f"Date: {date_str}\n")
        text_output.append(f"{'='*40}\n")
        
        text_output.append(f"🏠 {home_team.upper()} SQUAD:")
        text_output.append(f"{'-'*25}")
        for idx in range(1, 24):
            if idx == 16:
                text_output.append("\n[RESERVES]")
            text_output.append(f"{idx}. {POSITIONS_MAP[str(idx)]}: {home_players[idx-1]}")
            
        text_output.append(f"\n{'='*40}\n")
        text_output.append(f"🏃 {away_team.upper()} SQUAD:")
        text_output.append(f"{'-'*25}")
        for idx in range(1, 24):
            if idx == 16:
                text_output.append("\n[RESERVES]")

            
