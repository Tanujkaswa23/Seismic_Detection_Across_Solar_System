import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the custom seismic detection functions from the notebook
def load_data(file):
    """
    Loads the seismic data from the uploaded file, ensuring the correct format.
    """
    try:
        # Read the CSV file
        data = pd.read_csv(file)

        # Display data preview
        st.write("Data preview:")
        st.write(data.head())

        # Check for the required columns
        if 'time_abs(%Y-%m-%dT%H:%M:%S.%f)' not in data.columns or 'velocity(m/s)' not in data.columns:
            raise ValueError("The data file must contain 'time_abs(%Y-%m-%dT%H:%M:%S.%f)' and 'velocity(m/s)' columns.")
        
        # Convert 'time_abs' to datetime
        data['time_abs'] = pd.to_datetime(data['time_abs(%Y-%m-%dT%H:%M:%S.%f)'], format='%Y-%m-%dT%H:%M:%S.%f')
        data['amplitude'] = data['velocity(m/s)']  # Renaming for easier use in detection logic

        return data
    except Exception as e:
        st.error(f"Error processing the file: {e}")
        return None

def detect_seismic_events(data, threshold):
    """
    Detects seismic events based on a threshold on the amplitude (velocity).
    """
    st.write("Detecting seismic events...")
    
    # Display the threshold
    st.write(f"Detection Threshold (velocity): {threshold}")

    # Detect seismic events where the velocity exceeds the threshold
    data['seismic_event'] = data['amplitude'] > threshold
    
    # Filter to get detected events
    detected_events = data[data['seismic_event']]
    
    # If no events detected, show a message
    if detected_events.empty:
        st.warning("No seismic events detected above the threshold.")
    
    return detected_events

def plot_seismic_data(data, detected_events):
    """
    Plots the seismic data with detected events, squaring the amplitude.
    """
    fig, ax = plt.subplots()

    # Square the velocity for plotting
    data['amplitude_squared'] = data['amplitude'] ** 2

    # Plot the squared velocity over time
    ax.plot(data['time_abs'], data['amplitude_squared'], label='Squared Velocity (m/s^2)', color='blue')
    
    # Highlight detected seismic events
    if not detected_events.empty:
        ax.scatter(detected_events['time_abs'], detected_events['amplitude'] ** 2, color='red', label='Detected Events')

    ax.set_xlabel('Time')
    ax.set_ylabel('Squared Velocity (m/s^2)')
    ax.set_title('Seismic Data with Detected Events (Squared Velocity)')
    ax.legend()

    st.pyplot(fig)

def filter_data_by_time(data, start_time, end_time):
    """
    Filters the data based on the selected time range.
    """
    # Filter data within the selected time range
    filtered_data = data[(data['time_abs'] >= start_time) & (data['time_abs'] <= end_time)]
    return filtered_data

# Streamlit app
def main():
    st.title("Seismic Event Detection App")

    # Upload file
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        # Load the data
        data = load_data(uploaded_file)

        if data is not None:
            st.success("File loaded successfully!")

            # Display data range for user reference
            min_val = float(data['amplitude'].min())
            max_val = float(data['amplitude'].max())
            st.write(f"Data range: Min Velocity: {min_val:.2e}, Max Velocity: {max_val:.2e}")

            # Set a step size based on data range to make slider usable
            step_size = (max_val - min_val) / 100  # Adaptive step size
            
            # Ensure the detection threshold is positive
            threshold = st.slider('Detection Threshold (velocity)', 
                                   min_value=min_val if min_val > 0 else 0.0,  # Handle negative min values
                                   max_value=max_val, 
                                   value=max_val * 0.1,  # Default value set to 10% of max_val
                                   step=step_size)  # Adaptive step size

            # Allow the user to select a start and end time for the plot
            st.write("Select time range for plotting:")
            start_time = st.selectbox("Start time", data['time_abs'].dt.strftime('%Y-%m-%d %H:%M:%S').unique())
            end_time = st.selectbox("End time", data['time_abs'].dt.strftime('%Y-%m-%d %H:%M:%S').unique())

            # Convert selected time strings back to datetime objects
            start_time = pd.to_datetime(start_time)
            end_time = pd.to_datetime(end_time)

            # Filter the data based on the selected time range
            filtered_data = filter_data_by_time(data, start_time, end_time)

            # Perform seismic event detection on the filtered data
            detected_events = detect_seismic_events(filtered_data, threshold)

            # Display detected events
            st.write("Detected Seismic Events:")
            if not detected_events.empty:
                st.write(detected_events)
            else:
                st.write("No events detected with the current threshold.")

            # Plot the filtered data and detected events
            plot_seismic_data(filtered_data, detected_events)

if __name__ == "__main__":
    main()
