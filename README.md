# CITS3403-Project

Bootstrap: https://getbootstrap.com/docs/5.0/components/dropdowns/

https://themewagon.com/themes/free-bootstrap-5-admin-dashboard-template-darkpan/

Project Overview

Spotify Sentiment Analyser is an innovative web application that harnesses the power of the Spotify and Genius APIs to provide users with deep insights into the emotional tone of the music they listen to. By analysing your listening history and performing sentiment analysis on song lyrics, the application delivers a personalized “mood profile” that reflects your musical tastes over time.

Project Description
The Spotify Sentiment Analyser is designed to explore the intersection of music, emotion, and data analytics. It achieves this by seamlessly integrating two powerful APIs:

Spotify API:
The application first connects to a user's Spotify account to fetch their listening history, playlists, and favorite tracks. Through Spotify’s OAuth authentication, users can securely grant access to their music data. This data forms the foundation of our analysis, offering a comprehensive view of the user’s listening patterns.

Genius API:
For every track in the user’s history, the application then queries the Genius API to retrieve the corresponding lyrics. Not every track may have available lyrics, so the system intelligently filters out those without complete data, ensuring the analysis remains accurate and meaningful.

Sentiment Analysis:
Once the lyrics are collected, the application employs sentiment analysis techniques using libraries such as TextBlob or VADER. This analysis examines the emotional tone of the lyrics—whether they’re positive, negative, or neutral. The outcome is an aggregate sentiment score that reflects the overall mood of the user’s musical preferences.

Personalised Insights:
Based on the sentiment scores, the application generates insightful reports and visualisations. For instance, users might receive a summary such as “You listen to music with moody lyrics” or see trends that reveal shifts in their musical mood over time. These insights can help users understand how their music choices correlate with their emotional well-being and even guide them toward discovering new music that aligns with their mood.

Key Features
User Authentication & Integration:
Securely connect to Spotify via OAuth to access a personalized listening history.

Automated Data Retrieval:
Automatically pull song data from Spotify and fetch corresponding lyrics from Genius, ensuring a smooth and hands-free user experience.

Robust Sentiment Analysis:
Apply natural language processing techniques to assess the sentiment of song lyrics and generate meaningful mood profiles.

Dynamic Visualizations:
Present data through engaging charts and graphs, allowing users to track their sentiment trends and compare different playlists or time periods.

Community Sharing & Comparison:
Enable users to share their mood profiles and sentiment insights with friends or the broader community, fostering discussions about music and emotional health.