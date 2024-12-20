import streamlit as st
import pandas as pd
from datetime import timedelta

# Set the page configuration
st.set_page_config(
    page_title="Outlier Earnings Analyzer",
    layout="wide",
    initial_sidebar_state="auto",
)

# Title of the app
st.title("📈 Outlier Earnings Analyzer")

# File uploader
st.header("Upload your CSV file")
uploaded_file = st.file_uploader("Drag and drop your CSV file here", type=["csv"])

if uploaded_file is not None:
    try:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)

        # Check if required columns exist (case-insensitive)
        required_columns = ['workDate', 'payout']
        if not all(col in df.columns for col in required_columns):
            st.error("The CSV file must contain 'workDate' and 'payout' columns.")
        else:
            # Clean and convert 'payout' column
            # Remove any dollar signs and commas, then convert to float
            df['payout'] = df['payout'].replace('[\$,]', '', regex=True).astype(float)

            # Convert 'workDate' to datetime
            # Specify the format to match "Dec 17, 2024"
            df['workDate'] = pd.to_datetime(df['workDate'], format='%b %d, %Y', errors='coerce')

            # Drop rows with invalid 'workDate' entries
            df = df.dropna(subset=['workDate'])

            # Sort the DataFrame by 'workDate' in descending order
            df = df.sort_values('workDate', ascending=False)

            # Group by 'workDate' without sorting the group keys
            grouped = df.groupby(df['workDate'].dt.date, sort=False)

            # Calculate total earnings
            total_earnings = df['payout'].sum()

            # Calculate average earnings per workDate
            number_of_groups = grouped.ngroups
            average_earnings = total_earnings / number_of_groups if number_of_groups > 0 else 0

     
            # Calculate Current Pay Period
            # -------------------------------
            # Identify the most recent date
            most_recent_date = df['workDate'].max()
            
            # Determine the day of the week (Monday=0, Tuesday=1, ..., Sunday=6)
            day_of_week = most_recent_date.weekday()
            
            # Determine the start and end of the current pay period (Tuesday to Monday)
            if day_of_week >= 1:  # Day is Tuesday (1) or later
                pay_period_start = most_recent_date - pd.Timedelta(days=(day_of_week - 1))  # Tuesday of current week
            else:  # Day is Monday (0)
                pay_period_start = most_recent_date - pd.Timedelta(days=6)  # Previous Tuesday
            
            pay_period_end = pay_period_start + pd.Timedelta(days=6)  # Following Monday
            
            # Sum payouts from pay_period_start to pay_period_end, inclusive
            current_pay_period = df[
                (df['workDate'] >= pay_period_start) & (df['workDate'] <= pay_period_end)
            ]['payout'].sum()
            
            # Debugging prints (optional)
            # print("Most recent date:", most_recent_date)
            # print("Pay period start:", pay_period_start)
            # print("Pay period end:", pay_period_end)
            # print("Current pay period payout sum:", current_pay_period)

            # -------------------------------
            # Display Metrics in Three Columns
            # -------------------------------
            # Create three columns for total, average, and current pay period earnings
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(
                    f"""
                    <div style="background-color: #d4edda; padding: 20px; border-radius: 5px;">
                        <h3 style="color: #155724;">Total Earnings</h3>
                        <p style="color: #155724; font-size: 15px; margin-top: -10px;">From Dec 7, 2024</p>
                        <p style="color: #155724; font-size: 24px;">${total_earnings:,.2f}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown(
                    f"""
                    <div style="background-color: #fff3cd; padding: 20px; border-radius: 5px;">
                        <h3 style="color: #856404;">Daily Avarage</h3>
                        <p style="color: #856404; font-size: 15px; margin-top: -10px;">Estimated on {number_of_groups} days</p>
                        <p style="color: #856404; font-size: 24px;">${average_earnings:,.2f}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col3:
                st.markdown(
                    f"""
                    <div style="background-color: #d3d3d3; padding: 20px; border-radius: 5px;">
                        <h3 style="color: #4f4f4f;">This Pay Period</h3>
                        <p style="color: #4f4f4f; font-size: 15px; margin-top: -10px;">
                            {pay_period_start.strftime('%b %d, %Y')} - {pay_period_end.strftime('%b %d, %Y')}
                        </p>
                        <p style="color: #4f4f4f; font-size: 24px;">${current_pay_period:,.2f}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("---")  # Horizontal separator

            # Iterate through each group and display in an expander
            for name, group in grouped:
                # Format the date as "Dec 17, 2024"
                formatted_date = pd.to_datetime(name).strftime("%b %d, %Y")
                total_payout = group['payout'].sum()
                with st.expander(f"## {formatted_date} &nbsp; &nbsp; &nbsp; **Earnings: ${total_payout:.2f}**"):
                    st.dataframe(group.reset_index(drop=True))

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
else:
    st.info("Awaiting CSV file upload.")