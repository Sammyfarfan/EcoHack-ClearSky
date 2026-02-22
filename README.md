🌤 ClearSky Chelsea
Real-Time Community Air Health

ClearSky is an accessible, community-centered air quality tool built during EcoHack to help Chelsea residents answer one simple question:

Is it safe to go outside right now?

We transform real-time sensor data into clear, readable, and actionable information designed especially for older adults, families, and residents without technical backgrounds.

🌍 The Problem

Existing air quality dashboards are:

Overwhelming

Data-heavy

Hard to interpret

Not designed for seniors or non-technical users

Chelsea is a community heavily impacted by traffic, airport activity, and industrial emissions. Residents deserve clear, understandable air quality information — not cluttered scientific dashboards.

💡 Our Solution

ClearSky Chelsea provides:

🟢 Large, easy-to-read air quality status (Good / Moderate / Unhealthy)

📍 Location-based sensor selection

🗺 Interactive Chelsea-only map

📈 24-hour trend visualization

⚠️ Community alert for highest PM2.5 right now

♿ Accessible design focused on older adults

🔎 Searchable locations

📖 Transparent explanation of data limitations

We designed for clarity first, complexity second.

🫁 Why PM2.5?

PM2.5 refers to tiny air pollution particles that can:

Penetrate deep into the lungs

Enter the bloodstream

Increase risk of asthma and heart conditions

We focus on PM2.5 because it has the strongest evidence for direct health impacts.

🏗 Tech Stack

Python

Streamlit

Pandas

PyDeck (interactive maps)

Plotly

QuantAQ iSUPER API

📊 Data Source

Air quality data is sourced from community-deployed QuantAQ iSUPER sensors in Chelsea.

⚠️ Note:

Low-cost sensors may experience calibration drift or temporary gaps.

We display the most recent reading and a 24-hour trend for transparency.

♿ Accessibility & Ethics

ClearSky was designed to prioritize:

Human-centered simplicity

Large readable typography

Clear health messaging

Minimal cognitive load

Transparent data explanation

Community-first framing

We believe environmental data should empower — not intimidate.

How to Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

🏆 Built for EcoHack

Team: ClearSky

Focus: Accessible environmental intelligence

Community: Chelsea, MA
